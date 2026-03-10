from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout

def create_text_main_panel():
    panel = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)

    # フォント種類表示と選択
    font_spinner = Spinner(
        text='Default font',
        values=('Arial', 'Verdana', 'Helvetica', 'Times New Roman'),
        size_hint_y=None, height=40, size_hint_x=0.15
    )

    # フォントサイズ変更
    font_size_slider = Slider(min=8, max=72, value=12, size_hint_y=None, height=30, size_hint_x=0.2)
    font_size_input = TextInput(text='12', size_hint_y=None, height=40, size_hint_x=0.05)
    font_size_spinner = Spinner(
        values=[str(x) for x in range(8, 73)],
        text='12',
        size_hint_y=None, height=30, size_hint_x=0.05
    )

    # 文字色変更
    color_slider = Slider(min=0, max=255, value=128, size_hint_y=None, height=40, size_hint_x=0.2)  # 簡易例で、RGB一括調整用のスライダー
    color_input = TextInput(text='#808080', size_hint_y=None, height=40, size_hint_x=0.1)
    color_spinner = Spinner(
        values=['#FF0000', '#00FF00', '#0000FF', '#FFFF00'],
        text='Red',
        size_hint_y=None, height=40, size_hint_x=0.1
    )

    # ウィジェットをパネルに追加
    panel.add_widget(Label(text='Font:', size_hint_y=None, height=40, size_hint_x=0.075))
    panel.add_widget(font_spinner)
    panel.add_widget(font_size_slider)
    panel.add_widget(font_size_input)
    panel.add_widget(font_size_spinner)
    panel.add_widget(color_slider)
    panel.add_widget(color_input)
    panel.add_widget(color_spinner)

    return panel

def create_text_sub_panel():
    panel = BoxLayout(orientation='vertical', size_hint_y=None, height=120)
    
    # トグルボタンのグループ名を設定
    group_name = 'text_sub_panel_toggles'
    
    # テキストの基点を指定する9点のトグルスイッチ
    grid = GridLayout(
        cols=3,
        size_hint=(None, None),
        size=(90, 90),  # 正方形のトグルボタン
    )
    
    for pos in ['7', '8', '9', '4', '5', '6', '1', '2', '3']:
        toggle = ToggleButton(
            text=pos,
            size_hint=(None, None),
            size=(30, 30),
            group=group_name  # グループ名を指定
        )
        grid.add_widget(toggle)
    
    # 20x20トグルボタン下に配置するフォームとボタン
    button_layout = BoxLayout(size_hint_y=None, height=30)
    
    panel.add_widget(grid)
    panel.add_widget(button_layout)
    
    return panel


