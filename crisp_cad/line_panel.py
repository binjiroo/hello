# line_panel.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner

def create_line_panel():
    panel = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)

    # 線幅調整用のウィジェット
    line_width_slider = Slider(min=1, max=10, value=1, size_hint_x=0.3)  # スライダーの横幅比を3に設定
    line_width_input = TextInput(text='1', size_hint_x=0.1)              # 入力フォームの横幅比を1に設定
    line_width_spinner = Spinner(values=[str(x) for x in range(1, 11)], text='1', size_hint_x=0.1)  # スピナーの横幅比を1に設定

    # 線種調整用のウィジェット
    line_style_slider = Slider(min=1, max=5, value=1, size_hint_x=0.3)  # スライダーの横幅比を3に設定
    line_style_input = TextInput(text='1', size_hint_x=0.1)             # 入力フォームの横幅比を1に設定
    line_style_spinner = Spinner(values=[str(x) for x in range(1, 6)], text='1', size_hint_x=0.1)   # スピナーの横幅比を1に設定

    # ウィジェットをパネルに追加
    panel.add_widget(line_width_slider)
    panel.add_widget(line_width_input)
    panel.add_widget(line_width_spinner)
    panel.add_widget(line_style_slider)
    panel.add_widget(line_style_input)
    panel.add_widget(line_style_spinner)

    return panel
