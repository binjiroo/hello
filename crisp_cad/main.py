# main.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from widget import create_widget_a, create_widget_b  # widget.pyからウィジェット生成関数をインポート

class ScreenOne(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # 初期表示のウィジェットA
        self.current_widget = create_widget_a()
        layout.add_widget(self.current_widget)

        # ウィジェットを切り替えるボタン
        button_a = Button(text="Show Widget A", size_hint=(None, None), size=(200, 50), pos=(100, 100))
        button_b = Button(text="Show Widget B", size_hint=(None, None), size=(200, 50), pos=(400, 100))

        button_a.bind(on_press=self.show_widget_a)
        button_b.bind(on_press=self.show_widget_b)

        layout.add_widget(button_a)
        layout.add_widget(button_b)

        self.add_widget(layout)

    def show_widget_a(self, instance):
        """ウィジェットAを表示"""
        if self.current_widget:
            self.remove_widget(self.current_widget)
        self.current_widget = create_widget_a()
        self.add_widget(self.current_widget)

    def show_widget_b(self, instance):
        """ウィジェットBを表示"""
        if self.current_widget:
            self.remove_widget(self.current_widget)
        self.current_widget = create_widget_b()
        self.add_widget(self.current_widget)

class ScreenTwo(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # 初期表示のウィジェットA
        self.current_widget = create_widget_a()
        layout.add_widget(self.current_widget)

        # ウィジェットを切り替えるボタン
        button_a = Button(text="Show Widget A", size_hint=(None, None), size=(200, 50), pos=(100, 100))
        button_b = Button(text="Show Widget B", size_hint=(None, None), size=(200, 50), pos=(400, 100))

        button_a.bind(on_press=self.show_widget_a)
        button_b.bind(on_press=self.show_widget_b)

        layout.add_widget(button_a)
        layout.add_widget(button_b)

        self.add_widget(layout)

    def show_widget_a(self, instance):
        """ウィジェットAを表示"""
        if self.current_widget:
            self.remove_widget(self.current_widget)
        self.current_widget = create_widget_a()
        self.add_widget(self.current_widget)

    def show_widget_b(self, instance):
        """ウィジェットBを表示"""
        if self.current_widget:
            self.remove_widget(self.current_widget)
        self.current_widget = create_widget_b()
        self.add_widget(self.current_widget)

class MyApp(App):
    def build(self):
        sm = ScreenManager()

        # スクリーンを追加
        screen_one = ScreenOne(name='screen_one')  # ScreenOneを作成
        screen_two = ScreenTwo(name='screen_two')  # ScreenTwoを作成

        sm.add_widget(screen_one)  # ScreenOneをScreenManagerに追加
        sm.add_widget(screen_two)  # ScreenTwoをScreenManagerに追加

        # 初期スクリーンを設定
        sm.current = 'screen_one'  # 最初に表示するスクリーンを設定

        return sm

if __name__ == '__main__':
    MyApp().run()
