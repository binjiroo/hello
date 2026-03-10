# widget.py
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout

def create_widget_a():
    """ウィジェットAを作成"""
    layout = FloatLayout()
    label = Label(text="This is Widget A", size_hint=(None, None), size=(200, 50), pos=(100, 300))
    button = Button(text="Button A", size_hint=(None, None), size=(200, 50), pos=(100, 200))
    layout.add_widget(label)
    layout.add_widget(button)
    return layout

def create_widget_b():
    """ウィジェットBを作成"""
    layout = FloatLayout()
    label = Label(text="This is Widget B", size_hint=(None, None), size=(200, 50), pos=(100, 300))
    button = Button(text="Button B", size_hint=(None, None), size=(200, 50), pos=(100, 200))
    layout.add_widget(label)
    layout.add_widget(button)
    return layout
