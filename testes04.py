import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from sympy import symbols, diff, integrate, sympify, lambdify
import matplotlib.pyplot as plt
import numpy as np

class CalcWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(CalcWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'

        input_layout = BoxLayout(size_hint_y=None, height=50)
        self.input_label = Label(text='関数を入力してください (例: x**2 + 3*x + 2):', size_hint_x=None, width=400)
        input_layout.add_widget(self.input_label)

        self.function_input = TextInput(multiline=False, size_hint_y=None, height=50)
        input_layout.add_widget(self.function_input)
        self.add_widget(input_layout)

        button_layout = BoxLayout(size_hint_y=None, height=50)
        
        self.diff_button = Button(text='微分', size_hint_y=None, height=50)
        self.diff_button.bind(on_press=self.calculate_diff)
        button_layout.add_widget(self.diff_button)

        self.integrate_button = Button(text='積分', size_hint_y=None, height=50)
        self.integrate_button.bind(on_press=self.calculate_integrate)
        button_layout.add_widget(self.integrate_button)

        self.plot_button = Button(text='グラフ表示', size_hint_y=None, height=50)
        self.plot_button.bind(on_press=self.plot_function)
        button_layout.add_widget(self.plot_button)

        self.add_widget(button_layout)

        self.result_label = Label(text='結果:')
        self.add_widget(self.result_label)

    def calculate_diff(self, instance):
        x = symbols('x')
        function_text = self.function_input.text
        try:
            function = sympify(function_text)
            derivative = diff(function, x)
            self.result_label.text = f'微分結果: {derivative}'
        except Exception as e:
            self.show_popup(f'エラー: {str(e)}')

    def calculate_integrate(self, instance):
        x = symbols('x')
        function_text = self.function_input.text
        try:
            function = sympify(function_text)
            integral = integrate(function, x)
            self.result_label.text = f'積分結果: {integral}'
        except Exception as e:
            self.show_popup(f'エラー: {str(e)}')

    def plot_function(self, instance):
        x = symbols('x')
        function_text = self.function_input.text
        try:
            function = sympify(function_text)
            x_vals = np.linspace(-10, 10, 400)
            f_lambdified = lambdify(x, function, 'numpy')
            y_vals = f_lambdified(x_vals)

            plt.plot(x_vals, y_vals, label=str(function))
            plt.xlabel('x')
            plt.ylabel('f(x)')
            plt.title('関数のグラフ')
            plt.legend()
            plt.grid(True)
            plt.show()
        except Exception as e:
            self.show_popup(f'エラー: {str(e)}')

    def show_popup(self, message):
        popup = Popup(title='エラー',
                      content=Label(text=message),
                      size_hint=(None, None), size=(400, 400))
        popup.open()

class CalcApp(App):
    def build(self):
        return CalcWidget()

if __name__ == '__main__':
    CalcApp().run()
