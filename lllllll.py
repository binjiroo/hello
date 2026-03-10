from kivy.core.window import Window
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock

class StopwatchApp(App):

    def build(self):
        # ウインドウサイズの設定
        Window.size = (360, 120)

        # レイアウトの作成
        layout = BoxLayout(orientation='vertical')

        # 時間表示ラベル
        self.time_label = Label(text='00:00,00.00', size_hint=(1, 0.5), font_size=50, halign='center')
        layout.add_widget(self.time_label)

        # ボタンとチェックボックスのレイアウト
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.5))

        # 開始/停止ボタン
        self.start_stop_button = Button(text='Start', on_press=self.start_stop, size_hint=(0.30, 1), font_size=28)
        self.start_stop_button.bind(on_press=self.change_label)
        button_layout.add_widget(self.start_stop_button)

        # リセットボタン
        reset_button = Button(text='Reset', on_press=self.reset, size_hint=(0.30, 1), font_size=28)
        button_layout.add_widget(reset_button)

        self.copy_button = Button(text='copy', on_press=self.reset, size_hint=(0.30,1), font_size=28)
        self.copy_button.bind(on_press=self.change_label)
        button_layout.add_widget(self.copy_button)

        # 最前列チェックボックス
        self.always_on_top_checkbox = CheckBox(active=False, size_hint=(0.1, 1))
        self.always_on_top_checkbox.bind(active=self.toggle_always_on_top)
        button_layout.add_widget(self.always_on_top_checkbox)

        layout.add_widget(button_layout)

        # タイマー初期化
        self.elapsed_time = 0
        self.is_running = False

        # タイマー更新用のメソッドを1秒ごとに呼び出す
        Clock.schedule_interval(self.update_timer, 0.01)

        return layout

    def update_timer(self, dt):
        if self.is_running:
            self.elapsed_time += dt
            minutes, seconds = divmod(self.elapsed_time, 60)
            hours, minutes = divmod(minutes, 60)
            self.time_label.text = '%02d:%02d,%02d.%02d' % (int(hours), int(minutes), int(seconds), int((self.elapsed_time * 100) % 100))

    def start_stop(self, instance):
        if self.is_running:
            self.is_running = False
            self.start_stop_button.text = 'Start'
        else:
            self.is_running = True
            self.start_stop_button.text = 'Stop'

    def reset(self, instance):
        self.elapsed_time = 0
        self.is_running = False
        self.start_stop_button.text = 'Start'
        self.time_label.text = '00:00,00.00'

    def toggle_always_on_top(self, instance, value):
        self.root_window.always_on_top = value

    def change_label(self,instance):
        if instance.text == "start":
            instance.text = "stop"
        else:
            instance.text = "start"
        

if __name__ == '__main__':
    StopwatchApp().run()
