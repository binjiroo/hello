from kivy.config import Config
Config.set('kivy', 'default_font', [
    'Meiryo',
    'C:\\Windows\\Fonts\\meiryo.ttc'
])

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.core.clipboard import Clipboard
from kivy.uix.scrollview import ScrollView
import MeCab
import time

import logging

# ロギングの基本設定
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
Config.set('graphics', 'resizable', '1')

class CustomTextInput(TextInput):
    def __init__(self, **kwargs):
        super(CustomTextInput, self).__init__(**kwargs)
        self.bind(text=self.on_text)

    def on_text(self, instance, value):
        self.height = max(50, len(self.text.split('\n')) * 20)  # 行ごとの高さを20と仮定

class TextRecognitionAppLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(TextRecognitionAppLayout, self).__init__(**kwargs)
        self.orientation = 'horizontal'

        # CustomTextInput のインスタンスを作成
        self.text_input = CustomTextInput(size_hint_y=None, height=50, multiline=True, font_size=18, font_name='Meiryo')

        # テキストエリアのスクロールビューを追加
        self.scroll_view = ScrollView(size_hint=(1, 1), size=(800, 500))
        self.scroll_view.add_widget(self.text_input)

        # ボタングループ①
        button_group_1 = BoxLayout(size_hint_y=None, height=50)
        buttons = ["新規", "開く", "保存", "上書", "コピー", "ペースト", "クリア", "解析", "戻る", "進む"]
        for label in buttons:
            button = Button(text=label, size_hint_x=None, width=80)
            button.bind(on_press=self.button_pressed)
            button_group_1.add_widget(button)

        # ボタングループ②
        button_group_2 = BoxLayout(size_hint_y=None, height=50)
        buttons_2 = ["選択文字削除", "入力文字削除", "解析開始", "次の行を解析"]
        for label in buttons_2:
            button = Button(text=label, size_hint_x=None, width=130)
            button.bind(on_press=self.button_pressed)
            button_group_2.add_widget(button)

        # 左側のレイアウトにウィジェットを追加
        left_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=800)
        left_layout.add_widget(self.scroll_view) 
        left_layout.add_widget(button_group_1)
        left_layout.add_widget(button_group_2)
        left_layout.size_hint_y = 1  # ウィジェットの高さを自動調整しないように設定        left_layout.size_hint_y = None  # ウィジェットの高さを自動調整しないように設定
        left_layout.height = 600  # 適切な高さを設定 
        
        # 左側のレイアウトを追加
        self.add_widget(left_layout)

        # 入力フォームとフォントサイズ調整プルダウンの追加
        self.input_form = TextInput(size_hint_x=None, width=180)
        button_group_2.add_widget(self.input_form)

        self.font_size_spinner = Spinner(
            text='18', values=('12', '14', '16', '18', '20', '22', '24', '26', '28', '30', '32'), size_hint_x=None, width=100
        )
        self.font_size_spinner.bind(text=self.on_font_size_select)
        button_group_2.add_widget(self.font_size_spinner)

        # 右側のレイアウト（ボタン生成スペース）
        self.button_columns = [BoxLayout(orientation='vertical', size_hint_x=None, width=120) for _ in range(3)]
        self.right_layout = BoxLayout(orientation='horizontal', size_hint_x=None, width=360)
        for column in self.button_columns:
            self.right_layout.add_widget(column)
            print(f'BoxLayout を right_layout に追加')  # ログ出力
        self.add_widget(self.right_layout)

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
            tagger = MeCab.Tagger(r"C:\MeCab-64\dic")  # 辞書のパスを適切に設定
            result = tagger.parse(self.text_input.text)
            print(result)
        except Exception as e:
            print("MeCabでエラーが発生しました:", e)
            
    def remove_selected_text(self):
        #logging.debug('remove_selected_text 関数が呼び出されました')
        selected_text = self.text_input.selection_text
        if selected_text:
            self.text_input.text = self.text_input.text.replace(selected_text, "")
            self.remove_blank_lines()

    def remove_input_text(self):
        #logging.debug('remove_input_text 関数が呼び出されました')
        input_text = self.input_form.text
        if input_text:
            self.text_input.text = self.text_input.text.replace(input_text, "")
            self.remove_blank_lines()

    def move_to_next_line_and_analyze(self):
        #logging.debug('meve_to_next_line_and_analyze 関数が呼び出されました')
        lines = self.text_input.text.split('\n')
        current_index = self.get_current_line_index()
        if current_index < len(lines) - 1:
            self.text_input.cursor = (0, current_index + 1)
            self.generate_buttons_from_current_line()

    def clear_buttons(self):
        #logging.debug('clear_buttons 関数が呼び出されました')
        for column in self.button_columns:
            column.clear_widgets()
        #logging.debug('全てのボタンがクリアされました')

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

    def move_text_to_previous_line(self, button_instance):
        row_number = button_instance.row_number
        button_text = button_instance.text
        #logging.debug('move_text_to_previous_line 関数が呼び出されました')

        if row_number < 0 or row_number >= len(self.text_input._lines) - 1:
            #logging.error('指定された行番号が不正です。操作を中断します。')
            return

        #logging.debug(f"指定された行番号: {row_number}")
        current_line = self.text_input._lines[row_number]
        next_line = self.text_input._lines[row_number + 1]

        button_text_index = current_line.find(button_text)
        if button_text_index != -1:
            text_to_move = current_line[button_text_index:]
            self.text_input._lines[row_number] = current_line[:button_text_index]
            self.text_input._lines[row_number + 1] = text_to_move + next_line

        self.text_input.text = '\n'.join(self.text_input._lines)
        self.remove_blank_lines()
        self.text_input.cursor = (0, row_number + 1)
        self.generate_buttons_for_line(self.text_input._lines[row_number + 1])
        #logging.debug(f"移動後のカーソル位置: {self.text_input.cursor}")

    def move_text_to_next_line(self, button_instance):
        row_number = button_instance.row_number
        button_text = button_instance.text
        logging.debug('move_text_to_next_line 関数が呼び出されました')

        if row_number < 1:
            logging.error('指定された行番号が不正です。操作を中断します。')
            return

        lines = self.text_input.text.split('\n')
        if row_number >= len(lines):
            logging.error('指定された行番号が範囲外です。操作を中断します。')
            return

        logging.debug(f"指定された行番号: {row_number}")
        current_line = lines[row_number]
        previous_line = lines[row_number - 1]


        button_text_index = current_line.find(button_text)
        if button_text_index != -1:
            text_to_move = current_line[:button_text_index + len(button_text)]
            lines[row_number] = current_line[button_text_index + len(button_text):]
            lines[row_number - 1] = previous_line + text_to_move

        self.text_input.text = '\n'.join(lines)
        self.remove_blank_lines()
        self.text_input.cursor = (0, row_number)
        self.generate_buttons_for_line(lines[row_number])
        logging.debug(f"移動後のカーソル位置: {self.text_input.cursor}")

    def update_text_and_get_line_index(self, instance, move_up):
        """テキストを更新し、更新された行のインデックスを返すヘルパーメソッド"""
        
        current_line_index = self.get_current_line_index()
        lines = self.text_input.text.split('\n')  # テキストを行ごとに分割

        # move_up が True の場合、前の行のインデックスを返す
        if move_up and current_line_index > 0:
            return current_line_index - 1
        # move_up が False の場合、次の行のインデックスを返す
        elif not move_up and current_line_index < len(lines) - 1:
            return current_line_index + 1

        # それ以外の場合、現在の行のインデックスを返す
        return current_line_index

    def select_text_on_line(self, instance):
        current_line_index = self.get_current_line_index()
        lines = self.text_input.text.split('\n')
        if current_line_index < len(lines):
            current_line = lines[current_line_index]
            start = current_line.find(instance.text)
            if start != -1:
                end = start + len(instance.text)
                # カーソル位置を設定
                self.text_input.cursor = (start, current_line_index)
                # 選択開始位置と選択終了位置を設定
                self.text_input.select_from = self.text_input.cursor_index()
                self.text_input.cursor = (end, current_line_index)
                self.text_input.select_to = self.text_input.cursor_index()

    # generate_buttons_from_current_line メソッドの修正
    def generate_buttons_from_current_line(self):
        #logging.debug('generate_buttons_from_current_line 関数が呼び出されました')
        self.clear_buttons()
        tagger = MeCab.Tagger()
        node = tagger.parseToNode(self.get_current_line())
        current_row = self.get_current_line_index()  # 現在の行番号を取得

        column_index = 0

        while node:
            if node.surface:
                #logging.debug('ノード解析: %s', node.surface)
                # 各列にボタンを追加
                for i, column in enumerate(self.button_columns):
                    button = CustomButton(text=node.surface, size_hint_y=None, height=35, row_number=current_row)
                    self.bind_text_operations(button, i)
                    column.add_widget(button)
                    #print(f'ボタン "{node.surface}" を列 {i} に追加')  # ログ出力
                    #logging.debug('ボタン %s を列 %s に追加', node.surface, i)
                column_index = (column_index + 1) % len(self.button_columns)
                if node.surface != '':
                    current_line_index = self.get_current_line_index()
                    self.select_text_on_line_manual(node.surface, current_line_index)

            node = node.next

    def remove_blank_lines(self):
        #logging.debug('remove_blank_lines 関数が呼び出されました')
        lines = self.text_input.text.split('\n')
        non_blank_lines = [line for line in lines if line.strip()]
        # 変更前後での行のインデックスを追跡
        removed_line_indices = [i for i, line in enumerate(lines) if not line.strip()]
        self.text_input.text = '\n'.join(non_blank_lines)
        
        # 削除された行の前後のテキストに基づいてボタンを再生成
        for index in removed_line_indices:
            # インデックスの調整
            if index >= len(non_blank_lines):
                index = len(non_blank_lines) - 1
            if index > 0:
                line_text = non_blank_lines[index - 1]  # 1つ上の行のテキスト
                self.generate_buttons_for_line(line_text)

    def bind_text_operations(self, button, column_index):
        logging.debug('bind_text_operations 関数が呼び出されました')
        if column_index == 0:
            button.bind(on_press=lambda *args: self.move_text_to_next_line(args[0]) if isinstance(args[0], Button) else None)
            logging.debug('A列のボタンにバインドしました。')
        elif column_index == 1:
            button.bind(on_press=lambda *args: self.move_text_to_previous_line(args[0]) if isinstance(args[0], Button) else None)
            logging.debug('B列のボタンにバインドしました。')
        elif column_index == 2:
            # ここも適切に設定する必要があるかもしれません（例: 別の操作を行う）
            button.bind(on_press=lambda *args: self.select_text_on_line(args[0]) if isinstance(args[0], Button) else None)
            logging.debug('C列のボタンにバインドしました。')

    def generate_buttons_for_line(self, line_text):
        #logging.debug('generate_buttons_for_line 関数が呼び出されました')
        self.clear_buttons()
        tagger = MeCab.Tagger()
        node = tagger.parseToNode(line_text)
        current_line_index = self.get_current_line_index()  # 現在の行のインデックスを取得

        while node:
            if node.surface:
                for i, column in enumerate(self.button_columns):
                    button = CustomButton(row_number=current_line_index, text=node.surface, size_hint_y=None, height=35)  # row_number 引数を追加
                    self.bind_text_operations(button, i)
                    column.add_widget(button)
            node = node.next

    def select_text_on_line_manual(self, text, line_index):
        #logging.debug(f"select_text_on_line_manual 関数が呼び出されました: '{text}' on line {line_index}")
        line = self.text_input._lines[line_index]
        start = line.find(text)
        end = start + len(text)
        if start != -1:
            logging.info(f"テキスト '{text}' が行 {line_index} の位置 {start} から {end} まで見つかりました。")
            self.select_text(line_index, start, end)
        else:
            logging.warning(f"テキスト '{text}' は行 {line_index} で見つかりませんでした。")

    def select_text(self, line_index, start, end):
        self.text_input.cursor = (start, line_index)
        self.text_input.select_from = self.text_input.cursor_index()
        self.text_input.cursor = (end, line_index)
        self.text_input.select_to = self.text_input.cursor_index()
        #logging.debug(f"行 {line_index} でのテキスト選択が位置 {start} から {end} まで設定されました。")

class TextRecognitionApp(App):
    def build(self):
        return TextRecognitionAppLayout()
    
class CustomButton(Button):
    def __init__(self, row_number, text, **kwargs):
        super().__init__(**kwargs)
        self.row_number = row_number  # 行番号を保持
        self.text = text  # ボタンに関連するテキストを保持
        #logging.info(f"テキスト '{text}'。")

    def on_press(self):
        # ボタンが押された時のアクション
        # 例えば、行番号とテキストを表示するなど
        print(f"Row Number: {self.row_number}, Text: {self.text}")

    def on_custom_button_pressed(self, custom_button_instance):
        # custom_button_instance は CustomButton のインスタンス
        self.select_text(custom_button_instance.line_index, custom_button_instance.start, custom_button_instance.end)

if __name__ == '__main__':
    TextRecognitionApp().run()