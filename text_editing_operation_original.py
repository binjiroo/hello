from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.togglebutton import ToggleButton
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
import MeCab
import logging

logging.basicConfig(level=logging.DEBUG)

# MeCabの初期設定を更新し、UniDic辞書を指定
dic_path = "-d C:/MeCab-64/dic/UniDic"
tagger = MeCab.Tagger(dic_path)

class MainApp(App):
    def build(self):
        Window.bind(on_keyboard=self.on_keyboard)
        self.saved_selection = None  # Add this line to initialize saved selection

        self.stopwatch_active = False
        self.stopwatch_time = 0
        # Always-on-top state attribute
        self.always_on_top = False  # Track always-on-top state

        Window.size = (1400, 750)
        Window.left = (Window.system_size[0] - Window.width) // 2
        Window.top = (Window.system_size[1] - Window.height) // 2

        main_layout = BoxLayout(orientation='horizontal')
        left_layout = BoxLayout(orientation='vertical', size_hint_x=0.9)
        right_layout = BoxLayout(orientation='vertical', size_hint_x=0.1)

        self.stats_label = Label(text='', font_size=24, size_hint_y=None, height=40)
        left_layout.add_widget(self.stats_label)

        self.text_input = TextInput(size_hint_y=None, multiline=True, height=600)
        self.text_input.bind(on_text=self.update_text_input_height)
        self.text_input.bind(cursor_row=self.update_stats)
        self.text_input.bind(text=self.on_text_input_change)  # Bind the text change event

        control_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        control_layout.add_widget(Button(text='新規作成', on_press=self.new_file))
        control_layout.add_widget(Button(text='開く'))
        control_layout.add_widget(Button(text='名付けて保存'))
        control_layout.add_widget(Button(text='保存'))
        control_layout.add_widget(Button(text='コピー', on_press=self.copy_text))
        control_layout.add_widget(Button(text='ペースト', on_press=self.paste_text))
        control_layout.add_widget(Button(text='クリア', on_press=self.clear_text))
        control_layout.add_widget(Button(text='解析開始', on_press=self.on_analyze_button_press))
        control_layout.add_widget(Button(text='上行解析', on_press=self.analyze_previous_line))
        control_layout.add_widget(Button(text='下行解析', on_press=self.analyze_next_line))

        slider_and_stopwatch_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)

        font_size_slider = Slider(min=10, max=32, step=2, value=14, size_hint_x=0.5)
        font_size_slider.bind(value=self.adjust_font_size)

        self.stopwatch_label = Label(text="00:00,00.00", font_size=24, size_hint_x=0.2)
        self.stopwatch_button = Button(text='開始', size_hint_x=0.1, height=50)
        self.stopwatch_button.bind(on_press=self.toggle_stopwatch)

        reset_button = Button(text='リセット', on_press=self.reset_stopwatch, size_hint_x=0.1)
        self.always_on_top_button = ToggleButton(text='off', size_hint_x=0.1)  # Initialize with "off"
        self.always_on_top_button.bind(on_press=self.toggle_always_on_top)

        slider_and_stopwatch_layout.add_widget(font_size_slider)
        slider_and_stopwatch_layout.add_widget(self.stopwatch_label)
        slider_and_stopwatch_layout.add_widget(self.stopwatch_button)
        slider_and_stopwatch_layout.add_widget(reset_button)
        slider_and_stopwatch_layout.add_widget(self.always_on_top_button)  # Add the always-on-top button

        left_layout.add_widget(self.text_input)
        left_layout.add_widget(control_layout)
        left_layout.add_widget(slider_and_stopwatch_layout)

        self.node_scroll_view = ScrollView(size_hint=(1, None), size=(400, 600))
        self.node_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.node_layout.bind(minimum_height=self.node_layout.setter('height'))
        self.node_scroll_view.add_widget(self.node_layout)
        right_layout.add_widget(self.node_scroll_view)

        main_layout.add_widget(left_layout)
        main_layout.add_widget(right_layout)

        self.update_stats()

        return main_layout

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        if 'shift' in modifier:
            print("Codepoint:", codepoint)  # codepointの値を出力
            if codepoint == 'e':  # Change 'e' to 'E' for uppercase 'E'
                self.select_previous_node()
            elif codepoint == 'r':  # Change 'r' to 'R' for uppercase 'R'
                self.select_next_node()
            elif codepoint in 'cvdaxs':
                self.text_input.focus = False
                if codepoint == 'c':
                    self.copy_text(None)
                elif codepoint == 'v':
                    self.paste_text(None)
                elif codepoint == 'd':
                    self.clear_text(None)
                elif codepoint == 'a':
                    self.on_analyze_button_press(None)
                elif codepoint == 's':
                    self.analyze_previous_line(None)
                elif codepoint == 'x':
                    self.analyze_next_line(None)
            elif codepoint == 'q':
                self.toggle_stopwatch(None)
            elif codepoint == 'w':
                self.reset_stopwatch(None)
            elif codepoint == 'z':
                self.text_input.focus = not self.text_input.focus  # Toggle the focus of the TextInput
                if self.text_input.focus and self.saved_selection:
                    # Restore the saved selection range if focus is on the text input
                    self.text_input.select_text(*self.saved_selection)
        return True  # イベントを続けて伝播させない

    def select_previous_node(self):
        if self.saved_selection:
            start, end = self.saved_selection
            lines = self.text_input.text.split('\n')
            line_index = sum(len(line) + 1 for line in lines[:self.text_input.cursor_row])
            cursor_index = start - line_index - 1  # Cursor index should start from 0
            print("Cursor Index:", cursor_index)  # cursor_indexの値を出力
            for node in self.nodes:
                surface, _, _, node_start, node_end, _ = node
                if node_start <= cursor_index < node_end:
                    print("Selected Node:", surface, node_start, node_end)  # 選択されたノードの情報を出力
                    new_end = node_start + len(surface) + line_index
                    self.saved_selection = (node_start + line_index, new_end)
                    self.text_input.select_text(*self.saved_selection)
                    break

    def select_next_node(self):
        if self.saved_selection:
            start, end = self.saved_selection
            lines = self.text_input.text.split('\n')
            line_index = sum(len(line) + 1 for line in lines[:self.text_input.cursor_row])
            cursor_index = start - line_index
            print("Cursor Index:", cursor_index)  # cursor_indexの値を出力
            for node in self.nodes:
                surface, _, _, node_start, node_end, _ = node
                if node_start <= cursor_index < node_end:
                    print("Selected Node:", surface, node_start, node_end)  # 選択されたノードの情報を出力
                    new_start = node_end + line_index
                    self.saved_selection = (new_start, node_end + len(surface) + line_index)
                    self.text_input.select_text(*self.saved_selection)
                    break

    def toggle_always_on_top(self, instance):
        if instance.state == "down":
            instance.text = "on"
            Window.always_on_top = True
        else:
            instance.text = "off"
            Window.always_on_top = False

    # 以下の関数は、ボタンの操作と同じように定義されていますが、パラメータを取り除いて直接呼び出せるようにしています。
    def copy_text(self, *args):
        Clipboard.copy(self.text_input.text)

    def paste_text(self, *args):
        self.text_input.text += Clipboard.paste()

    def clear_text(self, *args):
        self.text_input.text = ""

    def on_analyze_button_press(self, *args):
        self.reanalyze_text()

    def analyze_previous_line(self, *args):
        current_row = self.text_input.cursor_row
        if current_row > 0:
            self.text_input.cursor = (0, current_row - 1)
            self.reanalyze_text()

    def analyze_next_line(self, *args):
        current_row = self.text_input.cursor_row
        lines = self.text_input.text.split('\n')
        if current_row < len(lines) - 1:
            self.text_input.cursor = (0, current_row + 1)
            self.reanalyze_text()
    
    def toggle_stopwatch(self, instance):
        if self.stopwatch_active:
            self.stopwatch_button.text = '開始'
            Clock.unschedule(self.update_stopwatch)
        else:
            self.stopwatch_button.text = '停止'
            Clock.schedule_interval(self.update_stopwatch, 0.01)
        self.stopwatch_active = not self.stopwatch_active

    def update_stopwatch(self, dt):
        self.stopwatch_time += dt
        minutes, seconds = divmod(self.stopwatch_time, 60)
        hours, minutes = divmod(minutes, 60)
        centiseconds = int((seconds - int(seconds)) * 100)
        self.stopwatch_label.text = f"{int(hours):02}:{int(minutes):02},{int(seconds):02}.{centiseconds:02}"

    def reset_stopwatch(self, instance):
        self.stopwatch_time = 0
        self.stopwatch_label.text = "00:00,00.00"
        Clock.unschedule(self.update_stopwatch)
        self.stopwatch_button.text = '開始'
        self.stopwatch_active = False

    def adjust_font_size(self, instance, value):
        self.text_input.font_size = value

    def on_analyze_button_press(self, instance):
        self.reanalyze_text()

    def reanalyze_text(self):
        cursor_index = self.text_input.cursor_row
        lines = self.text_input.text.split('\n')
        current_line = lines[cursor_index] if cursor_index < len(lines) else ""
        self.nodes = self.analyze_text(current_line, cursor_index)
        self.build_node_buttons()
        self.update_stats()

    def analyze_previous_line(self, instance):
        current_row = self.text_input.cursor_row
        if current_row > 0:
            self.text_input.cursor = (0, current_row - 1)
            self.reanalyze_text()

    def analyze_next_line(self, instance):
        current_row = self.text_input.cursor_row
        lines = self.text_input.text.split('\n')
        if current_row < len(lines) - 1:
            self.text_input.cursor = (0, current_row + 1)
            self.reanalyze_text()

    def build_node_buttons(self):
        self.node_layout.clear_widgets()
        for node in self.nodes:
            surface, feature, reading, start, end, line_index = node
            button = Button(text=surface, size_hint_y=None, height=44)
            button.font_size = 14
            button.bind(on_release=lambda btn, s=start, e=end, l=line_index: self.edit_node_text(s, e, l))
            self.node_layout.add_widget(button)

    def edit_node_text(self, start, end, line_index):
        lines = self.text_input.text.split('\n')
        line_start_index = sum(len(line) + 1 for line in lines[:line_index])
        self.text_input.focus = True
        self.text_input.select_text(line_start_index + start, line_start_index + end)
        self.text_input.cursor = (line_start_index + start, line_index)
        self.saved_selection = (line_start_index + start, line_start_index + end)  # Save the selection range

    def analyze_text(self, text, line_index):
        mecab = MeCab.Tagger("-Ochasen")
        parsed = mecab.parse(text)
        nodes = []
        current_position = 0
        for chunk in parsed.splitlines()[:-1]:
            cols = chunk.split('\t')
            if len(cols) >= 6:
                surface, feature, reading = cols[0], cols[3], cols[1]
                start_position = current_position
                end_position = start_position + len(surface)
                current_position += len(surface)
                nodes.append((surface, feature, reading, start_position, end_position, line_index))
        return nodes

    def update_text_input_height(self, instance, value):
        lines = len(value.split('\n'))
        line_height = 30
        new_height = lines * line_height
        instance.height = max(new_height, 600)
        self.update_stats()

    def new_file(self, instance):
        self.text_input.text = ""

    def copy_text(self, instance):
        Clipboard.copy(self.text_input.text)

    def paste_text(self, instance):
        self.text_input.text += Clipboard.paste()

    def clear_text(self, instance):
        self.text_input.text = ""

    def update_stats(self, *args):
        total_chars = len(self.text_input.text)
        total_lines = len(self.text_input.text.split('\n'))
        cursor_line = self.text_input.cursor_row
        current_line_text = self.text_input.text.split('\n')[cursor_line] if cursor_line < total_lines else ''
        current_line_chars = len(current_line_text)
        self.nodes = self.analyze_text(current_line_text, cursor_line)
        current_line_nodes = len(self.nodes)
        all_nodes = sum(len(self.analyze_text(line, index)) for index, line in enumerate(self.text_input.text.split('\n')))
        stats_text = (
            f"総文字数: {total_chars} | "
            f"総行数: {total_lines} | "
            f"総ノード数: {all_nodes} | "
            f"現在行: {cursor_line + 1} | "
            f"文字数: {current_line_chars} | "
            f"ノード数: {current_line_nodes}"
        )
        self.stats_label.text = stats_text

    def on_text_input_change(self, instance, value):
        self.reanalyze_text()  # Reanalyze the text whenever it changes

if __name__ == '__main__':
    MainApp().run()