from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.app import App

def create_drawing_main_panel():
    panel = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
    drawing_tools = ['点', '線', '矩形', '円', '円弧', '曲線', '多角形', '自由線']
    for tool in drawing_tools:
        btn = Button(text=tool)
        btn.bind(on_press=lambda x, tool=tool: App.get_running_app().activate_tool(tool))
        panel.add_widget(btn)
    return panel

def create_drawing_sub_panel():
    panel = BoxLayout(orientation='vertical', size_hint_y=None, height=120)

    # カラー入力フォーム（RGB値入力用）
    drawing_input = TextInput(text='#808080', size_hint_y=None, height=40)

    # カラースライダー（RGB各色を想定）
    drawing_slider = Slider(min=0, max=255, value=128, size_hint_y=None, height=40)

    # カラースピナー（色選択用）
    drawing_spinner = Spinner(values=['#FF0000', '#00FF00', '#0000FF', '#FFFF00'], text='Red', size_hint_y=None, height=40)

    panel.add_widget(drawing_input)
    panel.add_widget(drawing_slider)
    panel.add_widget(drawing_spinner)

    return panel

def activate_tool(tool):
    app = App.get_running_app()
    if hasattr(app, 'activate_tool'):
        app.activate_tool(tool)  # MainApp の activate_tool メソッドを呼び出し
    print(f"{tool} ツールがアクティブになりました")
