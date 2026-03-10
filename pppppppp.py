from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

def factorize(n):
    factors = []
    for i in range(1, n + 1):
        if n % i == 0:
            factors.append(i)
    return factors

def prime_factorize(n):
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors

class FactorizationApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        self.input_label = Label(text="整数を入力してください:")
        layout.add_widget(self.input_label)
        
        self.text_input = TextInput(text='', multiline=False)
        layout.add_widget(self.text_input)
        
        self.factor_button = Button(text="因数分解")
        self.factor_button.bind(on_press=self.display_factors)
        layout.add_widget(self.factor_button)
        
        self.prime_factor_button = Button(text="素因数分解")
        self.prime_factor_button.bind(on_press=self.display_prime_factors)
        layout.add_widget(self.prime_factor_button)
        
        self.result_label = Label(text="結果がここに表示されます")
        layout.add_widget(self.result_label)
        
        return layout
    
    def display_factors(self, instance):
        try:
            num = int(self.text_input.text)
            factors = factorize(num)
            self.result_label.text = f"因数分解: {factors}"
        except ValueError:
            self.result_label.text = "無効な入力です。整数を入力してください。"
    
    def display_prime_factors(self, instance):
        try:
            num = int(self.text_input.text)
            prime_factors = prime_factorize(num)
            self.result_label.text = f"素因数分解: {prime_factors}"
        except ValueError:
            self.result_label.text = "無効な入力です。整数を入力してください。"

if __name__ == "__main__":
    FactorizationApp().run()
