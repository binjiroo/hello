from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionButton, ActionGroup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # 右クリックで赤い丸を表示しない

class ColorToggleButton(ToggleButton):
    active_buttons = {}  # アクティブなボタンを追跡するためのクラス変数

    def __init__(self, layer_type='main', row_number=0, **kwargs):
        super().__init__(**kwargs)
        self.layer_type = layer_type  # レイヤータイプを追加 (main or sub)
        self.row_number = row_number  # 行番号を追加
        self.state_index = 0
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
        # 左クリックで状態を循環させる
        if self.state == 'down':
            self.state_index = (self.state_index + 1) % 3
            self.update_color()

    def update_active_state(self):
        # グループ内でアクティブなボタンを更新
        key = (self.layer_type, self.row_number)
        if key in ColorToggleButton.active_buttons:
            # 既にアクティブなボタンがあればリセット
            active_button = ColorToggleButton.active_buttons[key]
            active_button.state = 'normal'
            active_button.state_index = 0
            active_button.update_color()

        # このボタンをアクティブに設定
        self.state = 'down'
        self.state_index = 3  # ピンク色の状態に
        self.update_color()
        ColorToggleButton.active_buttons[key] = self

    def update_color(self):
        # 状態に応じて背景色を設定
        colors = [(0.4, 0.4, 0.4, 0.9), (0.4, 0.6, 1, 1), (1, 0.8, 0.6, 1), (1, 0.4, 0.6, 1)]
        self.background_color = colors[self.state_index]

class MainApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical')
        
        # Action Bar (Menu Bar)
        action_bar = ActionBar(pos_hint={'top': 1})
        action_view = ActionView(use_separator=True)
        
        action_previous = ActionPrevious(app_icon='path/to/your/logo.png', title='アプリ名', with_previous=False)
        action_view.add_widget(action_previous)
        
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
            action_group = ActionGroup(text=menu_text, mode='spinner')
            for item in items:
                action_button = ActionButton(text=item)
                action_group.add_widget(action_button)
            action_view.add_widget(action_group)

        action_bar.add_widget(action_view)
        root.add_widget(action_bar)
        
        # Main Panel
        main_panel = BoxLayout(size_hint_y=None, height=40)
        buttons = ['作図', '線', '色', '文字', '寸法', '編集', '操作', '開発', '自動', 'adoin']
        for text in buttons:
            btn = Button(text=text)
            main_panel.add_widget(btn)
        root.add_widget(main_panel)
        
        # Screen Manager Switch Layout 1
        screen_switch_1 = BoxLayout(size_hint_y=None, height=40)
        screen_switch_1.add_widget(Label(text='画面1'))
        screen_switch_1.add_widget(Label(text='画面2'))
        screen_switch_1.add_widget(Label(text='画面3'))
        root.add_widget(screen_switch_1)
        
        # Canvas
        canvas = BoxLayout()  # This is placeholder for your actual canvas widget
        root.add_widget(canvas)
        
        # Status Bar
        status_bar = Label(size_hint_y=None, height=20, text='ステータスバー')
        root.add_widget(status_bar)
        
        # Layer Panel (Right side)
        layer_panel = BoxLayout(orientation='vertical', size_hint_x=None, width=100)
        
        # Screen Manager Switch Layout 2 (Above Layer Buttons)
        screen_switch_2 = BoxLayout(size_hint_y=None, height=40)
        screen_switch_2.add_widget(Label(text='画面A'))
        screen_switch_2.add_widget(Label(text='画面B'))
        screen_switch_2.add_widget(Label(text='画面C'))
        layer_panel.add_widget(screen_switch_2)
        
        for i in range(10):
            row = BoxLayout(size_hint_y=None, height=40, padding=[1, 1, 1, 1], spacing=2)
            for j in range(2):
                toggle_btn = ColorToggleButton(
                    size_hint=(None, None),
                    size=(40, 39),
                    text=str(i * 2 + j + 1)
                )
                row.add_widget(toggle_btn)
            layer_panel.add_widget(row)
        for _ in range(2):
            toggle_button = ToggleButton(size_hint=(None, None), size=(80, 40), text='メイン')
            toggle_button.bind(on_press=self.switch_main_sub)
            layer_panel.add_widget(toggle_button)
        
        # Combine main layout and layer panel
        final_layout = BoxLayout()
        final_layout.add_widget(root)
        final_layout.add_widget(layer_panel)
        
        return final_layout

    def switch_main_sub(self, instance):
        if instance.text == 'メイン':
            instance.text = 'サブ'
        else:
            instance.text = 'メイン'

if __name__ == '__main__':
    MainApp().run()
