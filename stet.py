from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Ellipse, Color
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton

class DrawWidget(Widget):
    def __init__(self, **kwargs):
        super(DrawWidget, self).__init__(**kwargs)
        self.mode = 'draw'  # 初期モードは点描画モード
        self.selected_dot = None
        self.dots = []  # 描画した点のリスト
        self.shift_active = False  # Shiftキーが押されているかどうかを追跡
        self.ctrl_active = False  # Ctrlキーが押されているかどうかを追跡
        self.shift_start_pos = None  # Shiftを押した時の開始位置を保持

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):  # クリックがこのウィジェット上で行われたか確認
            if self.mode == 'draw':
                # 点描画モード
                with self.canvas:
                    Color(1, 0, 0, 1)  # 赤色で点を描画
                    d = 20
                    dot = Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
                    self.dots.append(dot)

            elif self.mode == 'select':
                # 選択モードで既存の点をクリック
                for dot in self.dots:
                    if dot.pos[0] < touch.x < dot.pos[0] + dot.size[0] and dot.pos[1] < touch.y < dot.pos[1] + dot.size[1]:
                        self.selected_dot = dot
                        self.shift_start_pos = dot.pos  # Shift移動の基準となる開始位置を保存
                        break

    def on_touch_move(self, touch):
        if self.selected_dot:
            if self.ctrl_active:
                # Ctrlキーが押されている場合は他の点にスナップ
                nearest_x = None
                nearest_y = None
                min_dist_x = float('inf')
                min_dist_y = float('inf')

                for dot in self.dots:
                    if dot == self.selected_dot:
                        continue

                    # x座標のスナップ
                    dist_x = abs(dot.pos[0] - self.selected_dot.pos[0])
                    if dist_x < min_dist_x:
                        min_dist_x = dist_x
                        nearest_x = dot.pos[0]

                    # y座標のスナップ
                    dist_y = abs(dot.pos[1] - self.selected_dot.pos[1])
                    if dist_y < min_dist_y:
                        min_dist_y = dist_y
                        nearest_y = dot.pos[1]

                # 最も近い距離に基づいてスナップ
                if min_dist_x < min_dist_y:
                    self.selected_dot.pos = (nearest_x, self.selected_dot.pos[1])
                else:
                    self.selected_dot.pos = (self.selected_dot.pos[0], nearest_y)

            elif self.shift_active:
                # Shiftキーが押されている場合は水平または垂直に移動
                start_x, start_y = self.shift_start_pos
                dx = abs(touch.x - start_x)
                dy = abs(touch.y - start_y)

                if dx > dy:
                    # 水平移動
                    self.selected_dot.pos = (touch.x - self.selected_dot.size[0] / 2, start_y)
                else:
                    # 垂直移動
                    self.selected_dot.pos = (start_x, touch.y - self.selected_dot.size[1] / 2)
            else:
                # 通常のドラッグ移動
                self.selected_dot.pos = (touch.x - self.selected_dot.size[0] / 2, touch.y - self.selected_dot.size[1] / 2)

    def on_touch_up(self, touch):
        # ドラッグ終了
        self.selected_dot = None
        self.shift_start_pos = None  # Shift移動の基準位置をリセット

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        # キー押下イベントをトラッキングし、ShiftキーまたはCtrlキーが押されたかを確認
        if 'shift' in modifiers:
            self.shift_active = True
        if 'ctrl' in modifiers:
            self.ctrl_active = True

    def on_key_up(self, window, key, scancode):
        # キーが離された時にShiftキーまたはCtrlキーを無効化
        if key == 304:  # Shiftキーのキーコード
            self.shift_active = False
        if key == 305:  # Ctrlキーのキーコード
            self.ctrl_active = False

class DrawingApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        # 描画ウィジェット
        self.draw_widget = DrawWidget()

        # ボタンレイアウト
        button_layout = BoxLayout(size_hint_y=0.1)

        # 点描画モードボタン
        draw_button = ToggleButton(text='Draw Mode', group='mode', state='down')
        draw_button.bind(on_press=self.set_draw_mode)

        # 選択モードボタン
        select_button = ToggleButton(text='Select Mode', group='mode')
        select_button.bind(on_press=self.set_select_mode)

        button_layout.add_widget(draw_button)
        button_layout.add_widget(select_button)

        layout.add_widget(button_layout)
        layout.add_widget(self.draw_widget)

        # キーボードイベントをトラッキングする
        from kivy.core.window import Window
        Window.bind(on_key_down=self.draw_widget.on_key_down)
        Window.bind(on_key_up=self.draw_widget.on_key_up)

        return layout

    def set_draw_mode(self, instance):
        self.draw_widget.mode = 'draw'

    def set_select_mode(self, instance):
        self.draw_widget.mode = 'select'


if __name__ == '__main__':
    DrawingApp().run()
