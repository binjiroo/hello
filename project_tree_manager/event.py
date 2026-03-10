# event.py
from kivy.uix.treeview import TreeViewLabel
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.graphics import Rectangle, Line, Color
from kivy.properties import ColorProperty, NumericProperty
from kivy.logger import Logger  # Logger をインポート
from labels import CustomTreeViewLabel  # 追加


class EventHandlers:
    def __init__(self, widget):
        self.widget = widget

    def on_project_name_change(self, instance, value):
        if self.widget.tree_view and self.widget.tree_view.root_node:
            self.widget.tree_view.root_node.text = value

    def delete_all_folders(self, instance):
        nodes_to_remove = [
            node for node in self.widget.tree_view.iterate_all_nodes()
            if isinstance(node, CustomTreeViewLabel) and 'フォルダー' in node.text
        ]
        for node in nodes_to_remove:
            self.widget.tree_view.remove_node(node)
        self.update_hierarchy_spinner()

    def delete_all_modules(self, instance):
        nodes_to_remove = [
            node for node in self.widget.tree_view.iterate_all_nodes()
            if isinstance(node, CustomTreeViewLabel) and 'モジュール' in node.text
        ]
        for node in nodes_to_remove:
            self.widget.tree_view.remove_node(node)

    def add_folder(self, instance):
        try:
            # 現在選択されている階層を取得
            selected_node = self.get_selected_node()
            # 新しいフォルダーのノードを作成
            folder_name = f'フォルダー{len(selected_node.nodes) + 1}'
            folder_node = self.widget.tree_view.add_node(
                CustomTreeViewLabel(text=folder_name), selected_node)
            # フォルダー固有のウィジェットを追加
            self.add_folder_widgets(folder_node)
            self.update_hierarchy_spinner()
        except Exception as e:
            Logger.exception(f"Error in add_folder: {e}")

    def delete_folder(self, node):
        # 指定されたノードを削除
        self.widget.tree_view.remove_node(node)
        self.update_hierarchy_spinner()

    def add_module(self, instance):
        selected_node = self.get_selected_node()
        module_name = f'モジュール{len(selected_node.nodes) + 1}'
        module_node = self.widget.tree_view.add_node(
            CustomTreeViewLabel(text=module_name), selected_node)
        self.add_module_widgets(module_node)

    def delete_module(self, node):
        self.widget.tree_view.remove_node(node)

    def on_hierarchy_change(self, spinner, text):
        # 選択された階層に応じて処理を変更可能
        pass

    def get_selected_node(self):
        hierarchy = self.widget.hierarchy_spinner.text
        for node in self.widget.tree_view.iterate_all_nodes():
            if node.text == hierarchy:
                return node
        return self.widget.tree_view.root

    def add_folder_widgets(self, folder_node):
        # フォルダー名入力フォーム
        folder_name_input = TextInput(text=folder_node.text, size_hint_x=0.2)
        folder_name_input.bind(text=lambda instance, value: setattr(folder_node, 'text', value))
        
        # 背景色スピナー
        bg_color_spinner = Spinner(
            text='White', values=('White', 'Red', 'Green', 'Blue'), size_hint_x=0.1)
        bg_color_spinner.bind(text=lambda instance, value: self.change_node_bg_color(folder_node, value))
        
        # 枠線色スピナー
        border_color_spinner = Spinner(
            text='Black', values=('Black', 'Red', 'Green', 'Blue'), size_hint_x=0.1)
        border_color_spinner.bind(text=lambda instance, value: self.change_node_border_color(folder_node, value))
        
        # 枠線幅スピナー
        border_width_spinner = Spinner(
            text='1', values=('1', '2', '3', '4', '5'), size_hint_x=0.1)
        border_width_spinner.bind(text=lambda instance, value: self.change_node_border_width(folder_node, int(value)))
        
        # フォルダー追加・削除ボタン
        folder_add_button = Button(text='フォルダー追加', size_hint_x=0.1)
        folder_add_button.bind(on_press=self.add_folder)
        
        folder_delete_button = Button(text='フォルダー削除', size_hint_x=0.1)
        folder_delete_button.bind(on_press=lambda x: self.delete_folder(folder_node))
        
        # ウィジェットを配置するレイアウト
        layout = self.create_node_layout([
            folder_name_input, bg_color_spinner, border_color_spinner,
            border_width_spinner, folder_add_button, folder_delete_button
        ])
        
        # ノードにレイアウトを関連付け
        folder_node.add_widget(layout)

    def add_module_widgets(self, module_node):
        module_name_input = TextInput(text=module_node.text, size_hint_x=0.2)
        module_name_input.bind(text=lambda instance, value: setattr(module_node, 'text', value))
        
        bg_color_spinner = Spinner(
            text='White', values=('White', 'Red', 'Green', 'Blue'), size_hint_x=0.1)
        bg_color_spinner.bind(text=lambda instance, value: self.change_node_bg_color(module_node, value))
        
        border_color_spinner = Spinner(
            text='Black', values=('Black', 'Red', 'Green', 'Blue'), size_hint_x=0.1)
        border_color_spinner.bind(text=lambda instance, value: self.change_node_border_color(module_node, value))
        
        border_width_spinner = Spinner(
            text='1', values=('1', '2', '3', '4', '5'), size_hint_x=0.1)
        border_width_spinner.bind(text=lambda instance, value: self.change_node_border_width(module_node, int(value)))
        
        module_add_button = Button(text='モジュール追加', size_hint_x=0.1)
        module_add_button.bind(on_press=self.add_module)
        
        module_delete_button = Button(text='モジュール削除', size_hint_x=0.1)
        module_delete_button.bind(on_press=lambda x: self.delete_module(module_node))
        
        layout = self.create_node_layout([
            module_name_input, bg_color_spinner, border_color_spinner,
            border_width_spinner, module_add_button, module_delete_button
        ])
        
        module_node.add_widget(layout)

    def change_node_bg_color(self, node, color_name):
        color_dict = {'White': (1, 1, 1, 1), 'Red': (1, 0, 0, 1),
                    'Green': (0, 1, 0, 1), 'Blue': (0, 0, 1, 1)}
        node.background_color = color_dict.get(color_name, (1, 1, 1, 1))

    def change_node_border_color(self, node, color_name):
        color_dict = {'Black': (0, 0, 0, 1), 'Red': (1, 0, 0, 1),
                    'Green': (0, 1, 0, 1), 'Blue': (0, 0, 1, 1)}
        node.border_color = color_dict.get(color_name, (0, 0, 0, 1))

    def change_node_border_width(self, node, width):
        node.border_width = width

    def create_node_layout(self, widgets):
        from kivy.uix.boxlayout import BoxLayout
        layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        for widget in widgets:
            layout.add_widget(widget)
        return layout

    def update_all_nodes(self, instance):
        bg_color = self.widget.bg_color_spinner.text
        border_color = self.widget.border_color_spinner.text
        border_width = int(self.widget.border_width_spinner.text)
        
        for node in self.widget.tree_view.iterate_all_nodes():
            self.change_node_bg_color(node, bg_color)
            self.change_node_border_color(node, border_color)
            self.change_node_border_width(node, border_width)

    def update_hierarchy_spinner(self):
        # スピナーの選択肢を更新
        folder_names = ['ルート']
        for node in self.widget.tree_view.iterate_all_nodes():
            if isinstance(node, CustomTreeViewLabel) and 'フォルダー' in node.text:
                folder_names.append(node.text)
        self.widget.hierarchy_spinner.values = folder_names
