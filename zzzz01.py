from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from sympy import symbols, expand

class EquationApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # Input field for the equation
        self.input_field = TextInput(font_size=24, hint_text="例: (x+y)^2", multiline=False)
        self.add_widget(self.input_field)

        # Button to calculate the result
        self.calculate_button = Button(text="計算", font_size=24)
        self.calculate_button.bind(on_press=self.calculate)
        self.add_widget(self.calculate_button)

        # Label to display the result
        self.result_label = Label(text="結果がここに表示されます", font_size=24)
        self.add_widget(self.result_label)

        # Button to clear the input field
        self.clear_input_button = Button(text="入力クリア", font_size=24)
        self.clear_input_button.bind(on_press=self.clear_input)
        self.add_widget(self.clear_input_button)

        # Button to clear the result field
        self.clear_result_button = Button(text="結果クリア", font_size=24)
        self.clear_result_button.bind(on_press=self.clear_result)
        self.add_widget(self.clear_result_button)

    def calculate(self, instance):
        try:
            # Parse the input equation
            x, y = symbols('x y')
            expression = self.input_field.text
            expanded_expression = expand(expression)

            # Display the result
            self.result_label.text = f'展開結果: {expanded_expression}'
        except Exception as e:
            self.result_label.text = f'エラー: {str(e)}'

    def clear_input(self, instance):
        self.input_field.text = ''

    def clear_result(self, instance):
        self.result_label.text = '結果がここに表示されます'

class EquationAppApp(App):
    def build(self):
        return EquationApp()

if __name__ == '__main__':
    EquationAppApp().run()
