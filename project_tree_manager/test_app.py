from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivy.core.window import Window

class TestApp(MDApp):
    def build(self):
        Window.size = (300, 200)
        return MDLabel(text="Hello, KivyMD!", halign="center")

if __name__ == "__main__":
    TestApp().run()
