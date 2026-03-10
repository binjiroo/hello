from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider  # Slider をインポート
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionButton, ActionGroup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.actionbar import ActionView
from kivy.graphics import Line, Color, InstructionGroup
from functools import partial
from collections import Counter
from kivy.config import Config
import os
import logging

logging.basicConfig(level=logging.INFO)

os.chdir('C:\\Users\\kokada\\hello\\crisp_cad')
from drawing_panel import create_drawing_main_panel, create_drawing_sub_panel
from line_panel import create_line_panel
from color_panel import create_color_panel
from text_panel import create_text_main_panel, create_text_sub_panel
from dimension_panel import create_dimension_main_panel, create_dimension_sub_panel

from drawing import ShapeDrawer, Shape, AddShapeAction

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # 右クリックで赤い丸を表示しない

# Shape インスタンスを作成
instructions = InstructionGroup()
instructions.add(Color(1, 0, 0))  # 色を赤に設定
instructions.add(Line(points=[0, 0, 100, 100]))  # 線を描画
shape = Shape(shape_type='line', instructions=instructions, color=(1, 0, 0))

# shapes_list を管理するリスト
shapes_list = []

# AddShapeAction インスタンスを作成
# shape と instructions を追加し、全ての形状を追跡するリストも渡す
add_shape_action = AddShapeAction(shape=shape, shape_instructions=instructions, shapes_list=shapes_list)

class ColorToggleButton(ToggleButton):
    active_buttons = {}  # アクティブなボタンを追跡するためのクラス変数

    def __init__(self, layer_type='main', row_number=0, **kwargs):
        super().__init__(**kwargs)
        self.layer_type = layer_type  # レイヤータイプ
        self.row_number = row_number  # 行番号
        self.state_index = 1  # 水色（編集モード）をデフォルトに設定
        self.background_normal = ''
        self.background_down = ''
        self.update_color()

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            if touch.button == 'right':
                self.update_active_state()
                return True
        return False

    def on_press(self):
        super().on_press()
        # 1回のクリックで状態を循環させる。インデックスは0から3まで（グレー、水色、オレンジ、ピンク）
        self.state_index = (self.state_index + 1) % 3
        self.update_color()  # ボタンの色を更新

        # 対応するレイヤーの表示・編集設定を更新するロジックをここに実装
        self.update_layer_visibility_and_editability()

    def update_active_state(self):
        key = (self.layer_type, self.row_number)
        if key in ColorToggleButton.active_buttons:
            active_button = ColorToggleButton.active_buttons[key]
            active_button.state = 'normal'
            active_button.state_index = 0
            active_button.update_color()
        self.state = 'down'
        self.state_index = 3
        self.update_color()
        ColorToggleButton.active_buttons[key] = self

    def update_color(self):
        # 状態に応じて背景色を設定
        colors = [(0.4, 0.4, 0.4, 0.9), (0.4, 0.6, 1, 1), (1, 0.8, 0.6, 1), (1, 0.4, 0.6, 1)]
        self.background_color = colors[self.state_index]
    
    def update_layer_visibility_and_editability(self):
        main_layer = self.get_parent_main_layer()
        sub_layer_name = f"sub{self.row_number + 1}"
        if self.state_index == 0:
            main_layer.set_sub_layer_state(sub_layer_name, 'hidden')
        elif self.state_index == 1:
            main_layer.set_sub_layer_state(sub_layer_name, 'editable')
        elif self.state_index == 2:
            main_layer.set_sub_layer_state(sub_layer_name, 'view_only')
        elif self.state_index == 3:
            main_layer.set_sub_layer_state(sub_layer_name, 'active')

    def get_parent_main_layer(self):
        # 現在アクティブなメインレイヤーを返す
        return App.get_running_app().layers[App.get_running_app().current_main_layer]

    @classmethod
    def update_all_buttons(cls):
        # 全てのボタンの色を一括で更新
        for button in cls.active_buttons.values():
            button.state_index = (button.state_index + 1) % 2  # 状態をサイクルさせる
            button.update_color()

class DrawingWidget(Widget):
    def __init__(self, **kwargs):
        super(DrawingWidget, self).__init__(**kwargs)
        with self.canvas:
            # InstructionGroup のインスタンスを作成
            self.instructions = InstructionGroup()

            # 描画の色を設定（赤色）
            self.instructions.add(Color(1, 0, 0))

            # 線を描画（開始点: (100, 100), 終了点: (200, 200)）
            self.instructions.add(Line(points=[100, 100, 200, 200], width=2))

            # キャンバスに命令グループを追加
            self.canvas.add(self.instructions)

class DrawingApp(App):
    def build(self):
        return DrawingWidget()

class DrawingMainPanelScreen(Screen):
    def __init__(self, **kwargs):
        super(DrawingMainPanelScreen, self).__init__(**kwargs)
        panel = create_drawing_main_panel()
        panel.pos_hint = {'top': 1}  # パネルを親の上端に配置
        self.add_widget(panel)

class DrawingSubPanelScreen(Screen):
    def __init__(self, **kwargs):
        super(DrawingSubPanelScreen, self).__init__(**kwargs)
        panel = create_drawing_sub_panel()
        panel.pos_hint = {'top': 1}  # パネルを親の上端に配置
        self.add_widget(panel)

class LinePanelScreen(Screen):
    def __init__(self, **kwargs):
        super(LinePanelScreen, self).__init__(**kwargs)
        panel = create_line_panel()
        panel.pos_hint = {'top': 1}  # パネルを親の上端に配置
        self.add_widget(panel)

class ColorPanelScreen(Screen):
    def __init__(self, **kwargs):
        super(ColorPanelScreen, self).__init__(**kwargs)
        panel = create_color_panel()
        panel.pos_hint = {'top': 1}  # パネルを親の上端に配置
        self.add_widget(panel)  # color_panel をこのスクリーンに追加

class TextMainPanelScreen(Screen):
    def __init__(self, **kwargs):
        super(TextMainPanelScreen, self).__init__(**kwargs)
        panel = create_text_main_panel()
        panel.pos_hint = {'top': 1}  # パネルを親の上端に配置
        self.add_widget(panel)  # text_main_panel をこのスクリーンに追加

class TextSubPanelScreen(Screen):
    def __init__(self, **kwargs):
        super(TextSubPanelScreen, self).__init__(**kwargs)
        panel = create_text_sub_panel()
        panel.pos_hint = {'top': 1}  # パネルを親の上端に配置
        self.add_widget(panel)  # text_sub_panel をこのスクリーンに追加

class DimensionMainPanelScreen(Screen):
    def __init__(self, **kwargs):
        super(DimensionMainPanelScreen, self).__init__(**kwargs)
        panel = create_dimension_main_panel()
        panel.pos_hint = {'top': 1}
        self.add_widget(panel)

class DimensionSubPanelScreen(Screen):
    def __init__(self, **kwargs):
        super(DimensionSubPanelScreen, self).__init__(**kwargs)
        panel = create_dimension_sub_panel()
        panel.pos_hint = {'top': 1}
        self.add_widget(panel)

class LayerState:
    def __init__(self):
        # サブレイヤーの状態を保存する辞書
        self.sub_layers = {f"sub{j+1}": 'visible' for j in range(20)}  # 初期状態はすべて表示

    def set_sub_layer_state(self, sub_layer_name, state):
        self.sub_layers[sub_layer_name] = state

    def get_sub_layer_state(self, sub_layer_name):
        return self.sub_layers[sub_layer_name]

class CustomBoxLayout(BoxLayout):
    def add_widget(self, widget, index=0):
        super(CustomBoxLayout, self).add_widget(widget, index)
        logging.info(f"Adding {widget} to {self}")

class MainApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layers = {f"main{i+1}": LayerState() for i in range(20)}
        self.all_toggle_buttons = []  # トグルボタンリストを初期化
        self.current_main_layer = "main1"  # 初期メインレイヤー設定（必要に応じて）

    def build(self):
        self.shape_drawer = ShapeDrawer()  # ShapeDrawer インスタンスを作成
        
        return self.setup_ui()
    
    def setup_ui(self):
        root = BoxLayout(orientation='vertical')
        self.sm = ScreenManager(size_hint=(1, 1), pos_hint={'top': 1})
        self.sm.add_widget(DrawingMainPanelScreen(name='drawing_main_panel'))
        self.sm.add_widget(LinePanelScreen(name='line_panel'))
        self.sm.add_widget(ColorPanelScreen(name='color_panel'))
        self.sm.add_widget(TextMainPanelScreen(name='text_main_panel'))
        self.sm.add_widget(DimensionMainPanelScreen(name='dimension_main_panel'))  # 追加

        self.sm.current = 'drawing_main_panel'

        self.sm2 = ScreenManager(size_hint=(1, None), height=120, pos_hint={'top': 1})
        self.sm2.add_widget(DrawingSubPanelScreen(name='drawing_sub_panel'))
        self.sm2.add_widget(TextSubPanelScreen(name='text_sub_panel'))
        self.sm2.add_widget(DimensionSubPanelScreen(name='dimension_sub_panel'))  # 追加
        # 親ウィジェットの確認
        if self.sm2.parent:
            print("This button's parent is:", self.sm2.parent)
        else:
            print("This button has no parent.")

        self.sm2.current = 'drawing_sub_panel'

        action_bar, action_view = self.create_action_bar()
        root.add_widget(action_bar)
        
        # Define menu groups and items
        menu_structure = {
            'ファイル': ['新規', '開く', '保存', '名前を付けて保存', '終了'],
            '編集': ['元に戻す', 'やり直し', '切り取り', 'コピー', '貼り付け', '消去', 'クリア'],
            '表示': ['表示', '編集', '切り取り', 'コピー', '貼り付け'],
            '作図': ['点', '線', '矩形', '円', '円弧', '曲線', '多角形', '自由線'],
            '計算': ['計算機', '表計算', '式計算', '範囲計算', '測定', '計測', '集計'],
            '設定': ['設定項目1', '設定項目2'],
            '開発': ['開発ツール1', '開発ツール2'],
            '自動': ['自動機能1', '自動機能2'],
            'その他': ['その他項目1', 'その他項目2'],
            'ヘルプ': ['ヘルプ項目1', 'ヘルプ項目2'],
        }        
        for menu_text, items in menu_structure.items():
            action_group = ActionGroup(text=menu_text, mode='spinner', padding=[10, 10, 10, 10])  # パディング値は例です
            for item in items:
                action_button = ActionButton(text=item)
                action_group.add_widget(action_button)
            action_view.add_widget(action_group)
        
        # Main Panel に Screen 切り替えボタンを追加
        main_panel = BoxLayout(size_hint_y=None, height=40)
        buttons = [
            ('作図', 'drawing_main_panel', 'drawing_sub_panel'),
            ('線', 'line_panel', None),
            ('色', 'color_panel', None),
            ('文字', 'text_main_panel', 'text_sub_panel'),
            ('寸法', 'dimension_main_panel', 'dimension_sub_panel'),
            ('編集', None, None),
            ('操作', None, None),
            ('開発', None, None),
            ('自動', None, None)
        ]

        for button_info in buttons:
            text = button_info[0]
            screen_name = button_info[1]
            sm_key = button_info[2]  # sm_key はサブスクリーン名（Noneの場合もあり）

            btn = Button(text=text)

            if sm_key is not None:
                # メインスクリーンとサブスクリーンを同時に切り替える
                btn.bind(on_press=lambda instance, sn=screen_name, sk=sm_key: (
                    self.set_current_screen(self.sm, sn),
                    self.set_current_screen(self.sm2, sk)
                ))
            else:
                # メインスクリーンのみを切り替える
                btn.bind(on_press=lambda instance, sm=self.sm, sn=screen_name: self.set_current_screen(sm, sn))

            main_panel.add_widget(btn)

        root.add_widget(main_panel)
        root.add_widget(self.sm)  # sm を root widget に追加
        
        # Canvas
        canvas = BoxLayout()  # This is placeholder for your actual canvas widget
        root.add_widget(canvas)
        
        # Status Bar
        status_bar = Label(size_hint_y=None, height=20, text='ステータスバー')
        root.add_widget(status_bar)
        
        # Layer Panel (Right side)
        layer_panel = BoxLayout(orientation='vertical', size_hint_x=None)
        
        layer_panel.add_widget(self.sm2)
        
        # トグルボタンのグリッドを作成
        for i in range(10):  # 10行のトグルボタンを作成
            row = BoxLayout(size_hint_y=None, height=40, padding=[1, 1, 1, 1], spacing=2)
            for j in range(2):  # 各行に2つのボタン
                toggle_btn = ColorToggleButton(
                    size_hint=(None, None),
                    size=(48, 39),
                    text=str(i * 2 + j + 1)
                )
                self.all_toggle_buttons.append(toggle_btn)  # ボタンをリストに追加
                row.add_widget(toggle_btn)  # 行にボタンを追加
            layer_panel.add_widget(row)  # 行をレイアウトに追加

        # 「メイン」ボタンを追加
        toggle_button = ToggleButton(size_hint=(None, None), size=(100, 40), text='メイン')
        toggle_button.bind(on_press=self.switch_main_sub)
        layer_panel.add_widget(toggle_button)

        # 「Update All Colors」ボタンを1つだけ追加
        convert_all_btn = Button(size_hint=(None, None), size=(100, 40), text='All')
        convert_all_btn.bind(on_press=self.switch_convert_all)  # 一括更新ボタンにbind
        layer_panel.add_widget(convert_all_btn)  # ボタンをレイアウトに追加

        # 最終的なレイアウトを作成
        final_layout = BoxLayout()
        final_layout.add_widget(root)  # rootレイアウトをfinal_layoutに追加
        final_layout.add_widget(layer_panel)  # layer_panelをfinal_layoutに追加

        return final_layout  # 追加する必要があります

    def safe_add_screen(self, screen_manager, screen):
        """スクリーンを安全にScreenManagerに追加するメソッド。
        
        すでにスクリーンがScreenManagerに追加されている場合は、
        currentを設定することでそのスクリーンに切り替えます。
        """
        if screen.name in screen_manager.screen_names:
            screen_manager.current = screen.name
        else:
            screen_manager.add_widget(screen)
            screen_manager.current = screen.name

    def safe_add_widget(self, parent, widget):
        """ウィジェットを安全に親ウィジェットに追加するメソッド。
        
        既に他の親ウィジェットに属しているウィジェットを追加しようとした場合に警告を表示します。
        """
        if widget.parent is not None:
            print(f"Warning: {widget} already has a parent {widget.parent}")
        else:
            parent.add_widget(widget)

        if widget.parent is not None:
            widget.parent.remove_widget(widget)
        parent.add_widget(widget)

    def create_action_bar(self):
        action_bar = ActionBar(pos_hint={'top': 1})
        action_view = ActionView(use_separator=True)
        action_previous = ActionPrevious(app_icon='path/to/your/logo.png', title='アプリ名', with_previous=False)
        action_view.add_widget(action_previous)
        action_bar.add_widget(action_view)
        return action_bar, action_view

    def activate_tool(self, tool_name):
        self.shape_drawer.set_drawing_mode(tool_name)
        print(f"Activated tool: {tool_name}")

    def set_current_screen(self, screen_manager, screen_name):
        if screen_name is not None:
            logging.debug(f"Before switching: {screen_manager.current}")
            screen_manager.current = screen_name
            logging.debug(f"After switching: {screen_manager.current}")

            # sm で切り替えた場合、次に sm2 を切り替える処理を追加
            if screen_manager == self.sm:
                logging.debug("Switching in main screen manager (sm)")
                # 必要に応じて sm2 の切り替えを追加
                self.sm2.current = 'drawing_sub_panel'  # サブスクリーンの初期設定に切り替え
            elif screen_manager == self.sm2:
                logging.debug("Switching in sub screen manager (sm2)")

    def switch_main_sub(self, instance):
        if instance.state == 'down':
            instance.text = 'サブ'
            # サブレイヤーグループへ切り替え
            self.load_layer_state('sub_layer_group')
        else:
            instance.text = 'メイン'
            # メインレイヤーグループへ切り替え
            self.load_layer_state('main_layer_group')

    def load_layer_state(self, layer_group):
        for i in range(20):
            main_layer_name = f"main{i+1}"
            layer_state = self.layers[main_layer_name]
            # 各サブレイヤーの状態を復元
            for sub_layer_name, state in layer_state.sub_layers.items():
                # ここで各サブレイヤーの表示/非表示を設定
                pass

    def switch_convert_all(self, instance):
        # 全てのトグルボタンの state_index のリストを取得
        state_indices = [btn.state_index for btn in self.all_toggle_buttons]

        # 最も多い state_index を取得
        from collections import Counter
        state_count = Counter(state_indices)
        most_common_state, _ = state_count.most_common(1)[0]

        # 全てのボタンの state_index を最も多い値に揃える
        for toggle_btn in self.all_toggle_buttons:
            if toggle_btn.state_index != most_common_state:
                toggle_btn.state_index = most_common_state
                toggle_btn.update_color()

        # 一括で状態を切り替える
        new_state_index = (most_common_state + 1) % 3  # 状態を循環させる
        for toggle_btn in self.all_toggle_buttons:
            toggle_btn.state_index = new_state_index
            toggle_btn.update_color()

if __name__ == '__main__':
    MainApp().run()
