# color_panel モジュール
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label

def create_color_panel():
    panel = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)

    # カラースライダー（RGB各色を想定）
    color_slider = Slider(min=0, max=255, value=128, size_hint_x=0.2)

    # カラー入力フォーム（RGB値入力用）
    color_input = TextInput(text='#808080', size_hint_x=0.1)

    # カラースピナー（色選択用）
    color_spinner = Spinner(values=['#FF0000', '#00FF00', '#0000FF', '#FFFF00'], text='Red', size_hint_x=0.1)

    # カラー見本（選択した色を表示）
    color_sample = Label(size_hint_x=0.1, color=[1, 0, 0, 1])  # 初期値は赤色

    # 色モード切替トグルボタン
    color_mode_toggle = ToggleButton(text='RGB', size_hint_x=0.2)
    color_mode_toggle.bind(on_press=lambda instance: toggle_color_mode(instance))

    # ウィジェットをパネルに追加
    panel.add_widget(color_slider)
    panel.add_widget(color_input)
    panel.add_widget(color_spinner)
    panel.add_widget(color_sample)
    panel.add_widget(color_mode_toggle)

    return panel

def toggle_color_mode(button):
    if button.text == 'RGB':
        button.text = 'CMYK'
    elif button.text == 'CMYK':
        button.text = 'Grayscale'
    else:
        button.text = 'RGB'

    # ロジックを追加して色の表示や選択をモードに応じて更新
    # 例えば、スライダーやカラーサンプルの設定を切り替える

# このモジュールの使用例
if __name__ == '__main__':
    from kivy.app import App

    class ColorPanelApp(App):
        def build(self):
            return create_color_panel()

    ColorPanelApp().run()
