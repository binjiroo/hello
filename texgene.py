from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView  # ScrollViewのインポート
from kivy.metrics import dp  # dpを使用するためのインポート
import random
import string
import platform

# スマホの解像度 (AQUOS sense5G) に合わせてウィンドウサイズを設定
Window.size = (540, 1140)  # Full HD+ (1,080 x 2,280) の解像度に対応

# get_font_size関数をここに追加
def get_font_size():
    return 24  # スマホ用に調整されたフォントサイズ

def get_dynamic_size(desktop_size, mobile_size):
    # スクリーンサイズに応じて動的にサイズを変化させる
    return dp(desktop_size) if not platform == 'android' else dp(mobile_size)

class MainWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'

        scroll = ScrollView()
        inner_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        inner_layout.bind(minimum_height=inner_layout.setter('height'))

        self.display_label = Label(text='', font_size=get_font_size(), height=get_dynamic_size(80, 60), size_hint_y=None)
        inner_layout.add_widget(self.display_label)

        self.input_text = TextInput(multiline=False, font_size=get_font_size(), height=get_dynamic_size(80, 60), size_hint_y=None)
        self.input_text.bind(on_text_validate=self.check_match)
        inner_layout.add_widget(self.input_text)

        self.char_count_slider = Slider(min=1, max=40, value=5, height=get_dynamic_size(50, 40), size_hint_y=None)
        self.char_count_slider.bind(value=self.update_char_count)
        inner_layout.add_widget(self.char_count_slider)

        self.time_slider = Slider(min=1, max=60, value=10, height=get_dynamic_size(50, 40), size_hint_y=None)
        self.time_slider.bind(value=self.update_time)
        inner_layout.add_widget(self.time_slider)

        self.char_count_label = Label(text='文字数: 5', font_size=get_font_size(), height=get_dynamic_size(50, 40), size_hint_y=None)
        inner_layout.add_widget(self.char_count_label)

        self.time_label = Label(text='count: 10', font_size=get_font_size(), height=get_dynamic_size(50, 40), size_hint_y=None)
        inner_layout.add_widget(self.time_label)

        button_layout = BoxLayout(size_hint_y=None, height=get_dynamic_size(70, 60))

        self.gen_button = Button(text='Generate', font_size=get_font_size(), size_hint=(1, None), height=get_dynamic_size(50, 40))
        self.gen_button.bind(on_press=self.generate_text)
        button_layout.add_widget(self.gen_button)

        self.reset_button = Button(text='Reset', font_size=get_font_size(), size_hint=(1, None), height=get_dynamic_size(50, 40))
        self.reset_button.bind(on_press=self.reset_input)
        button_layout.add_widget(self.reset_button)

        inner_layout.add_widget(button_layout)

        self.char_type = '数字'
        self.char_type_buttons = BoxLayout(size_hint_y=None, height=get_dynamic_size(70, 60))
        for char_type in ['数字', '英字', 'かな', 'カナ']:
            btn = Button(text=char_type, font_size=get_font_size(), size_hint=(1, None), height=get_dynamic_size(50, 40))
            btn.bind(on_press=self.set_char_type)
            self.char_type_buttons.add_widget(btn)
        inner_layout.add_widget(self.char_type_buttons)

        scroll.add_widget(inner_layout)
        self.add_widget(scroll)

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

        # カウントダウンの最初の値を即座に表示
        self.update_countdown(0)

        self.countdown_event = Clock.schedule_interval(self.update_countdown, 1)
        # 表示をクリアするタイミングを設定時間プラス2秒に設定
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

class TestApp(App):
    def build(self):
        return MainWidget()

if __name__ == '__main__':
    TestApp().run()