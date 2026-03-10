import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock
import webview

class YouTubeApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        
        self.url_input = TextInput(hint_text='Enter YouTube URL', size_hint=(1, 0.1))
        self.layout.add_widget(self.url_input)
        
        self.play_button = Button(text='Play', size_hint=(1, 0.1))
        self.play_button.bind(on_press=self.play_video)
        self.layout.add_widget(self.play_button)
        
        return self.layout
    
    def play_video(self, instance):
        url = self.url_input.text
        
        # open_webviewメソッドをメインスレッドで実行する
        Clock.schedule_once(lambda dt: self.open_webview(url))

    def open_webview(self, url):
        # WebView2ウィンドウを作成してURLを表示
        webview.create_window('YouTube Video', url, width=600, height=1000, x=0, y=0)
        webview.start()

        # イベントループ内でウィンドウのイベントを処理
        while webview.window_should_continue():
            webview.dispatch([])

        # ウィンドウが閉じられた後にKivyアプリケーションを終了
        App.get_running_app().stop()

if __name__ == '__main__':
    YouTubeApp().run()
