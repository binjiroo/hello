import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Ellipse, Rectangle, Mesh, InstructionGroup
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown  # 追加
from kivy.uix.popup import Popup
from kivy.clock import Clock
from copy import deepcopy
import copy
from math import atan2, degrees, radians, sin, cos, sqrt
kivy.require('2.1.0')


class Action:
    def undo(self):
        pass

    def redo(self):
        pass


class AddShapeAction(Action):
    def __init__(self, shape, shape_instructions, shapes_list):
        self.shape = shape
        self.shape_instructions = shape_instructions
        self.shapes_list = shapes_list

    def undo(self):
        # 図形をキャンバスとリストから削除
        self.shape_instructions.remove(self.shape.instructions)
        self.shapes_list.remove(self.shape)

    def redo(self):
        # 図形をキャンバスとリストに追加
        self.shape_instructions.add(self.shape.instructions)
        self.shapes_list.append(self.shape)


class MoveShapeAction(Action):
    def __init__(self, shape, dx, dy):
        self.shape = shape
        self.dx = dx
        self.dy = dy

    def undo(self):
        self.shape.move(-self.dx, -self.dy)

    def redo(self):
        self.shape.move(self.dx, self.dy)


class RotateShapeAction(Action):
    def __init__(self, shape, angle, pivot):
        self.shape = shape
        self.angle = angle
        self.pivot = pivot

    def undo(self):
        self.shape.rotate(-self.angle, self.pivot)

    def redo(self):
        self.shape.rotate(self.angle, self.pivot)


class ClearCanvasAction(Action):
    def __init__(self, shapes_copy, shape_instructions, shapes_list):
        self.shapes_copy = shapes_copy
        self.shape_instructions = shape_instructions
        self.shapes_list = shapes_list

    def undo(self):
        for shape in self.shapes_copy:
            self.shape_instructions.add(shape.instructions)
        self.shapes_list.extend(self.shapes_copy)

    def redo(self):
        for shape in self.shapes_copy:
            self.shape_instructions.remove(shape.instructions)
        self.shapes_list.clear()


class Shape:
    def __init__(self, shape_type, instructions, color, **kwargs):
        self.shape_type = shape_type
        self.instructions = instructions  # InstructionGroup
        self.kwargs = kwargs  # 位置やサイズなどの追加パラメータ
        self.color = color  # 色を保持

    def copy_state(self):
        # 現在の図形の状態をコピーして保存
        return {
            'type': self.shape_type,
            'color': self.color,
            'kwargs': self.kwargs.copy()
        }

    def load_state(self, state):
        # 保存した状態から図形のパラメータを復元
        self.shape_type = state['type']
        self.color = state['color']
        self.kwargs = state['kwargs'].copy()
        self.redraw()  # 再描画

    def collide_point(self, x, y):
        # Collision detection depends on shape type
        if self.shape_type == 'point':
            pos = self.kwargs.get('pos', (0, 0))
            size = self.kwargs.get('size', (5, 5))
            dx = x - (pos[0] + size[0] / 2)
            dy = y - (pos[1] + size[1] / 2)
            distance = sqrt(dx * dx + dy * dy)
            radius = size[0] / 2
            return distance <= radius
        elif self.shape_type == 'line':
            start = self.kwargs.get('start', (0, 0))
            end = self.kwargs.get('end', (0, 0))
            # Calculate distance from point to line segment
            return self.point_line_distance((x, y), start, end) <= self.kwargs.get('width', 1)
        elif self.shape_type == 'rectangle':
            corners = self.kwargs['corners']
            if self.point_in_polygon(x, y, corners):
                return True
            else:
                # エッジや角付近の点を検出するために、エッジとの距離をチェック
                edge_tolerance = 10  # エッジからの許容距離（ピクセル）
                for i in range(len(corners)):
                    start = corners[i]
                    end = corners[(i + 1) % len(corners)]
                    if self.distance_point_to_segment((x, y), start, end) <= edge_tolerance:
                        return True
            return False
        elif self.shape_type == 'circle':
            center = self.kwargs.get('center', (0, 0))
            radius = self.kwargs.get('radius', 0)
            dx = x - center[0]
            dy = y - center[1]
            distance = sqrt(dx * dx + dy * dy)
            return distance <= radius
        elif self.shape_type == 'arc':
            center = self.kwargs.get('center', (0, 0))
            radius_x = self.kwargs.get('radius_x', 0)
            radius_y = self.kwargs.get('radius_y', 0)
            # Simplified collision detection for arc
            dx = x - center[0]
            dy = y - center[1]
            if radius_x == 0 or radius_y == 0:
                return False
            distance = (dx ** 2) / (radius_x ** 2) + (dy ** 2) / (radius_y ** 2)
            return distance <= 1.0
        return False

    def point_in_polygon(self, x, y, polygon):
        num = len(polygon)
        j = num - 1
        c = False
        for i in range(num):
            xi, yi = polygon[i]
            xj, yj = polygon[j]
            if ((yi > y) != (yj > y)) and \
            (x < (xj - xi) * (y - yi) / (yj - yi + 1e-10) + xi):
                c = not c
            j = i
        return c

    def point_line_distance(self, point, start, end):
        # Calculate the distance from a point to a line segment
        x0, y0 = point
        x1, y1 = start
        x2, y2 = end
        numerator = abs((y2 - y1)*x0 - (x2 - x1)*y0 + x2*y1 - y2*x1)
        denominator = sqrt((y2 - y1)**2 + (x2 - x1)**2)
        if denominator == 0:
            return sqrt((x0 - x1)**2 + (y0 - y1)**2)
        return numerator / denominator

    def distance_point_to_segment(self, point, start, end):
        x0, y0 = point
        x1, y1 = start
        x2, y2 = end

        dx = x2 - x1
        dy = y2 - y1
        if dx == dy == 0:
            # It's a point not a line segment.
            return sqrt((x0 - x1)**2 + (y0 - y1)**2)

        # Calculate the t that minimizes the distance.
        t = ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)

        # See if this represents one of the segment's
        # end points or a point in the middle.
        if t < 0:
            dx = x0 - x1
            dy = y0 - y1
        elif t > 1:
            dx = x0 - x2
            dy = y0 - y2
        else:
            near_x = x1 + t * dx
            near_y = y1 + t * dy
            dx = x0 - near_x
            dy = y0 - near_y

        return sqrt(dx * dx + dy * dy)

    def move(self, dx, dy):
        for key in ['pos', 'start', 'end', 'center', 'start_point', 'end_point']:
            if key in self.kwargs:
                self.kwargs[key] = (self.kwargs[key][0] + dx, self.kwargs[key][1] + dy)
        # 矩形のcornersも移動
        if 'corners' in self.kwargs:
            self.kwargs['corners'] = [(x + dx, y + dy) for (x, y) in self.kwargs['corners']]
        self.redraw()

    def __deepcopy__(self, memo):
        # 新しいInstructionGroupを作成
        new_instructions = InstructionGroup()
        # 必要に応じてグラフィック命令を再生成
        new_shape = Shape(self.shape_type, new_instructions, deepcopy(self.color, memo), **deepcopy(self.kwargs, memo))
        new_shape.redraw()  # 新しいInstructionGroupにグラフィックを再描画
        return new_shape

    def redraw(self):
        # 既存の指示をクリア
        self.instructions.clear()
        # 保存された色を使用
        self.instructions.add(Color(*self.color))
        # 図形の種類と更新されたkwargsに基づいて再描画
        if self.shape_type == 'point':
            self.instructions.add(Ellipse(pos=self.kwargs['pos'], size=self.kwargs['size']))
        elif self.shape_type == 'line':
            self.instructions.add(Line(points=[*self.kwargs['start'], *self.kwargs['end']],
                                    width=self.kwargs.get('width', 1)))
        elif self.shape_type == 'rectangle':
            corners = self.kwargs['corners']
            if self.kwargs.get('fill', False):
                # 塗りつぶされたポリゴンを描画
                vertices = []
                indices = []
                for corner in corners:
                    vertices.extend([corner[0], corner[1], 0, 0])
                indices = [0, 1, 2, 2, 3, 0]
                self.instructions.add(Mesh(vertices=vertices, indices=indices, mode='triangles'))
            else:
                points = []
                for corner in corners:
                    points.extend([corner[0], corner[1]])
                points.extend([corners[0][0], corners[0][1]])  # 閉じる
                self.instructions.add(Line(points=points, width=self.kwargs.get('width', 1)))
        elif self.shape_type == 'circle':
            center = self.kwargs['center']
            radius = self.kwargs['radius']
            if self.kwargs.get('fill', False):
                self.instructions.add(Ellipse(pos=(center[0] - radius, center[1] - radius),
                                            size=(radius * 2, radius * 2)))
            else:
                self.instructions.add(Line(circle=(center[0], center[1], radius),
                                        width=self.kwargs.get('width', 1)))
        elif self.shape_type == 'arc':
            # 弧を再描画
            if self.kwargs.get('fill', False):
                self.draw_filled_arc_segment(
                    self.kwargs['start_angle'],
                    self.kwargs['end_angle'],
                    self.instructions)
            else:
                self.draw_arc_segment(
                    self.kwargs['start_angle'],
                    self.kwargs['end_angle'],
                    self.instructions)
            # 線とポイントを描画
            self.instructions.add(Color(0, 0, 1, 1))
            self.instructions.add(Line(points=[
                self.kwargs['center'][0], self.kwargs['center'][1],
                self.kwargs['start_point'][0], self.kwargs['start_point'][1]], width=1))
            self.instructions.add(Line(points=[
                self.kwargs['center'][0], self.kwargs['center'][1],
                self.kwargs['end_point'][0], self.kwargs['end_point'][1]], width=1))
            # 開始点と終了点
            self.instructions.add(Color(1, 0, 0, 1))
            self.instructions.add(Line(circle=(self.kwargs['start_point'][0],
                                            self.kwargs['start_point'][1], 5), width=2))
            self.instructions.add(Line(circle=(self.kwargs['end_point'][0],
                                            self.kwargs['end_point'][1], 5), width=2))

    def draw_arc_segment(self, start_angle, end_angle, instr):
        center = self.kwargs['center']
        radius_x = self.kwargs['radius_x']
        radius_y = self.kwargs['radius_y']
        step = 1  # Adjust precision
        points = []
        angle = start_angle
        if end_angle < start_angle:
            end_angle += 360
        while angle <= end_angle:
            rad = radians(angle)
            x = center[0] + radius_x * cos(rad)
            y = center[1] + radius_y * sin(rad)
            points.extend([x, y])
            angle += step
        instr.add(Line(points=points, width=self.kwargs.get('width', 1)))

    def draw_filled_arc_segment(self, start_angle, end_angle, instr):
        center = self.kwargs['center']
        radius_x = self.kwargs['radius_x']
        radius_y = self.kwargs['radius_y']
        step = 5  # Adjust precision
        vertices = [center[0], center[1], 0, 0]
        indices = []
        angle = start_angle
        if end_angle < start_angle:
            end_angle += 360
        while angle <= end_angle:
            rad = radians(angle)
            x = center[0] + radius_x * cos(rad)
            y = center[1] + radius_y * sin(rad)
            vertices.extend([x, y, 0, 0])
            angle += step
        num_vertices = len(vertices) // 4
        for i in range(1, num_vertices - 1):
            indices.extend([0, i, i + 1])
        instr.add(Mesh(vertices=vertices, indices=indices, mode='triangles'))

    def copy(self):
        # 図形のコピーを作成
        new_instructions = InstructionGroup()
        new_kwargs = self.kwargs.copy()
        if 'corners' in new_kwargs:
            new_kwargs['corners'] = new_kwargs['corners'][:]
        new_shape = Shape(self.shape_type, new_instructions, self.color, **new_kwargs)
        return new_shape
    
    def load_state(self, other_shape):
        # 他の図形の状態をこの図形にロード
        self.kwargs = other_shape.kwargs.copy()
        if 'corners' in self.kwargs:
            self.kwargs['corners'] = self.kwargs['corners'][:]
        self.redraw()

    def get_center(self):
        if self.shape_type == 'rectangle':
            corners = self.kwargs['corners']
            xs = [p[0] for p in corners]
            ys = [p[1] for p in corners]
            center = (sum(xs) / 4, sum(ys) / 4)
            return center
        elif self.shape_type == 'line':
            start = self.kwargs.get('start')
            end = self.kwargs.get('end')
            center = ((start[0] + end[0])/2, (start[1] + end[1])/2)
        elif self.shape_type == 'circle':
            center = self.kwargs.get('center', (0, 0))
        elif self.shape_type == 'arc':
            center = self.kwargs.get('center', (0, 0))
        else:
            center = (0, 0)
        return center

    def is_point_on_start_point(self, x, y):
        if self.shape_type == 'line':
            start = self.kwargs.get('start', (0, 0))
            size = 10
            return abs(x - start[0]) <= size and abs(y - start[1]) <= size
        elif self.shape_type == 'arc':
            start_point = self.kwargs.get('start_point', (0, 0))
            size = 10
            return abs(x - start_point[0]) <= size and abs(y - start_point[1]) <= size
        else:
            return False

    def is_point_on_end_point(self, x, y):
        if self.shape_type == 'line':
            end = self.kwargs.get('end', (0, 0))
            size = 10
            return abs(x - end[0]) <= size and abs(y - end[1]) <= size
        elif self.shape_type == 'arc':
            end_point = self.kwargs.get('end_point', (0, 0))
            size = 10
            return abs(x - end_point[0]) <= size and abs(y - end_point[1]) <= size
        else:
            return False

    def is_point_on_midpoint(self, x, y):
        if self.shape_type == 'line':
            start = self.kwargs.get('start', (0, 0))
            end = self.kwargs.get('end', (0, 0))
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            size = 10
            return abs(x - mid_x) <= size and abs(y - mid_y) <= size
        else:
            return False

    def is_point_on_center(self, x, y):
        if self.shape_type in ['rectangle', 'circle', 'arc']:
            center = self.get_center()
            size = 10
            return abs(x - center[0]) <= size and abs(y - center[1]) <= size
        else:
            return False

    def is_point_on_corner(self, x, y):
        if self.shape_type == 'rectangle':
            corners = self.kwargs['corners']
            size_tolerance = 10
            for corner in corners:
                if sqrt((x - corner[0])**2 + (y - corner[1])**2) <= size_tolerance:
                    return True
            return False
        else:
            return False

    def get_clicked_corner(self, x, y):
        if self.shape_type != 'rectangle':
            return None
        corners = self.kwargs['corners']
        size_tolerance = 10
        for corner in corners:
            if sqrt((x - corner[0])**2 + (y - corner[1])**2) <= size_tolerance:
                return corner
        return None

    def get_opposite_corner(self, corner):
        if self.shape_type != 'rectangle':
            return None
        corners = self.kwargs['corners']
        if corner in corners:
            index = corners.index(corner)
            opposite_index = (index + 2) % 4
            return corners[opposite_index]
        return None

    def is_point_on_edge(self, x, y):
        if self.shape_type == 'rectangle':
            corners = self.kwargs['corners']
            edge_tolerance = 10
            for i in range(len(corners)):
                start = corners[i]
                end = corners[(i + 1) % len(corners)]
                if self.distance_point_to_segment((x, y), start, end) <= edge_tolerance:
                    return True
            return False
        return False

    def is_point_on_line(self, x, y):
        if self.shape_type == 'line':
            start = self.kwargs.get('start', (0, 0))
            end = self.kwargs.get('end', (0, 0))
            line_tolerance = 10
            distance = self.distance_point_to_segment((x, y), start, end)
            return distance <= line_tolerance
        return False

    def is_point_on_circle_circumference(self, x, y):
        if self.shape_type == 'circle':
            center = self.kwargs.get('center', (0, 0))
            radius = self.kwargs.get('radius', 0)
            distance = sqrt((x - center[0])**2 + (y - center[1])**2)
            return abs(distance - radius) <= 10
        return False

    def is_point_on_arc_circumference(self, x, y):
        if self.shape_type == 'arc':
            center = self.kwargs.get('center', (0, 0))
            radius_x = self.kwargs.get('radius_x', 0)
            radius_y = self.kwargs.get('radius_y', 0)
            dx = x - center[0]
            dy = y - center[1]
            distance = (dx ** 2) / (radius_x ** 2) + (dy ** 2) / (radius_y ** 2)
            return abs(distance - 1) <= 0.1
        return False

    def get_nearest_point_on_line(self, x, y):
        if self.shape_type == 'line':
            start = self.kwargs.get('start')
            end = self.kwargs.get('end')
            x0, y0 = x, y
            x1, y1 = start
            x2, y2 = end
            dx = x2 - x1
            dy = y2 - y1
            if dx == dy == 0:
                return start
            t = ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)
            t = max(0, min(1, t))
            nearest_x = x1 + t * dx
            nearest_y = y1 + t * dy
            return (nearest_x, nearest_y)
        return None

    def get_nearest_point_on_edge(self, x, y):
        if self.shape_type == 'rectangle':
            corners = self.kwargs['corners']
            min_distance = float('inf')
            nearest_point = None
            for i in range(len(corners)):
                start = corners[i]
                end = corners[(i + 1) % len(corners)]
                point = self.get_nearest_point_on_segment((x, y), start, end)
                distance = sqrt((x - point[0])**2 + (y - point[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_point = point
            return nearest_point
        return None

    def get_nearest_point_on_segment(self, point, start, end):
        x0, y0 = point
        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1
        if dx == dy == 0:
            return start
        t = ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))
        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy
        return (nearest_x, nearest_y)

    def get_nearest_point_on_circle(self, x, y):
        if self.shape_type == 'circle':
            center = self.kwargs.get('center')
            radius = self.kwargs.get('radius')
            dx = x - center[0]
            dy = y - center[1]
            distance = sqrt(dx * dx + dy * dy)
            if distance == 0:
                return center
            scale = radius / distance
            return (center[0] + dx * scale, center[1] + dy * scale)
        return None

    def get_nearest_point_on_arc(self, x, y):
        if self.shape_type == 'arc':
            center = self.kwargs.get('center')
            radius_x = self.kwargs.get('radius_x')
            radius_y = self.kwargs.get('radius_y')
            angle = degrees(atan2(y - center[1], x - center[0]))
            angle = (angle + 360) % 360
            start_angle = self.kwargs.get('start_angle')
            end_angle = self.kwargs.get('end_angle')
            if end_angle < start_angle:
                end_angle += 360
            if start_angle <= angle <= end_angle:
                rad = radians(angle)
                x_on_arc = center[0] + radius_x * cos(rad)
                y_on_arc = center[1] + radius_y * sin(rad)
                return (x_on_arc, y_on_arc)
        return None

    def rotate(self, angle, pivot):
        # Rotate the shape around the pivot point by angle (in degrees)
        angle_rad = radians(angle)
        cos_a = cos(angle_rad)
        sin_a = sin(angle_rad)

        def rotate_point(p):
            x, y = p
            x -= pivot[0]
            y -= pivot[1]
            x_new = x * cos_a - y * sin_a
            y_new = x * sin_a + y * cos_a
            x_new += pivot[0]
            y_new += pivot[1]
            return (x_new, y_new)

        if self.shape_type == 'line':
            self.kwargs['start'] = rotate_point(self.kwargs['start'])
            self.kwargs['end'] = rotate_point(self.kwargs['end'])
        elif self.shape_type == 'rectangle':
            corners = self.kwargs['corners']
            rotated_corners = [rotate_point(corner) for corner in corners]
            self.kwargs['corners'] = rotated_corners
        elif self.shape_type == 'circle':
            self.kwargs['center'] = rotate_point(self.kwargs['center'])
        elif self.shape_type == 'arc':
            self.kwargs['center'] = rotate_point(self.kwargs['center'])
            self.kwargs['start_point'] = rotate_point(self.kwargs['start_point'])
            self.kwargs['end_point'] = rotate_point(self.kwargs['end_point'])
            self.kwargs['start_angle'] += angle
            self.kwargs['end_angle'] += angle

        self.redraw()

class RecordedAction:
    def __init__(self, action_type, params):
        self.action_type = action_type
        self.params = params

class ShapeDrawer(Widget):
    def __init__(self, **kwargs):
        # すべての図形を保持するInstructionGroup
        self.layers = {}  # レイヤー情報を保持する辞書
        self.current_main_layer = 0  # 現在のメインレイヤー
        self.current_sub_layer = 0   # 現在のサブレイヤー
        self.shapes = []  # 描画された図形のリスト
         # アクションスタックを初期化
        self.undo_stack = []
        self.redo_stack = []

        self.shape_instructions = InstructionGroup()

        super().__init__(**kwargs)
        self.selected_shape = None
        self.selection_mode = False
        self.rotation_mode = False  # 回転モードフラグ
        self.last_touch_pos = None

        # 回転機能に関する追加変数
        self.rotation_angle_input = None  # 入力された角度
        self.rotation_step = None         # 回転ステップ
        self.initial_shape_state = None   # 図形の初期状態
        self.total_rotation_angle = 0     # 合計回転角度
        self.current_snapped_angle = 0    # 現在のスナップされた角度

        self.center_point = None
        self.start_point = None
        self.end_point = None
        self.radius_x = None
        self.radius_y = None
        self.flattening_rate = 0.0  # 扁平率
        self.start_angle = None
        self.end_angle = None
        self.dragging = False
        self.drawing_mode = 'point'  # デフォルトの描画モード
        self.fill_mode = 'stroke'    # 'stroke'または'fill'
        self.line_width = 1          # 線幅
        self.temp_shape = None

        self.total_dx = 0
        self.total_dy = 0

        self.copied_shape = None     # コピー・ペースト機能用
        self.is_dragging_shape = False  # ドラッグ中のペーストを無効化

        # 回転のための変数
        self.rotation_pivot = None
        self.rotation_start_angle = None
        self.rotation_mode_detail = None  # 回転に関する詳細情報

        # 現在の色を初期化
        self.current_color = (0, 0, 0, 1)

        # スナップモードを初期化
        self.snap_mode = False

        # 録画機能に関する追加変数
        self.is_recording = False           # 録画中かどうかのフラグ
        self.recorded_actions = []          # 録画されたアクションのリスト
        self.replay_index = 0               # 再生中のアクションのインデックス

        # レイヤー機能のための初期化
        self.is_main_layer_mode = True  # メインレイヤーモードかどうか

    def on_kv_post(self, base_widget):
        # KVファイルが処理された後に呼ばれるイベントハンドラ
        super().on_kv_post(base_widget)
        self.initialize_layer(self.current_main_layer, self.current_sub_layer)
        self.canvas.add(self.shape_instructions)

    def set_flattening_rate(self, value):
        try:
            self.flattening_rate = float(value)
            if not 0 <= self.flattening_rate < 1:
                self.flattening_rate = 0.0
        except ValueError:
            self.flattening_rate = 0.0

    def set_drawing_mode(self, mode):
        self.drawing_mode = mode
        self.selection_mode = (mode == 'select')
        self.rotation_mode = (mode == 'rotate')
        if self.selection_mode:
            print("選択モードが有効になりました。")  # デバッグメッセージ
        self.reset()

    def set_fill_mode(self, mode):
        self.fill_mode = mode

    def set_line_width(self, width):
        self.line_width = width

    def set_current_color(self, color):
        self.current_color = color

    def set_snap_mode(self, mode):
        self.snap_mode = mode

    def clear_canvas(self):
        # キャンバスとシェイプリストからすべての図形を削除し、アンドゥスタックにこのアクションを記録します。
        shapes_backup = [(shape, shape.copy_state()) for shape in self.shapes]  # 図形の状態を保存
        self.shape_instructions.clear()  # キャンバスからすべての描画命令をクリア
        self.shapes.clear()  # 図形リストをクリア

        # クリアアクションをスタックに追加
        action = ClearCanvasAction(shapes_backup, self.shape_instructions, self.shapes)
        self.undo_stack.append(action)
        self.redo_stack.clear()

        # 選択をリセット
        self.selected_shape = None
        # 一時的な描画を削除
        self.canvas.remove_group('temp')

    def set_rotation_angle(self, value):
        try:
            self.rotation_angle_input = float(value)
        except ValueError:
            self.rotation_angle_input = None

    def set_rotation_step(self, value):
        if value == 'フリー':
            self.rotation_step = None
        else:
            self.rotation_step = int(value.split('度')[0])  # '15度'から数値を取得    

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False

        if self.selection_mode:
            for shape in reversed(self.shapes):  # 図形リストを逆順に検査
                if shape.collide_point(*touch.pos):
                    self.selected_shape = shape
                    self.last_touch_pos = touch.pos
                    self.total_dx = 0  # ドラッグ距離をリセット
                    self.total_dy = 0  # ドラッグ距離をリセット
                    print(f"選択された図形: {shape}")  # デバッグメッセージ
                    return True
        elif self.drawing_mode == 'point':
            self.draw_point(touch.pos)
            return True

        if self.rotation_mode:
            # 現在のレイヤー内の図形を逆順にチェック（上に描画された図形から）
            for shape in reversed(self.shapes):
                if shape.collide_point(*touch.pos):
                    self.selected_shape = shape
                    self.last_touch_pos = touch.pos
                    self.total_rotation_angle = 0
                    self.current_snapped_angle = 0
                    self.initial_shape_state = shape.copy()

                    # クリック位置に応じた回転ピボットと中心を設定
                    if shape.shape_type == 'line':
                        if shape.is_point_on_start_point(*touch.pos):
                            self.rotation_pivot = shape.kwargs.get('end')
                            self.rotation_center = shape.kwargs.get('start')
                            self.rotation_mode_detail = 'line_start'
                        elif shape.is_point_on_end_point(*touch.pos):
                            self.rotation_pivot = shape.kwargs.get('start')
                            self.rotation_center = shape.kwargs.get('end')
                            self.rotation_mode_detail = 'line_end'
                        else:
                            # 線上の他の部分をクリックした場合、中間点を軸に回転
                            self.rotation_pivot = shape.get_center()
                            self.rotation_center = shape.get_center()
                            self.rotation_mode_detail = 'line_center'

                    elif shape.shape_type == 'arc':
                        if shape.is_point_on_start_point(*touch.pos):
                            self.rotation_pivot = shape.kwargs.get('end_point')
                            self.rotation_center = shape.kwargs.get('start_point')
                            self.rotation_mode_detail = 'arc_start'
                        elif shape.is_point_on_end_point(*touch.pos):
                            self.rotation_pivot = shape.kwargs.get('start_point')
                            self.rotation_center = shape.kwargs.get('end_point')
                            self.rotation_mode_detail = 'arc_end'
                        else:
                            # 円弧の他の部分をクリックした場合、中心を軸に回転
                            self.rotation_pivot = shape.get_center()
                            self.rotation_center = shape.get_center()
                            self.rotation_mode_detail = 'arc_center'

                    elif shape.shape_type == 'rectangle':
                        if shape.is_point_on_corner(*touch.pos):
                            clicked_corner = shape.get_clicked_corner(*touch.pos)
                            opposite_corner = shape.get_opposite_corner(clicked_corner)
                            self.rotation_pivot = opposite_corner
                            self.rotation_center = clicked_corner
                            self.rotation_mode_detail = 'rectangle_corner'
                        else:
                            self.rotation_pivot = shape.get_center()
                            self.rotation_center = shape.get_center()
                            self.rotation_mode_detail = 'rectangle_center'

                    elif shape.shape_type == 'circle':
                        self.rotation_pivot = shape.get_center()
                        self.rotation_center = shape.get_center()
                        self.rotation_mode_detail = 'circle_center'

                    elif shape.shape_type == 'arc':
                        if shape.is_point_on_center(*touch.pos):
                            self.rotation_pivot = shape.get_center()
                            self.rotation_center = shape.get_center()
                            self.rotation_mode_detail = 'arc_center'
                        elif shape.is_point_on_start_point(*touch.pos):
                            self.rotation_pivot = shape.kwargs.get('end_point')
                            self.rotation_center = shape.kwargs.get('start_point')
                            self.rotation_mode_detail = 'arc_start'
                        elif shape.is_point_on_end_point(*touch.pos):
                            self.rotation_pivot = shape.kwargs.get('start_point')
                            self.rotation_center = shape.kwargs.get('end_point')
                            self.rotation_mode_detail = 'arc_end'
                        else:
                            self.rotation_pivot = shape.get_center()
                            self.rotation_center = shape.get_center()
                            self.rotation_mode_detail = 'arc_center'
                    else:
                        self.rotation_pivot = shape.get_center()
                        self.rotation_center = shape.get_center()

                    self.rotation_start_angle = self.get_angle(self.rotation_pivot, touch.pos)

                    # 角度入力がある場合、即座に回転を適用
                    if self.rotation_angle_input is not None:
                        self.rotate_shape(self.selected_shape, self.rotation_angle_input, self.rotation_pivot)
                        # アクションをスタックに追加
                        action = RotateShapeAction(self.selected_shape, self.rotation_angle_input, self.rotation_pivot)
                        self.undo_stack.append(action)
                        self.redo_stack.clear()
                        self.selected_shape = None
                    return True
            return False
        else:
            if self.collide_point(*touch.pos):
                if self.snap_mode:
                    snap_pos = self.get_snap_point(touch.pos)
                else:
                    snap_pos = touch.pos
                if self.drawing_mode == 'point':
                    self.draw_point(snap_pos)
                    return True
                elif self.drawing_mode == 'line':
                    self.start_point = snap_pos
                    self.dragging = True
                    return True
                elif self.drawing_mode == 'rectangle':
                    self.start_point = snap_pos
                    self.dragging = True
                    return True
                elif self.drawing_mode == 'circle':
                    self.center_point = snap_pos
                    self.dragging = True
                    return True
                elif self.drawing_mode == 'arc':
                    if not self.center_point:
                        self.center_point = snap_pos
                        self.dragging = True
                        return True
                    elif not self.radius_x:
                        self.radius_x = self.get_distance(self.center_point, snap_pos)
                        self.radius_y = self.radius_x * (1 - self.flattening_rate)
                        self.dragging = True
                        return True
                    elif self.start_angle is None:
                        self.start_angle = self.get_angle_point(self.center_point, snap_pos)
                        self.start_point = self.get_ellipse_point(self.start_angle)
                        self.dragging = True
                        return True
                    elif self.end_angle is None:
                        self.end_angle = self.get_angle_point(self.center_point, snap_pos)
                        self.end_point = self.get_ellipse_point(self.end_angle)
                        self.draw_arc()
                        self.reset()
                        return True
            return super().on_touch_down(touch)

    def get_snap_point(self, pos):
        x, y = pos
        snap_distance = 15  # スナップする許容距離
        closest_point = pos
        min_distance = snap_distance

        for shape in self.shapes:
            if shape.shape_type == 'point':
                center = (shape.kwargs['pos'][0] + shape.kwargs['size'][0]/2,
                          shape.kwargs['pos'][1] + shape.kwargs['size'][1]/2)
                distance = sqrt((x - center[0])**2 + (y - center[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    closest_point = center
            elif shape.shape_type == 'line':
                # 端点
                for key in ['start', 'end']:
                    point = shape.kwargs[key]
                    distance = sqrt((x - point[0])**2 + (y - point[1])**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_point = point
                # 中間点や線上
                if shape.is_point_on_line(x, y):
                    nearest_point = shape.get_nearest_point_on_line(x, y)
                    distance = sqrt((x - nearest_point[0])**2 + (y - nearest_point[1])**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_point = nearest_point
            elif shape.shape_type == 'rectangle':
                # 中心
                center = shape.get_center()
                distance = sqrt((x - center[0])**2 + (y - center[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    closest_point = center
                # 角
                for corner in shape.kwargs['corners']:
                    distance = sqrt((x - corner[0])**2 + (y - corner[1])**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_point = corner
                # 辺上
                if shape.is_point_on_edge(x, y):
                    nearest_point = shape.get_nearest_point_on_edge(x, y)
                    distance = sqrt((x - nearest_point[0])**2 + (y - nearest_point[1])**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_point = nearest_point
            elif shape.shape_type == 'circle':
                # 中心
                center = shape.kwargs['center']
                distance = sqrt((x - center[0])**2 + (y - center[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    closest_point = center
                # 円周上
                if shape.is_point_on_circle_circumference(x, y):
                    nearest_point = shape.get_nearest_point_on_circle(x, y)
                    distance = sqrt((x - nearest_point[0])**2 + (y - nearest_point[1])**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_point = nearest_point
            elif shape.shape_type == 'arc':
                # 中心
                center = shape.kwargs['center']
                distance = sqrt((x - center[0])**2 + (y - center[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    closest_point = center
                # 始点・終点
                for key in ['start_point', 'end_point']:
                    point = shape.kwargs[key]
                    distance = sqrt((x - point[0])**2 + (y - point[1])**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_point = point
                # 円周上
                if shape.is_point_on_arc_circumference(x, y):
                    nearest_point = shape.get_nearest_point_on_arc(x, y)
                    if nearest_point:
                        distance = sqrt((x - nearest_point[0])**2 + (y - nearest_point[1])**2)
                        if distance < min_distance:
                            min_distance = distance
                            closest_point = nearest_point
                # 中心から始点・終点を結ぶ線上
                for key in ['start_point', 'end_point']:
                    start = center
                    end = shape.kwargs[key]
                    nearest_point = shape.get_nearest_point_on_segment((x, y), start, end)
                    distance = sqrt((x - nearest_point[0])**2 + (y - nearest_point[1])**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_point = nearest_point

        return closest_point

    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos):
            return False

        if self.selection_mode and self.selected_shape:
            # 図形を移動中の処理
            current_pos = touch.pos
            dx, dy = current_pos[0] - self.last_touch_pos[0], current_pos[1] - self.last_touch_pos[1]
            self.total_dx += dx
            self.total_dy += dy
            self.move_shape(self.selected_shape, dx, dy)
            self.last_touch_pos = current_pos
            return True

        if self.rotation_mode and self.selected_shape:
            current_angle = self.get_angle(self.rotation_pivot, touch.pos)
            angle_diff = current_angle - self.rotation_start_angle
            self.total_rotation_angle += angle_diff

            if self.rotation_step is not None:
                snapped_angle = round(self.total_rotation_angle / self.rotation_step) * self.rotation_step
            else:
                snapped_angle = self.total_rotation_angle

            # 図形を初期状態にリセット
            self.selected_shape.load_state(self.initial_shape_state)

            # 回転を適用
            self.selected_shape.rotate(snapped_angle, self.rotation_pivot)

            self.rotation_start_angle = current_angle
            return True

        if self.dragging:
            if self.snap_mode:
                snap_pos = self.get_snap_point(touch.pos)
            else:
                snap_pos = touch.pos
            if self.drawing_mode == 'line':
                self.draw_temp_line(snap_pos)
                return True
            elif self.drawing_mode == 'rectangle':
                self.draw_temp_rectangle(snap_pos)
                return True
            elif self.drawing_mode == 'circle':
                self.draw_temp_circle(snap_pos)
                return True
            elif self.drawing_mode == 'arc':
                if not self.radius_x:
                    self.draw_temp_ellipse(snap_pos)
                    return True
                elif self.start_angle is not None and self.end_angle is None:
                    self.draw_temp_arc(snap_pos)
                    return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if not self.collide_point(*touch.pos):
            return False  # Ignore touches outside the ShapeDrawer area

        if self.selection_mode and self.selected_shape:
            # 図形の移動が完了したときの処理
            if self.total_dx != 0 or self.total_dy != 0:
                action = MoveShapeAction(self.selected_shape, self.total_dx, self.total_dy)
                self.undo_stack.append(action)
                self.redo_stack.clear()
            self.selected_shape = None
            self.last_touch_pos = None
            self.is_dragging_shape = False  # Reset dragging flag
            return True

        if self.rotation_mode and self.selected_shape:
            # 回転が完了したときの処理
            if self.total_rotation_angle != 0:
                if self.rotation_step is not None:
                    final_angle = round(self.total_rotation_angle / self.rotation_step) * self.rotation_step
                else:
                    final_angle = self.total_rotation_angle

                action = RotateShapeAction(self.selected_shape, final_angle, self.rotation_pivot)
                self.undo_stack.append(action)
                self.redo_stack.clear()
            self.selected_shape = None
            self.rotation_pivot = None
            self.rotation_start_angle = None
            self.rotation_mode_detail = None
            return True

        if self.dragging:
            # 図形の描画が完了したときの処理
            if self.snap_mode:
                snap_pos = self.get_snap_point(touch.pos)
            else:
                snap_pos = touch.pos
            if self.drawing_mode == 'line':
                self.end_point = snap_pos
                self.draw_line(self.start_point, self.end_point)
                self.reset()
                return True
            elif self.drawing_mode == 'rectangle':
                self.end_point = snap_pos
                self.draw_rectangle(self.start_point, self.end_point)
                self.reset()
                return True
            elif self.drawing_mode == 'circle':
                self.radius = self.get_distance(self.center_point, snap_pos)
                self.draw_circle(self.center_point, self.radius)
                self.reset()
                return True
            elif self.drawing_mode == 'arc':
                if not self.radius_x:
                    self.radius_x = self.get_distance(self.center_point, snap_pos)
                    self.radius_y = self.radius_x * (1 - self.flattening_rate)
                    self.dragging = True
                    return True
                elif self.start_angle is not None and self.end_angle is None:
                    self.end_angle = self.get_angle_point(self.center_point, snap_pos)
                    self.end_point = self.get_ellipse_point(self.end_angle)
                    self.draw_arc()
                    self.reset()
                    return True
        return super().on_touch_up(touch)

    def move_shape(self, shape, dx, dy):
        # Move the shape by updating positions and redrawing
        shape.move(dx, dy)

    def paste_shape(self, pos):
        # Copy the shape
        new_shape = self.copied_shape.copy()
        # Get the center of the copied shape
        original_center = self.copied_shape.get_center()
        # Compute the offset
        dx = pos[0] - original_center[0]
        dy = pos[1] - original_center[1]
        # Move the new shape
        new_shape.move(dx, dy)
        # Add to canvas and shapes list
        self.shape_instructions.add(new_shape.instructions)
        self.shapes.append(new_shape)
        # アクションをスタックに追加
        action = AddShapeAction(new_shape, self.shape_instructions, self.shapes)
        self.undo_stack.append(action)
        self.redo_stack.clear()
        # 録画中であれば、アクションを録画
        if self.is_recording:
            self.recorded_actions.append(copy.deepcopy(action))

    def draw_point(self, pos):
        size = self.line_width * 2  # 線幅に基づいてポイントサイズを調整
        instr = InstructionGroup()
        instr.add(Color(*self.current_color))
        instr.add(Ellipse(pos=(pos[0] - size / 2, pos[1] - size / 2), size=(size, size)))
        shape = Shape('point', instr, self.current_color, pos=(pos[0] - size / 2, pos[1] - size / 2), size=(size, size))
        self.shape_instructions.add(instr)
        self.shapes.append(shape)
        # 現在のレイヤーに追加
        layer = self.layers[self.current_main_layer][self.current_sub_layer]
        layer['instructions'].add(instr)
        layer['shapes'].append(shape)
        # アクションをスタックに追加
        action = AddShapeAction(shape, self.shape_instructions, self.shapes)
        self.undo_stack.append(action)
        self.redo_stack.clear()
        # 録画中であれば、アクションを録画
        if self.is_recording:
            recorded_action = RecordedAction('draw_point', {
                'pos': pos,
                'color': self.current_color,
                'line_width': self.line_width
            })
            self.recorded_actions.append(recorded_action)

    def draw_line(self, start, end):
        instr = InstructionGroup()
        instr.add(Color(*self.current_color))
        instr.add(Line(points=[start[0], start[1], end[0], end[1]], width=self.line_width))
        shape = Shape('line', instr, self.current_color, start=start, end=end, width=self.line_width)
        self.shape_instructions.add(instr)
        self.shapes.append(shape)
        # 現在のレイヤーに追加
        layer = self.layers[self.current_main_layer][self.current_sub_layer]
        layer['instructions'].add(instr)
        layer['shapes'].append(shape)
        # アクションをスタックに追加
        action = AddShapeAction(shape, self.shape_instructions, self.shapes)
        self.undo_stack.append(action)
        self.redo_stack.clear()
        # 録画中であれば、アクションを録画
        if self.is_recording:
            recorded_action = RecordedAction('draw_line', {
                'start': start,
                'end': end,
                'color': self.current_color,
                'line_width': self.line_width
            })
            self.recorded_actions.append(recorded_action)

    def draw_rectangle(self, start, end):
        instr = InstructionGroup()
        instr.add(Color(*self.current_color))
        pos = (min(start[0], end[0]), min(start[1], end[1]))
        size = (abs(end[0] - start[0]), abs(end[1] - start[1]))
        corners = [
            pos,
            (pos[0] + size[0], pos[1]),
            (pos[0] + size[0], pos[1] + size[1]),
            (pos[0], pos[1] + size[1])
        ]
        if self.fill_mode == 'fill':
            instr.add(Rectangle(pos=pos, size=size))
            fill = True
        else:
            instr.add(Line(points=[*corners[0], *corners[1], *corners[2], *corners[3], *corners[0]],
                        width=self.line_width))
            fill = False
        shape = Shape('rectangle', instr, self.current_color, corners=corners, fill=fill, width=self.line_width)
        self.shape_instructions.add(instr)
        self.shapes.append(shape)
        # 現在のレイヤーに追加
        layer = self.layers[self.current_main_layer][self.current_sub_layer]
        layer['instructions'].add(instr)
        layer['shapes'].append(shape)
        # アクションをスタックに追加
        action = AddShapeAction(shape, self.shape_instructions, self.shapes)
        self.undo_stack.append(action)
        self.redo_stack.clear()
        # 録画中であれば、アクションを録画
        if self.is_recording:
            recorded_action = RecordedAction('draw_rectangle', {
                'start': start,
                'end': end,
                'color': self.current_color,
                'line_width': self.line_width,
                'fill_mode': self.fill_mode
            })
            self.recorded_actions.append(recorded_action)

    def draw_circle(self, center, radius):
        instr = InstructionGroup()
        instr.add(Color(*self.current_color))
        if self.fill_mode == 'fill':
            instr.add(Ellipse(pos=(center[0] - radius, center[1] - radius),
                            size=(radius * 2, radius * 2)))
            fill = True
        else:
            instr.add(Line(circle=(center[0], center[1], radius), width=self.line_width))
            fill = False
        shape = Shape('circle', instr, self.current_color, center=center, radius=radius, fill=fill, width=self.line_width)
        self.shape_instructions.add(instr)
        self.shapes.append(shape)
        # 現在のレイヤーに追加
        layer = self.layers[self.current_main_layer][self.current_sub_layer]
        layer['instructions'].add(instr)
        layer['shapes'].append(shape)
        # アクションをスタックに追加
        action = AddShapeAction(shape, self.shape_instructions, self.shapes)
        self.undo_stack.append(action)
        self.redo_stack.clear()
        # 録画中であれば、アクションを録画
        if self.is_recording:
            recorded_action = RecordedAction('draw_circle', {
                'center': center,
                'radius': radius,
                'color': self.current_color,
                'line_width': self.line_width,
                'fill_mode': self.fill_mode
            })
            self.recorded_actions.append(recorded_action)

    def draw_arc(self):
        adjusted_end_angle = self.adjust_angle(self.start_angle, self.end_angle)
        instr = InstructionGroup()
        instr.add(Color(*self.current_color))
        if self.fill_mode == 'fill':
            self.draw_filled_arc_segment(self.start_angle, adjusted_end_angle, instr)
            fill = True
        else:
            self.draw_arc_segment(self.start_angle, adjusted_end_angle, instr)
            fill = False
        # 線とポイントを描画
        instr.add(Color(0, 0, 1, 1))
        instr.add(Line(points=[self.center_point[0], self.center_point[1],
                            self.start_point[0], self.start_point[1]], width=1))
        instr.add(Line(points=[self.center_point[0], self.center_point[1],
                            self.end_point[0], self.end_point[1]], width=1))
        # 開始点と終了点
        instr.add(Color(1, 0, 0, 1))
        instr.add(Line(circle=(self.start_point[0], self.start_point[1], 5), width=2))
        instr.add(Line(circle=(self.end_point[0], self.end_point[1], 5), width=2))
        shape = Shape('arc', instr, self.current_color,
                    center=self.center_point,
                    radius_x=self.radius_x,
                    radius_y=self.radius_y,
                    start_angle=self.start_angle,
                    end_angle=adjusted_end_angle,
                    start_point=self.start_point,
                    end_point=self.end_point,
                    width=self.line_width,
                    fill=fill)
        self.shape_instructions.add(instr)
        self.shapes.append(shape)
        # 現在のレイヤーに追加
        layer = self.layers[self.current_main_layer][self.current_sub_layer]
        layer['instructions'].add(instr)
        layer['shapes'].append(shape)
        # アクションをスタックに追加
        action = AddShapeAction(shape, self.shape_instructions, self.shapes)
        self.undo_stack.append(action)
        self.redo_stack.clear()
        # 録画中であれば、アクションを録画
        if self.is_recording:
            recorded_action = RecordedAction('draw_arc', {
                'center_point': self.center_point,
                'radius_x': self.radius_x,
                'radius_y': self.radius_y,
                'start_angle': self.start_angle,
                'end_angle': adjusted_end_angle,
                'start_point': self.start_point,
                'end_point': self.end_point,
                'color': self.current_color,
                'line_width': self.line_width,
                'fill_mode': self.fill_mode
            })
            self.recorded_actions.append(recorded_action)

    def draw_arc_segment(self, start_angle, end_angle, instr):
        step = 1  # Adjust precision
        points = []
        angle = start_angle
        if end_angle < start_angle:
            end_angle += 360
        while angle <= end_angle:
            rad = radians(angle)
            x = self.center_point[0] + self.radius_x * cos(rad)
            y = self.center_point[1] + self.radius_y * sin(rad)
            points.extend([x, y])
            angle += step
        instr.add(Line(points=points, width=self.line_width))

    def draw_filled_arc_segment(self, start_angle, end_angle, instr):
        step = 5  # Adjust precision
        vertices = [self.center_point[0], self.center_point[1], 0, 0]
        indices = []
        angle = start_angle
        if end_angle < start_angle:
            end_angle += 360
        while angle <= end_angle:
            rad = radians(angle)
            x = self.center_point[0] + self.radius_x * cos(rad)
            y = self.center_point[1] + self.radius_y * sin(rad)
            vertices.extend([x, y, 0, 0])
            angle += step
        num_vertices = len(vertices) // 4
        for i in range(1, num_vertices - 1):
            indices.extend([0, i, i + 1])
        instr.add(Mesh(vertices=vertices, indices=indices, mode='triangles'))

    def draw_temp_line(self, pos):
        self.canvas.remove_group('temp')
        with self.canvas:
            Color(0, 1, 0, 0.5, group='temp')
            Line(points=[self.start_point[0], self.start_point[1],
                         pos[0], pos[1]], width=self.line_width, group='temp')

    def draw_temp_rectangle(self, pos):
        self.canvas.remove_group('temp')
        with self.canvas:
            Color(0, 0, 1, 0.5, group='temp')
            if self.fill_mode == 'fill':
                Rectangle(pos=(min(self.start_point[0], pos[0]), min(self.start_point[1], pos[1])),
                          size=(abs(pos[0] - self.start_point[0]), abs(pos[1] - self.start_point[1])),
                          group='temp')
            else:
                Line(rectangle=(min(self.start_point[0], pos[0]), min(self.start_point[1], pos[1]),
                                abs(pos[0] - self.start_point[0]), abs(pos[1] - self.start_point[1])),
                     width=self.line_width, group='temp')

    def draw_temp_circle(self, pos):
        self.canvas.remove_group('temp')
        radius = self.get_distance(self.center_point, pos)
        with self.canvas:
            Color(1, 0, 1, 0.5, group='temp')
            if self.fill_mode == 'fill':
                Ellipse(pos=(self.center_point[0] - radius, self.center_point[1] - radius),
                        size=(radius * 2, radius * 2), group='temp')
            else:
                Line(circle=(self.center_point[0], self.center_point[1], radius),
                     width=self.line_width, group='temp')

    def draw_temp_ellipse(self, pos):
        self.canvas.remove_group('temp')
        rx = self.get_distance(self.center_point, pos)
        ry = rx * (1 - self.flattening_rate)
        with self.canvas:
            Color(1, 0, 0, 0.5, group='temp')
            if self.fill_mode == 'fill':
                self.draw_filled_ellipse_temp(self.center_point, rx, ry, group='temp')
            else:
                self.draw_ellipse_temp(self.center_point, rx, ry, group='temp')
            Line(points=[self.center_point[0], self.center_point[1],
                         pos[0], pos[1]], width=1, group='temp')

    def draw_ellipse_temp(self, center, rx, ry, group=None):
        step = 1  # Adjust precision
        points = []
        for angle in range(0, 360 + step, step):
            rad = radians(angle)
            x = center[0] + rx * sin(rad)
            y = center[1] + ry * cos(rad)
            points.extend([x, y])
        Line(points=points, width=self.line_width, group=group)

    def draw_filled_ellipse_temp(self, center, rx, ry, group=None):
        step = 5  # Adjust precision
        vertices = []
        indices = []
        angle = 0
        while angle <= 360:
            rad = radians(angle)
            x = center[0] + rx * sin(rad)
            y = center[1] + ry * cos(rad)
            vertices.extend([x, y, 0, 0])
            angle += step
        num_vertices = len(vertices) // 4
        for i in range(1, num_vertices - 1):
            indices.extend([0, i, i + 1])
        Mesh(vertices=vertices, indices=indices, mode='triangles', group=group)

    def draw_temp_arc(self, pos):
        self.canvas.remove_group('temp')
        current_angle = self.get_angle_point(self.center_point, pos)
        adjusted_end_angle = self.adjust_angle(self.start_angle, current_angle)
        with self.canvas:
            # Temporary arc
            Color(0, 0, 1, 0.5, group='temp')
            if self.fill_mode == 'fill':
                self.draw_filled_arc_segment_temp(self.start_angle, adjusted_end_angle, group='temp')
            else:
                self.draw_arc_segment_temp(self.start_angle, adjusted_end_angle, group='temp')
            # Lines from center to start and current position
            Color(1, 0, 0, 0.5, group='temp')
            Line(points=[self.center_point[0], self.center_point[1],
                         self.start_point[0], self.start_point[1]], width=1, group='temp')
            Line(points=[self.center_point[0], self.center_point[1],
                         pos[0], pos[1]], width=1, group='temp')

    def draw_arc_segment_temp(self, start_angle, end_angle, group=None):
        step = 1  # Adjust precision
        points = []
        angle = start_angle
        if end_angle < start_angle:
            end_angle += 360
        while angle <= end_angle:
            rad = radians(angle)
            x = self.center_point[0] + self.radius_x * cos(rad)
            y = self.center_point[1] + self.radius_y * sin(rad)
            points.extend([x, y])
            angle += step
        Line(points=points, width=self.line_width, group=group)

    def draw_filled_arc_segment_temp(self, start_angle, end_angle, group=None):
        step = 5  # Adjust precision
        vertices = [self.center_point[0], self.center_point[1], 0, 0]
        indices = []
        angle = start_angle
        while angle <= end_angle:
            rad = radians(angle)
            x = self.center_point[0] + self.radius_x * sin(rad)
            y = self.center_point[1] + self.radius_y * cos(rad)
            vertices.extend([x, y, 0, 0])
            angle += step
        num_vertices = len(vertices) // 4
        for i in range(1, num_vertices - 1):
            indices.extend([0, i, i + 1])
        Mesh(vertices=vertices, indices=indices, mode='triangles', group=group)

    def adjust_angle(self, start_angle, end_angle):
        adjusted_end_angle = end_angle
        if adjusted_end_angle < start_angle:
            adjusted_end_angle += 360
        return adjusted_end_angle

    def get_distance(self, p1, p2):
        return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def get_angle_point(self, center, pos):
        dx = pos[0] - center[0]
        dy = pos[1] - center[1]
        angle = degrees(atan2(dy, dx))
        if angle < 0:
            angle += 360
        return angle
    
    def rotate_shape(self, shape, angle, pivot):
        shape.rotate(angle, pivot)

    def get_angle(self, pivot, point):
        dx = point[0] - pivot[0]
        dy = point[1] - pivot[1]
        angle = degrees(atan2(dy, dx))
        return angle

    def get_ellipse_point(self, angle):
        angle_rad = radians(angle)
        x = self.center_point[0] + self.radius_x * cos(angle_rad)
        y = self.center_point[1] + self.radius_y * sin(angle_rad)
        return (x, y)

    def reset(self):
        self.center_point = None
        self.start_point = None
        self.end_point = None
        self.radius_x = None
        self.radius_y = None
        self.start_angle = None
        self.end_angle = None
        self.dragging = False
        self.canvas.remove_group('temp')

    def undo(self):
        if self.undo_stack:
            action = self.undo_stack.pop()
            action.undo()
            self.redo_stack.append(action)
            if self.is_recording:
                recorded_action = RecordedAction('undo', {})
                self.recorded_actions.append(recorded_action)

    def redo(self):
        if self.redo_stack:
            action = self.redo_stack.pop()
            action.redo()
            self.undo_stack.append(action)
            # 録画中であれば、アクションを録画
            if self.is_recording:
                recorded_action = RecordedAction('redo', {})
                self.recorded_actions.append(recorded_action)

    def start_recording(self):
        self.is_recording = True
        self.recorded_actions.clear()

    def stop_recording(self):
        self.is_recording = False

    def replay_actions(self):
        if not self.recorded_actions:
            return
        self.clear_canvas()
        self.replay_index = 0
        self.schedule_replay()

    def schedule_replay(self, dt=0):
        if self.replay_index < len(self.recorded_actions):
            recorded_action = self.recorded_actions[self.replay_index]
            self.execute_recorded_action(recorded_action)
            self.replay_index += 1
            # アクション間の時間間隔（0.5秒）を設定
            Clock.schedule_once(self.schedule_replay, 0.5)

    def execute_recorded_action(self, recorded_action):
        if recorded_action.action_type == 'draw_point':
            params = recorded_action.params
            self.current_color = params['color']
            self.line_width = params['line_width']
            self.draw_point(params['pos'])
        elif recorded_action.action_type == 'draw_line':
            params = recorded_action.params
            self.current_color = params['color']
            self.line_width = params['line_width']
            self.draw_line(params['start'], params['end'])
        elif recorded_action.action_type == 'draw_rectangle':
            params = recorded_action.params
            self.current_color = params['color']
            self.line_width = params['line_width']
            self.fill_mode = params['fill_mode']
            self.draw_rectangle(params['start'], params['end'])
        elif recorded_action.action_type == 'draw_circle':
            params = recorded_action.params
            self.current_color = params['color']
            self.line_width = params['line_width']
            self.fill_mode = params['fill_mode']
            self.draw_circle(params['center'], params['radius'])
        elif recorded_action.action_type == 'draw_arc':
            params = recorded_action.params
            self.current_color = params['color']
            self.line_width = params['line_width']
            self.fill_mode = params['fill_mode']
            # 円弧の描画に必要なパラメータを設定
            self.center_point = params['center_point']
            self.radius_x = params['radius_x']
            self.radius_y = params['radius_y']
            self.start_angle = params['start_angle']
            self.end_angle = params['end_angle']
            self.start_point = params['start_point']
            self.end_point = params['end_point']
            self.draw_arc()
        if recorded_action.action_type == 'redo':
            self.redo()
            self.reset()

    def initialize_layer(self, main_layer, sub_layer):
        if main_layer not in self.layers:
            self.layers[main_layer] = {}
        if sub_layer not in self.layers[main_layer]:
            self.layers[main_layer][sub_layer] = {
                'shapes': [],
                'instructions': InstructionGroup(),
                'visible': True
            }
            self.canvas.add(self.layers[main_layer][sub_layer]['instructions'])

    def initialize_layers(self, num_main_layers=20, num_sub_layers=20):
        self.layers = {}
        for main_layer in range(num_main_layers):
            self.layers[main_layer] = {}
            for sub_layer in range(num_sub_layers):
                self.layers[main_layer][sub_layer] = {
                    'shapes': [],
                    'instructions': InstructionGroup(),
                    'visible': True
                }
                self.canvas.add(self.layers[main_layer][sub_layer]['instructions'])

    def switch_layer(self, main_layer=None, sub_layer=None):
        # 指定されたメインレイヤーおよびサブレイヤーが存在するかをチェック
        if main_layer is not None and main_layer not in self.layers:
            print(f"Error: Main layer {main_layer} does not exist.")
            return
        if sub_layer is not None and sub_layer not in self.layers.get(main_layer, {}):
            print(f"Error: Sub layer {sub_layer} in main layer {main_layer} does not exist.")
            return

        if main_layer is not None:
            self.current_main_layer = main_layer
        if sub_layer is not None:
            self.current_sub_layer = sub_layer

        # 更新された現在のレイヤーを表示
        for m_layer, sub_layers in self.layers.items():
            for s_layer, layer_info in sub_layers.items():
                if m_layer == self.current_main_layer and s_layer == self.current_sub_layer:
                    self.canvas.add(layer_info['instructions'])
                else:
                    self.canvas.remove(layer_info['instructions'])

class ShapeApp(App):
    def build(self):
        # ルートレイアウトを水平方向のBoxLayoutに設定
        root = BoxLayout(orientation='horizontal')
        self.drawer = ShapeDrawer()

        # メインパネルとレイヤーパネルを作成
        main_panel = BoxLayout(orientation='vertical', size_hint=(0.9, 1))
        layer_panel = BoxLayout(orientation='vertical', size_hint=(0.1, 1))

        # メニューバーの作成
        menu_bar = BoxLayout(size_hint=(1, None), height=30, orientation='horizontal')

        # ファイルメニューのドロップダウンを作成
        file_dropdown = DropDown()

        # ファイルメニューの項目を追加
        file_items = [
            '新規作成', '開く', '上書き保存', '名前を付けて保存',
            '印刷', 'プリンタ設定', '---',
            '最近のファイル', '---',
            '再起動', '保存して再起動', '閉じる'
        ]

        for item in file_items:
            if item == '---':
                # 区切り線としてラベルを追加
                separator = Label(text='----------------', size_hint_y=None, height=20)
                file_dropdown.add_widget(separator)
            elif item == '最近のファイル':
                # 最近のファイルのサブメニューを作成
                recent_files_dropdown = DropDown()
                self.recent_files = self.load_recent_files()  # 最近のファイルをロード

                if self.recent_files:
                    for filename in self.recent_files:
                        btn = Button(text=filename, size_hint_y=None, height=30)
                        btn.bind(on_release=lambda btn: recent_files_dropdown.select(btn.text))
                        recent_files_dropdown.add_widget(btn)
                else:
                    btn = Button(text='最近のファイルはありません', size_hint_y=None, height=30)
                    btn.disabled = True
                    recent_files_dropdown.add_widget(btn)

                # 「最近のファイル」ボタンを作成し、サブメニューをバインド
                recent_files_btn = Button(text='最近のファイル', size_hint_y=None, height=30)
                recent_files_btn.bind(on_release=recent_files_dropdown.open)
                recent_files_dropdown.bind(on_select=lambda instance, x: self.on_recent_file_select(x))
                file_dropdown.add_widget(recent_files_btn)
            else:
                btn = Button(text=item, size_hint_y=None, height=30)
                btn.bind(on_release=lambda btn: file_dropdown.select(btn.text))
                file_dropdown.add_widget(btn)

        # ファイルボタンを作成し、ドロップダウンをバインド
        file_btn = Button(text='ファイル', size_hint=(None, 1), width=80)
        file_btn.bind(on_release=file_dropdown.open)
        file_dropdown.bind(on_select=lambda instance, x: self.on_file_menu_select(x))
        menu_bar.add_widget(file_btn)

        # メニュー項目の追加
        menu_items = ['編集', '表示', '作図', '設定', 'レイヤー', '開発', '操作', 'その他', 'ヘルプ']
        for item in menu_items:
            btn = Button(text=item, size_hint=(None, 1), width=80)
            btn.bind(on_press=self.on_menu_button)
            menu_bar.add_widget(btn)

        # コントロールパネル（描画モードとクリアボタン）
        control_panel = BoxLayout(size_hint=(1, None), height=50, orientation='horizontal')

        # 描画モードボタン
        modes = ['点', '線', '矩形', '円', '円弧', '選択', '回転']
        for mode_name in modes:
            btn = Button(text=mode_name, size_hint=(0.1, 1))
            btn.bind(on_press=self.on_mode_button)
            control_panel.add_widget(btn)

        # 戻るボタン
        back_button = Button(text='戻る', size_hint=(0.1, 1))
        back_button.bind(on_press=self.on_back_button)
        control_panel.add_widget(back_button)

        # 進むボタン
        forward_button = Button(text='進む', size_hint=(0.1, 1))
        forward_button.bind(on_press=self.on_forward_button)
        control_panel.add_widget(forward_button)

        # クリアボタン
        clear_button = Button(text='クリア', size_hint=(0.1, 1))
        clear_button.bind(on_press=self.on_clear_button)
        control_panel.add_widget(clear_button)

        # スナップモードトグルボタン
        self.snap_toggle = ToggleButton(text='スナップOFF', size_hint=(0.1, 1))
        self.snap_toggle.bind(on_press=self.on_snap_toggle)
        control_panel.add_widget(self.snap_toggle)

        # 下部のコントロールパネル（線幅、扁平率、塗りモード）
        line_width_panel = BoxLayout(size_hint=(1, None), height=40, orientation='horizontal')

        # 線幅ラベル
        line_width_label = Label(text='線幅:', size_hint=(0.1, 1))
        line_width_panel.add_widget(line_width_label)

        # 線幅スライダー
        line_width_slider = Slider(min=1, max=20, value=1, step=1, size_hint=(0.5, 1))
        line_width_slider.bind(value=self.on_line_width_slider)
        line_width_panel.add_widget(line_width_slider)

        # 線幅入力
        line_width_input = TextInput(text='1', multiline=False, size_hint=(0.1, 1))
        line_width_input.bind(text=self.on_line_width_input)
        line_width_panel.add_widget(line_width_input)

        # 線幅スピナー
        line_width_spinner = Spinner(
            text='1',
            values=[str(i) for i in range(1, 21)],
            size_hint=(0.1, 1)
        )
        line_width_spinner.bind(text=self.on_line_width_spinner)
        line_width_panel.add_widget(line_width_spinner)

        # 扁平率入力
        flattening_input = TextInput(text='0.0', multiline=False, size_hint=(0.1, 1))
        flattening_input.bind(text=self.on_flattening_input)
        line_width_panel.add_widget(flattening_input)

        # 扁平率スピナー
        flattening_spinner = Spinner(
            text='扁平率',
            values=('0.0', '0.1', '0.2', '0.3', '0.4', '0.5'),
            size_hint=(0.1, 1)
        )
        flattening_spinner.bind(text=self.on_flattening_spinner)
        line_width_panel.add_widget(flattening_spinner)

        # 塗りモードトグルボタン
        self.fill_toggle = ToggleButton(text='塗り', size_hint=(0.1, 1))
        self.fill_toggle.bind(on_press=self.on_fill_toggle)
        line_width_panel.add_widget(self.fill_toggle)

        # スナップモードトグルボタンを追加
        self.snap_toggle = ToggleButton(text='スナップOFF', size_hint=(0.1, 1))
        self.snap_toggle.bind(on_press=self.on_snap_toggle)
        line_width_panel.add_widget(self.snap_toggle)

        # 色コントロールパネル
        color_panel = BoxLayout(size_hint=(1, None), height=40, orientation='horizontal')

        # 色ラベル
        color_label = Label(text='色:', size_hint=(0.1, 1))
        color_panel.add_widget(color_label)

        # 色スライダー
        color_slider = Slider(min=0, max=11, value=0, step=1, size_hint=(0.5, 1))
        color_slider.bind(value=self.on_color_slider)
        color_panel.add_widget(color_slider)

        # 色入力
        color_input = TextInput(text='0', multiline=False, size_hint=(0.1, 1))
        color_input.bind(text=self.on_color_input)
        color_panel.add_widget(color_input)

        # 色スピナー
        color_spinner = Spinner(
            text='0',
            values=[str(i) for i in range(12)],
            size_hint=(0.1, 1)
        )
        color_spinner.bind(text=self.on_color_spinner)
        color_panel.add_widget(color_spinner)

        # 色見本表示（Widgetを使用）
        color_sample = Widget(size_hint=(0.1, 1))
        color_panel.add_widget(color_sample)

        # カラーモードスピナー
        color_mode_spinner = Spinner(
            text='RGB',
            values=('RGB', 'CMYK', 'グレースケール'),
            size_hint=(0.1, 1)
        )
        color_mode_spinner.bind(text=self.on_color_mode_spinner)
        color_panel.add_widget(color_mode_spinner)

        # 角度入力フォームを追加
        angle_input = TextInput(text='', multiline=False, size_hint=(0.1, 1))
        angle_input.bind(text=self.on_angle_input)
        color_panel.add_widget(angle_input)

        # 回転ステップスピナーを追加
        rotation_step_spinner = Spinner(
            text='フリー',
            values=('フリー', '15度', '30度', '45度', '90度'),
            size_hint=(0.1, 1)
        )
        rotation_step_spinner.bind(text=self.on_rotation_step_spinner)
        color_panel.add_widget(rotation_step_spinner)

        # ウィジェットへの参照を保存
        self.line_width_slider = line_width_slider
        self.line_width_input = line_width_input
        self.line_width_spinner = line_width_spinner
        self.color_slider = color_slider
        self.color_input = color_input
        self.color_spinner = color_spinner
        self.color_sample = color_sample
        self.color_mode_spinner = color_mode_spinner

        # 録画制御パネル
        record_panel = BoxLayout(size_hint=(1, None), height=40, orientation='horizontal')

        # 録画開始ボタン
        self.record_button = ToggleButton(text='録画開始', size_hint=(0.1, 1))
        self.record_button.bind(on_press=self.on_record_toggle)
        record_panel.add_widget(self.record_button)

        # 再生ボタン
        replay_button = Button(text='再生', size_hint=(0.1, 1))
        replay_button.bind(on_press=self.on_replay_button)
        record_panel.add_widget(replay_button)

        # 色設定を初期化
        self.color_value = 0  # 0から11まで
        self.color_mode = 'RGB'  # 'RGB', 'CMYK', 'グレースケール'

        # RGBモードの色を定義
        self.colors_rgb = [
            (0, 0, 0),       # 0 黒
            (1, 0, 0),       # 1 赤
            (0, 1, 0),       # 2 緑
            (0, 0, 1),       # 3 青
            (1, 1, 0),       # 4 黄色
            (0, 1, 1),       # 5 シアン
            (1, 0, 1),       # 6 マゼンタ
            (1, 1, 1),       # 7 白
            (1, 0.5, 0),     # 8 オレンジ
            (0.5, 0, 0.5),   # 9 紫
            (0.6, 0.3, 0),   # 10 茶色
            (0.5, 0.5, 0.5)  # 11 グレー
        ]

        # CMYKの値を定義
        self.colors_cmyk_values = [
            (0, 0, 0, 1),       # 0 黒
            (1, 0, 0, 0),       # 1 シアン
            (0, 1, 0, 0),       # 2 マゼンタ
            (0, 0, 1, 0),       # 3 イエロー
            (1, 1, 0, 0),       # 4 ブルー
            (0, 1, 1, 0),       # 5 レッド
            (1, 0, 1, 0),       # 6 グリーン
            (0, 0, 0, 0),       # 7 白
            (0, 0.5, 1, 0),     # 8 オリーブ
            (0.5, 1, 0, 0),     # 9 パープル
            (1, 0.5, 0, 0),     # 10 ティール
            (0, 0, 0, 0.5)      # 11 グレー
        ]

        # 既存のウィジェットをメインパネルに追加
        main_panel.add_widget(menu_bar)
        main_panel.add_widget(control_panel)
        main_panel.add_widget(line_width_panel)
        main_panel.add_widget(color_panel)
        main_panel.add_widget(record_panel)
        main_panel.add_widget(self.drawer)

        # レイヤーパネルを構築
        layer_grid = GridLayout(cols=2, rows=10, size_hint=(1, None), height=400)  # 20個のレイヤーボタンを配置
        self.layer_buttons = []
        for i in range(20):  # 20個のメインレイヤーボタンを作成
            btn = ToggleButton(text=f' {i+1}', size_hint=(None, None), width=40, height=40)
            btn.bind(on_press=self.on_layer_toggle)
            self.layer_buttons.append(btn)
            layer_grid.add_widget(btn)
        layer_panel.add_widget(layer_grid)

        # レイヤー切換えボタンを追加
        self.layer_switch_button = ToggleButton(text='メイン', size_hint=(None, None), width=80, height=40)
        self.layer_switch_button.bind(on_press=self.on_layer_switch_toggle)
        layer_panel.add_widget(self.layer_switch_button)

        # パネルをルートに追加
        root.add_widget(main_panel)
        root.add_widget(layer_panel)

        # 初期設定
        self.is_main_layer_mode = True
        self.current_main_layer = 0
        self.current_sub_layer = 0
        self.layer_buttons[self.current_main_layer].state = 'down'

        # 初期線幅設定
        self.line_width = 1

        # 初期色を設定
        self.drawer.set_current_color(self.get_current_color())
        self.update_color_sample()

        return root

    def build_ui(self):
        layer_selector = Spinner(
            text='Select Layer',
            values=[f"Main {i+1}" for i in range(num_main_layers)],
            size_hint=(None, None),
            size=(100, 44),
            pos=(10, 10)
        )
        layer_selector.bind(text=self.on_layer_selected)
        return layer_selector

    def on_layer_selected(self, spinner, text):
        main_layer_index = int(text.split()[1]) - 1
        self.switch_layer(main_layer=main_layer_index)
    
    def on_layer_toggle(self, instance):
        index = self.layer_buttons.index(instance)
        if self.is_main_layer_mode:
            self.current_main_layer = index
            self.drawer.switch_layer(main_layer=self.current_main_layer)
        else:
            self.current_sub_layer = index
            self.drawer.switch_layer(sub_layer=self.current_sub_layer)
        # 他のボタンの状態をリセット
        for btn in self.layer_buttons:
            if btn != instance:
                btn.state = 'normal'
        instance.state = 'down'
        # レイヤーを切換え
        self.drawer.switch_layer(
            main_layer=self.current_main_layer if self.is_main_layer_mode else None,
            sub_layer=None if self.is_main_layer_mode else self.current_sub_layer
        )

    def on_layer_switch_toggle(self, instance):
        self.is_main_layer_mode = not self.is_main_layer_mode
        if self.is_main_layer_mode:
            instance.text = 'メイン'
        else:
            instance.text = 'サブ'
        # ボタンの状態をリセット
        for btn in self.layer_buttons:
            btn.state = 'normal'
        # 現在のレイヤーのボタンを選択状態に
        index = self.current_main_layer if self.is_main_layer_mode else self.current_sub_layer
        self.layer_buttons[index].state = 'down'

    def on_record_toggle(self, instance):
        if instance.state == 'down':
            self.drawer.start_recording()
            instance.text = '録画中...'
        else:
            self.drawer.stop_recording()
            instance.text = '録画開始'

    def initialize_layer(self, main_layer, sub_layer):
        if main_layer not in self.layers:
            self.layers[main_layer] = {}
        for sub in range(5):  # 各メインレイヤーに5個のサブレイヤーを作成
            if sub not in self.layers[main_layer]:
                self.layers[main_layer][sub] = {
                    'shapes': [],
                    'instructions': InstructionGroup(),
                    'visible': True
                }
                self.canvas.add(self.layers[main_layer][sub]['instructions'])

    def switch_layer(self, main_layer=None, sub_layer=None):
        # 現在のレイヤーの表示を制御
        for sub, layer_info in self.layers[self.current_main_layer].items():
            if sub == self.current_sub_layer:
                if layer_info['visible']:
                    self.canvas.add(layer_info['instructions'])
                else:
                    self.canvas.remove(layer_info['instructions'])
            else:
                self.canvas.remove(layer_info['instructions'])
        if main_layer is not None:
            self.current_main_layer = main_layer
        if sub_layer is not None:
            self.current_sub_layer = sub_layer

    def on_replay_button(self, instance):
        self.drawer.stop_recording()  # 録画を停止
        self.drawer.replay_actions()
    
    def load_recent_files(self):
        # 過去に編集したファイル名のリストを取得（例として固定のリストを返す）
        # 実際にはファイルを保存・開く際に更新する必要があります
        return [
            'drawing1.kv', 'drawing2.kv', 'drawing3.kv',
            'drawing4.kv', 'drawing5.kv', 'drawing6.kv',
            'drawing7.kv', 'drawing8.kv', 'drawing9.kv',
            'drawing10.kv'
        ]

    def on_file_menu_select(self, selection):
        # ファイルメニューの項目が選択されたときの処理
        if selection == '新規作成':
            self.new_file()
        elif selection == '開く':
            self.open_file()
        elif selection == '上書き保存':
            self.save_file()
        elif selection == '名前を付けて保存':
            self.save_file_as()
        elif selection == '印刷':
            self.print_file()
        elif selection == 'プリンタ設定':
            self.printer_settings()
        elif selection == '再起動':
            self.restart_app()
        elif selection == '保存して再起動':
            self.save_and_restart_app()
        elif selection == '閉じる':
            self.close_app()

    def on_recent_file_select(self, filename):
        # 最近のファイルが選択されたときの処理
        self.load_file(filename)
    
    def on_menu_button(self, instance):
        # メニューボタンが押されたときの処理
        if instance.text == 'ファイル':
            # ファイルメニューの処理を実装
            pass
        elif instance.text == '編集':
            # 編集メニューの処理を実装
            pass
        elif instance.text == '表示':
            # 表示メニューの処理を実装
            pass
        elif instance.text == '作図':
            # 表示メニューの処理を実装
            pass
        elif instance.text == '設定':
            # 表示メニューの処理を実装
            pass
        elif instance.text == 'レイヤー':
            # 表示メニューの処理を実装
            pass
        elif instance.text == '開発':
            # 表示メニューの処理を実装
            pass
        elif instance.text == '操作':
            # 表示メニューの処理を実装
            pass
        elif instance.text == 'その他':
            # 表示メニューの処理を実装
            pass
        elif instance.text == 'ヘルプ':
            # ヘルプメニューの処理を実装
            pass
    
    def on_angle_input(self, instance, value):
        self.drawer.set_rotation_angle(value)

    def on_rotation_step_spinner(self, spinner, text):
        self.drawer.set_rotation_step(text)

    def on_mode_button(self, instance):
        mode_dict = {'点': 'point', '線': 'line', '矩形': 'rectangle',
                    '円': 'circle', '円弧': 'arc', '選択': 'select', '回転': 'rotate'}
        mode = mode_dict.get(instance.text, 'point')
        self.drawer.set_drawing_mode(mode)

    def on_clear_button(self, instance):
        self.drawer.clear_canvas()

    def on_flattening_input(self, instance, value):
        self.drawer.set_flattening_rate(value)

    def on_flattening_spinner(self, spinner, text):
        self.drawer.set_flattening_rate(text)

    def on_fill_toggle(self, instance):
        if instance.state == 'down':
            self.drawer.set_fill_mode('fill')
            instance.text = '線'
        else:
            self.drawer.set_fill_mode('stroke')
            instance.text = '塗り'

    def on_snap_toggle(self, instance):
        if instance.state == 'down':
            self.drawer.set_snap_mode(True)
            instance.text = 'スナップON'
        else:
            self.drawer.set_snap_mode(False)
            instance.text = 'スナップOFF'

    def on_line_width_slider(self, instance, value):
        self.line_width = int(value)
        self.line_width_input.text = str(self.line_width)
        self.line_width_spinner.text = str(self.line_width)
        self.drawer.set_line_width(self.line_width)

    def on_line_width_input(self, instance, value):
        try:
            val = int(value)
            if 1 <= val <= 20:
                self.line_width = val
                self.line_width_slider.value = val
                self.line_width_spinner.text = str(val)
                self.drawer.set_line_width(self.line_width)
            else:
                instance.text = str(self.line_width)
        except ValueError:
            instance.text = str(self.line_width)

    def on_line_width_spinner(self, instance, text):
        val = int(text)
        self.line_width = val
        self.line_width_slider.value = val
        self.line_width_input.text = str(val)
        self.drawer.set_line_width(self.line_width)

    def on_color_slider(self, instance, value):
        self.color_value = int(value)
        self.color_input.text = str(self.color_value)
        self.color_spinner.text = str(self.color_value)
        self.update_color_sample()
        self.drawer.set_current_color(self.get_current_color())

    def on_color_input(self, instance, value):
        try:
            val = int(value)
            if 0 <= val <= 11:
                self.color_value = val
                self.color_slider.value = val
                self.color_spinner.text = str(val)
                self.update_color_sample()
                self.drawer.set_current_color(self.get_current_color())
            else:
                instance.text = str(self.color_value)
        except ValueError:
            instance.text = str(self.color_value)

    def on_color_spinner(self, spinner, text):
        val = int(text)
        self.color_value = val
        self.color_slider.value = val
        self.color_input.text = str(val)
        self.update_color_sample()
        self.drawer.set_current_color(self.get_current_color())

    def on_color_mode_spinner(self, spinner, text):
        self.color_mode = text
        self.update_color_sample()
        self.drawer.set_current_color(self.get_current_color())

    def update_color_sample(self):
        color = self.get_current_color()
        # 色見本の背景色を更新
        self.color_sample.canvas.before.clear()
        with self.color_sample.canvas.before:
            Color(*color)
            Rectangle(pos=self.color_sample.pos, size=self.color_sample.size)

    def get_current_color(self):
        if self.color_mode == 'RGB':
            color = self.colors_rgb[self.color_value]
            return color + (1,)
        elif self.color_mode == 'CMYK':
            cmyk = self.colors_cmyk_values[self.color_value]
            rgb = self.cmyk_to_rgb(*cmyk)
            return rgb + (1,)
        elif self.color_mode == 'グレースケール':
            gray = self.color_value / 11.0
            return (gray, gray, gray, 1)
        else:
            return (0, 0, 0, 1)

    def cmyk_to_rgb(self, c, m, y, k):
        r = (1 - c) * (1 - k)
        g = (1 - m) * (1 - k)
        b = (1 - y) * (1 - k)
        return (r, g, b)

    def on_back_button(self, instance):
        self.drawer.undo()

    def on_forward_button(self, instance):
        self.drawer.redo()

if __name__ == '__main__':
    ShapeApp().run()