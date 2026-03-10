import os
import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from cefpython3 import cefpython as cef
import subprocess

# CEFのパスを環境変数に追加
cef_dir = r'C:\Users\kokada\projectpython\myenv\Lib\cef_binary_126.1.14+g2be337f+chromium-126.0.6478.57_windows64 (1)\cef_binary_126.1.14+g2be337f+chromium-126.0.6478.57_windows64\Release'
os.environ['PATH'] += f';{cef_dir}'

class CefBrowser(Widget):
    def __init__(self, **kwargs):
        super(CefBrowser, self).__init__(**kwargs)
        self.browser = None
        self.browser_ready = False
        self.bind(size=self.on_size, pos=self.on_position)

    def start_cef(self, url):
        sys.excepthook = cef.ExceptHook
        settings = {
            "auto_zooming": "100%",
        }
        cef.Initialize(settings=settings)
        window_info = cef.WindowInfo()
        window_info.SetAsChild(int(Window.get_window_info().window), [0, 0, int(self.width), int(self.height)])
        self.browser = cef.CreateBrowserSync(window_info, url=url, window_title="YouTube")
        self.browser_ready = True
        self.set_browser_geometry()
        Clock.schedule_interval(self.update, 0.01)

    def on_size(self, instance, value):
        self.set_browser_geometry()

    def on_position(self, instance, value):
        self.set_browser_geometry()

    def set_browser_geometry(self):
        if self.browser:
            x, y = self.to_window(self.x, self.y)
            width, height = self.size
            self.browser.SetBounds(0, 0, int(width), int(height))  # 修正：SetBoundsの引数を変更
            self.browser.WasResized()

    def update(self, dt):
        cef.MessageLoopWork()

    def on_close(self):
        if self.browser:
            self.browser.CloseBrowser()

class WebViewApp(App):
    def __init__(self, **kwargs):
        super(WebViewApp, self).__init__(**kwargs)
        self.jar_path = os.path.join(os.path.dirname(__file__), 'YouTubePlayerApp.jar')
        if os.path.exists(self.jar_path):
            subprocess.Popen(['java', '-jar', self.jar_path])
        else:
            print(f"Error: Unable to access jarfile {self.jar_path}")

    def build(self):
        layout = BoxLayout(orientation='vertical')

        # YouTube動画表示用のCEFブラウザを追加
        self.cef_browser = CefBrowser(size_hint=(1, 0.8))  # サイズを調整
        self.cef_browser.start_cef("https://www.youtube.com")
        layout.add_widget(self.cef_browser)

        # 入力フォームを追加
        self.url_input = TextInput(text='https://www.youtube.com', size_hint=(1, 0.1), multiline=False)
        layout.add_widget(self.url_input)

        # ボタンを追加
        self.load_button = Button(text='Load Video', size_hint=(1, 0.1))
        self.load_button.bind(on_press=self.load_video)
        layout.add_widget(self.load_button)

        return layout

    def load_video(self, instance):
        url = self.url_input.text
        if url:
            Clock.schedule_once(lambda dt: self.load_url_when_ready(url), 0.1)

    def load_url_when_ready(self, url):
        if self.cef_browser.browser_ready and self.cef_browser.browser:
            self.cef_browser.browser.LoadUrl(url)
        else:
            Clock.schedule_once(lambda dt: self.load_url_when_ready(url), 0.1)

    def on_stop(self):
        self.cef_browser.on_close()
        cef.Shutdown()

if __name__ == '__main__':
    WebViewApp().run()
