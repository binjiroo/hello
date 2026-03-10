from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import random
import string

# ------------------------
# メニューバーウィジェット
# ------------------------
class MenuBar(BoxLayout):
    def __init__(self, **kwargs):
        super(MenuBar, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 70

        # メニューの階層構造（トップレベルの項目をキー、その中身はリストまたはdict）
        self.menu_structure = {
            "ファイル": ["新規", "開く", "上書保存", "名付て保存", "印刷", "プリンタ設定", "オプション", "終了"],
            "編集": ["戻る", "進む", "切取り", "コピー", "貼付け", "削除"],
            "表示": ["拡大", "縮小"],
            "作図": ["点", "線", "矩形", "円", "円弧"],
            "設定": {
                "基本設定": ["コマンド", "キー割当て"],
                "環境設定": None,
                "寸法設定": None,
                "線設定": None,
                "文字設定": None,
                "オフセット": None,
                "属性取得": None,
                "角度取得": None,
                "寸法取得": None,
                "中心点取得": None,
            },
            "その他": ["図形", "線記号", "座標ファイル", "測定", "表計算", "式計算", "図形登録", "文字整理"],
            "ヘルプ": ["トピック検索", "バージョン情報"],
        }

        # トップレベルの各メニュー用ボタンを作成
        for menu_name in self.menu_structure.keys():
            btn = Button(text=menu_name,
                         size_hint_x=None,
                         width=150,
                         font_size=24)
            btn.bind(on_release=self.open_menu)
            self.add_widget(btn)

    def open_menu(self, instance):
        menu_name = instance.text
        menu_data = self.menu_structure[menu_name]
        dropdown = self.create_dropdown(menu_data)
        dropdown.bind(on_select=lambda instance, x: self.menu_item_selected(menu_name, x))
        dropdown.open(instance)

    def create_dropdown(self, menu_data):
        dropdown = DropDown()
        # メニュー項目がリストの場合
        if isinstance(menu_data, list):
            for item in menu_data:
                btn = Button(text=item,
                             size_hint_y=None,
                             height=44,
                             font_size=24)
                # 現在のitemをデフォルト引数に束縛
                btn.bind(on_release=lambda btn, text=item: dropdown.select(text))
                dropdown.add_widget(btn)
        # メニュー項目が辞書（＝サブメニューを持つ場合）
        elif isinstance(menu_data, dict):
            for key, val in menu_data.items():
                if val is None:
                    btn = Button(text=key,
                                 size_hint_y=None,
                                 height=44,
                                 font_size=24)
                    btn.bind(on_release=lambda btn, text=key: dropdown.select(text))
                    dropdown.add_widget(btn)
                else:
                    # サブメニューがある項目は矢印付きの表記にする
                    btn = Button(text=key + " ▶",
                                 size_hint_y=None,
                                 height=44,
                                 font_size=24)
                    btn.bind(on_release=lambda btn, submenu=val, key=key: self.open_submenu(btn, submenu, dropdown))
                    dropdown.add_widget(btn)
        return dropdown

    def open_submenu(self, parent_button, submenu_data, parent_dropdown):
        # サブメニュー用のDropDownを作成
        sub_dropdown = self.create_dropdown(submenu_data)
        sub_dropdown.bind(on_select=lambda instance, x: self.menu_item_selected(parent_button.text.replace(" ▶", ""), x))
        sub_dropdown.open(parent_button)
        # ※必要に応じて親メニューを閉じる場合は以下をコメントアウト解除
        # parent_dropdown.dismiss()

    def menu_item_selected(self, menu_name, item_text):
        print(f"Menu '{menu_name}' -> '{item_text}' selected")
        # ここに各メニュー項目の実際の機能を実装してください


# ------------------------
# メインウィジェット
# ------------------------
class MainWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'

        # メニューバーを上部に配置（BoxLayoutは追加順によって配置順が変わるため index=0 で上部へ）
        self.add_widget(MenuBar(), index=0)

        self.display_label = Label(text='', font_size=48)
        self.add_widget(self.display_label)

        self.input_text = TextInput(multiline=False, font_size=48)
        self.input_text.bind(on_text_validate=self.check_match)
        self.add_widget(self.input_text)

        self.char_count_slider = Slider(min=1, max=40, value=5)
        self.char_count_slider.bind(value=self.update_char_count)
        self.add_widget(self.char_count_slider)

        self.time_slider = Slider(min=1, max=60, value=10)
        self.time_slider.bind(value=self.update_time)
        self.add_widget(self.time_slider)

        self.char_count_label = Label(text='文字数: 5', font_size=48)
        self.add_widget(self.char_count_label)

        self.time_label = Label(text='count: 10', font_size=48)
        self.add_widget(self.time_label)

        button_layout = BoxLayout(size_hint_y=None, height=70)

        self.gen_button = Button(text='Generate', font_size=48)
        self.gen_button.bind(on_press=self.generate_text)
        button_layout.add_widget(self.gen_button)

        self.reset_button = Button(text='Reset', font_size=48)
        self.reset_button.bind(on_press=self.reset_input)
        button_layout.add_widget(self.reset_button)

        self.add_widget(button_layout)

        self.char_type = '数字'  # 初期は数字
        self.char_type_buttons = BoxLayout(size_hint_y=None, height=70)
        for char_type in ['数字', '英字', 'かな', 'カナ']:
            btn = Button(text=char_type, font_size=48)
            btn.bind(on_press=self.set_char_type)
            self.char_type_buttons.add_widget(btn)
        self.add_widget(self.char_type_buttons)

        self.previous_display_text = ''
        self.display_event = None
        self.countdown_event = None
        self.remaining_time = 0

    def generate_text(self, instance):
        if self.display_event:
            self.display_event.cancel()
        if self.countdown_event:
            self.countdown_event.cancel()

        char_count = int(self.char_count_slider.value)
        if self.char_type == '数字':
            self.display_label.text = ''.join(random.choices(string.digits, k=char_count))
        elif self.char_type == '英字':
            self.display_label.text = ''.join(random.choices(string.ascii_letters, k=char_count))
        elif self.char_type == 'かな':
            hiragana_chars = 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん'
            self.display_label.text = ''.join(random.choices(hiragana_chars, k=char_count))
        elif self.char_type == 'カナ':
            katakana_chars = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン'
            self.display_label.text = ''.join(random.choices(katakana_chars, k=char_count))

        self.previous_display_text = self.display_label.text  # 直前の表示を保持
        self.remaining_time = int(self.time_slider.value)
        self.update_time_label()

        # カウントダウンの初期値を即座に表示
        self.update_countdown(0)

        self.countdown_event = Clock.schedule_interval(self.update_countdown, 1)
        # 表示をクリアするタイミングを設定時間＋1.01秒後に設定
        self.display_event = Clock.schedule_once(self.clear_display, self.remaining_time + 1.01)

    def set_char_type(self, instance):
        self.char_type = instance.text

    def update_char_count(self, instance, value):
        self.char_count_label.text = f'文字数: {int(value)}'

    def update_time(self, instance, value):
        self.time_label.text = f'count: {int(value)}'

    def check_match(self, instance):
        if self.input_text.text == self.previous_display_text:
            self.input_text.background_color = (0, 1, 0, 1)  # 緑
        else:
            self.input_text.background_color = (1, 0, 0, 1)  # 赤

    def clear_display(self, dt):
        self.display_label.text = ''
        if self.countdown_event:
            self.countdown_event.cancel()

    def reset_input(self, instance):
        if self.display_event:
            self.display_event.cancel()
        if self.countdown_event:
            self.countdown_event.cancel()
        self.input_text.text = ''
        self.input_text.background_color = (1, 1, 1, 1)  # 白
        self.display_label.text = ''
        self.remaining_time = 0
        self.update_time(None, self.time_slider.value)

    def update_countdown(self, dt):
        if self.remaining_time >= 0:
            self.update_time_label()
            self.remaining_time -= 1
        if self.remaining_time < 0:
            self.time_label.text = 'count: 0'
            self.countdown_event.cancel()

    def update_time_label(self):
        self.time_label.text = f'count: {self.remaining_time}'
        print(dir(self.time_label.text))


class TestApp(App):
    def build(self):
        return MainWidget()


if __name__ == '__main__':
    TestApp().run()
