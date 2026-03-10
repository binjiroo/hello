# 標準ライブラリ
import json
import os
from os.path import expanduser

# サードパーティライブラリ（Kivy関連）
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.treeview import TreeView, TreeViewLabel

# Config設定
Config.set('kivy', 'default_font', ['Meiryo', 'C:\\Windows\\Fonts\\meiryo.ttc'])

# ユーザーホームディレクトリの定義
home_directory = expanduser("~")

class CustomFileChooser(FileChooserIconView):
    """カスタムファイルチューザークラスで、指定されたシステムファイルをフィルタリングします。"""

    # システムファイルリスト
    system_files = ['hiberfil.sys', 'pagefile.sys', 'swapfile.sys', 'dumpstack.log.tmp']

    def __init__(self, **kwargs):
        """初期化メソッドでは、カスタムフィルタをフィルタリストに設定します。"""
        super().__init__(**kwargs)  # Python 3のスタイルに更新
        self.filters = [self.custom_filter]

    def custom_filter(self, directory, filename):
        """ディレクトリとファイル名を受け取り、システムファイルをフィルタリングします。"""
        # ファイル名がシステムファイルリストに含まれているかどうかをチェック
        return filename.lower() not in self.system_files
    
# 仮想のCustomFileChooserインスタンスを作成
custom_file_chooser = CustomFileChooser()

# システムファイルと通常のファイル名でメソッドをテスト
assert not custom_file_chooser.custom_filter("", "hiberfil.sys")  # Falseが返るべき
assert not custom_file_chooser.custom_filter("", "pagefile.sys")  # Falseが返るべき
assert custom_file_chooser.custom_filter("", "document.txt")      # Trueが返るべき

class FileChooserPopupSave(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.9)
        layout = BoxLayout(orientation='vertical')

        # CustomFileChooserを使用するように変更
        self.custom_filechooser = CustomFileChooser()

        self.filename_input = TextInput(size_hint_y=None, height=30, multiline=False)
        save_button = Button(text='保存', size_hint_y=None, height=50)
        up_button = Button(text='上へ', size_hint_y=None, height=50)  # 上位ディレクトリへのボタンを追加

        layout.add_widget(self.custom_filechooser)
        layout.add_widget(self.filename_input)
        layout.add_widget(save_button)
        layout.add_widget(up_button)  # レイアウトに上位ディレクトリへのボタンを追加
        self.content = layout

        save_button.bind(on_press=self.save)
        up_button.bind(on_press=self.go_up)  # 上へボタンのイベントハンドラをバインド

    def save(self, instance):
        filename = self.filename_input.text.strip()
        if not filename:
            print("ファイル名が入力されていません。")
            return

        # self.filechooser.path を self.custom_filechooser.path に修正
        file_path = os.path.join(self.custom_filechooser.path, filename)
        if not os.path.isdir(self.custom_filechooser.path):
            print(f"指定されたパスはディレクトリではありません: {self.custom_filechooser.path}")
            return

        try:
            MainLayout.save_data(file_path)
        except PermissionError as e:
            print(f"ファイルの保存に失敗しました: {e}")
        else:
            self.dismiss()
    
    def go_up(self, instance):
        parent_path = os.path.dirname(self.custom_filechooser.path)
        self.custom_filechooser.path = parent_path

class FileChooserPopupOpen(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.9)
        layout = BoxLayout(orientation='vertical')

        # CustomFileChooserを使用するように変更
        self.custom_filechooser = CustomFileChooser(path=home_directory)

        open_button = Button(text='開く', size_hint_y=None, height=50)
        up_button = Button(text='上へ', size_hint_y=None, height=50)  # 上位ディレクトリへのボタンを追加

        layout.add_widget(self.custom_filechooser)
        layout.add_widget(open_button)
        layout.add_widget(up_button)  # レイアウトに上位ディレクトリへのボタンを追加
        self.content = layout

        open_button.bind(on_press=self.open_file)
        up_button.bind(on_press=self.go_up)  # 上へボタンのイベントハンドラをバインド

    def open_file(self, instance):
        selected_filenames = self.custom_filechooser.selection
        if selected_filenames:
            file_path = selected_filenames[0]
            # 親のMainLayoutインスタンスを参照してload_dataを呼び出す
            main_layout = App.get_running_app().root
            main_layout.load_data(file_path)
            self.dismiss()
        
    def go_up(self, instance):
        parent_path = os.path.dirname(self.custom_filechooser.path)
        self.custom_filechooser.path = parent_path

class ScrollableTreeView(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (Window.width, Window.height)
        self.tree_view = TreeView(hide_root=True, size_hint_y=None)
        self.add_widget(self.tree_view)
        self.tree_view.bind(minimum_height=self.tree_view.setter('height'))

class RightClickMenu(Popup):
    def __init__(self, title_obj, **kwargs):
        super().__init__(**kwargs)
        self.title_obj = title_obj
        self.size_hint = (None, None)
        self.size = (200, 150)
        layout = BoxLayout(orientation='vertical')
        duplicate_btn = Button(text='複製')
        delete_btn = Button(text='削除')
        rename_btn = Button(text='名前の変更')
        layout.add_widget(duplicate_btn)
        layout.add_widget(delete_btn)
        layout.add_widget(rename_btn)
        self.add_widget(layout)
        duplicate_btn.bind(on_press=self.duplicate_title)
        delete_btn.bind(on_press=self.delete_title)
        rename_btn.bind(on_press=lambda instance: self.rename_title())

    def duplicate_title(self, instance):
        # 実際の複製処理
        new_label = TreeViewLabel(text=self.title_obj.text + ' のコピー')
        self.title_obj.parent.add_node(new_label)
        self.dismiss()

    def delete_title(self, instance):
        # 実際の削除処理
        self.title_obj.parent.remove_node(self.title_obj)
        self.dismiss()

    def rename_title(self):
        # 名前変更用のダイアログを開く
        dialog = TitleInputDialog()
        dialog.title_input.text = self.title_obj.text
        dialog.submit_button.unbind(on_press=dialog.submit_title)  # これはもはや必要ありません
        dialog.submit_button.bind(on_press=lambda instance: self.update_title(dialog.title_input.text, dialog))
        dialog.open()

    def update_title(self, new_name, dialog):
        if new_name.strip() != '':
            self.title_obj.text = new_name
            dialog.dismiss()  # 正しくダイアログを閉じる
            self.dismiss()

class TitleInputDialog(Popup):
    def __init__(self, callback, hint_text='タイトル名を入力', **kwargs):
        super().__init__(**kwargs)
        self.callback = callback  # コールバック関数をインスタンス変数に保存
        self.size_hint = (None, None)
        self.size = (400, 200)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        # hint_textを直接TextInputの初期化時に指定
        self.title_input = TextInput(hint_text=hint_text, size_hint_y=None, height=30)
        self.submit_button = Button(text='追加', size_hint_y=None, height=50)
        layout.add_widget(self.title_input)
        layout.add_widget(self.submit_button)
        self.add_widget(layout)
        # イベントハンドラのバインドを変更
        self.submit_button.bind(on_press=self.on_submit)

    def on_submit(self, instance):
        # callback関数を呼び出す
        self.callback(self.title_input.text.strip())
        self.dismiss()

    def submit_title(self, instance):
        if self.title_input.text.strip() != '':
            app = App.get_running_app()
            app.root.add_title_with_name(self.title_input.text)
            self.dismiss()

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'

        # TreeViewsを横に並べるためのBoxLayoutを作成
        trees_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        self.add_widget(trees_layout)

        # タイトル用のスクロール可能なTreeViewを追加
        self.titles_scroll_view = ScrollView(size_hint=(0.5, 1))
        self.titles_tree_view = TreeView(hide_root=True, size_hint_y=None)
        self.titles_tree_view.bind(minimum_height=self.titles_tree_view.setter('height'))
        self.titles_scroll_view.add_widget(self.titles_tree_view)
        trees_layout.add_widget(self.titles_scroll_view)

        # ページ用のスクロール可能なTreeViewを追加
        self.pages_scroll_view = ScrollView(size_hint=(0.5, 1))
        self.pages_tree_view = TreeView(hide_root=True, size_hint_y=None)
        self.pages_tree_view.bind(minimum_height=self.pages_tree_view.setter('height'))
        self.pages_scroll_view.add_widget(self.pages_tree_view)
        trees_layout.add_widget(self.pages_scroll_view)

        # 各タイトルとそれに関連するページリストを保持する辞書を初期化
        self.titles_pages = {}

        # 選択されたタイトルとページを追跡する変数を初期化
        self.selected_title = None
        self.selected_page = None  # ここでselected_pageを初期化


        # ボタンとSpinnerを含むBoxLayoutの設定
        button_layout = BoxLayout(size_hint_y=None, height=50)
        self.add_widget(button_layout)

        add_title_button = Button(text='新規タイトル')
        add_page_button = Button(text='ページ追加')
        save_as_button = Button(text='名付けて保存')  # save_buttonをsave_as_buttonに名前変更
        save_button = Button(text='保存')
        open_button = Button(text='開く')  # open_buttonを新たに追加

        # ボタンをbutton_layoutに追加
        button_layout.add_widget(add_title_button)
        button_layout.add_widget(add_page_button)
        button_layout.add_widget(save_as_button)
        button_layout.add_widget(save_button)
        button_layout.add_widget(open_button)

        # フォントサイズ変更用のSpinnerを追加
        self.font_size_spinner = Spinner(
            text='フォントサイズ',
            values=('24', '28', '32', '36'),
            size_hint_y=None,
            height=50
        )
        button_layout.add_widget(self.font_size_spinner)

        # テキスト入力エリアを追加（画面の残りの部分を占める）
        self.text_input = TextInput(multiline=True, size_hint_y=0.9)
        self.add_widget(self.text_input)

        # イベントハンドラーの設定
        self.font_size_spinner.bind(text=self.on_font_size_change)
        add_title_button.bind(on_press=self.show_add_title_dialog)
        # 修正: ページ追加ボタンにshow_add_page_dialogメソッドをバインド
        add_page_button.bind(on_press=self.show_add_page_dialog)
        save_as_button.bind(on_press=self.save_content)
        open_button.bind(on_press=self.open_content)

    def show_right_click_menu(self, node):
        # RightClickMenuポップアップを表示する
        menu = RightClickMenu(title_obj=node)
        menu.open()
    
    def show_add_title_dialog(self, instance):
        """新しいタイトルを追加するダイアログを表示するメソッド"""
        print("show_add_title_dialogイベントハンドラが呼び出されました")
        dialog = TitleInputDialog(callback=self.add_title_with_name, hint_text="タイトル名を入力")
        dialog.open()
        # submit_titleメソッドの修正箇所に注目
        print("イベントハンドラXが呼び出されました")
        dialog.submit_button.bind(on_press=lambda inst: self.submit_title(dialog, inst))

    def submit_title(self, dialog, instance):
        """ダイアログからタイトルを追加するメソッド。"""
        print("submit_titleイベントハンドラが呼び出されました")
        name = dialog.title_input.text.strip()
        if name:
            self.add_title_with_name(name)
            dialog.dismiss()  # ダイアログを閉じる

    def add_title_with_name(self, name):
        if name not in self.titles_pages:
            self.titles_pages[name] = {}
            new_node = self.titles_tree_view.add_node(TreeViewLabel(text=name))
            new_node.bind(on_touch_down=self.on_title_select)
            print(f"新しいタイトル '{name}' が追加されました。")
        else:
            print(f"タイトル '{name}' は既に存在します。")

    def on_title_select(self, node, touch):
        if node.collide_point(*touch.pos):
            self.selected_title = node.text
            print("Selected title:", self.selected_title)
            self.update_pages_tree_view()
            return True  # イベントを処理済みとしてマーク

    def on_submit(self, instance):
        self.callback(self.title_input.text.strip())
        self.dismiss()

    def on_page_select(self, node, touch):
        # タッチされたノードがページであることを確認
        if node.collide_point(*touch.pos):
            # 現在のページのテキストを保存
            if self.selected_title and self.selected_page:
                self.update_page_text(self.selected_title, self.selected_page, self.text_input.text)
            
            # 新しいページを選択
            self.selected_page = node.text
            print("Selected page:", self.selected_page)
            
            # 選択されたページのテキストを表示
            self.display_page_text(self.selected_title, self.selected_page)

    def display_page_text(self, title_name, page_name):
        # 選択されたページのテキストをテキストエリアに表示
        if title_name in self.titles_pages and page_name in self.titles_pages[title_name]:
            # 辞書からテキストを取得して表示
            self.text_input.text = self.titles_pages[title_name][page_name]['text']
        else:
            self.text_input.text = ''  # ページが見つからない場合は空にする

    def update_page_text(self, title_name, page_name, text):
        if title_name in self.titles_pages and page_name in self.titles_pages[title_name]:
            self.titles_pages[title_name][page_name]['text'] = text
            print(f"タイトル '{title_name}' のページ '{page_name}' のテキストが更新されました。")
        else:
            print(f"更新対象のページ '{page_name}' またはタイトル '{title_name}' が見つかりません。")

    def update_pages_tree_view(self):
        # 既存の全ページノードをクリア
        for node in list(self.pages_tree_view.iterate_all_nodes()):
            self.pages_tree_view.remove_node(node)
        
        # 選択されたタイトルに関連するページを追加
        for page in self.titles_pages.get(self.selected_title, []):
            added_node = self.pages_tree_view.add_node(TreeViewLabel(text=page))
            # ページノードにイベントハンドラをバインド
            added_node.bind(on_touch_down=self.on_page_select)
            print(f"ページTreeViewに '{page}' を追加しました: {added_node}")

    def show_add_page_dialog(self, instance):
        if not self.selected_title:
            print("タイトルが選択されていません。")
            return
        dialog = TitleInputDialog(callback=lambda text: self.add_page_to_title(self.selected_title, text), hint_text="ページ名を入力")
        dialog.open()

    def submit_page(self, dialog, instance):
        print("submit_pageメソッドが開始されました。")  # 開始時のログ
        page_name = dialog.title_input.text.strip()
        if page_name and self.selected_title:
            self.add_page_to_title(self.selected_title, page_name)
            dialog.dismiss()
        print("submit_pageメソッドが終了しました。")  # 終了時のログ

    def add_page_to_title(self, title_name, page_name):
        if title_name in self.titles_pages:
            if page_name not in self.titles_pages[title_name]:
                # ページ情報を辞書で追加（テキストの初期値を空文字列に設定）
                self.titles_pages[title_name][page_name] = {'text': ''}
                self.update_pages_tree_view()  # ページビューを更新
                print(f"タイトル '{title_name}' に新しいページ '{page_name}' が追加されました。")
            else:
                print(f"ページ '{page_name}' はタイトル '{title_name}' 内に既に存在します。")
        else:
            print(f"タイトル '{title_name}' が見つかりません。")

    def update_page_text(self, title_name, page_name, text):
        if title_name in self.titles_pages and page_name in self.titles_pages[title_name]:
            self.titles_pages[title_name][page_name]['text'] = text
            print(f"タイトル '{title_name}' のページ '{page_name}' のテキストが更新されました。")
        else:
            print(f"更新対象のページ '{page_name}' またはタイトル '{title_name}' が見つかりません。")

    def save_content(self, instance):
        dialog = FileChooserPopupSave()
        dialog.open()

    @staticmethod
    def save_data(file_path):
        app = App.get_running_app()
        # titles_pagesとcurrent_textを含む辞書を作成
        data = {
            'titles_pages': app.root.titles_pages,
            'current_text': app.root.text_input.text
        }
        # JSON形式でファイルに書き込み
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("データが保存されました。")

    def open_content(self, instance):
        dialog = FileChooserPopupOpen()
        dialog.open()

    def refresh_treeviews(self):
        # 既存のノードをクリア
        self.titles_tree_view.clear_widgets()
        # TreeViewは、clear_widgetsではなくremove_nodeを使用して子ノードを削除します
        self.pages_tree_view.clear_widgets()

        # titles_pagesからデータを取得してTreeViewに追加
        for title, pages in self.titles_pages.items():
            # タイトルをtitlesのTreeViewに追加
            title_node = self.titles_tree_view.add_node(TreeViewLabel(text=title))
            # タイトルに関連するページを追加
            for page in pages.keys():
                # ページをtitlesのTreeViewにタイトルの子として追加
                self.titles_tree_view.add_node(TreeViewLabel(text=page), parent=title_node)

    def load_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # 以前のコードで app を直接参照していた部分を self で置き換え
            self.titles_pages = data['titles_pages']
            self.text_input.text = data['current_text']
            print("データが読み込まれました。")
        # データ読み込み後にUIを更新
        self.refresh_treeviews()

    def on_font_size_change(self, spinner, text):
        self.text_input.font_size = int(text)
    
    def on_node_touch_down(self, node, touch):
        # 左クリックでタイトルを選択
        if touch.button == 'left' and node.collide_point(*touch.pos):
            self.selected_title = node.text  # 選択されたタイトルを更新
            return True
        elif touch.button == 'right' and node.collide_point(*touch.pos):
            self.show_right_click_menu(node)
            return True
        return super(TreeViewLabel, node).on_touch_down(touch)

class MyApp(App):
    def build(self):
        return MainLayout()

if __name__ == '__main__':
    MyApp().run()