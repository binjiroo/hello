# main.py
from kivymd.app import MDApp
from kivy.core.window import Window
from widget import ProjectTreeWidget
import kivy
from kivy.logger import Logger
from kivy.core.text import LabelBase  # フォント登録のために追加

# フォントの登録
LabelBase.register(name='NotoSansJP', fn_regular='fonts/NotoSansJP-VariableFont_wght.ttf')  # フォントファイルのパスを確認

class ProjectTreeManagerApp(MDApp):
    def build(self):
        # フォントスタイルの変更
        self.theme_cls.font_styles = {
            "H1": ["NotoSansJP", 32, False, False],
            "H2": ["NotoSansJP", 24, False, False],
            "H3": ["NotoSansJP", 20, False, False],
            "H4": ["NotoSansJP", 18, False, False],
            "H5": ["NotoSansJP", 16, False, False],
            "H6": ["NotoSansJP", 14, False, False],
            "Subtitle1": ["NotoSansJP", 16, False, False],
            "Subtitle2": ["NotoSansJP", 14, False, False],
            "Body1": ["NotoSansJP", 16, False, False],
            "Body2": ["NotoSansJP", 14, False, False],
            "Button": ["NotoSansJP", 14, True, False],
            "Caption": ["NotoSansJP", 12, False, False],
            "Overline": ["NotoSansJP", 10, False, False],
        }
        
        # ウィンドウのタイトルを設定
        self.title = 'Project Tree Manager'
        
        # ウィンドウのサイズを設定
        Window.size = (800, 600)
        
        # ルートウィジェットとして ProjectTreeWidget を返す
        return ProjectTreeWidget()

    def on_start(self):
        import sys
        sys.excepthook = self.handle_exception

    def handle_exception(self, exctype, value, tb):
        Logger.exception('Uncaught exception:', exc_info=(exctype, value, tb))
        import traceback
        traceback.print_exception(exctype, value, tb)

if __name__ == '__main__':
    ProjectTreeManagerApp().run()
