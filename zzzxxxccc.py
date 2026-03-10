from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import (Color, Line, Rectangle, Ellipse, Rotate,
                           PushMatrix, PopMatrix, Translate, Mesh, InstructionGroup)
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label, CoreLabel
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

def intersect_segments(p1, p2, p3, p4):
    """
    線分 p1->p2 と p3->p4 が交差していれば、(x, y) を返す。
    交差しない場合や平行の場合は None を返す。
    
    p1, p2, p3, p4: (x, y) タプル
    """

    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    # 2直線のパラメータ表現での判定
    denom = (y4 - y3)*(x2 - x1) - (x4 - x3)*(y2 - y1)
    if abs(denom) < 1e-12:
        # 平行、あるいはほぼ平行
        return None

    ua = ((x4 - x3)*(y1 - y3) - (y4 - y3)*(x1 - x3)) / denom
    ub = ((x2 - x1)*(y1 - y3) - (y2 - y1)*(x1 - x3)) / denom

    # 交点が "線分" 同士に含まれるかを判定 (0 <= ua <= 1, 0 <= ub <= 1)
    if 0 <= ua <= 1 and 0 <= ub <= 1:
        # 交点 (ix, iy) を求める
        ix = x1 + ua*(x2 - x1)
        iy = y1 + ua*(y2 - y1)
        return (ix, iy)
    else:
        return None

def polygon_area(xs, ys):
    """ポリゴンの面積（符号付き）を求める簡易的な関数。"""
    n = len(xs)
    area = 0
    for i in range(n):
        j = (i+1) % n
        area += xs[i]*ys[j] - xs[j]*ys[i]
    return abs(area)/2

class Shape:
    """
    既存の図形クラス。ここに変更はほとんど加えず、
    図形の端点(ピボット候補等) を取得するメソッドなどを活用します。
    """
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
        """図形の端点・コーナー・中心などをまとめて返す。"""
        cands = []
        st = self.shape_type
        if st == 'point':
            # pointは自前の points[0], points[1] が端点扱い
            if len(self.points) >= 2:
                px = self.points[0] + self.offset_x
                py = self.points[1] + self.offset_y
                cands.append((px, py, 10))
            return cands
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
                (rx+rw, ry),
                (rx+rw, ry+rh),
                (rx, ry+rh)
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
            cands.append((cxo, cyo, 10))  # 中心
            # 主要方向4点
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
        # pivotに当たれば回転用 → ここでは当たり判定しない
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
        """図形の情報をまとめて文字列にして返す。"""
        st = self.shape_type
        info = f"Shape: {st}\n"
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


# -------------------------------------------------------
# 寸法線をまとめて描画するためのクラス
# -------------------------------------------------------
class DimensionShape:
    """
    2点間の寸法線、補助線、終端記号(●)、および寸法値テキストをまとめて描画するクラス。
    寸法文字を寸法線に対して平行に表示する。
    """
    def __init__(self, p1, p2, text="", color=(1,1,1,1), offset=20, layer=None):
        self.p1 = p1
        self.p2 = p2
        self.text = text
        self.color = color
        self.offset = offset
        self.font_size = 18  # 18pt
        self.layer = layer  # 所属レイヤー（1～8など）

    def draw(self):
        """
        オフセット付き寸法線 (p1->p2 に対して法線方向へずらす)、
        補助線・終端記号(●)・寸法値テキストをまとめて InstructionGroup で返す。
        """
        x1, y1 = self.p1
        x2, y2 = self.p2

        dx = x2 - x1
        dy = y2 - y1
        base_len = math.hypot(dx, dy)
        if base_len < 1e-7:
            return None  # 2点が同じなら描画しない

        # 法線方向(90度回転)を求める
        nx = -dy
        ny = dx
        nn = math.hypot(nx, ny)
        nx /= nn
        ny /= nn

        # 寸法線を元の直線から offset 分だけ離す
        ox = 4 * nx * self.offset
        oy = 4 * ny * self.offset

        # 寸法線の端点
        dim_p1 = (x1 + ox, y1 + oy)
        dim_p2 = (x2 + ox, y2 + oy)

        # 寸法値テキストを配置する中心座標 (寸法線の真ん中)
        mx = (dim_p1[0] + dim_p2[0]) / 2
        my = (dim_p1[1] + dim_p2[1]) / 2

        # 寸法線方向の角度(度数)
        angle_degrees = math.degrees(math.atan2(dy, dx))

        # 寸法線に平行になるような角度を計算
        #  dx, dy は 寸法線(= p1->p2 の向き) と同じベクトルなので、その向きの角度を得る
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        # 文字が上下反転しにくいように、ある角度を超えたら180度回転して正しい向きにする
        #  例) 90〜270度のあいだは文字が逆さになるので +180
        if angle_deg > 90 or angle_deg < -90:
            angle_deg += 180

        ig = InstructionGroup()
        ig.add(Color(*self.color))

        # ---------------------------
        # 補助線(端点→寸法線端)
        ig.add(Line(points=[x1, y1, dim_p1[0], dim_p1[1]], width=1))
        ig.add(Line(points=[x2, y2, dim_p2[0], dim_p2[1]], width=1))

        # 寸法線
        ig.add(Line(points=[dim_p1[0], dim_p1[1], dim_p2[0], dim_p2[1]], width=1))

        # 終端記号(●) (半径=5)
        r = 5
        ig.add(Ellipse(pos=(dim_p1[0]-r, dim_p1[1]-r), size=(r*2, r*2)))
        ig.add(Ellipse(pos=(dim_p2[0]-r, dim_p2[1]-r), size=(r*2, r*2)))

        # ---------------------------
        # 寸法値テキスト (CoreLabel + texture) を寸法線に平行に配置
        lbl = CoreLabel(text=self.text, font_size=self.font_size, color=self.color)
        lbl.refresh()
        tw, th = lbl.texture.size

        # PushMatrix ~ PopMatrix で変換行列を適用
        ig.add(PushMatrix())
        # 1) テキストの描画原点を寸法線の中央へ移動
        ig.add(Translate(mx, my))
        # 2) 寸法線と同じ角度に回転 (補正済み angle_deg)
        # 2) 寸法線の角度だけ回転 (line方向へ)
        ig.add(Rotate(angle=angle_degrees, axis=(0,0,1)))
        # 3) ローカル座標で「線から 5px 上」にテキストの下端が来るように配置
        margin = 5
        #   -tw/2 で X方向は中央寄せ
        #    margin で Y方向に 5px 上げる (底辺がy=5になる)
        ig.add(Rectangle(texture=lbl.texture,
                         pos=(-tw/2, margin),
                         size=(tw, th)))
        ig.add(PopMatrix())

        return ig

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
        self.current_width = 0.5
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

        # info_label への参照を後からセット
        self.info_label = None

        # ==== スナップ機能フラグ ====
        self.snap_enabled = False

        # ==== 寸法線管理リスト ====
        self.dimension_shapes = []

        # ==== point_dimensions 用のクリック状態 ====
        self.dim_points = []  # クリックした端点を2つまで保持

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
        # info_label もクリア
        self.update_info_label(None)

        # 寸法モードなら補助用リスト初期化
        if mode in ('point_dimensions', 'line_dimensions', 'ellipse_dimensions'):
            self.dim_points = []

    def toggle_border_mode(self, instance, value):
        self.border_mode = value
        print("Border mode set to:", "border" if value else "fill")

    def toggle_snap_mode(self, instance, value):
        self.snap_enabled = value
        print("Snap mode set to:", value)

    def clear_current_layer(self):
        idx = self.current_layer - 1
        self.layer_shapes[idx].clear()
        # 現在のレイヤーに属する寸法線のみを削除する
        self.dimension_shapes = [dim for dim in self.dimension_shapes if dim.layer != self.current_layer]
        self.update_canvas()

    def clear_all_layers(self):
        for i in range(8):
            self.layer_shapes[i].clear()
        # 寸法線もクリア
        self.dimension_shapes.clear()
        self.update_canvas()

    def update_canvas(self):
        self.canvas.clear()
        with self.canvas:
            # 各レイヤーの図形描画
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

            # 一時形状 (新規作成ドラッグ中)
            if self.temp_shape:
                self.temp_shape.draw()

            # 寸法線を後からまとめて描画（所属レイヤーの可視性を考慮）
            for dim in self.dimension_shapes:
                # 寸法線に所属レイヤーが設定されている場合、該当レイヤーが可視かチェック
                if dim.layer is not None:
                    if not self.layers[dim.layer - 1]['visible']:
                        continue  # 非表示のレイヤーに属する寸法線は描画しない
                ig = dim.draw()
                if ig:
                    self.canvas.add(ig)

    def update_info_label(self, shape):
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
                # 端点・コーナー等
                pivots = shape.get_pivot_candidates()
                for (px, py, _) in pivots:
                    points_list.append((px, py))

                # shape_type 別に線分を追加
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

                # ellipseは円弧なので線分ではなくなるため、ここでは省略
                # 必要なら近似線分化するなどの方法で追加する

        # ---------------------------
        # **追加: すべての線分ペア間の交点を調べる**
        # ---------------------------
        n_segments = len(segments_list)
        for i in range(n_segments):
            for j in range(i+1, n_segments):
                segA = segments_list[i]
                segB = segments_list[j]
                p1, p2 = segA
                p3, p4 = segB
                ip = intersect_segments(p1, p2, p3, p4)
                if ip is not None:
                    # 交点ipをpoints_listに追加
                    points_list.append(ip)
        
        return points_list, segments_list

    def get_snapped_coords(self, tx, ty, snap_threshold=15):
        if not self.snap_enabled:
            return (tx, ty)

        points_list, segments_list = self.get_all_snap_candidates()

        snapped_x, snapped_y = tx, ty
        min_dist = float('inf')

        # 点へのスナップ
        for px, py in points_list:
            d = math.hypot(tx - px, ty - py)
            if d < snap_threshold and d < min_dist:
                min_dist = d
                snapped_x, snapped_y = px, py

        # 線分へのスナップ
        for (p1, p2) in segments_list:
            (x1, y1) = p1
            (x2, y2) = p2
            d, (projx, projy) = distance_point_to_segment(tx, ty, x1, y1, x2, y2)
            if d < snap_threshold and d < min_dist:
                min_dist = d
                snapped_x, snapped_y = projx, projy

        return (snapped_x, snapped_y)

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return False
        idx = self.current_layer - 1
        if not (self.layers[idx]['visible'] and self.layers[idx]['drawable']):
            return False

        sx, sy = self.get_snapped_coords(touch.x, touch.y)
        self.start_x, self.start_y = sx, sy

        # -----------------------------
        # 寸法モード (point_dimensions)
        #   Point, Line, Rectangle, Polygon の端点を2つクリックし距離を表示
        # -----------------------------
        if self.draw_mode == 'point_dimensions':
            # まず図形を探し、端点候補を取得して一番近い端点を選ぶ
            found = None
            found_dist = 9999999
            found_pt = None

            # どの図形かは限定せず、現在レイヤーの全shape対象 (または全部のレイヤーでもOK)
            for sh in self.layer_shapes[idx]:
                if sh.shape_type in ('point','line','rectangle','polygon'):
                    # pivot_candidates() で端点やコーナーを取得
                    cands = sh.get_pivot_candidates()
                    for (px,py,r) in cands:
                        d = math.hypot(sx - px, sy - py)
                        if d < found_dist and d <= 15:  # 端点近くをクリック
                            found_dist = d
                            found = sh
                            found_pt = (px, py)
            
            if found and found_pt:
                self.dim_points.append(found_pt)
                print("Select dimension endpoint:", found_pt)
            if len(self.dim_points) == 2:
                p1 = self.dim_points[0]
                p2 = self.dim_points[1]
                dist_val = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
                text = f"{dist_val:.2f}"
                # 現在のレイヤー情報を渡す
                dim_obj = DimensionShape(p1, p2, text=text, color=(1,1,0,1), offset=20, layer=self.current_layer)
                self.dimension_shapes.append(dim_obj)
                self.dim_points.clear()
                self.update_canvas()

            return True

        # -----------------------------
        # 寸法モード (line_dimensions)
        #   Point, Line, Rectangle, Polygon の「線」をクリック → その線の寸法
        #   （Lineならその長さ, RectangleやPolygonならクリックした辺の長さ）
        # -----------------------------
        if self.draw_mode == 'line_dimensions':
            found = None
            # クリック位置に応じて最も近い「線分」を求める
            found_line_pts = None
            found_dist = 9999999

            # shapeごとに線分へ当たり判定
            for sh in self.layer_shapes[idx]:
                st = sh.shape_type
                if st not in ('point','line','rectangle','polygon'):
                    continue
                # shape 内の線分を列挙
                offset_pts = []
                for j in range(0, len(sh.points), 2):
                    offset_pts.append( (sh.points[j]+sh.offset_x,
                                        sh.points[j+1]+sh.offset_y) )

                if st == 'point':
                    # pointは線分無いが、もし強引にやるなら長さ0?
                    # クリックが近いなら採用
                    if offset_pts:
                        px, py = offset_pts[0]
                        d = math.hypot(sx-px, sy-py)
                        if d<15 and d<found_dist:
                            found_dist = d
                            found_line_pts = (px, py, px, py)  # 同一点
                            found = sh
                elif st == 'line':
                    if len(offset_pts)==2:
                        x1,y1 = offset_pts[0]
                        x2,y2 = offset_pts[1]
                        d, _ = distance_point_to_segment(sx, sy, x1,y1,x2,y2)
                        if d<15 and d<found_dist:
                            found_dist = d
                            found_line_pts = (x1,y1,x2,y2)
                            found = sh
                elif st == 'rectangle':
                    if len(offset_pts)>=2:
                        # rectangleは cornersを計算
                        x1,y1,x2,y2 = sh.points[:4]
                        rx, ry = min(x1,x2), min(y1,y2)
                        rw = abs(x2 - x1)
                        rh = abs(y2 - y1)
                        rx += sh.offset_x
                        ry += sh.offset_y
                        corner_list = [
                            (rx, ry),
                            (rx+rw, ry),
                            (rx+rw, ry+rh),
                            (rx, ry+rh)
                        ]
                        # 各辺に対してチェック
                        for i in range(4):
                            j = (i+1)%4
                            pA = corner_list[i]
                            pB = corner_list[j]
                            d, (projx, projy) = distance_point_to_segment(sx, sy, pA[0],pA[1], pB[0],pB[1])
                            if d<15 and d<found_dist:
                                found_dist = d
                                found_line_pts = (pA[0],pA[1], pB[0],pB[1])
                                found = sh
                elif st == 'polygon':
                    n = len(offset_pts)
                    if n>=2:
                        # polygonの連続する頂点を線分とみなす
                        for i in range(n):
                            j = (i+1)%n
                            x1,y1 = offset_pts[i]
                            x2,y2 = offset_pts[j]
                            d, proj = distance_point_to_segment(sx, sy, x1,y1, x2,y2)
                            if d<15 and d<found_dist:
                                found_dist = d
                                found_line_pts = (x1,y1,x2,y2)
                                found = sh

            if found and found_line_pts:
                x1,y1,x2,y2 = found_line_pts
                length = math.hypot(x2-x1, y2-y1)
                text = f"{length:.2f}"
                # 寸法線追加
                dim_obj = DimensionShape((x1,y1), (x2,y2), text=text, color=(1,1,0,1), offset=20)
                self.dimension_shapes.append(dim_obj)
                self.update_canvas()

            return True

        # -----------------------------
        # 寸法モード (ellipse_dimensions)
        #   Ellipse クリックで「円周をクリック → 円周(近似)の寸法」,
        #             「中心付近をクリック → 半径の寸法」 を表示
        # -----------------------------
        if self.draw_mode == 'ellipse_dimensions':
            found = None
            for sh in self.layer_shapes[idx]:
                if sh.shape_type == 'ellipse':
                    # 楕円情報取得
                    if len(sh.points)>=4:
                        cx, cy, rx, ry = sh.points[:4]
                        cxo = cx+sh.offset_x
                        cyo = cy+sh.offset_y
                        # クリックが中心付近かどうか
                        dist_center = math.hypot(sx-cxo, sy-cyo)
                        # 半径(平均的なもの)と周囲との誤差チェック
                        # ここでは "rx ~ ry" なら円とみなし、
                        #   円周クリック -> dist_center ~ rx の近辺
                        #   中心クリック -> dist_center が rxの10%以下 などとする例
                        if abs(rx-ry) < 1e-6:  # ほぼ円とみなす
                            # 円の半径
                            r_ = rx
                            # クリックが円周近くか？
                            if abs(dist_center - r_)<15:
                                # 円周寸法 = 2*pi*r
                                length = 2*math.pi*r_
                                text = f"Circumference={length:.2f}"
                                # 寸法線は簡易的に: 中心～円周の2点で描画
                                # (円周上のクリック点を正確に出すのは省略)
                                # ここではユーザのタッチ位置sx,syを円周上に正規化して使う
                                dx = sx - cxo
                                dy = sy - cyo
                                dlen = math.hypot(dx, dy)
                                if dlen>1e-7:
                                    ratio = r_/dlen
                                    px = cxo + dx*ratio
                                    py = cyo + dy*ratio
                                    dim_obj = DimensionShape((cxo,cyo), (px,py), text=text, color=(1,1,0,1), offset=20)
                                    self.dimension_shapes.append(dim_obj)
                                    self.update_canvas()
                                    found = sh
                                    break
                            else:
                                # 中心近くなら -> 半径
                                if dist_center < r_*0.2:
                                    text = f"Radius={r_:.2f}"
                                    # 寸法線(中心→円周)
                                    px = cxo + rx  # x軸正方向へ
                                    py = cyo
                                    dim_obj = DimensionShape((cxo,cyo), (px,py), text=text, color=(1,1,0,1), offset=20)
                                    self.dimension_shapes.append(dim_obj)
                                    self.update_canvas()
                                    found = sh
                                    break
                        else:
                            # 楕円の場合の簡易処理(本来は楕円周長は近似式)
                            # とりあえずクリックが中心近くなら -> (rx,ry)を表示
                            if dist_center < min(rx, ry)*0.2:
                                text = f"RadiusX={rx:.2f}, RadiusY={ry:.2f}"
                                px = cxo + rx
                                py = cyo
                                dim_obj = DimensionShape((cxo,cyo), (px,py), text=text, color=(1,1,0,1), offset=20)
                                self.dimension_shapes.append(dim_obj)
                                self.update_canvas()
                                found = sh
                                break
                            else:
                                # 周囲クリック -> 周長近似
                                # Ramanujan近似などあるが、ここでは簡易的に円形近似
                                # -> 2*pi*sqrt((rx^2+ry^2)/2)
                                perimeter = 2*math.pi * math.sqrt((rx*rx+ry*ry)/2.0)
                                text = f"Perimeter~{perimeter:.2f}"
                                # 寸法線(中心→クリック点を半径方向へ正規化)
                                dx = sx - cxo
                                dy = sy - cyo
                                dlen = math.hypot(dx, dy)
                                if dlen>1e-7:
                                    ratio = max(rx,ry)/dlen
                                    px = cxo + dx*ratio
                                    py = cyo + dy*ratio
                                    dim_obj = DimensionShape((cxo,cyo), (px,py), text=text, color=(1,1,0,1), offset=20)
                                    self.dimension_shapes.append(dim_obj)
                                    self.update_canvas()
                                    found = sh
                                    break
            if found:
                return True
            return False

        # -----------------------------------
        # それ以外の既存モード(選択, 回転, 新規図形描画)は従来の処理
        # -----------------------------------

        # ======================= selectモード (移動)
        if self.draw_mode == 'select':
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
            self.drag_mode = 'move'
            self.update_canvas()
            self.update_info_label(self.selected_shape)
            return True

        # ======================= spinモード (回転)
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

        # ========================= 新規図形モード
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
                                    [sx, sy, 0, 0],
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

        mx, my = self.get_snapped_coords(touch.x, touch.y)

        # selectモード → 図形移動
        if self.draw_mode == 'select' and self.selected_shape:
            if self.drag_mode == 'move':
                dx = mx - self.start_x
                dy = my - self.start_y
                self.selected_shape.move(dx, dy)
                self.start_x, self.start_y = mx, my
                self.update_canvas()
                self.update_info_label(self.selected_shape)
                return True

        # spinモード → pivotで回転
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

        # 新規図形モード: ドラッグプレビュー
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

        # selectモード終了
        if self.draw_mode == 'select':
            self.drag_mode = None
            return True

        # spinモード終了
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

class SnapController:
    def __init__(self):
        self.snap_enabled = True
        self.layers = []  # レイヤー情報を格納
        self.layer_shapes = []  # 各レイヤーの図形データを格納

    def get_all_snap_candidates(self):
        # スナップ対象のカテゴリ別リストを初期化
        endpoints = []
        centers = []
        segments = []
        intersections = []

        # 各レイヤーの図形からスナップ対象を分類
        for i, layer_info in enumerate(self.layers):
            if not layer_info['visible']:
                continue
            for shape in self.layer_shapes[i]:
                if shape.shape_type == 'line':
                    # 端点を追加
                    endpoints.extend(shape.get_endpoints())
                    # 線分を追加
                    segments.append((shape.start_point, shape.end_point))
                elif shape.shape_type == 'rectangle':
                    # 四隅を端点として追加
                    endpoints.extend(shape.get_corners())
                    # 中心点を追加
                    centers.append(shape.get_center())
                # 他の図形タイプについても同様に処理

        # 交点の計算は省略
        # return はカテゴリ別のリスト
        return endpoints, centers, segments, intersections

    def get_snapped_coords(self, tx, ty, snap_threshold=15):
        if not self.snap_enabled:
            return (tx, ty)
        
        # スナップ対象を取得
        endpoints, centers, segments, _ = self.get_all_snap_candidates()
        
        # スナップ処理
        for candidates in [endpoints, centers, segments]:
            snapped_point = self.find_near_point(tx, ty, candidates, snap_threshold)
            if snapped_point:
                return snapped_point

        # どのカテゴリにも該当しない場合は元の座標を返す
        return (tx, ty)

    def find_near_point(self, tx, ty, points, threshold):
        # 最も近い点を検索
        closest_point = None
        min_distance = float('inf')
        for px, py in points:
            distance = math.hypot(tx - px, ty - py)
            if distance < threshold and distance < min_distance:
                closest_point = (px, py)
                min_distance = distance
        return closest_point

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

        # スナップ
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

        # -----------------
        # 寸法モード用ボタン
        # -----------------
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

        info_label_layout = BoxLayout(size_hint_y=None, height=50)
        self.add_widget(info_label_layout)

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
