from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionGroup, ActionButton, ActionDropDown
from kivy.uix.filechooser import FileChooserIconView
from kivy.graphics import Color, Rectangle
import os
import shutil

class CustomDropDown(ActionDropDown):
    def __init__(self, **kwargs):
        super(CustomDropDown, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 0.9)  # グレー色の背景を設定、透明度も調整可能
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class FileManager(BoxLayout):
    def __init__(self, **kwargs):
        super(FileManager, self).__init__(orientation='vertical', **kwargs)

        # アクションバーの設定
        self.actionbar = ActionBar(pos_hint={'top': 1})
        self.action_view = ActionView()
        self.actionbar.add_widget(self.action_view)

        self.action_previous = ActionPrevious(title='メインメニュー', with_previous=False)
        self.action_view.add_widget(self.action_previous)

        # ファイルメニューの設定
        self.file_menu = self.create_menu('ファイル', [
            ('新規作成', self.new_file),
            ('開く', self.open_file),
            ('名付て保存', self.save_file_as),
            ('上書き保存', self.save_file),
            ('ファイルコピー', self.copy_file),
            ('ファイルペースト', self.paste_file)
        ])
        self.action_view.add_widget(self.file_menu)

        # 他のメニューアイテム
        self.action_view.add_widget(self.create_menu('編集', []))
        self.action_view.add_widget(self.create_menu('表示', []))
        self.action_view.add_widget(self.create_menu('設定', []))
        self.action_view.add_widget(self.create_menu('その他', []))

        self.add_widget(self.actionbar)

        # ファイル選択コンポーネント
        self.filechooser = FileChooserIconView(size_hint=(1, 0.8))
        self.add_widget(self.filechooser)

        # テキスト編集エリア
        self.text_input = TextInput(size_hint=(1, 0.2))
        self.add_widget(self.text_input)

    def create_menu(self, title, items):
        dropdown = CustomDropDown()
        for item_text, item_callback in items:
            btn = ActionButton(text=item_text, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            btn.bind(on_release=item_callback)
            dropdown.add_widget(btn)
        
        main_button = ActionButton(text=title, size_hint_y=None, height=44)
        main_button.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(main_button, 'text', x))
        return main_button

    def new_file(self, instance):
        self.filechooser.path = ''
        self.text_input.text = ''

    def open_file(self, instance):
        if self.filechooser.selection:
            selected_path = self.filechooser.selection[0]
            try:
                with open(selected_path, 'r') as file:
                    self.text_input.text = file.read()
            except Exception as e:
                self.text_input.text = f'エラー: {e}'

    def save_file_as(self, instance):
        self.save_text('名付て保存')

    def save_file(self, instance):
        if self.filechooser.selection:
            selected_path = self.filechooser.selection[0]
            self.save_text('上書き保存', selected_path)

    def save_text(self, mode, file_path=None):
        if mode == '名付て保存':
            file_path = self.filechooser.path + '/' + self.text_input.text.split('\n')[0] + '.txt'
        with open(file_path, 'w') as file:
            file.write(self.text_input.text)

    def copy_file(self, instance):
        if self.filechooser.selection:
            self.clipboard = self.filechooser.selection[0]
            self.text_input.text = 'ファイルをコピーしました。'

    def paste_file(self, instance):
        if hasattr(self, 'clipboard') and self.clipboard:
            destination = os.path.join(self.filechooser.path, os.path.basename(self.clipboard))
            shutil.copy(self.clipboard, destination)
            self.text_input.text = 'ファイルをペーストしました。'

class FileManagerApp(App):
    def build(self):
        return FileManager()

if __name__ == '__main__':
    FileManagerApp().run()
