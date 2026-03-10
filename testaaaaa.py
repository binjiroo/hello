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


class CustomTextInput(TextInput):
    def __init__(self, **kwargs):
        super(CustomTextInput, self).__init__(**kwargs)
        self.touch_start_time = 0
        # 長押しした位置の行のインデックスを記録する変数を追加
        self.long_press_row_index = 0

    def on_touch_down(self, touch):
        self.touch_start_time = time.time()
        # タッチがテキスト入力ウィジェット内で発生した場合、その時点の行のインデックスを記録
        if self.collide_point(*touch.pos):
            self.long_press_row_index = self.cursor_row
        return super(CustomTextInput, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        touch_duration = time.time() - self.touch_start_time
        if touch_duration > 1:  # 1秒以上の長押し
            # カーソルを長押しした位置の行の先頭に移動
            self.cursor = (0, self.long_press_row_index)
        return super(CustomTextInput, self).on_touch_up(touch)

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
        self.text_input.bind(text=self.on_text_changed)  # テキスト変更イベントにバインド    

    def on_text_changed(self, instance, value):
        # テキスト変更が発生したときに呼び出されるメソッド
        self.clear_buttons()  # 既存のボタンをクリア
        self.generate_buttons_from_current_line()  # 現在の行に対応するボタンを再生成

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
            self.generate_buttons_from_current_line()  # regenerate_buttons の代わりにこの行を使用

    def remove_input_text(self):
        #logging.debug('remove_input_text 関数が呼び出されました')
        input_text = self.input_form.text
        if input_text:
            self.text_input.text = self.text_input.text.replace(input_text, "")
            self.remove_blank_lines()
            self.generate_buttons_from_current_line()  # regenerate_buttons の代わりにこの行を使用

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

    def move_text_to_previous_line(self, instance):
        #logging.debug('move_text_to_previous_line 関数が呼び出されました')
        current_line_index = self.get_current_line_index()
        if current_line_index > 0:
            lines = self.text_input.text.split('\n')
            current_line = lines[current_line_index]
            previous_line = lines[current_line_index - 1]

            button_text_index = current_line.find(instance.text)
            if button_text_index != -1:
                text_to_move = current_line[:button_text_index + len(instance.text)]
                lines[current_line_index] = current_line[button_text_index + len(instance.text):]
                lines[current_line_index - 1] = previous_line + text_to_move

            self.text_input.text = '\n'.join(lines)
            self.remove_blank_lines()
            self.text_input.cursor = (0, current_line_index - 1)
            # 再生成するボタンのためのテキストを指定
            self.generate_buttons_for_line(lines[current_line_index - 1])

            updated_line_index = self.get_current_line_index()
            self.generate_buttons_for_line(self.text_input.text.split('\n')[updated_line_index])
            self.text_input.cursor = (0, current_line_index - 1)  # カーソルを移動した行に更新

    def move_text_to_next_line(self, instance):
        current_line_index = self.get_current_line_index()
        lines = self.text_input.text.split('\n')
        if current_line_index >= len(lines) - 1:
            # 現在の行が最後の行の場合、新しい空行を追加
            lines.append('')

        current_line = lines[current_line_index]
        next_line = lines[current_line_index + 1]

        button_text_index = current_line.find(instance.text)
        if button_text_index != -1:
            text_to_move = current_line[button_text_index:]
            lines[current_line_index] = current_line[:button_text_index]
            lines[current_line_index + 1] = text_to_move + next_line

        self.text_input.text = '\n'.join(lines)
        self.remove_blank_lines()
        self.generate_buttons_for_line(lines[current_line_index + 1])

        # テキストを移動した後、カーソルを次の行の適切な位置に設定
        self.text_input.cursor = (0, current_line_index + 1)

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
        # テキスト入力にフォーカスを設定
        self.text_input.focus = True

        # 現在のカーソル行を取得
        current_line_index = self.text_input.cursor_row
        current_line = self.get_current_line()

        # 指定したテキストの開始位置と終了位置を検索
        start = current_line.find(instance.text)
        if start != -1:
            end = start + len(instance.text)

            # 全テキストでの絶対位置を計算
            absolute_start = sum(len(line) + 1 for line in self.text_input._lines[:current_line_index]) + start
            absolute_end = absolute_start + len(instance.text)

            # 選択範囲を設定
            self.text_input.select_text(absolute_start, absolute_end)

    # generate_buttons_from_current_line メソッドの修正
    def generate_buttons_from_current_line(self):
        self.clear_buttons()
        tagger = MeCab.Tagger()
        # 現在の行を取得
        current_line_text = self.get_current_line()
        # 現在の行番号を取得
        current_line_index = self.get_current_line_index()
        node = tagger.parseToNode(current_line_text)
        column_index = 0
        while node:
            if node.surface:
                # ここで行番号を含めてログを出力
                logging.debug(f'行 {current_line_index} のノード解析: {node.surface}')
                # 各列にボタンを追加するロジック
                for i, column in enumerate(self.button_columns):
                    button = Button(text=node.surface, size_hint_y=None, height=40)
                    # 各ボタンに機能をバインド
                    self.bind_text_operations(button, i)
                    column.add_widget(button)
                    # ここでログにボタン追加情報と行番号を含める
                    logging.debug(f'行 {current_line_index} のボタン {node.surface} を列 {i} に追加')
                column_index = (column_index + 1) % len(self.button_columns)
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
        #logging.debug('bind_text_operations 関数が呼び出されました')
        if column_index == 0:
            button.bind(on_press=self.move_text_to_previous_line)
        elif column_index == 1:
            button.bind(on_press=self.move_text_to_next_line)
        elif column_index == 2:
            button.bind(on_press=self.select_text_on_line)

        # ここで select_text_on_line メソッドをバインド
        button.bind(on_release=self.select_text_on_line)

    def generate_buttons_for_line(self, line_text):
        #logging.debug('generate_buttons_from_line 関数が呼び出されました')
        self.clear_buttons()
        tagger = MeCab.Tagger()
        node = tagger.parseToNode(line_text)
        while node:
            if node.surface:
                for i, column in enumerate(self.button_columns):
                    button = Button(text=node.surface, size_hint_y=None, height=40)
                    self.bind_text_operations(button, i)
                    column.add_widget(button)
                    self.select_text_on_line_manual(node.surface)  # この行を追加
                if node.surface != '':
                    self.select_text_on_line_manual(node.surface)
            node = node.next

    def select_text_on_line_manual(self, text):
        #logging.debug(f"select_text_on_line_manual 関数が呼び出されました: '{text}'")
        found = False  # テキストが見つかったかどうかを追跡する変数
        for i, line in enumerate(self.text_input._lines):
            if text in line:
                start = line.find(text)
                end = start + len(text)
                logging.info(f"テキスト '{text}' が行 {i} の位置 {start} から {end} まで見つかりました。")
                self.select_text(i, start, end)
                found = True
                break
        if not found:
            logging.warning(f"テキスト '{text}' は見つかりませんでした。")
            # ここでカーソル位置を変更しないための追加処理は不要です

    def select_text(self, line_index, start, end):
        self.text_input.cursor = (start, line_index)
        self.text_input.select_from = self.text_input.cursor_index()
        self.text_input.cursor = (end, line_index)
        self.text_input.select_to = self.text_input.cursor_index()
        logging.debug(f"行 {line_index} でのテキスト選択が位置 {start} から {end} まで設定されました。")

class TextRecognitionApp(App):
    def build(self):
        return TextRecognitionAppLayout()

if __name__ == '__main__':
    TextRecognitionApp().run()