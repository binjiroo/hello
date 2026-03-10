from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.togglebutton import ToggleButton
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import MeCab
import logging

logging.basicConfig(level=logging.DEBUG)

# MeCabの初期設定を更新し、UniDic辞書を指定
dic_path = "-d C:/MeCab-64/dic/ipaDic"
tagger = MeCab.Tagger(dic_path)

class JapaneseTextInput(TextInput):
    def __init__(self, **kwargs):
        super(JapaneseTextInput, self).__init__(**kwargs)
        self._composition_text = ""
        Window.bind(on_textedit=self._on_textedit)

    def _on_textedit(self, window, ime_text):
        if self.focus:
            logging.debug(f"_on_textedit: Received ime_text: {ime_text}")
            cursor_position = self.cursor_index()
            text_before_cursor = self.text[:cursor_position - len(self._composition_text)]
            text_after_cursor = self.text[cursor_position:]
            self._composition_text = ime_text
            logging.debug(f"Before update: text='{self.text}', cursor_position={cursor_position}, composition_text='{self._composition_text}'")

            # First, complete the expression
            self.text = text_before_cursor + self._composition_text + text_after_cursor

            # Then clear the text_before_cursor part
            self.text = self._composition_text + text_after_cursor
            new_cursor_position = len(self._composition_text)
            self.cursor = (new_cursor_position, 0)
            logging.debug(f"After update: text='{self.text}', cursor={self.cursor}")

    def insert_text(self, substring, from_undo=False):
        cursor_position = self.cursor_index()
        logging.debug(f"insert_text: substring={substring}, from_undo={from_undo}, cursor_position={cursor_position}")
        super(JapaneseTextInput, self).insert_text(substring, from_undo)
        self._composition_text = ""  # リセット
        logging.debug(f"After insert_text: text='{self.text}', cursor={self.cursor}")

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        logging.debug(f"keyboard_on_key_down: keycode={keycode}, text={text}, modifiers={modifiers}")
        if keycode[1] == 'enter' and self._composition_text:
            self._composition_text = ""
        return super(JapaneseTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)

class TextEditingOperation(Screen):
    def __init__(self, **kwargs):
        super(TextEditingOperation, self).__init__(**kwargs)
        self.saved_selection = None
        self.stopwatch_active = False
        self.stopwatch_time = 0
        self.always_on_top = False
        self.nodes = []

        try:
            self.tagger = MeCab.Tagger(dic_path)
            logging.debug("MeCab tagger initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize MeCab tagger: {e}")

        self.generated_text_buttons = []
        self.bracket_buttons = []
        self.symbol_buttons = []

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

        self.text_input = JapaneseTextInput(size_hint_y=None, multiline=True, height=600)
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
        control_layout.add_widget(Button(text='前挿入', on_press=self.insert_text_at_line_start))
        control_layout.add_widget(Button(text='両端挿入', on_press=self.wrap_text_in_brackets))
        control_layout.add_widget(Button(text='後挿入', on_press=self.insert_text_at_line_end))

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

        self.node_scroll_view = ScrollView(size_hint=(1, None), size=(400, Window.height - 50))
        self.node_layout = GridLayout(cols=1, size_hint_y=None, spacing=0)
        self.node_layout.bind(minimum_height=self.node_layout.setter('height'))
        self.node_scroll_view.add_widget(self.node_layout)
        right_layout.add_widget(self.node_scroll_view)

        input_button_layout = BoxLayout(orientation='vertical', size_hint_y=0.3, height=40)
        self.input_form = TextInput(size_hint_y=None, height=40, multiline=False)
        input_button_layout.add_widget(self.input_form)
        self.generate_button = ToggleButton(text='生成', on_press=self.generate_text_button, height=40)
        input_button_layout.add_widget(self.generate_button)
        self.clear_button = Button(text='クリア', on_press=self.clear_input_form, height=40)
        input_button_layout.add_widget(self.clear_button)
        right_layout.add_widget(input_button_layout)

        bracket_buttons_layout = self.add_bracket_buttons()
        right_layout.add_widget(bracket_buttons_layout)

        symbol_buttons_layout = self.add_symbol_buttons()
        right_layout.add_widget(symbol_buttons_layout)

        self.node_scroll_view.size_hint_y = 1
        self.node_scroll_view.size = (400, Window.height)

        main_layout.add_widget(left_layout)
        main_layout.add_widget(right_layout)

        self.add_widget(main_layout)

        self.generated_buttons = []

        self.update_stats()

        return Builder.load_file('imeapp.kv')

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
                    self.insert_text_at_line_start(None)
                elif codepoint == 's':
                    self.wrap_text_in_brackets(None)
                elif codepoint == 'x':
                    self.insert_text_at_line_end(None)
            elif codepoint == 'q':
                self.toggle_stopwatch(None)
            elif codepoint == 'w':
                self.reset_stopwatch(None)
            elif codepoint == 'z':
                self.text_input.focus = not self.text_input.focus
                if self.text_input.focus and self.saved_selection:
                    self.text_input.select_text(*self.saved_selection)
        return True

    def add_bracket_buttons(self):
        brackets = ['[]', '()', '{}', '「」', '【】', '『』']
        grid_layout = GridLayout(cols=2, spacing=0, size_hint_y=0.5)
        for bracket in brackets:
            button = ToggleButton(text=bracket, on_press=self.insert_brackets)
            grid_layout.add_widget(button)
            self.bracket_buttons.append(button)
        return grid_layout

    def insert_brackets(self, instance):
        if instance.state == 'down':
            self.input_form.text += instance.text
        else:
            self.input_form.text = self.input_form.text.replace(instance.text, '')

    def add_symbol_buttons(self):
        symbols = [';', ':', ',', '.', '、', '。']  # Add more symbols as needed
        grid_layout = GridLayout(cols=2, spacing=0, size_hint_y=None)
        for symbol in symbols:
            button = ToggleButton(text=symbol, size_hint_y=None, height=40)
            button.bind(on_press=self.insert_symbol)
            grid_layout.add_widget(button)
            self.symbol_buttons.append(button)
        return grid_layout

    def insert_symbol(self, instance):
        if instance.state == 'down':
            selected_line = self.text_input.text.split('\n')[self.text_input.cursor_row]
            self.text_input.text = selected_line + instance.text

    def display_nodes(self, nodes):
        self.nodes = nodes
        self.node_layout.clear_widgets()

        for node in nodes:
            surface, feature, cost, start, end, _ = node
            button_text = f"{surface} ({feature})"
            button = Button(text=button_text, size_hint_y=None, height=40)
            button.bind(on_press=self.on_node_button_press)
            self.node_layout.add_widget(button)

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

    def paste_text(self, instance):
        clipboard_text = Clipboard.paste()
        self.text_input.insert_text(clipboard_text)

        # Only pasting the text of the "down" state ToggleButton
        for button in self.generated_buttons:
            if button.state == 'down':
                clipboard_text = button.text
                self.text_input.insert_text(clipboard_text)

    def clear_text(self, *args):
        self.text_input.text = ""

    def insert_text_at_line_start(self, instance):
        cursor_row = self.text_input.cursor_row
        lines = self.text_input.text.split('\n')
        selected_texts = [button.text for button in self.generated_buttons + self.symbol_buttons if button.state == "down"]
        selected_text = "".join(selected_texts)
        
        if cursor_row < len(lines):
            lines[cursor_row] = selected_text + lines[cursor_row]
            cursor_row += 1  # Move cursor to the next line
        else:
            lines.append(selected_text)  # Insert text at the end if cursor is at the last line

        self.text_input.text = '\n'.join(lines)
        self.text_input.cursor = (0, cursor_row)  # Set cursor position to the next line

    def wrap_text_in_brackets(self, instance):
        cursor_row = self.text_input.cursor_row
        lines = self.text_input.text.split('\n')
        
        # 既存のbracket_pairsを保持
        bracket_pairs = [(button.text[0], button.text[1]) for button in self.bracket_buttons if button.state == 'down']

        # generated_buttonsのテキストを取得
        generated_texts = [button.text for button in self.generated_buttons if button.state == 'down']

        if cursor_row < len(lines) - 1:
            new_line = lines[cursor_row]
            for start_bracket, end_bracket in bracket_pairs:
                new_line = start_bracket + new_line + end_bracket
            for gen_text in generated_texts:
                new_line = gen_text + new_line
            lines[cursor_row] = new_line
            cursor_row += 1  # Move cursor to the next line
        else:
            new_line = lines[cursor_row]  # Copy existing line
            for start_bracket, end_bracket in bracket_pairs:
                new_line = start_bracket + new_line + end_bracket
            for gen_text in generated_texts:
                new_line = gen_text + new_line
            lines[cursor_row] = new_line  # Insert text at the current line

        self.text_input.text = '\n'.join(lines)
        self.text_input.cursor = (0, cursor_row)  # Set cursor position to the next line

    def insert_text_at_line_end(self, instance):
        cursor_row = self.text_input.cursor_row
        lines = self.text_input.text.split('\n')
        selected_texts = [button.text for button in self.symbol_buttons + self.generated_buttons if button.state == "down"]
        selected_text = "".join(selected_texts)
        
        if cursor_row < len(lines):
            lines[cursor_row] = lines[cursor_row] + selected_text
            cursor_row += 1  # Move cursor to the next line
        else:
            lines.append(selected_text)  # Insert text at the end if cursor is at the last line

        self.text_input.text = '\n'.join(lines)
        self.text_input.cursor = (0, cursor_row)  # Set cursor position to the next line

    def generate_text_button(self, instance):
        button = ToggleButton(text=self.input_form.text, size_hint_y=None, height=40)
        button.bind(on_press=self.analyze_text_from_button)
        button.bind(on_release=self.select_button)  # ボタンがリリースされたときに選択するメソッドを呼び出す
        self.node_layout.add_widget(button)
        self.node_scroll_view.height = self.node_layout.minimum_height  # コンテンツに合わせて高さを調整
        self.generated_buttons.append(button)  # 生成されたボタンをリストに追加

    def select_button(self, instance):
        for button in self.generated_buttons:
            button.state = "normal"  # 全てのボタンを通常状態に戻す
        instance.state = "down"  # 押されたボタンをdown状態に設定

    def analyze_text_from_button(self, button):
        text = button.text
        node_layout = self.node_layout

        result = tagger.parse(text)
        self.nodes = []

        lines = result.split('\n')
        for line in lines:
            if '\t' in line:
                surface, feature = line.split('\t')
                feature_list = feature.split(',')
                if len(feature_list) > 6:
                    pos = feature_list[0]
                    base = feature_list[6]
                else:
                    pos = feature_list[0]
                    base = ''
                node_start = text.find(surface)
                node_end = node_start + len(surface)
                node = (surface, pos, base, node_start, node_end, feature)
                self.nodes.append(node)
                button = Button(text=surface)
                button.bind(on_press=self.on_node_button_press)

    def on_node_button_press(self, instance):
        button_text = instance.text
        for node in self.nodes:
            surface, pos, base, node_start, node_end, feature = node
            if button_text == surface:
                self.text_input.select_text(node_start, node_end)
                break

    def adjust_font_size(self, instance, value):
        self.text_input.font_size = value

    def toggle_stopwatch(self, instance):
        if not self.stopwatch_active:
            self.stopwatch_button.text = '停止'
            self.stopwatch_event = Clock.schedule_interval(self.update_stopwatch, 0.01)
        else:
            self.stopwatch_button.text = '開始'
            self.stopwatch_event.cancel()
        self.stopwatch_active = not self.stopwatch_active

    def update_stopwatch(self, dt):
        self.stopwatch_time += dt
        minutes, seconds = divmod(self.stopwatch_time, 60)
        self.stopwatch_label.text = "{:02}:{:05.2f}".format(int(minutes), seconds)

    def reset_stopwatch(self, instance):
        self.stopwatch_time = 0
        self.stopwatch_label.text = "00:00.00"
        if self.stopwatch_active:
            self.stopwatch_event.cancel()
            self.stopwatch_active = False
            self.stopwatch_button.text = '開始'

    def update_text_input_height(self, instance, value):
        lines = value.split('\n')
        self.text_input.height = max(600, len(lines) * (self.text_input.line_height + 4))

    def clear_input_form(self, instance):
        self.input_form.text = ""

    def new_file(self, instance):
        self.text_input.text = ''
        self.update_stats()

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
                    f"行番号: {current_line_num} | 文字数: {current_line_chars} | node数: {current_line_nodes}"
        self.stats_label.text = stats_text

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TextEditingOperation(name='text_edit'))
        return sm

if __name__ == '__main__':
    MyApp().run()
