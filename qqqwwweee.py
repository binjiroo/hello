from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import (Color, Line, Rectangle, Ellipse, Rotate,
                           PushMatrix, PopMatrix, Translate, Mesh)
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
import math

def distance_point_to_segment(px, py, x1, y1, x2, y2):
    seg_len2 = (x2 - x1)**2 + (y2 - y1)**2
    if seg_len2 == 0:
        return math.hypot(px - x1, py - y1), (x1, y1)  # 点と同じ場合
    t = ((px - x1)*(x2 - x1) + (py - y1)*(y2 - y1))/seg_len2
    if t < 0:
        return math.hypot(px - x1, py - y1), (x1, y1)
    elif t > 1:
        return math.hypot(px - x2, py - y2), (x2, y2)
    else:
        projx = x1 + t*(x2 - x1)
        projy = y1 + t*(y2 - y1)
        return math.hypot(px - projx, py - projy), (projx, projy)

def polygon_area(xs, ys):
    """ポリゴンの面積（符号付き）を求める簡易的な関数。"""
    n = len(xs)
    area = 0
    for i in range(n):
        j = (i+1) % n
        area += xs[i]*ys[j] - xs[j]*ys[i]
    return abs(area)/2

class Shape:
    def __init__(
            self, shape_type='point',
            points=None,
            color=(1,1,1,1),
            line_width=2,
            border_mode=False,
            angle=0.0,
            offset_x=0.0,
            offset_y=0.0
        ):
        self.shape_type = shape_type
        self.color = color
        self.line_width = line_width
        self.border_mode = border_mode

        # 回転関連
        self.angle = angle
        self.pivot_x = 0.0
        self.pivot_y = 0.0

        # 図形の移動用
        self.offset_x = offset_x
        self.offset_y = offset_y

        if points is None:
            points = []
        self.points = points

        self.selected = False

    def draw(self):
        Color(*self.color)
        PushMatrix()
        Translate(self.offset_x, self.offset_y)
        Rotate(angle=self.angle, origin=(self.pivot_x, self.pivot_y))

        if self.shape_type == 'polygon':
            n = len(self.points)//2
            if n >= 3:
                if self.border_mode:
                    Line(points=self.points + self.points[:2],
                         width=self.line_width, close=True)
                else:
                    vertices = []
                    for i in range(n):
                        x = self.points[2*i]
                        y = self.points[2*i+1]
                        vertices += [x, y, 0, 0]
                    indices = []
                    for i in range(1, n-1):
                        indices += [0, i, i+1]
                    Mesh(vertices=vertices, indices=indices, mode='triangles')

        elif self.shape_type == 'freeline':
            if len(self.points) >= 2:
                Line(points=self.points, width=self.line_width)

        elif self.shape_type == 'line':
            if len(self.points) >= 4:
                Line(points=self.points, width=self.line_width)

        elif self.shape_type == 'rectangle':
            if len(self.points) >= 4:
                x1, y1, x2, y2 = self.points[:4]
                rx = min(x1, x2)
                ry = min(y1, y2)
                rw = abs(x2-x1)
                rh = abs(y2-y1)
                if self.border_mode:
                    Line(rectangle=(rx, ry, rw, rh), width=self.line_width)
                else:
                    Rectangle(pos=(rx, ry), size=(rw, rh))

        elif self.shape_type == 'ellipse':
            if len(self.points) >= 4:
                cx, cy, rx, ry = self.points[:4]
                if self.border_mode:
                    Line(ellipse=(cx-rx, cy-ry, rx*2, ry*2), width=self.line_width)
                else:
                    Ellipse(pos=(cx-rx, cy-ry), size=(rx*2, ry*2))

        elif self.shape_type == 'point':
            if len(self.points) >= 2:
                x, y = self.points[:2]
                sz = self.line_width*2
                Ellipse(pos=(x - sz/2, y - sz/2), size=(sz, sz))

        PopMatrix()

    def rotate(self, pivot_x, pivot_y, angle_degs):
        """頂点を書き換えることで実際の座標を更新する例"""
        theta = math.radians(angle_degs)
        s = math.sin(theta)
        c = math.cos(theta)
        for i in range(0, len(self.points), 2):
            x = self.points[i]
            y = self.points[i+1]
            dx = x - pivot_x
            dy = y - pivot_y
            rx = c*dx - s*dy
            ry = s*dx + c*dy
            self.points[i]   = pivot_x + rx
            self.points[i+1] = pivot_y + ry

    def move(self, dx, dy):
        for i in range(0, len(self.points), 2):
            self.points[i]   += dx
            self.points[i+1] += dy
        self.pivot_x += dx
        self.pivot_y += dy

    def get_bounding_box(self):
        if not self.points:
            return (0,0,0,0)
        xs = self.points[0::2]
        ys = self.points[1::2]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        minx += self.offset_x
        maxx += self.offset_x
        miny += self.offset_y
        maxy += self.offset_y
        return (minx, miny, maxx, maxy)

    def get_center(self):
        bb = self.get_bounding_box()
        return ((bb[0]+bb[2])/2, (bb[1]+bb[3])/2)

    def collide_point(self, tx, ty, threshold=10):
        bb = self.get_bounding_box()
        return (bb[0]-threshold <= tx <= bb[2]+threshold and
                bb[1]-threshold <= ty <= bb[3]+threshold)

    def get_pivot_candidates(self):
        """回転用などに使える、図形の代表点を返す。select/spin で使用。"""
        cands = []
        st = self.shape_type
        # Point は回転なし → pivotなし
        if st == 'point':
            return cands

        # Line
        if st == 'line' and len(self.points) >= 4:
            x1,y1,x2,y2 = self.points[:4]
            x1o, y1o = x1 + self.offset_x, y1 + self.offset_y
            x2o, y2o = x2 + self.offset_x, y2 + self.offset_y
            cx, cy = (x1o+x2o)/2, (y1o+y2o)/2
            cands.append((x1o,y1o,10))
            cands.append((x2o,y2o,10))
            cands.append((cx, cy, 10))
        elif st == 'rectangle' and len(self.points) >= 4:
            x1,y1,x2,y2 = self.points[:4]
            rx, ry = min(x1,x2), min(y1,y2)
            rw = abs(x2-x1)
            rh = abs(y2-y1)
            rx += self.offset_x
            ry += self.offset_y
            corners = [
                (rx,ry),
                (rx, ry+rh),
                (rx+rw, ry),
                (rx+rw, ry+rh)
            ]
            for c in corners:
                cands.append((c[0], c[1], 10))
            cx = rx + rw/2
            cy = ry + rh/2
            cands.append((cx, cy, 10))
        elif st == 'ellipse' and len(self.points) >= 4:
            cx,cy,rx,ry = self.points[:4]
            cxo = cx + self.offset_x
            cyo = cy + self.offset_y
            # 中心 + 主要方向4点
            cands.append((cxo, cyo, 10))
            cands.append((cxo, cyo+ry, 10))
            cands.append((cxo, cyo-ry, 10))
            cands.append((cxo-rx, cyo, 10))
            cands.append((cxo+rx, cyo, 10))
        elif st == 'freeline' and len(self.points) >= 4:
            x1,y1 = self.points[0], self.points[1]
            x2,y2 = self.points[-2], self.points[-1]
            x1o,y1o = x1+self.offset_x, y1+self.offset_y
            x2o,y2o = x2+self.offset_x, y2+self.offset_y
            cands.append((x1o,y1o,10))
            cands.append((x2o,y2o,10))
            bb = self.get_bounding_box()
            cx, cy = (bb[0]+bb[2])/2, (bb[1]+bb[3])/2
            cands.append((cx, cy, 10))
        elif st == 'polygon':
            n = len(self.points)//2
            if n >= 3:
                for i in range(n):
                    vx = self.points[2*i]   + self.offset_x
                    vy = self.points[2*i+1] + self.offset_y
                    cands.append((vx, vy, 10))
                bb = self.get_bounding_box()
                cx, cy = (bb[0]+bb[2])/2, (bb[1]+bb[3])/2
                cands.append((cx,cy,10))
        return cands

    def is_point_on_shape(self, tx, ty):
        # pivot候補に当たれば「形状上」扱いにしない → spin用
        for (px,py,r) in self.get_pivot_candidates():
            if math.hypot(tx-px, ty-py) <= r:
                return False

        st = self.shape_type
        if st == 'point':
            if len(self.points)>=2:
                px = self.points[0]+self.offset_x
                py = self.points[1]+self.offset_y
                d = math.hypot(tx-px, ty-py)
                return (d<=10)
        elif st == 'line':
            if len(self.points)>=4:
                x1,y1,x2,y2 = self.points[:4]
                x1o, y1o = x1+self.offset_x, y1+self.offset_y
                x2o, y2o = x2+self.offset_x, y2+self.offset_y
                dist_line = distance_point_to_segment(tx,ty, x1o,y1o,x2o,y2o)[0]
                return (dist_line<=10)
        elif st=='rectangle':
            if len(self.points)>=4:
                x1,y1,x2,y2 = self.points[:4]
                rx, ry = min(x1,x2), min(y1,y2)
                rw = abs(x2-x1)
                rh = abs(y2-y1)
                rx += self.offset_x
                ry += self.offset_y
                if self.border_mode:
                    pass  # 枠線への判定などは省略
                else:
                    # 塗りつぶし内
                    if rx<=tx<=rx+rw and ry<=ty<=ry+rh:
                        return True
        elif st=='ellipse':
            if len(self.points)>=4:
                cx,cy,rx_,ry_ = self.points[:4]
                cxo = cx+self.offset_x
                cyo = cy+self.offset_y
                val = ((tx-cxo)**2)/(rx_**2) + ((ty-cyo)**2)/(ry_**2)
                return (val<=1.0)
        elif st=='freeline':
            pts = self.points
            for i in range(0,len(pts)-2,2):
                x1o = pts[i]+self.offset_x
                y1o = pts[i+1]+self.offset_y
                x2o = pts[i+2]+self.offset_x
                y2o = pts[i+3]+self.offset_y
                d,_ = distance_point_to_segment(tx,ty,x1o,y1o,x2o,y2o)
                if d<=10:
                    return True
        elif st=='polygon':
            n = len(self.points)//2
            if n>=3:
                bb = self.get_bounding_box()
                if bb[0]<=tx<=bb[2] and bb[1]<=ty<=bb[3]:
                    return True
        return False

    def get_navigation_info(self):
        """図形ごとの情報をまとめて文字列にして返す。"""
        st = self.shape_type
        info = f"Shape: {st}\n"
        # offsetのみ反映した頂点リストを作成
        pts_x = [self.points[i]   + self.offset_x for i in range(0,len(self.points),2)]
        pts_y = [self.points[i+1] + self.offset_y for i in range(0,len(self.points),2)]
        
        if st == 'freeline':
            if len(pts_x) >= 2:
                x1, y1 = pts_x[0], pts_y[0]
                x2, y2 = pts_x[-1], pts_y[-1]
                info += f"Start=({x1:.1f}, {y1:.1f}) End=({x2:.1f}, {y2:.1f})\n"
                length = 0
                for i in range(len(pts_x)-1):
                    dx = pts_x[i+1] - pts_x[i]
                    dy = pts_y[i+1] - pts_y[i]
                    length += math.hypot(dx, dy)
                info += f"Length={length:.2f}\n"

        elif st == 'line':
            if len(pts_x) >= 2:
                x1, y1, x2, y2 = pts_x[0], pts_y[0], pts_x[1], pts_y[1]
                info += f"Endpoint1=({x1:.1f}, {y1:.1f}) Endpoint2=({x2:.1f}, {y2:.1f})\n"
                cx = (x1+x2)/2
                cy = (y1+y2)/2
                info += f"Center=({cx:.1f}, {cy:.1f})\n"
                length = math.hypot(x2-x1, y2-y1)
                info += f"Length={length:.2f}\n"

        elif st == 'rectangle':
            if len(pts_x) >= 2:
                x1, y1, x2, y2 = pts_x[0], pts_y[0], pts_x[1], pts_y[1]
                rx, ry = min(x1,x2), min(y1,y2)
                rw = abs(x2 - x1)
                rh = abs(y2 - y1)
                corners = [
                    (rx, ry),
                    (rx+rw, ry),
                    (rx+rw, ry+rh),
                    (rx, ry+rh)
                ]
                info += "Corners: " + ", ".join(f"({c[0]:.1f},{c[1]:.1f})" for c in corners) + "\n"
                cx, cy = rx + rw/2, ry + rh/2
                info += f"Center=({cx:.1f},{cy:.1f})\n"
                info += f"Width={rw:.1f} Height={rh:.1f}\n"
                area = rw*rh
                info += f"Area={area:.2f}\n"

        elif st == 'ellipse':
            if len(pts_x) >= 4:
                cxo = self.points[0] + self.offset_x
                cyo = self.points[1] + self.offset_y
                rx_ = abs(self.points[2])
                ry_ = abs(self.points[3])
                info += f"Center=({cxo:.1f},{cyo:.1f}) RadiusX={rx_:.1f} RadiusY={ry_:.1f}\n"
                ratio = rx_/ry_ if ry_ != 0 else 0
                info += f"FlattenRatio(rx/ry)={ratio:.3f}\n"
                area = math.pi * rx_ * ry_
                info += f"Area={area:.2f}\n"

        elif st == 'polygon':
            n = len(pts_x)
            if n >= 3:
                corner_str = ", ".join(f"({pts_x[i]:.1f},{pts_y[i]:.1f})" for i in range(n))
                info += f"Corners: {corner_str}\n"
                bb = self.get_bounding_box()
                cx, cy = (bb[0]+bb[2])/2, (bb[1]+bb[3])/2
                info += f"Center=({cx:.1f},{cy:.1f})\n"
                w = bb[2]-bb[0]
                h = bb[3]-bb[1]
                info += f"Width={w:.1f} Height={h:.1f}\n"
                area_ = polygon_area(pts_x, pts_y)
                info += f"Area={area_:.2f}\n"

        elif st == 'point':
            if len(pts_x) >= 1:
                x, y = pts_x[0], pts_y[0]
                info += f"Point=({x:.1f},{y:.1f})\n"

        return info

class MultiLayerDrawingWidget(Widget):
    def __init__(self, **kwargs):
        super(MultiLayerDrawingWidget, self).__init__(**kwargs)
        self.colors = [
            (1,1,1,1),
            (1,0,0,1),
            (0,1,0,1),
            (0,0,1,1),
            (1,1,0,1),
            (1,0,1,1),
            (0,1,1,1),
            (0.5,0.5,0.5,1)
        ]
        self.current_color = self.colors[0]
        self.current_layer = 1
        self.current_width = 2
        self.border_mode = False
        self.draw_mode = 'freeline'
        self.polygon_sides = 3

        self.layers = [
            {'visible': True, 'drawable': True},
            {'visible': True, 'drawable': True},
            {'visible': True, 'drawable': True},
            {'visible': True, 'drawable': True},
            {'visible': True, 'drawable': True},
            {'visible': True, 'drawable': True},
            {'visible': True, 'drawable': True},
            {'visible': True, 'drawable': True},
        ]
        self.layer_shapes = [[] for _ in range(8)]

        self.selected_shape = None
        self.drag_mode = None
        self.temp_shape = None

        self.start_x = 0
        self.start_y = 0

        # 回転用
        self.touch_start_angle = 0.0
        self.initial_angle = 0.0

        # info_label への参照（MainLayoutでセット）
        self.info_label = None

        # スナップ機能フラグ
        self.snap_enabled = False

        # ---- 寸法表示系で使用する変数 ----
        # point_dimensions で 2 点を選択するための格納
        self.dim_points_for_distance = []  # [(x1, y1), (x2, y2)] 2点

    def set_layer(self, layer):
        self.current_layer = layer

    def toggle_visibility(self, layer_index):
        self.layers[layer_index]['visible'] = not self.layers[layer_index]['visible']
        self.update_canvas()

    def toggle_drawable(self, layer_index):
        self.layers[layer_index]['drawable'] = not self.layers[layer_index]['drawable']

    def set_draw_mode(self, mode):
        self.draw_mode = mode
        print("Drawing mode set to:", mode)
        # 選択状態を解除
        if self.selected_shape:
            self.selected_shape.selected = False
            self.selected_shape = None
        self.drag_mode = None
        self.update_canvas()
        # 選択解除したので info_label もクリア
        self.update_info_label(None)
        # point_dimensions モードなどに入ったタイミングで、2点保持をクリア
        if mode == 'point_dimensions':
            self.dim_points_for_distance.clear()

    def toggle_border_mode(self, instance, value):
        self.border_mode = value
        print("Border mode set to:", "border" if value else "fill")

    def toggle_snap_mode(self, instance, value):
        self.snap_enabled = value
        print("Snap mode set to:", value)

    def clear_current_layer(self):
        idx = self.current_layer - 1
        self.layer_shapes[idx].clear()
        self.update_canvas()

    def clear_all_layers(self):
        for i in range(8):
            self.layer_shapes[i].clear()
        self.update_canvas()

    def update_canvas(self):
        self.canvas.clear()
        with self.canvas:
            for i, layer_info in enumerate(self.layers):
                if not layer_info['visible']:
                    continue
                for shape in self.layer_shapes[i]:
                    if shape.selected:
                        old_col = shape.color
                        shape.color = (1,1,0,0.7)  # 選択中の強調色
                        shape.draw()
                        shape.color = old_col
                    else:
                        shape.draw()
            if self.temp_shape:
                self.temp_shape.draw()

    def update_info_label(self, shape):
        """info_label に図形情報や寸法を表示する。shape=None ならクリア。"""
        if not self.info_label:
            return
        if shape:
            self.info_label.text = shape.get_navigation_info()
        else:
            self.info_label.text = ""

    def get_all_snap_candidates(self):
        points_list = []
        segments_list = []
        for i, layer_info in enumerate(self.layers):
            if not layer_info['visible']:
                continue
            for shape in self.layer_shapes[i]:
                # pivot_points
                pivots = shape.get_pivot_candidates()
                for (px, py, _) in pivots:
                    points_list.append((px, py))

                # shape_type 別に線分追加
                st = shape.shape_type
                offset_pts = []
                for j in range(0, len(shape.points), 2):
                    offset_pts.append( (shape.points[j]+shape.offset_x,
                                        shape.points[j+1]+shape.offset_y) )

                if st in ('freeline', 'polygon'):
                    for k in range(len(offset_pts)-1):
                        segments_list.append((offset_pts[k], offset_pts[k+1]))
                elif st == 'line' and len(offset_pts) == 2:
                    segments_list.append((offset_pts[0], offset_pts[1]))
                elif st == 'rectangle' and len(shape.points) >= 4:
                    x1,y1,x2,y2 = shape.points[:4]
                    rx, ry = min(x1,x2), min(y1,y2)
                    rw = abs(x2 - x1)
                    rh = abs(y2 - y1)
                    rx += shape.offset_x
                    ry += shape.offset_y
                    p1 = (rx,       ry)
                    p2 = (rx+rw,    ry)
                    p3 = (rx+rw,    ry+rh)
                    p4 = (rx,       ry+rh)
                    segments_list.append((p1, p2))
                    segments_list.append((p2, p3))
                    segments_list.append((p3, p4))
                    segments_list.append((p4, p1))
                # ellipse / point は線分なしとみなす
        return points_list, segments_list

    def get_snapped_coords(self, tx, ty, snap_threshold=15):
        if not self.snap_enabled:
            return (tx, ty)
        points_list, segments_list = self.get_all_snap_candidates()
        snapped_x, snapped_y = tx, ty
        min_dist = float('inf')

        # 1) ポイントへのスナップ
        for px, py in points_list:
            d = math.hypot(tx - px, ty - py)
            if d < snap_threshold and d < min_dist:
                min_dist = d
                snapped_x, snapped_y = px, py

        # 2) 線分へのスナップ
        for (p1, p2) in segments_list:
            (x1, y1) = p1
            (x2, y2) = p2
            d, (projx, projy) = distance_point_to_segment(tx, ty, x1, y1, x2, y2)
            if d < snap_threshold and d < min_dist:
                min_dist = d
                snapped_x, snapped_y = projx, projy

        return (snapped_x, snapped_y)

    # ------------------------------
    # ここから寸法表示用の補助関数群
    # ------------------------------
    def get_measurement_endpoints(self, shape):
        """
        shape が point/line/rectangle/polygon の場合に、
        距離計測用の端点リストを返す。
        (オフセット込みの実座標)
        """
        st = shape.shape_type
        pts = []
        if st == 'point':
            if len(shape.points) >= 2:
                x = shape.points[0] + shape.offset_x
                y = shape.points[1] + shape.offset_y
                pts.append((x, y))
        elif st == 'line':
            if len(shape.points) >= 4:
                x1 = shape.points[0] + shape.offset_x
                y1 = shape.points[1] + shape.offset_y
                x2 = shape.points[2] + shape.offset_x
                y2 = shape.points[3] + shape.offset_y
                pts.append((x1, y1))
                pts.append((x2, y2))
        elif st == 'rectangle':
            if len(shape.points) >= 4:
                x1, y1, x2, y2 = shape.points[:4]
                rx, ry = min(x1,x2), min(y1,y2)
                rw = abs(x2 - x1)
                rh = abs(y2 - y1)
                rx += shape.offset_x
                ry += shape.offset_y
                corners = [
                    (rx,        ry),
                    (rx+rw,     ry),
                    (rx+rw,     ry+rh),
                    (rx,        ry+rh)
                ]
                pts.extend(corners)
        elif st == 'polygon':
            n = len(shape.points)//2
            for i in range(n):
                px = shape.points[2*i]   + shape.offset_x
                py = shape.points[2*i+1] + shape.offset_y
                pts.append((px, py))
        return pts

    def check_line_segments(self, shape):
        """
        shape が line/rectangle/polygon の場合に、
        線分の一覧 [((x1,y1),(x2,y2)), ...] を返す
        """
        st = shape.shape_type
        segs = []
        if st == 'line':
            if len(shape.points) >= 4:
                x1 = shape.points[0] + shape.offset_x
                y1 = shape.points[1] + shape.offset_y
                x2 = shape.points[2] + shape.offset_x
                y2 = shape.points[3] + shape.offset_y
                segs.append(((x1,y1),(x2,y2)))
        elif st == 'rectangle':
            if len(shape.points) >= 4:
                x1, y1, x2, y2 = shape.points[:4]
                rx, ry = min(x1,x2), min(y1,y2)
                rw = abs(x2 - x1)
                rh = abs(y2 - y1)
                rx += shape.offset_x
                ry += shape.offset_y
                p1 = (rx,     ry)
                p2 = (rx+rw,  ry)
                p3 = (rx+rw,  ry+rh)
                p4 = (rx,     ry+rh)
                segs.append((p1,p2))
                segs.append((p2,p3))
                segs.append((p3,p4))
                segs.append((p4,p1))
        elif st == 'polygon':
            n = len(shape.points)//2
            pts = []
            for i in range(n):
                px = shape.points[2*i]   + shape.offset_x
                py = shape.points[2*i+1] + shape.offset_y
                pts.append((px, py))
            for i in range(n-1):
                segs.append((pts[i], pts[i+1]))
            # ポリゴンを閉じる場合
            if n >= 3:
                segs.append((pts[-1], pts[0]))
        # point は線分なし, freeline は複雑だが対象外 (仕様により)
        return segs

    def approximate_ellipse_perimeter(self, rx, ry):
        """
        楕円周長のラマヌジャン近似
        P \approx \pi [3(a+b) - \sqrt{(3a+b)(a+3b)}]
        """
        a = rx
        b = ry
        return math.pi * (3*(a+b) - math.sqrt((3*a+b)*(a+3*b)))

    # ------------------------------
    # on_touch_down / move / up
    # ------------------------------
    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return False
        idx = self.current_layer - 1
        if not (self.layers[idx]['visible'] and self.layers[idx]['drawable']):
            return False

        sx, sy = self.get_snapped_coords(touch.x, touch.y)

        # -----------------------------------------------
        # まずは特殊モード(寸法系)を先に判定
        # -----------------------------------------------
        # 1) point_dimensions
        if self.draw_mode == 'point_dimensions':
            # point/line/rectangle/polygon の端点を探す
            found_pt = None
            # 上の図形(=後ろから)を探す
            for sh in reversed(self.layer_shapes[idx]):
                if sh.shape_type in ('point','line','rectangle','polygon'):
                    endpoints = self.get_measurement_endpoints(sh)
                    # 各端点と (sx,sy) の距離をチェック
                    for ep in endpoints:
                        dist = math.hypot(ep[0]-sx, ep[1]-sy)
                        if dist <= 10:  # 閾値
                            found_pt = ep
                            break
                if found_pt:
                    break

            if found_pt:
                self.dim_points_for_distance.append(found_pt)
                # 2点揃ったら距離計測して表示
                if len(self.dim_points_for_distance) == 2:
                    p1 = self.dim_points_for_distance[0]
                    p2 = self.dim_points_for_distance[1]
                    dx = p2[0] - p1[0]
                    dy = p2[1] - p1[1]
                    dist_ = math.hypot(dx, dy)
                    if self.info_label:
                        self.info_label.text = f"Distance between points: {dist_:.2f}"
                    # 計測したらクリア or 続けて計測するならクリアしない等
                    self.dim_points_for_distance.clear()
            return True

        # 2) line_dimensions
        if self.draw_mode == 'line_dimensions':
            # point/line/rectangle/polygon の「線分」を探す
            # クリック地点に最も近い線分を検出 → 長さ表示
            candidate_seg = None
            candidate_dist = 1e9

            for sh in reversed(self.layer_shapes[idx]):
                if sh.shape_type in ('point','line','rectangle','polygon'):
                    segs = self.check_line_segments(sh)
                    for seg in segs:
                        d, proj = distance_point_to_segment(sx, sy,
                                                            seg[0][0], seg[0][1],
                                                            seg[1][0], seg[1][1])
                        if d < 10 and d < candidate_dist:
                            candidate_dist = d
                            candidate_seg = seg
            if candidate_seg:
                # candidate_seg = ((x1,y1),(x2,y2))
                x1, y1 = candidate_seg[0]
                x2, y2 = candidate_seg[1]
                length_ = math.hypot(x2 - x1, y2 - y1)
                if self.info_label:
                    self.info_label.text = f"Line length: {length_:.2f}"
            return True

        # 3) ellipse_dimensions
        if self.draw_mode == 'ellipse_dimensions':
            # ellipse を探す。クリック地点が中心付近 or 外周付近か判定 → 半径 or 周長表示
            found_ellipse = None
            for sh in reversed(self.layer_shapes[idx]):
                if sh.shape_type == 'ellipse' and len(sh.points) >= 4:
                    cx, cy, rx, ry = sh.points[:4]
                    cxo = cx + sh.offset_x
                    cyo = cy + sh.offset_y
                    # 中心との距離
                    dist_center = math.hypot(sx - cxo, sy - cyo)
                    # 楕円パラメータ: val = ((x-cx)^2/rx^2 + (y-cy)^2/ry^2)
                    # これが1前後なら外周付近
                    if rx > 0 and ry > 0:
                        val = ((sx - cxo)**2)/(rx**2) + ((sy - cyo)**2)/(ry**2)
                    else:
                        val = 9999
                    # 中心付近 or 外周付近をゆるく判定
                    if dist_center <= 10:
                        found_ellipse = ('center', sh)
                        break
                    # 周囲 (val ~ 1) の近さ
                    if abs(val - 1) < 0.2:
                        found_ellipse = ('boundary', sh)
                        break
            if found_ellipse:
                loc, shape_ = found_ellipse
                cx, cy, rx, ry = shape_.points[:4]
                rx_abs = abs(rx)
                ry_abs = abs(ry)
                if loc == 'center':
                    # 半径表示 (円なら1種類、楕円なら rx, ry)
                    if self.info_label:
                        if abs(rx_abs - ry_abs) < 1e-6:  # 円とみなす
                            self.info_label.text = f"Circle radius: {rx_abs:.2f}"
                        else:
                            self.info_label.text = f"Ellipse radii: rx={rx_abs:.2f}, ry={ry_abs:.2f}"
                else:
                    # 周長表示
                    if abs(rx_abs - ry_abs) < 1e-6:
                        # 円
                        cir = 2 * math.pi * rx_abs
                        if self.info_label:
                            self.info_label.text = f"Circle circumference: {cir:.2f}"
                    else:
                        # 楕円
                        peri = self.approximate_ellipse_perimeter(rx_abs, ry_abs)
                        if self.info_label:
                            self.info_label.text = f"Ellipse perimeter(approx): {peri:.2f}"
            return True

        # -----------------------------------------------
        # 既存の select/spin, および図形作成モード
        # -----------------------------------------------

        self.start_x, self.start_y = sx, sy

        # ========== selectモード ==========
        if self.draw_mode == 'select':
            self.selected_shape = None
            for sh in reversed(self.layer_shapes[idx]):
                if sh.collide_point(sx, sy, threshold=10):
                    self.selected_shape = sh
                    break
            if not self.selected_shape:
                self.update_info_label(None)
                return False

            # 選択確定、移動モード
            for s in self.layer_shapes[idx]:
                s.selected = False
            self.selected_shape.selected = True
            self.drag_mode = 'move'
            self.update_canvas()
            self.update_info_label(self.selected_shape)
            return True

        # ========== spinモード ==========
        if self.draw_mode == 'spin':
            self.selected_shape = None
            for sh in reversed(self.layer_shapes[idx]):
                if sh.collide_point(sx, sy, threshold=10):
                    self.selected_shape = sh
                    break
            if not self.selected_shape:
                self.update_info_label(None)
                return False

            for s in self.layer_shapes[idx]:
                s.selected = False
            self.selected_shape.selected = True

            # pivot候補を調べる
            pivot_found = False
            pivots = self.selected_shape.get_pivot_candidates()
            for (px, py, r) in pivots:
                dist = math.hypot(sx - px, sy - py)
                if dist <= r:
                    self.drag_mode = 'rotate'
                    self.selected_shape.pivot_x = px
                    self.selected_shape.pivot_y = py
                    self.initial_angle = self.selected_shape.angle
                    dx = sx - px
                    dy = sy - py
                    self.touch_start_angle = math.degrees(math.atan2(dy, dx))
                    pivot_found = True
                    break

            if not pivot_found:
                self.selected_shape.selected = False
                self.selected_shape = None
                self.update_info_label(None)
                return False

            self.update_canvas()
            self.update_info_label(self.selected_shape)
            return True

        # ========== 新規図形モード ==========
        if self.draw_mode == 'freeline':
            self.temp_shape = Shape('freeline',
                                    [sx, sy],
                                    color=self.current_color,
                                    line_width=self.current_width,
                                    border_mode=self.border_mode)
            self.update_canvas()
            self.update_info_label(self.temp_shape)
            return True
        elif self.draw_mode == 'line':
            self.temp_shape = Shape('line',
                                    [sx, sy, sx, sy],
                                    color=self.current_color,
                                    line_width=self.current_width,
                                    border_mode=self.border_mode)
            self.update_canvas()
            self.update_info_label(self.temp_shape)
            return True
        elif self.draw_mode == 'rectangle':
            self.temp_shape = Shape('rectangle',
                                    [sx, sy, sx, sy],
                                    color=self.current_color,
                                    line_width=self.current_width,
                                    border_mode=self.border_mode)
            self.update_canvas()
            self.update_info_label(self.temp_shape)
            return True
        elif self.draw_mode == 'ellipse':
            self.temp_shape = Shape('ellipse',
                                    [sx, sy, 0, 0], # (cx, cy, rx, ry)
                                    color=self.current_color,
                                    line_width=self.current_width,
                                    border_mode=self.border_mode)
            self.update_canvas()
            self.update_info_label(self.temp_shape)
            return True
        elif self.draw_mode == 'polygon':
            self.temp_shape = Shape('polygon',
                                    [],
                                    color=self.current_color,
                                    line_width=self.current_width,
                                    border_mode=self.border_mode)
            self.update_canvas()
            self.update_info_label(self.temp_shape)
            return True
        elif self.draw_mode == 'point':
            self.temp_shape = Shape('point',
                                    [sx, sy],
                                    color=self.current_color,
                                    line_width=self.current_width,
                                    border_mode=self.border_mode)
            self.update_canvas()
            self.update_info_label(self.temp_shape)
            return True

        return False

    def on_touch_move(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return False

        # point_dimensions などの寸法モード中は図形作成や移動を行わない
        if self.draw_mode in ('point_dimensions','line_dimensions','ellipse_dimensions'):
            return False

        mx, my = self.get_snapped_coords(touch.x, touch.y)

        if self.draw_mode == 'select' and self.selected_shape:
            if self.drag_mode == 'move':
                dx = mx - self.start_x
                dy = my - self.start_y
                self.selected_shape.move(dx, dy)
                self.start_x, self.start_y = mx, my
                self.update_canvas()
                self.update_info_label(self.selected_shape)
                return True

        if self.draw_mode == 'spin' and self.selected_shape:
            if self.drag_mode == 'rotate':
                px, py = self.selected_shape.pivot_x, self.selected_shape.pivot_y
                cx = mx - px
                cy = my - py
                curr_angle = math.degrees(math.atan2(cy, cx))
                diff = curr_angle - self.touch_start_angle
                self.selected_shape.angle = self.initial_angle + diff
                self.update_canvas()
                self.update_info_label(self.selected_shape)
                return True

        if self.temp_shape:
            sx, sy = self.start_x, self.start_y
            st = self.temp_shape.shape_type
            if st == 'freeline':
                self.temp_shape.points += [mx,my]
            elif st == 'line':
                self.temp_shape.points = [sx, sy, mx, my]
            elif st == 'rectangle':
                self.temp_shape.points = [sx, sy, mx, my]
            elif st == 'ellipse':
                cx = (sx + mx)/2
                cy = (sy + my)/2
                rx = abs(mx - cx)
                ry = abs(my - cy)
                self.temp_shape.points = [cx, cy, rx, ry]
            elif st == 'polygon':
                radius = math.hypot(mx - sx, my - sy)
                sides = self.polygon_sides
                pts = []
                for i in range(sides):
                    theta = 2*math.pi*i/sides
                    px = sx + radius*math.cos(theta)
                    py = sy + radius*math.sin(theta)
                    pts += [px, py]
                self.temp_shape.points = pts
            elif st == 'point':
                self.temp_shape.points = [mx, my]

            self.update_canvas()
            self.update_info_label(self.temp_shape)
            return True

        return False

    def on_touch_up(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return False

        # 寸法モード中はスルー
        if self.draw_mode in ('point_dimensions','line_dimensions','ellipse_dimensions'):
            return True

        if self.draw_mode == 'select':
            self.drag_mode = None
            return True

        if self.draw_mode == 'spin':
            self.drag_mode = None
            return True

        # 新規図形 確定
        idx = self.current_layer - 1
        if self.temp_shape:
            self.layer_shapes[idx].append(self.temp_shape)
            self.update_info_label(self.temp_shape)
            self.temp_shape = None
        self.update_canvas()
        return True

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.drawing_widget = MultiLayerDrawingWidget()
        self.add_widget(self.drawing_widget)

        controls_layout = BoxLayout(size_hint_y=None, height=50)
        self.add_widget(controls_layout)

        # 枠線描画モード
        border_checkbox = CheckBox(active=False)
        border_checkbox.bind(active=self.drawing_widget.toggle_border_mode)
        controls_layout.add_widget(border_checkbox)
        controls_layout.add_widget(Label(text='Draw Border Only'))

        # スナップON/OFF
        snap_checkbox = CheckBox(active=False)
        snap_checkbox.bind(active=self.drawing_widget.toggle_snap_mode)
        controls_layout.add_widget(snap_checkbox)
        controls_layout.add_widget(Label(text='snap_point'))

        draw_mode_layout = BoxLayout(size_hint_y=None, height=50)
        self.add_widget(draw_mode_layout)

        freeline_btn = Button(text='Free Line')
        freeline_btn.bind(on_press=lambda instance:
                          self.drawing_widget.set_draw_mode('freeline'))
        draw_mode_layout.add_widget(freeline_btn)

        point_btn = Button(text='Point')
        point_btn.bind(on_press=lambda instance:
                       self.drawing_widget.set_draw_mode('point'))
        draw_mode_layout.add_widget(point_btn)

        line_btn = Button(text='Line')
        line_btn.bind(on_press=lambda instance:
                      self.drawing_widget.set_draw_mode('line'))
        draw_mode_layout.add_widget(line_btn)

        rectangle_btn = Button(text='Rectangle')
        rectangle_btn.bind(on_press=lambda instance:
                           self.drawing_widget.set_draw_mode('rectangle'))
        draw_mode_layout.add_widget(rectangle_btn)

        ellipse_btn = Button(text='Ellipse')
        ellipse_btn.bind(on_press=lambda instance:
                         self.drawing_widget.set_draw_mode('ellipse'))
        draw_mode_layout.add_widget(ellipse_btn)

        polygon_btn = Button(text='Polygon')
        polygon_btn.bind(on_press=lambda instance:
                         self.drawing_widget.set_draw_mode('polygon'))
        draw_mode_layout.add_widget(polygon_btn)

        layer_clear_btn = Button(text='layer_clear')
        layer_clear_btn.bind(on_press=lambda instance:
                             self.drawing_widget.clear_current_layer())
        draw_mode_layout.add_widget(layer_clear_btn)

        clear_btn = Button(text='clear')
        clear_btn.bind(on_press=lambda instance:
                       self.drawing_widget.clear_all_layers())
        draw_mode_layout.add_widget(clear_btn)

        function_layout = BoxLayout(size_hint_y=None, height=50)
        self.add_widget(function_layout)

        select_btn = Button(text='select')
        select_btn.bind(on_press=lambda instance:
                        self.drawing_widget.set_draw_mode('select'))
        function_layout.add_widget(select_btn)

        spin_btn = Button(text='spin')
        spin_btn.bind(on_press=lambda instance:
                      self.drawing_widget.set_draw_mode('spin'))
        function_layout.add_widget(spin_btn)

        # ↓↓↓ ここで3つの寸法モードボタンを追加 ↓↓↓
        point_dimensions_btn = Button(text='point_dimensions')
        point_dimensions_btn.bind(on_press=lambda instance:
            self.drawing_widget.set_draw_mode('point_dimensions'))
        function_layout.add_widget(point_dimensions_btn)

        line_dimensions_btn = Button(text='line_dimensions')
        line_dimensions_btn.bind(on_press=lambda instance:
            self.drawing_widget.set_draw_mode('line_dimensions'))
        function_layout.add_widget(line_dimensions_btn)

        ellipse_dimensions_btn = Button(text='ellipse_dimensions')
        ellipse_dimensions_btn.bind(on_press=lambda instance:
            self.drawing_widget.set_draw_mode('ellipse_dimensions'))
        function_layout.add_widget(ellipse_dimensions_btn)
        # ↑↑↑ 修正部分。spin_btn 重複を削除して配置し直す ↑↑↑

        slider_layout = BoxLayout(size_hint_y=None, height=50)
        self.add_widget(slider_layout)

        color_slider = Slider(min=0, max=len(self.drawing_widget.colors)-1,
                              value=0, step=1)
        color_slider.size_hint_x = 0.5
        color_slider.bind(value=self.on_color_slider_change)
        slider_layout.add_widget(color_slider)

        width_slider = Slider(min=1, max=20, value=2, step=1)
        width_slider.size_hint_x = 0.5
        width_slider.bind(value=self.on_width_slider_change)
        slider_layout.add_widget(width_slider)

        sides_slider = Slider(min=3, max=12, value=3, step=1)
        sides_slider.size_hint_x = 0.5
        sides_slider.bind(value=self.on_sides_slider_change)
        slider_layout.add_widget(sides_slider)

        btn_layout = BoxLayout(size_hint_y=None, height=50)
        self.add_widget(btn_layout)
        self.layer_buttons = []
        for i in range(1, 9):
            btn = Button(text=f'Layer {i}')
            btn.bind(on_press=lambda inst, x=i: self.set_active_layer(x))
            btn_layout.add_widget(btn)
            self.layer_buttons.append(btn)

        btn_toggle = BoxLayout(size_hint_y=None, height=50)
        self.add_widget(btn_toggle)
        for i in range(8):
            v_btn = Button(text=f'Visibility {i+1}')
            v_btn.bind(on_press=lambda inst, x=i:
                       self.drawing_widget.toggle_visibility(x))
            btn_toggle.add_widget(v_btn)
            d_btn = Button(text=f'Drawable {i+1}')
            d_btn.bind(on_press=lambda inst, x=i:
                       self.drawing_widget.toggle_drawable(x))
            btn_toggle.add_widget(d_btn)

        self.info_label = Label(text="", size_hint_y=None, height=70)
        self.add_widget(self.info_label)
        self.drawing_widget.info_label = self.info_label

    def set_active_layer(self, layer):
        for idx, b in enumerate(self.layer_buttons, start=1):
            if idx == layer:
                b.background_color = (0,1,1,1)
            else:
                b.background_color = (0.9,0.9,0.9,1)
        self.drawing_widget.set_layer(layer)

    def on_color_slider_change(self, inst, val):
        c = self.drawing_widget.colors[int(val)]
        self.drawing_widget.current_color = c
        print("Color changed to:", c)

    def on_width_slider_change(self, inst, val):
        w = int(val)
        self.drawing_widget.current_width = w
        print("Line width changed to:", w)

    def on_sides_slider_change(self, inst, val):
        s = int(val)
        self.drawing_widget.polygon_sides = s
        print("Polygon sides set to:", s)

class MainApp(App):
    def build(self):
        return MainLayout()

if __name__=='__main__':
    MainApp().run()
