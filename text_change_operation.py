from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.uix.screenmanager import Screen, ScreenManager
import MeCab
import logging
import csv
from functools import partial
import time

logging.basicConfig(level=logging.DEBUG)

# MeCab settings for the local dictionary
dic_path = "-d C:/MeCab-64/dic/UniDic"
tagger = MeCab.Tagger(dic_path)
mecab_local_dict_path = "C:/MeCab-64/dic/mydic/mydic.csv"

# Load local dictionary from CSV
def load_local_dictionary(path):
    local_dict = {}
    with open(path, encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header
        for row in reader:
            surface, reading, feature, _, candidates = row
            local_dict[surface] = candidates.strip('"').split(',')
    return local_dict

local_dict = load_local_dictionary(mecab_local_dict_path)

class TextChangeOperation(Screen):
    def __init__(self, **kwargs):
        super(TextChangeOperation, self).__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        Window.size = (1400, 750)
        Window.left = (Window.system_size[0] - Window.width) // 2
        Window.top = (Window.system_size[1] - Window.height) // 2

        main_layout = BoxLayout(orientation='horizontal')
        left_layout = BoxLayout(orientation='vertical', size_hint_x=0.9)
        right_layout = BoxLayout(orientation='vertical', size_hint_x=0.1)

        # Info Label
        self.info_label = Label(size_hint_y=None, height=30, font_size=24)

        # Main Text Area
        self.text_input = TextInput(size_hint_y=None, multiline=True, height=600)
        self.text_input.bind(on_text=self.update_text_input_info)
        self.text_input.bind(cursor_row=self.update_text_input_info)

        # Control Button Layout
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

        # Font Size Slider and Stopwatch Layout
        slider_stopwatch_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        font_size_slider = Slider(min=10, max=32, step=2, value=14, size_hint_x=0.5)
        font_size_slider.bind(value=self.adjust_font_size)
        slider_stopwatch_layout.add_widget(font_size_slider)

        # Stopwatch Label
        self.stopwatch_label = Label(text='00:00,00.00', size_hint_x=0.2, font_size=24)
        slider_stopwatch_layout.add_widget(self.stopwatch_label)

        # Stopwatch Buttons
        self.stopwatch_start_stop_button = Button(text='開始', size_hint_x=0.1)
        self.stopwatch_start_stop_button.bind(on_press=self.toggle_stopwatch)
        self.stopwatch_reset_button = Button(text='リセット', on_press=self.reset_stopwatch, size_hint_x=0.1)
        slider_stopwatch_layout.add_widget(self.stopwatch_start_stop_button)
        slider_stopwatch_layout.add_widget(self.stopwatch_reset_button)

        # Additional Button
        additional_button = Button(text='button', size_hint_x=0.1)
        slider_stopwatch_layout.add_widget(additional_button)

        left_layout.add_widget(self.info_label)
        left_layout.add_widget(self.text_input)
        left_layout.add_widget(control_layout)
        left_layout.add_widget(slider_stopwatch_layout)

        # Node Analysis Result Spinners
        self.node_scroll_view = ScrollView(size_hint=(1, None), size=(400, 600))
        self.node_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.node_layout.bind(minimum_height=self.node_layout.setter('height'))
        self.node_scroll_view.add_widget(self.node_layout)
        right_layout.add_widget(self.node_scroll_view)

        main_layout.add_widget(left_layout)
        main_layout.add_widget(right_layout)

        # Initialize Stopwatch
        self.stopwatch_active = False
        self.start_time = 0
        self.elapsed_time = 0

        # Update initial info
        self.update_text_input_info()

        # Register keyboard handler
        Window.bind(on_keyboard=self.on_keyboard)

        self.add_widget(main_layout)

    def on_keyboard(self, window, key, scancode, codepoint, modifiers):
        if 'shift' in modifiers:
            if codepoint == 'z':
                self.toggle_text_input_focus()
                return True
            elif codepoint == 'c':
                self.copy_text(None)
                return True
            elif codepoint == 'v':
                self.paste_text(None)
                return True
            elif codepoint == 'd':
                self.clear_text(None)
                return True
            elif codepoint == 'a':
                self.on_analyze_button_press(None)
                return True
            elif codepoint == 's':
                self.analyze_previous_line(None)
                return True
            elif codepoint == 'x':
                self.analyze_next_line(None)
                return True
            elif codepoint == 'q':
                self.toggle_stopwatch(None)
                return True
            elif codepoint == 'w':
                self.reset_stopwatch(None)
                return True
        return False  # 他のキーイベントの場合は伝播を続ける

    def toggle_text_input_focus(self):
        self.text_input.focus = not self.text_input.focus

    def adjust_font_size(self, instance, value):
        self.text_input.font_size = value

    def update_text_input_info(self, *args):
        text = self.text_input.text
        lines = text.split('\n')
        cursor_index = self.text_input.cursor_row
        current_line = lines[cursor_index] if cursor_index < len(lines) else ""

        # 総文字数と行数
        total_characters = len(text)
        total_lines = len(lines)

        # 総ノード数
        total_nodes = sum(len(self.analyze_text(line, idx)) for idx, line in enumerate(lines))

        # 現在の行の文字数とノード数
        current_line_characters = len(current_line)
        current_line_nodes = len(self.analyze_text(current_line, cursor_index))

        info_text = (f"総文字数: {total_characters}, 総行数: {total_lines}, "
                     f"総ノード数: {total_nodes}, "
                     f"行番号: {cursor_index}, "
                     f"文字数: {current_line_characters}, "
                     f"ノード数: {current_line_nodes}")

        self.info_label.text = info_text

    def toggle_stopwatch(self, instance):
        if instance is None:
            instance = self.stopwatch_start_stop_button  # ボタンのインスタンスを直接参照

        if self.stopwatch_active:
            self.stopwatch_active = False
            self.elapsed_time += time.time() - self.start_time
            instance.text = '開始'
            Clock.unschedule(self.update_stopwatch)
        else:
            self.stopwatch_active = True
            self.start_time = time.time()
            instance.text = '停止'
            Clock.schedule_interval(self.update_stopwatch, 0.01)

    def reset_stopwatch(self, instance):
        if instance is None:
            instance = self.stopwatch_reset_button  # ボタンのインスタンスを直接参照

        self.stopwatch_active = False
        self.elapsed_time = 0
        self.stopwatch_start_stop_button.text = '開始'
        self.stopwatch_label.text = '00:00,00.00'
        Clock.unschedule(self.update_stopwatch)

    def update_stopwatch(self, dt):
        current_time = time.time()
        elapsed = current_time - self.start_time + self.elapsed_time
        minutes, seconds = divmod(elapsed, 60)
        hundredths = int((seconds - int(seconds)) * 100)
        self.stopwatch_label.text = f'{int(minutes):02}:{int(seconds):02},{hundredths:02}'

    def new_file(self, instance):
        self.text_input.text = ""

    def copy_text(self, instance):
        Clipboard.copy(self.text_input.text)

    def paste_text(self, instance):
        self.text_input.text += Clipboard.paste()

    def clear_text(self, instance):
        self.text_input.text = ""

    def analyze_previous_line(self, instance):
        cursor_row = self.text_input.cursor_row
        if cursor_row > 0:
            self.text_input.cursor = (0, cursor_row - 1)
            self.perform_analysis(cursor_row - 1)

    def analyze_next_line(self, instance):
        cursor_row = self.text_input.cursor_row
        lines = self.text_input.text.split('\n')
        if cursor_row < len(lines) - 1:
            self.text_input.cursor = (0, cursor_row + 1)
            self.perform_analysis(cursor_row + 1)

    def on_analyze_button_press(self, instance):
        self.perform_analysis(self.text_input.cursor_row)

    def analyze_text(self, text, line_num):
        node = tagger.parseToNode(text)
        nodes = []
        pos = 0
        while node:
            surface = node.surface
            feature = node.feature.split(',')
            if feature[0] != 'BOS/EOS':
                start_pos = pos
                end_pos = pos + len(surface)
                nodes.append({
                    'surface': surface,
                    'feature': feature,
                    'start_pos': start_pos,
                    'end_pos': end_pos,
                    'line_num': line_num
                })
                pos = end_pos
            node = node.next
        return nodes

    def perform_analysis(self, line_num):
        text = self.text_input.text
        lines = text.split('\n')
        if 0 <= line_num < len(lines):
            line = lines[line_num]
            nodes = self.analyze_text(line, line_num)
            self.display_nodes(nodes)

    def display_nodes(self, nodes):
        self.node_layout.clear_widgets()
        for node in nodes:
            spinner = self.create_spinner(node)
            self.node_layout.add_widget(spinner)

    def create_spinner(self, node):
        surface = node['surface']
        candidates = local_dict.get(surface, [])
        if not candidates:
            candidates = [surface]  # デフォルトで surface を候補に含める
        spinner = Spinner(
            text=surface,
            values=candidates,
            size_hint_y=None,
            height=44,
            background_color=(0.5, 0.5, 0.5, 1)  # グレー色を設定
        )
        spinner.bind(text=partial(self.update_text_input, node))
        return spinner

    def update_text_input(self, node, spinner, selected_text):
        line_num = node['line_num']
        start_pos = node['start_pos']
        end_pos = node['end_pos']
        text = self.text_input.text
        lines = text.split('\n')
        if 0 <= line_num < len(lines):
            line = lines[line_num]
            new_line = line[:start_pos] + selected_text + line[end_pos:]
            lines[line_num] = new_line
            self.text_input.text = '\n'.join(lines)
        # ノードの更新
        self.perform_analysis(line_num)

class TextChangeOperationApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TextChangeOperation(name='TextChangeOperation'))
        return sm

if __name__ == '__main__':
    TextChangeOperationApp().run()
