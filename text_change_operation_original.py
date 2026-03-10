# main.py

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from text_change_operation import TextChangeOperation
from text_editing_operation import TextEditingOperation  # 仮定
from text_modifiable_operation import TextModifiableOperation  # 仮定

Window.size = (1400, 750)

class TextChangeOperationScreen(Screen):
    def __init__(self, **kwargs):
        super(TextChangeOperationScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Text Change Operation'))
        layout.add_widget(TextChangeOperation())

        button_layout = BoxLayout(size_hint_y=None, height=50)
        btn_to_change = Button(text='Text Change Operation')
        btn_to_editing = Button(text='Text Editing Operation')
        btn_to_modifiable = Button(text='Text Modifiable Operation')
        
        btn_to_change.bind(on_press=self.go_to_change)
        btn_to_editing.bind(on_press=self.go_to_editing)
        btn_to_modifiable.bind(on_press=self.go_to_modifiable)
        
        button_layout.add_widget(btn_to_change)
        button_layout.add_widget(btn_to_editing)
        button_layout.add_widget(btn_to_modifiable)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)

    def go_to_change(self, *args):
        self.manager.current = 'text_change_operation'

    def go_to_editing(self, *args):
        self.manager.current = 'text_editing_operation'

    def go_to_modifiable(self, *args):
        self.manager.current = 'text_modifiable_operation'

class TextEditingOperationScreen(Screen):
    def __init__(self, **kwargs):
        super(TextEditingOperationScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Text Editing Operation'))
        layout.add_widget(TextEditingOperation())

        button_layout = BoxLayout(size_hint_y=None, height=50)
        btn_to_change = Button(text='Text Change Operation')
        btn_to_editing = Button(text='Text Editing Operation')
        btn_to_modifiable = Button(text='Text Modifiable Operation')
        
        btn_to_change.bind(on_press=self.go_to_change)
        btn_to_editing.bind(on_press=self.go_to_editing)
        btn_to_modifiable.bind(on_press=self.go_to_modifiable)
        
        button_layout.add_widget(btn_to_change)
        button_layout.add_widget(btn_to_editing)
        button_layout.add_widget(btn_to_modifiable)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)

    def go_to_change(self, *args):
        self.manager.current = 'text_change_operation'

    def go_to_editing(self, *args):
        self.manager.current = 'text_editing_operation'

    def go_to_modifiable(self, *args):
        self.manager.current = 'text_modifiable_operation'

class TextModifiableOperationScreen(Screen):
    def __init__(self, **kwargs):
        super(TextModifiableOperationScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Text Modifiable Operation'))
        layout.add_widget(TextModifiableOperation())

        button_layout = BoxLayout(size_hint_y=None, height=50)
        btn_to_change = Button(text='Text Change Operation')
        btn_to_editing = Button(text='Text Editing Operation')
        btn_to_modifiable = Button(text='Text Modifiable Operation')
        
        btn_to_change.bind(on_press=self.go_to_change)
        btn_to_editing.bind(on_press=self.go_to_editing)
        btn_to_modifiable.bind(on_press=self.go_to_modifiable)
        
        button_layout.add_widget(btn_to_change)
        button_layout.add_widget(btn_to_editing)
        button_layout.add_widget(btn_to_modifiable)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)

    def go_to_change(self, *args):
        self.manager.current = 'text_change_operation'

    def go_to_editing(self, *args):
        self.manager.current = 'text_editing_operation'

    def go_to_modifiable(self, *args):
        self.manager.current = 'text_modifiable_operation'

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TextChangeOperationScreen(name='text_change_operation'))
        sm.add_widget(TextEditingOperationScreen(name='text_editing_operation'))
        sm.add_widget(TextModifiableOperationScreen(name='text_modifiable_operation'))

        return sm

if __name__ == '__main__':
    MyApp().run()