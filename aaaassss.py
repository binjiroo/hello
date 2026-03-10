from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.dropdown import DropDown
import random
import logging

class CustomSpinner(Spinner):
    print("g")
    def __init__(self, **kwargs):
        print("h")
        super().__init__(**kwargs)
        print("h")
        self.font_size = 48
        print("i")
        self.dropdown_cls = CustomDropDown
        print("j")

class CustomDropDown(DropDown):
    print("k")
    def __init__(self, **kwargs):
        print("l")
        super().__init__(**kwargs)
        print("m")
        self.font_size = 48
        print("n")

    print("k2")
    def open(self, *args, **kwargs):
        print("o")
        super().open(*args, **kwargs)
        print("p")
        for item in self.container.children:
            print("q")
            item.font_size = 48
            print("r")

class RandomNumberApp(App):
    print("a")
    number1 = StringProperty("0")
    print("b")
    number2 = StringProperty("0")
    print("c")
    result = StringProperty("")
    print("d")
    digits = NumericProperty(1)
    print("e")

    print("f")
    def build(self):
        print("1")
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        print("2")

        self.number_label1 = Label(text=self.number1, font_size=48)
        print("3")
        self.number_label2 = Label(text=self.number2, font_size=48)
        print("4")
        self.result_label = Label(text=self.result, font_size=48)
        print("5")

        self.digits_slider = Slider(min=1, max=20, value=1, step=1)
        print("6")
        self.digits_slider.bind(value=self.on_slider_value_change)
        print("7")

        self.operator_spinner = CustomSpinner(text='+', values=('+', '-', '*', '/'))
        print("8")
        self.operator_spinner.bind(text=self.on_operator_select)
        print("9")

        generate_button = Button(text='生成', font_size=48, on_press=self.generate_numbers)
        print("10")
        answer_button = Button(text='解答', font_size=48, on_press=self.calculate_result)
        print("11")

        top_layout = BoxLayout(orientation='vertical', spacing=10)
        print("12")
        top_layout.add_widget(self.number_label1)
        print("13")
        top_layout.add_widget(self.number_label2)
        print("14")

        button_layout = BoxLayout(orientation='horizontal', spacing=10)
        print("15")
        button_layout.add_widget(generate_button)
        print("16")
        button_layout.add_widget(self.operator_spinner)
        print("17")
        button_layout.add_widget(answer_button)
        print("18")

        main_layout.add_widget(top_layout)
        print("19")
        main_layout.add_widget(self.result_label)
        print("20")
        main_layout.add_widget(self.digits_slider)
        print("21")
        main_layout.add_widget(button_layout)
        print("22")

        return main_layout

    def on_slider_value_change(self, instance, value):
        print("23")
        self.digits = int(value)
        print("24")
        print(f"Slider value changed to: {value}")  # 追跡用のprint

    def on_operator_select(self, spinner, text):
        print("25")
        print(f"Operator selected: {text}")  # 追跡用のprint
        pass

    def generate_numbers(self, instance):
        print("26")
        max_value = 10 ** self.digits - 1
        print("27")
        self.number1 = str(random.randint(0, max_value))
        print("28")
        self.number2 = str(random.randint(0, max_value))
        print("29")
        self.number_label1.text = self.number1
        print("30")
        self.number_label2.text = self.number2
        print("31")
        print(f"Generated numbers: {self.number1}, {self.number2}")  # 追跡用のprint

    def calculate_result(self, instance):
        print("32")
        num1 = int(self.number1)
        print("33")
        num2 = int(self.number2)
        print("34")
        operator = self.operator_spinner.text
        print("35")

        if operator == '+':
            print("36a")
            self.result = str(num1 + num2)
            print("36b")
        elif operator == '-':
            print("36c")
            self.result = str(num1 - num2)
            print("36d")
        elif operator == '*':
            print("36e")
            self.result = str(num1 * num2)
            print("36f")
        elif operator == '/':
            print("36g")
            if num2 != 0:
                print("36h")
                self.result = str(num1 / num2)
                print("36i")
            else:
                print("36j")
                self.result = "Error"
                print("36k")

        self.result_label.text = self.result
        print("37")
        print(f"Calculated result: {self.result}")  # 追跡用のprint

if __name__ == '__main__':
    print("0")
    RandomNumberApp().run()
    print("00")