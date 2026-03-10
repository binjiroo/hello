from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

class SquareRootApp(App):
    def build(self):
        self.title = '平方根計算機'
        
        # メインレイアウトの設定
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 入力フィールドの設定
        self.input_field = TextInput(
            hint_text='数字を入力してください',
            multiline=False,
            input_filter='float',
            size_hint_y=None,
            height=50,
            font_size=24
        )
        main_layout.add_widget(self.input_field)
        
        # 計算ボタンの設定
        calc_button = Button(
            text='計算',
            on_press=self.calculate_square_root,
            size_hint_y=None,
            height=50,
            font_size=24
        )
        main_layout.add_widget(calc_button)
        
        # スクロールビューの設定
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.result_container = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.result_container.bind(minimum_height=self.result_container.setter('height'))
        
        self.scroll_view.add_widget(self.result_container)
        main_layout.add_widget(self.scroll_view)
        
        return main_layout
    
    def calculate_square_root(self, instance):
        try:
            # ユーザーの入力を取得
            number = float(self.input_field.text)
            
            if number < 0:
                self.result_container.clear_widgets()
                self.result_container.add_widget(Label(text='平方根は負の数には計算できません。', font_size=24))
            else:
                # 初期の近似値の設定
                lower_bound = int(number**0.5)  # 初期の下限
                upper_bound = lower_bound + 1  # 初期の上限
                
                lower_bound_square = lower_bound ** 2
                upper_bound_square = upper_bound ** 2
                
                # 計算過程を生成
                process = []
                process.append(f'入力された数値: {number}')
                process.append(f'初期の近似範囲: {lower_bound}と{upper_bound}')
                
                # 近似範囲を縮めていく
                while upper_bound_square - lower_bound_square > 0.01:
                    midpoint = (lower_bound + upper_bound) / 2
                    midpoint_square = midpoint ** 2
                    
                    if midpoint_square < number:
                        lower_bound = midpoint
                    else:
                        upper_bound = midpoint
                    
                    lower_bound_square = lower_bound ** 2
                    upper_bound_square = upper_bound ** 2
                    
                    process.append(f'中間値: {midpoint:.2f}, {midpoint}^2 = {midpoint_square:.2f}')
                
                # 最終的な近似値
                sqrt_value = (lower_bound + upper_bound) / 2
                process.append(f'平方根の近似値: {sqrt_value:.2f}')
                
                # 結果表示
                self.result_container.clear_widgets()
                for line in process:
                    # 各行の高さを設定するために、size_hint_y を明示的に指定
                    label = Label(text=line, size_hint_y=None, height=20, font_size=24)
                    self.result_container.add_widget(label)
                
        except ValueError:
            self.result_container.clear_widgets()
            self.result_container.add_widget(Label(text='有効な数字を入力してください。', font_size=24))

if __name__ == '__main__':
    SquareRootApp().run()
