from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
import random


class CustomTextInput(TextInput):
    def __init__(self, digit_count, font_size, **kwargs):
        super(CustomTextInput, self).__init__(**kwargs)
        self.digit_count = digit_count
        self.font_size = font_size
        self.multiline = False
        self.input_filter = "int"
        self.hint_text = "Enter a number"
        self.generate_random_number()

    def generate_random_number(self):
        random_number = random.randint(0, 10**self.digit_count - 1)
        self.text = str(random_number).zfill(self.digit_count)


class CustomTextInputApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10)

        # Create a CustomTextInput instance with digit_count=5 and font_size=30
        custom_text_input = CustomTextInput(digit_count=5, font_size=30)
        layout.add_widget(custom_text_input)

        return layout


if __name__ == '__main__':
    CustomTextInputApp().run()
