# widget.py
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.treeview import TreeView
from kivy.uix.spinner import Spinner  # Kivy の Spinner を使用
from kivymd.uix.label import MDLabel  # 追加
from kivymd.uix.textfield import MDTextField  # 追加
from kivymd.uix.button import MDFlatButton  # 追加
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from event import EventHandlers
from labels import CustomTreeViewLabel  # 追加


class ProjectTreeWidget(BoxLayout):
    tree_view = ObjectProperty(None)
    project_name_input = ObjectProperty(None)
    bg_color_spinner = ObjectProperty(None)
    border_color_spinner = ObjectProperty(None)
    border_width_spinner = ObjectProperty(None)
    hierarchy_spinner = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(ProjectTreeWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.event_handlers = EventHandlers(self)

        self.create_toolbar()
        self.create_initial_widgets()
        self.create_tree_view()

    def create_toolbar(self):
        self.toolbar = MDToolbar(title="Project Tree Manager")
        self.toolbar.left_action_items = [
            ["menu", lambda x: self.menu_callback()]
        ]
        self.toolbar.right_action_items = [
            ["dots-vertical", lambda x: self.more_options_callback()]
        ]
        self.toolbar.size_hint_y = None
        self.toolbar.height = dp(56)
        self.add_widget(self.toolbar)

        # メニュー項目の定義
        menu_items = [
            {
                "text": "名付けて保存",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="名付けて保存": self.menu_item_selected(x),
            },
            {
                "text": "上書き保存",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="上書き保存": self.menu_item_selected(x),
            },
            {
                "text": "開く",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="開く": self.menu_item_selected(x),
            },
            {
                "text": "印刷",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="印刷": self.menu_item_selected(x),
            },
            {
                "text": "プリンター設定",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="プリンター設定": self.menu_item_selected(x),
            },
            {
                "text": "設定",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="設定": self.menu_item_selected(x),
            },
            {
                "text": "閉じる",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="閉じる": self.menu_item_selected(x),
            },
        ]
        self.menu = MDDropdownMenu(
            caller=self.toolbar.left_action_items[0][1],
            items=menu_items,
            width_mult=4,
        )

    def menu_callback(self, *args):
        self.menu.open()

    def menu_item_selected(self, text_item):
        print(f"選択されたメニュー項目: {text_item}")
        self.menu.dismiss()

    def more_options_callback(self, *args):
        # その他のオプションを表示する処理を実装
        pass

    def create_initial_widgets(self):
        control_panel = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            spacing=dp(10),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        
        # プロジェクト名入力
        control_panel.add_widget(MDLabel(text='プロジェクト名:', size_hint_x=0.15, font_style='Body1'))
        self.project_name_input = MDTextField(text='プロジェクト', size_hint_x=0.2)
        self.project_name_input.bind(text=self.event_handlers.on_project_name_change)
        control_panel.add_widget(self.project_name_input)
        
        # 背景色スピナー
        control_panel.add_widget(MDLabel(text='背景色:', size_hint_x=0.1, font_style='Body1'))
        self.bg_color_spinner = Spinner(
            text='White', values=('White', 'Red', 'Green', 'Blue'), size_hint_x=0.15)
        control_panel.add_widget(self.bg_color_spinner)
        
        # 枠線色スピナー
        control_panel.add_widget(MDLabel(text='枠線色:', size_hint_x=0.1, font_style='Body1'))
        self.border_color_spinner = Spinner(
            text='Black', values=('Black', 'Red', 'Green', 'Blue'), size_hint_x=0.15)
        control_panel.add_widget(self.border_color_spinner)
        
        # 枠線幅スピナー
        control_panel.add_widget(MDLabel(text='枠線幅:', size_hint_x=0.1, font_style='Body1'))
        self.border_width_spinner = Spinner(
            text='1', values=('1', '2', '3', '4', '5'), size_hint_x=0.1)
        control_panel.add_widget(self.border_width_spinner)
        
        # フォルダー追加ボタン
        folder_add_button = MDFlatButton(text='フォルダー追加', size_hint_x=0.15, font_style='Body1')
        folder_add_button.bind(on_press=self.event_handlers.add_folder)
        control_panel.add_widget(folder_add_button)
        
        # フォルダー削除ボタン
        folder_delete_button = MDFlatButton(text='フォルダー削除', size_hint_x=0.15, font_style='Body1')
        folder_delete_button.bind(on_press=self.event_handlers.delete_all_folders)
        control_panel.add_widget(folder_delete_button)
        
        # モジュール追加ボタン
        module_add_button = MDFlatButton(text='モジュール追加', size_hint_x=0.15, font_style='Body1')
        module_add_button.bind(on_press=self.event_handlers.add_module)
        control_panel.add_widget(module_add_button)
        
        # モジュール削除ボタン
        module_delete_button = MDFlatButton(text='モジュール削除', size_hint_x=0.15, font_style='Body1')
        module_delete_button.bind(on_press=self.event_handlers.delete_all_modules)
        control_panel.add_widget(module_delete_button)
        
        # 階層指定スピナー
        control_panel.add_widget(MDLabel(text='階層指定:', size_hint_x=0.1, font_style='Body1'))
        self.hierarchy_spinner = Spinner(
            text='ルート', values=('ルート',), size_hint_x=0.15, font_style='Body1')
        self.hierarchy_spinner.bind(text=self.event_handlers.on_hierarchy_change)
        control_panel.add_widget(self.hierarchy_spinner)
        
        self.add_widget(control_panel)

    def create_tree_view(self):
        self.tree_view = TreeView(root_options=dict(text=self.project_name_input.text), hide_root=False)
        self.tree_view.size_hint_y = 1
        self.add_widget(self.tree_view)
    
    def add_folder(self, instance):
        # フォルダーを追加するロジックを実装
        pass
    
    def delete_all_folders(self, instance):
        # 全てのフォルダーを削除するロジックを実装
        pass
    
    def add_module(self, instance):
        # モジュールを追加するロジックを実装
        pass
    
    def delete_all_modules(self, instance):
        # 全てのモジュールを削除するロジックを実装
        pass
