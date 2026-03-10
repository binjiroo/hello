from kivy.config import Config
Config.set('kivy', 'default_font', [
    'Meiryo',
    'C:\\Windows\\Fonts\\meiryo.ttc'
])
# マルチタッチエミュレーションを要求に応じてのみ有効にする
#Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.core.clipboard import Clipboard
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.togglebutton import ToggleButton
import MeCab
import time
import logging

# ロギングの基本設定
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.persistent_selection = False  # 選択状態を永続化するフラグ

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.touch_start_time = time.time()
            self.persistent_selection = True  # 選択を永続化
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        touch_duration = time.time() - self.touch_start_time
        if touch_duration > 1:
            self.cursor = (0, 0)
        if not self.persistent_selection:
            self.cancel_selection()
        return super().on_touch_up(touch)

class TextRecognitionAppLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(TextRecognitionAppLayout, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 600
        # 左側のレイアウト
        left_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=800)
        left_layout.size_hint_y = None
        left_layout.height = 600

        # テキストエリアのスクロールビュー
        self.scroll_view = ScrollView(size_hint=(1, None), size=(800, 500))
        self.text_input = CustomTextInput(size_hint_y=None, multiline=True, font_size=18, font_name='Meiryo')  # TextInputをCustomTextInputに変更
        self.text_input.bind(minimum_height=self.text_input.setter('height'))
        self.scroll_view.add_widget(self.text_input)
        left_layout.add_widget(self.scroll_view)

        # ボタングループ①
        button_group_1 = BoxLayout(size_hint_y=None, height=50)
        buttons = ["新規", "開く", "保存", "上書", "コピー", "ペースト", "クリア", "解析", "戻る", "進む"]
        for label in buttons:
            button = Button(text=label, size_hint_x=None, width=80)
            button.bind(on_press=self.button_pressed)
            button_group_1.add_widget(button)
        left_layout.add_widget(button_group_1)

        # ボタングループ②
        button_group_2 = BoxLayout(size_hint_y=None, height=50)
        buttons_2 = ["選択文字削除", "入力文字削除", "解析開始", "次の行を解析"]
        for label in buttons_2:
            button = Button(text=label, size_hint_x=None, width=130)
            button.bind(on_press=self.button_pressed)
            button_group_2.add_widget(button)

        # 入力フォーム
        self.input_form = TextInput(size_hint_x=None, width=180)
        button_group_2.add_widget(self.input_form)

        # フォントサイズ調整プルダウン
        self.font_size_spinner = Spinner(
            text='18', values=('12', '14', '16', '18', '20', '22', '24', '26', '28', '30', '32'), size_hint_x=None, width=100
        )
        self.font_size_spinner.bind(text=self.on_font_size_select)
        button_group_2.add_widget(self.font_size_spinner)

        left_layout.add_widget(button_group_2)
        self.add_widget(left_layout)

        # 右側のレイアウト（ボタン生成スペース）
        self.button_columns = [BoxLayout(orientation='vertical', size_hint_x=None, width=120) for _ in range(3)]
        self.right_layout = BoxLayout(orientation='horizontal', size_hint_x=None, width=360)

        for column in self.button_columns:
            self.right_layout.add_widget(column)

        self.add_widget(self.right_layout)

        # テキストが変更されたときのイベントハンドラを追加
        self.text_input.bind(text=self.on_text_changed)

    def on_text_changed(self, instance, value):
        # テキスト変更が発生したときに呼び出されるメソッド
        self.clear_buttons()  # 既存のボタンをクリア
        self.generate_buttons_from_current_line()  # 現在の行に対応するボタンを再生成

    def button_pressed(self, button):
        if button.text == "コピー":
            Clipboard.copy(self.text_input.text)
        elif button.text == "ペースト":
            self.text_input.text = Clipboard.paste()
        elif button.text == "クリア":
            self.text_input.text = ""
        elif button.text == "解析":
            self.analyze_text()
        elif button.text == "戻る":
            self.text_input.do_undo()
        elif button.text == "進む":
            self.text_input.do_redo()
        elif button.text == "選択文字削除":
            self.remove_selected_text()
        elif button.text == "入力文字削除":
            self.remove_input_text()
        elif button.text == "解析開始":
            self.generate_buttons_from_current_line()
        elif button.text == "次の行を解析":
            self.move_to_next_line_and_analyze()

    def analyze_text(self):
        try:
            tagger = MeCab.Tagger("C:/MeCab-64/dic")  # 辞書のパスを適切に設定
            result = tagger.parse(self.text_input.text)
            print(result)
        except Exception as e:
            print("MeCabでエラーが発生しました:", e)

    def remove_selected_text(self):
        selected_text = self.text_input.selection_text
        if selected_text:
            self.text_input.text = self.text_input.text.replace(selected_text, "")
            self.remove_blank_lines()
            self.generate_buttons_from_current_line()  # regenerate_buttons の代わりにこの行を使用

    def remove_input_text(self):
        input_text = self.input_form.text
        if input_text:
            self.text_input.text = self.text_input.text.replace(input_text, "")
            self.remove_blank_lines()
            self.generate_buttons_from_current_line()  # regenerate_buttons の代わりにこの行を使用

    def move_to_next_line_and_analyze(self):
        lines = self.text_input.text.split('\n')
        current_index = self.get_current_line_index()
        if current_index < len(lines) - 1:
            self.text_input.cursor = (0, current_index + 1)
            self.generate_buttons_from_current_line()

    def clear_buttons(self):
        for column in self.button_columns:
            column.clear_widgets()
        logging.debug('全てのボタンがクリアされました')

    def get_current_line(self):
        # カーソル行が有効範囲内にあることを確認
        if self.text_input.cursor_row < len(self.text_input._lines):
            return self.text_input._lines[self.text_input.cursor_row]
        return ""

    def get_current_line_index(self):
        return self.text_input.cursor_row

    def on_font_size_select(self, spinner, text):
        # フォントサイズを更新するメソッド
        self.text_input.font_size = int(text)

    def remove_blank_lines(self):
        lines = self.text_input.text.split('\n')
        # 空白でない行だけを保持
        non_blank_lines = [line for line in lines if line.strip()]
        self.text_input.text = '\n'.join(non_blank_lines)

    def move_text_to_next_line(self, text, start, end):
        """元の行から下の行にテキストを移動する"""
        current_line_index = self.get_current_line_index()
        lines = self.text_input.text.split('\n')
        if current_line_index == len(lines) - 1:
            lines.append("")  # 新しい空行を追加

        current_line = lines[current_line_index]
        next_line = lines[current_line_index + 1]
        new_current_line = current_line[:start]
        new_next_line = current_line[start:] + next_line

        if len(new_next_line) > 20:
            # 条件2: 20文字+αを超える場合の処理
            excess_text = new_next_line[20:]
            new_next_line = new_next_line[:20]

            if current_line_index + 1 == len(lines) - 1:
                lines.append("")  # 新しい空行を追加

            next_next_line = lines[current_line_index + 2]
            combined_length = len(excess_text + next_next_line)

            if combined_length <= 30:
                # 条件2a: 30文字以内なら結合
                new_next_next_line = excess_text + next_next_line
                lines[current_line_index + 2] = new_next_next_line
            else:
                # 条件2b: 30文字を超える場合、新しい行を追加
                lines.insert(current_line_index + 2, excess_text)

        lines[current_line_index] = new_current_line
        lines[current_line_index + 1] = new_next_line

        self.text_input.text = '\n'.join(lines)
        self.text_input.cursor = (0, current_line_index + 1)
        self.remove_blank_lines()  # 空白行を除去して上詰め
        self.generate_buttons_from_current_line()

    def move_text_to_previous_line(self, text, start, end):
        current_line_index = self.get_current_line_index()
        lines = self.text_input.text.split('\n')
        if current_line_index == 0:
            lines.insert(0, "")  # 新しい空行を追加
            current_line_index += 1  # 現在の行インデックスを更新

        previous_line = lines[current_line_index - 1]
        current_line = lines[current_line_index]
        new_previous_line = previous_line + current_line[:end]
        new_current_line = current_line[end:]

        lines[current_line_index - 1] = new_previous_line
        lines[current_line_index] = new_current_line

        self.text_input.text = '\n'.join(lines)
        self.text_input.cursor = (len(new_previous_line), current_line_index - 1)
        self.remove_blank_lines()  # 空白行を除去して上詰め
        self.generate_buttons_from_current_line()

    def create_button_handler(self, f, s, start, end):
        """各ボタンのアクションを設定するためのハンドラを生成する"""
        return lambda instance: self.debug_handler(f, s, start, end, instance)

    def debug_handler(self, f, s, start, end, instance):
        print(f"Handler called with text='{s}', start={start}, end={end}")
        try:
            f(s, start, end)
        except Exception as e:
            print(f"Error during operation: {e}")

    def bind_text_operations(self, button, column_index, text):
        if column_index == 0:
            button.bind(on_press=lambda instance: self.move_text_with_context(instance, text, self.move_text_to_previous_line))
        elif column_index == 1:
            button.bind(on_press=lambda instance: self.move_text_with_context(instance, text, self.move_text_to_next_line))
        elif column_index == 2:
            button.bind(on_press=lambda instance: self.select_text_with_context_and_focus(instance, text))

    def select_text_with_context_and_focus(self, instance, text):
        start, end = self.get_text_indices(text)
        if start is not None and end is not None:
            self.select_text_on_line(instance, text, start, end)
            self.text_input.focus = True  # フォーカスを設定
            self.text_input.persistent_selection = True  # 選択状態を永続化

    def move_text_with_context(self, instance, text, move_function):
        start, end = self.get_text_indices(text)
        if start is not None and end is not None:
            move_function(text, start, end)

    def get_text_indices(self, text):
        current_line_index = self.get_current_line_index()
        lines = self.text_input.text.split('\n')
        current_line = lines[current_line_index]
        start = current_line.find(text)
        if start != -1:
            end = start + len(text)
            return start, end
        return None, None

    def select_text_on_line(self, instance, text, start, end):
        self.text_input.focus = True
        current_line_index = self.get_current_line_index()
        current_line = self.get_current_line()

        start = current_line.find(text)
        if start != -1:
            end = start + len(text)
            absolute_start = sum(len(line) + 1 for line in self.text_input._lines[:current_line_index]) + start
            absolute_end = absolute_start + len(text)

            self.text_input.select_text(absolute_start, absolute_end)

        self.generate_buttons_from_current_line()

    def generate_buttons_from_current_line(self):
        self.clear_buttons()
        tagger = MeCab.Tagger()
        current_line_text = self.get_current_line()
        node = tagger.parseToNode(current_line_text)

        current_index = 0
        while node:
            if node.surface:
                length_of_surface = len(node.surface)
                start_position = current_index
                end_position = start_position + length_of_surface

                ops = [
                    ("前の行に移動", self.move_text_to_previous_line),
                    ("次の行に移動", self.move_text_to_next_line),
                    ("テキスト選択", self.select_text_on_line)
                ]

                for idx, (op_name, op_func) in enumerate(ops):
                    button = Button(text=node.surface, size_hint_y=None, height=20)
                    handler = self.create_button_handler(op_func, node.surface, start_position, end_position)
                    button.bind(on_press=handler)
                    self.button_columns[idx % 3].add_widget(button)

                current_index += length_of_surface
            node = node.next

class TextRecognitionApp(App):
    def build(self):
        Window.always_on_top = True
        return TextRecognitionAppLayout()

if __name__ == '__main__':
    TextRecognitionApp().run()
