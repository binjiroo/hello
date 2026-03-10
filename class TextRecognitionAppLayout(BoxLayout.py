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
from kivy.uix.screenmanager import ScreenManager, Screen
import MeCab
import logging

logging.basicConfig(level=logging.DEBUG)

# MeCabの初期設定を更新し、UniDic辞書を指定
dic_path = "-d C:/MeCab-64/dic/ipaDic"
tagger = MeCab.Tagger(dic_path)

class TextEditingOperation(Screen):
    def __init__(self, **kwargs):
        super(TextEditingOperation, self).__init__(**kwargs)
        self.saved_selection = None
        self.stopwatch_active = False
        self.stopwatch_time = 0
        self.always_on_top = False
        self.nodes = []  # Initialize self.nodes here

        try:
            self.tagger = MeCab.Tagger(dic_path)  # Instantiate the tagger object
            logging.debug("MeCab tagger initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize MeCab tagger: {e}")

        self.build_ui()

    def build_ui(self):
        Window.bind(on_keyboard=self.on_keyboard)

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
        self.text_input.bind(focus=self.on_text_input_focus)

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
        self.always_on_top_button = ToggleButton(text='off', size_hint_x=0.1)
        self.always_on_top_button.bind(on_press=self.toggle_always_on_top)

        slider_and_stopwatch_layout.add_widget(font_size_slider)
        slider_and_stopwatch_layout.add_widget(self.stopwatch_label)
        slider_and_stopwatch_layout.add_widget(self.stopwatch_button)
        slider_and_stopwatch_layout.add_widget(reset_button)
        slider_and_stopwatch_layout.add_widget(self.always_on_top_button)

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

        self.add_widget(main_layout)

        self.update_stats()  # Ensure self.nodes is initialized before calling this method

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        if 'shift' in modifier:
            if codepoint == 'e':
                self.select_previous_node()
            elif codepoint == 'r':
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
                self.text_input.focus = not self.text_input.focus
                if self.text_input.focus and self.saved_selection:
                    self.text_input.select_text(*self.saved_selection)
        return True

    def on_text_input_focus(self, instance, value):
        if value:
            self.text_input.focus = True
        else:
            self.text_input.focus = False

    def select_previous_node(self):
        if self.saved_selection:
            start, end = self.saved_selection
            lines = self.text_input.text.split('\n')
            line_index = sum(len(line) + 1 for line in lines[:self.text_input.cursor_row])
            cursor_index = start - line_index - 1
            for node in self.nodes:
                surface, _, _, node_start, node_end, _ = node
                if node_start <= cursor_index < node_end:
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
            for node in self.nodes:
                surface, _, _, node_start, node_end, _ = node
                if node_start <= cursor_index < node_end:
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

    def copy_text(self, *args):
        Clipboard.copy(self.text_input.text)

    def paste_text(self, *args):
        self.text_input.text += Clipboard.paste()

    def clear_text(self, *args):
        self.text_input.text = ""

    def on_analyze_button_press(self, *args):
        if self.text_input.text.strip():
            self.reanalyze_text()
        else:
            logging.debug("TextInput is empty. No analysis performed.")

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
        self.stopwatch_label.text = f"{int(hours):02}:{int(minutes):02},{seconds:05.2f}"

    def reset_stopwatch(self, instance):
        self.stopwatch_time = 0
        self.stopwatch_label.text = "00:00,00.00"

    def adjust_font_size(self, instance, value):
        self.text_input.font_size = value

    def update_text_input_height(self, instance, value):
        instance.height = len(instance._lines) * instance.line_height

    def reanalyze_text(self):
        self.node_layout.clear_widgets()  # Clear existing node buttons
        lines = self.text_input.text.split('\n')
        self.nodes = []  # Clear the node list

        logging.debug(f"Analyzing text: {self.text_input.text}")

        cursor_index = self.text_input.cursor_row  # Get the index of the selected line
        current_line = lines[cursor_index] if cursor_index < len(lines) else ""  # Get the text of the selected line

        node = self.tagger.parseToNode(current_line)  # Parse only the selected line
        start_pos = 0  # Initialize the node start position
        while node:
            if node.surface != '':
                surface = node.surface
                logging.debug(f"Node surface: {surface}, Feature: {node.feature}")
                end_pos = start_pos + len(surface)
                self.nodes.append((surface, node.feature, start_pos, end_pos, cursor_index))
                button = Button(text=surface, size_hint_y=None, height=40)
                button.bind(on_press=self.create_button_callback(start_pos, end_pos))
                self.node_layout.add_widget(button)
                start_pos = end_pos  # Update the start position for the next node
            node = node.next

        # Count the total number of nodes in all text
        total_nodes = sum(1 for line in lines for node in self.tagger.parse(line).split('\n') if node)
        self.update_stats(total_nodes=total_nodes)  # Pass the node count to update_stats
        logging.debug(f"Nodes: {self.nodes}")

    def create_button_callback(self, start, end):
        def callback(instance, start=start, end=end):  # 固定化した値を関数内で使用する
            print(f"Clicked node button for text from {start} to {end}")
            self.highlight_text(start, end)
        return callback

    def highlight_text(self, start, end):
        # カーソルの行番号と行内のカーソル位置を取得
        cursor_row, cursor_col = self.text_input.cursor
        cursor_index = sum(len(line) + 1 for line in self.text_input.text.split('\n')[:cursor_row]) + cursor_col

        # ノードの開始位置と終了位置を計算
        start += cursor_index
        end += cursor_index

        # 選択されたテキストの開始位置と終了位置を計算
        start_line = self.text_input.text.rfind('\n', 0, start) + 1
        end_line = self.text_input.text.find('\n', end)
        if end_line == -1:
            end_line = len(self.text_input.text)

        start_pos = start - start_line
        end_pos = end - start_line

        # 選択されたテキストをハイライト
        self.text_input.focus = True
        self.text_input.cursor = (start_line, start_pos)
        self.text_input.select_text(start, end)

        # 選択状態を維持するため、選択範囲の開始位置を記憶
        self.selection_from = start

        print(f"Selected text from {start} to {end} in line {cursor_row}")

        # デバッグログ
        print(f"Cursor row: {cursor_row}, Cursor index: {cursor_index}")
        print(f"Start line: {start_line}, End line: {end_line}, Start pos: {start_pos}, End pos: {end_pos}")

    def on_text_input_change(self, instance, value):
        self.reanalyze_text()

    def new_file(self, *args):
        self.text_input.text = ""
        self.node_layout.clear_widgets()

    def update_stats(self, total_nodes=None, *args):
        total_chars = len(self.text_input.text)
        total_lines = len(self.text_input.text.split('\n'))
        current_line_num = self.text_input.cursor_row + 1
        current_line = self.text_input.text.split('\n')[self.text_input.cursor_row]
        current_line_chars = len(current_line)
        current_line_nodes = sum(1 for node in self.nodes if node[2] == self.text_input.cursor_row)

        if total_nodes is None:
            total_nodes = len(self.nodes)

        stats_text = f"総文字数: {total_chars} | 総node数: {total_nodes} | 総行数: {total_lines} | " \
                    f"現在の行番号: {current_line_num} | 現在の行の文字数: {current_line_chars} | 現在の行のnode数: {current_line_nodes}"
        self.stats_label.text = stats_text

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TextEditingOperation(name='TextEditingOperation'))
        return sm

if __name__ == '__main__':
    MyApp().run()
