from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Ellipse, Line, Color
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton

class DrawWidget(Widget):
    def __init__(self, **kwargs):
        super(DrawWidget, self).__init__(**kwargs)
        self.mode = 'draw'  # 初期モードは点描画モード
        self.selected_shape = None
        self.dots = []  # 描画した点のリスト
        self.lines = []  # 描画した線のリスト
        self.shift_active = False  # Shiftキーが押されているかどうかを追跡
        self.ctrl_active = False  # Ctrlキーが押されているかどうかを追跡
        self.shift_start_pos = None  # Shiftを押した時の開始位置を保持
        self.line_start = None  # 線描画の始点を保持
        self.temp_line = None  # 仮線を保持

        # キーイベントリスナーを追加
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_key_down)
        self._keyboard.bind(on_key_up=self.on_key_up)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_key_down)
        self._keyboard.unbind(on_key_up=self.on_key_up)
        self._keyboard = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):  # クリックがこのウィジェット上で行われたか確認
            if self.mode == 'draw':
                # 点描画モード
                with self.canvas:
                    Color(1, 0, 0, 1)  # 赤色で点を描画
                    d = 20
                    dot = Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
                    self.dots.append(dot)

            elif self.mode == 'line':
                # 線描画モード
                self.line_start = (touch.x, touch.y)

            elif self.mode == 'select':
                # 選択モードで既存の図形をクリック
                for dot in self.dots:
                    if dot.pos[0] < touch.x < dot.pos[0] + dot.size[0] and dot.pos[1] < touch.y < dot.pos[1] + dot.size[1]:
                        self.selected_shape = ('dot', dot)
                        self.shift_start_pos = dot.pos  # Shift移動の基準となる開始位置を保存
                        break

                if not self.selected_shape:
                    for line, start, end in self.lines:
                        # 線の端をクリックした場合
                        if self.is_near(touch.pos, start):
                            self.selected_shape = ('line_end', line, start, end)
                            break
                        elif self.is_near(touch.pos, end):
                            self.selected_shape = ('line_end', line, end, start)
                            break
                        # 線の中間をクリックした場合
                        elif self.is_near_line(touch.pos, start, end):
                            self.selected_shape = ('line', line, start, end)
                            break

    def on_touch_move(self, touch):
        if self.selected_shape:
            shape_type, *shape = self.selected_shape

            if shape_type == 'dot':
                dot = shape[0]
                self.move_dot(dot, touch)

            elif shape_type == 'line':
                line, start, end = shape
                self.move_line(line, start, end, touch)

            elif shape_type == 'line_end':
                line, end, other_end = shape
                self.move_line_end(line, end, other_end, touch)

        elif self.mode == 'line' and self.line_start:
            # 仮線を描画
            if not self.temp_line:
                with self.canvas:
                    Color(0, 1, 0, 1)  # 緑色で仮線を描画
                    self.temp_line = Line(points=[self.line_start[0], self.line_start[1], touch.x, touch.y])
            else:
                self.temp_line.points = [self.line_start[0], self.line_start[1], touch.x, touch.y]

    def on_touch_up(self, touch):
        # 線の描画を確定
        if self.mode == 'line' and self.line_start:
            if self.temp_line:
                self.canvas.remove(self.temp_line)
                self.temp_line = None

            # 始点と終点が他の点や線端にスナップするように処理
            start_pos = self.line_start
            end_pos = (touch.x, touch.y)
            start_pos = self.snap_to_nearest(start_pos)
            end_pos = self.snap_to_nearest(end_pos)

            with self.canvas:
                Color(0, 1, 0, 1)  # 緑色で線を描画
                line = Line(points=[start_pos[0], start_pos[1], end_pos[0], end_pos[1]])
                self.lines.append((line, start_pos, end_pos))

            self.line_start = None

        # ドラッグ終了
        self.selected_shape = None
        self.shift_start_pos = None  # Shift移動の基準位置をリセット

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        print(f"window: {window}, key: {key}, scancode: {scancode}, codepoint: {codepoint}, modifiers: {modifiers}")

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

    def move_dot(self, dot, touch):
        if self.shift_active:
            # Shiftキーが押されている場合は水平または垂直に移動
            start_x, start_y = self.shift_start_pos
            dx = abs(touch.x - start_x)
            dy = abs(touch.y - start_y)

            if dx > dy:
                # 水平移動
                dot.pos = (touch.x - dot.size[0] / 2, start_y)
            else:
                # 垂直移動
                dot.pos = (start_x, touch.y - dot.size[1] / 2)
        elif self.ctrl_active:
            # Ctrlキーが押されている場合は他の点や線にスナップ
            dot.pos = self.snap_to_nearest((touch.x, touch.y))
        else:
            # 通常のドラッグ移動
            dot.pos = (touch.x - dot.size[0] / 2, touch.y - dot.size[1] / 2)

    def move_line(self, line, start, end, touch):
        dx = touch.x - self.shift_start_pos[0]
        dy = touch.y - self.shift_start_pos[1]
        new_start = (start[0] + dx, start[1] + dy)
        new_end = (end[0] + dx, end[1] + dy)

        # Shiftキーが押されている場合は水平または垂直に移動
        if self.shift_active:
            if abs(dx) > abs(dy):
                new_end = (new_start[0] + dx, new_start[1])
            else:
                new_end = (new_start[0], new_start[1] + dy)

        # Ctrlキーが押されている場合は他の点や線にスナップ
        if self.ctrl_active:
            new_start = self.snap_to_nearest(new_start)
            new_end = self.snap_to_nearest(new_end)

        # 更新された線の位置を設定
        line.points = [new_start[0], new_start[1], new_end[0], new_end[1]]
        self.shift_start_pos = (touch.x, touch.y)

    def move_line_end(self, line, end, other_end, touch):
        if self.shift_active:
            # Shiftキーが押されている場合は水平または垂直に移動
            dx = abs(touch.x - self.shift_start_pos[0])
            dy = abs(touch.y - self.shift_start_pos[1])

            if dx > dy:
                end = (touch.x, other_end[1])
            else:
                end = (other_end[0], touch.y)
        else:
            end = (touch.x, touch.y)

        # Ctrlキーが押されている場合は他の点や線にスナップ
        if self.ctrl_active:
            end = self.snap_to_nearest(end)

        # 更新された線の位置を設定
        line.points = [other_end[0], other_end[1], end[0], end[1]]
        self.shift_start_pos = (touch.x, touch.y)

    def snap_to_nearest(self, pos):
        min_dist_x, min_dist_y = float('inf'), float('inf')
        nearest_x, nearest_y = pos[0], pos[1]

        # 他の点や線端との距離を計算
        for dot in self.dots:
            dot_center = (dot.pos[0] + dot.size[0] / 2, dot.pos[1] + dot.size[1] / 2)
            dist_x = abs(dot_center[0] - pos[0])
            dist_y = abs(dot_center[1] - pos[1])

            if dist_x < min_dist_x:
                min_dist_x = dist_x
                nearest_x = dot_center[0]
            if dist_y < min_dist_y:
                min_dist_y = dist_y
                nearest_y = dot_center[1]

        for line, start, end in self.lines:
            for point in [start, end]:
                dist_x = abs(point[0] - pos[0])
                dist_y = abs(point[1] - pos[1])

                if dist_x < min_dist_x:
                    min_dist_x = dist_x
                    nearest_x = point[0]
                if dist_y < min_dist_y:
                    min_dist_y = dist_y
                    nearest_y = point[1]

        # 必要なら最も近い点や線端にスナップ
        snapped_x = nearest_x if min_dist_x < 10 else pos[0]
        snapped_y = nearest_y if min_dist_y < 10 else pos[1]
        return snapped_x, snapped_y

    def is_near(self, pos1, pos2, threshold=20):
        return abs(pos1[0] - pos2[0]) < threshold and abs(pos1[1] - pos2[1]) < threshold

    def is_near_line(self, point, start, end, threshold=10):
        """ 線と点の距離が近いかどうかを判断 """
        x1, y1 = start
        x2, y2 = end
        x0, y0 = point
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return False  # 線がない場合はfalseを返す
        # 点と線の距離を計算
        distance = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / (dx ** 2 + dy ** 2) ** 0.5
        return distance < threshold


class DrawingApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        # 描画ウィジェット
        self.draw_widget = DrawWidget()
        layout.add_widget(self.draw_widget)

        # モード切り替えボタン
        button_layout = BoxLayout(size_hint_y=0.1)
        self.draw_button = ToggleButton(text='Draw Points', group='mode')
        self.draw_button.bind(on_press=self.set_mode)
        self.line_button = ToggleButton(text='Draw Lines', group='mode')
        self.line_button.bind(on_press=self.set_mode)
        self.select_button = ToggleButton(text='Select Mode', group='mode')
        self.select_button.bind(on_press=self.set_mode)
        button_layout.add_widget(self.draw_button)
        button_layout.add_widget(self.line_button)
        button_layout.add_widget(self.select_button)

        layout.add_widget(button_layout)

        return layout

    def set_mode(self, instance):
        if instance == self.draw_button:
            self.draw_widget.mode = 'draw'
        elif instance == self.line_button:
            self.draw_widget.mode = 'line'
        elif instance == self.select_button:
            self.draw_widget.mode = 'select'


if __name__ == '__main__':
    DrawingApp().run()
