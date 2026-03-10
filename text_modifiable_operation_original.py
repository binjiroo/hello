from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
import MeCab
import logging

logging.basicConfig(level=logging.DEBUG)

dic_path = "-d C:/MeCab-64/dic/UniDic"
tagger = MeCab.Tagger(dic_path)

class MainApp(App):
    def build(self):
        Window.bind(on_keyboard=self.on_keyboard)
        self.stopwatch_active = False
        self.stopwatch_time = 0
        self.always_on_top = False
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
        left_layout.add_widget(self.text_input)

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
        left_layout.add_widget(control_layout)

        slider_and_stopwatch_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        font_size_slider = Slider(min=10, max=32, step=2, value=14, size_hint_x=0.5)
        font_size_slider.bind(value=self.adjust_font_size)
        self.stopwatch_label = Label(text="00:00,00.00", font_size=24, size_hint_x=0.2)
        self.stopwatch_button = Button(text='開始', size_hint_x=0.1, height=50)
        self.stopwatch_button.bind(on_press=self.toggle_stopwatch)
        reset_button = Button(text='リセット', on_press=self.reset_stopwatch, size_hint_x=0.1)
        self.always_on_top_button = ToggleButton(text='off', size_hint_x=0.1)
        self.always_on_top_button.bind(on_press=self.toggle_always_on_top)
        slider_and_stopwatch_layout.add_widget(font_size_slider)
        slider_and_stopwatch_layout.add_widget(self.stopwatch_label)
        slider_and_stopwatch_layout.add_widget(self.stopwatch_button)
        slider_and_stopwatch_layout.add_widget(reset_button)
        slider_and_stopwatch_layout.add_widget(self.always_on_top_button)
        left_layout.add_widget(slider_and_stopwatch_layout)

        self.node_scroll_view = ScrollView(size_hint=(1, None), size=(400, 600))
        self.node_layout = GridLayout(cols=2, size_hint_y=None)
        self.node_layout.bind(minimum_height=self.node_layout.setter('height'))
        self.node_scroll_view.add_widget(self.node_layout)
        right_layout.add_widget(self.node_scroll_view)

        main_layout.add_widget(left_layout)
        main_layout.add_widget(right_layout)

        self.update_stats()
        return main_layout

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        if 'shift' in modifier:
            if codepoint in 'cvdaxs':
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
                self.text_input.focus = not self.text_input.focus
        return True

    def toggle_always_on_top(self, instance):
        if instance.state == "down":
            instance.text = "on"
            Window.always_on_top = True
        else:
            instance.text = "off"
            Window.always_on_top = False

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
        centiseconds = int(seconds * 100 % 100)
        self.stopwatch_label.text = f"{int(hours):02}:{int(minutes):02},{int(seconds):02}.{centiseconds:02}"

    def reset_stopwatch(self, instance):
        self.stopwatch_time = 0
        self.stopwatch_label.text = "00:00,00.00"
        Clock.unschedule(self.update_stopwatch)
        self.stopwatch_button.text = '開始'
        self.stopwatch_active = False

    def adjust_font_size(self, instance, value):
        self.text_input.font_size = value

    def reanalyze_text(self):
        cursor_index = self.text_input.cursor_row
        lines = self.text_input.text.split('\n')
        current_line = lines[cursor_index] if cursor_index < len(lines) else ""
        self.nodes = self.analyze_text(current_line, cursor_index)
        self.build_node_buttons()
        self.update_stats()

    def analyze_text(self, text, line_index):
        node_list = []
        try:
            text = text.replace('\n', ' ')
            result = tagger.parse(text)
            lines = result.split('\n')
            pos = 0  # 文字位置の初期化
            for line in lines:
                if line == 'EOS' or line == '':
                    continue
                node = line.split('\t')
                if len(node) >= 2:
                    word_info = node[0]
                    start_pos = pos
                    end_pos = pos + len(word_info)
                    node_list.append((word_info, start_pos, end_pos))
                    pos = end_pos  # 次のノードの開始位置を更新
        except Exception as e:
            logging.exception("MeCab解析エラー:", exc_info=e)
        return node_list

    def build_node_buttons(self):
        self.node_layout.clear_widgets()
        for node, start_pos, end_pos in self.nodes:
            button1 = Button(text=node, size_hint_y=None, height=30)
            button1.bind(on_press=self.on_node_button_click_1)
            button1.start_pos = start_pos
            button1.end_pos = end_pos
            button2 = Button(text=node, size_hint_y=None, height=30)
            button2.bind(on_press=self.on_node_button_click_2)
            button2.start_pos = start_pos
            button2.end_pos = end_pos
            self.node_layout.add_widget(button1)
            self.node_layout.add_widget(button2)

            # セル間のスペースを設定
            self.node_layout.spacing = 5
            # セルの内側の余白を設定
            button1.padding = (5, 5)
            button2.padding = (5, 5)

    def on_node_button_click_1(self, instance):
        cursor_index = self.text_input.cursor_row
        lines = self.text_input.text.split('\n')
        current_line = lines[cursor_index]

        start_pos = instance.start_pos
        end_pos = instance.end_pos

        if cursor_index > 0:
            lines[cursor_index - 1] += current_line[:end_pos]
            lines[cursor_index] = current_line[end_pos:]
        else:
            lines.insert(0, current_line[:end_pos])
            lines[cursor_index + 1] = current_line[end_pos:]

        self.update_text_input(lines)
        self.split_long_lines()  # 追加

        # 元の行を解析
        self.text_input.cursor = (0, cursor_index)
        self.reanalyze_text()

    def on_node_button_click_2(self, instance):
        cursor_index = self.text_input.cursor_row
        lines = self.text_input.text.split('\n')
        current_line = lines[cursor_index]

        start_pos = instance.start_pos
        end_pos = instance.end_pos

        if cursor_index < len(lines) - 1:
            lines[cursor_index + 1] = current_line[start_pos:] + lines[cursor_index + 1]
            lines[cursor_index] = current_line[:start_pos]
        else:
            lines.append(current_line[start_pos:])
            lines[cursor_index] = current_line[:start_pos]

        self.update_text_input(lines)
        self.split_long_lines()  # 追加

        # 移動先の行を解析
        self.text_input.cursor = (0, cursor_index + 1)
        self.reanalyze_text()

    def update_text_input(self, lines):
        self.text_input.text = '\n'.join(line for line in lines if line.strip() != '')
        self.update_stats()
        # 現在のカーソル位置の行を解析
        self.reanalyze_text()

    def split_long_lines(self):
        lines = self.text_input.text.split('\n')
        new_lines = []
        for line in lines:
            while len(line) > 30:
                new_lines.append(line[:30])
                line = line[30:]
            new_lines.append(line)
        self.text_input.text = '\n'.join(new_lines)
        self.update_stats()
        # 現在のカーソル位置の行を解析
        self.reanalyze_text()

    def reanalyze_specific_line(self, line_index):
        lines = self.text_input.text.split('\n')
        if line_index < len(lines):
            current_line = lines[line_index]
            self.nodes = self.analyze_text(current_line, line_index)
            self.build_node_buttons()
            self.update_stats()

    def new_file(self, *args):
        self.text_input.text = ''

    def update_text_input_height(self, *args):
        self.text_input.height = max(600, len(self.text_input.text.split('\n')) * 20)

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

if __name__ == '__main__':
    MainApp().run()
