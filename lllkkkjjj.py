import kivy
from kivy.app import App
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, Line, Rectangle, PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.core.window import Window
from kivy.properties import ObjectProperty

kivy.require('1.11.1')

# モード定数
MODE_DRAW_LINE = 1
MODE_DRAW_RECT = 2
MODE_PAN_ZOOM   = 3

def get_scatter_inverse(scatter):
    """
    scatter の変換行列の逆行列を算出します
    Scatter は内部で transform というMatrixを持っていますが、
    ここでは簡易的に scale と pos に対する逆変換を行います。
    
    ※ 複雑な変換（rotation など）がない場合での例です。
    """
    inv_scale = 1.0 / scatter.scale
    inv_tx = -scatter.pos[0] * inv_scale
    inv_ty = -scatter.pos[1] * inv_scale
    return inv_scale, inv_tx, inv_ty

class DrawWidget(Widget):
    scatter_ref = ObjectProperty(None)  # 親のScatterウィジェットを参照するプロパティ

    def __init__(self, **kwargs):
        super(DrawWidget, self).__init__(**kwargs)
        self.mode = MODE_DRAW_LINE
        self.start_pos = None
        self.current_obj = None

    def set_mode(self, mode):
        self.mode = mode

    def _convert_touch(self, touch):
        """
        タッチ座標 (touch.pos) を scatter の変換を考慮してキャンバス座標に変換する。
        ここでは、Scatter の scale と pos の逆変換を自前で適用します。
        """
        if not self.scatter_ref:
            return touch.pos
        inv_scale, inv_tx, inv_ty = get_scatter_inverse(self.scatter_ref)
        # touch.pos はウィンドウ座標ですが、scatter.to_widget() は既に内部で逆変換してくれるはずなので、
        # ここでは scatter の平行移動とスケールを補正する
        x, y = touch.pos
        # まず scatter の to_widget で、Scatter のローカル座標に変換
        local = self.scatter_ref.to_widget(x, y, relative=False)
        # 次に、上記逆変換を適用
        cx = (local[0] + inv_tx) * inv_scale
        cy = (local[1] + inv_ty) * inv_scale
        return (cx, cy)

    def on_touch_down(self, touch):
        if self.mode == MODE_PAN_ZOOM:
            return super(DrawWidget, self).on_touch_down(touch)
        # 変換後の座標を取得
        local_pos = self._convert_touch(touch)
        self.start_pos = local_pos

        with self.canvas:
            Color(1, 0, 0)
            if self.mode == MODE_DRAW_LINE:
                self.current_obj = Line(points=[local_pos[0], local_pos[1]], width=2)
            elif self.mode == MODE_DRAW_RECT:
                self.current_obj = Rectangle(pos=local_pos, size=(0, 0))
        return True

    def on_touch_move(self, touch):
        if self.mode == MODE_PAN_ZOOM:
            return super(DrawWidget, self).on_touch_move(touch)
        if not self.start_pos:
            return
        local_pos = self._convert_touch(touch)
        if self.mode == MODE_DRAW_LINE and self.current_obj:
            self.current_obj.points = [self.start_pos[0], self.start_pos[1], local_pos[0], local_pos[1]]
        elif self.mode == MODE_DRAW_RECT and self.current_obj:
            x1, y1 = self.start_pos
            x2, y2 = local_pos
            pos = (min(x1, x2), min(y1, y2))
            size = (abs(x2 - x1), abs(y2 - y1))
            self.current_obj.pos = pos
            self.current_obj.size = size
            print(pos)
        return True

    def on_touch_up(self, touch):
        if self.mode == MODE_PAN_ZOOM:
            return super(DrawWidget, self).on_touch_up(touch)
        self.start_pos = None
        self.current_obj = None
        return True

class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.orientation = "vertical"

        # 操作用パネル
        panel = BoxLayout(size_hint_y=None, height=50)
        btn_line = Button(text="線描画モード")
        btn_rect = Button(text="矩形描画モード")
        btn_pan_zoom = Button(text="パン・ズームモード")
        btn_reset = Button(text="リセット")
        btn_line.bind(on_release=self.set_line_mode)
        btn_rect.bind(on_release=self.set_rect_mode)
        btn_pan_zoom.bind(on_release=self.set_pan_zoom_mode)
        btn_reset.bind(on_release=self.reset_canvas)
        panel.add_widget(btn_line)
        panel.add_widget(btn_rect)
        panel.add_widget(btn_pan_zoom)
        panel.add_widget(btn_reset)
        self.add_widget(panel)

        # 描画領域はウィンドウサイズより広くする（例：2000x2000）
        canvas_width = 2000
        canvas_height = 2000
        self.draw_widget = DrawWidget(size=(canvas_width, canvas_height))
        self.draw_widget.size_hint = (None, None)

        # Scatterによるパン・ズーム
        self.scatter = Scatter(do_rotation=False, do_translation=True, do_scale=True,
                               scale=1, scale_min=0.5, scale_max=4)
        self.scatter.add_widget(self.draw_widget)
        self.add_widget(self.scatter)

        # DrawWidget に Scatter の参照をセット
        self.draw_widget.scatter_ref = self.scatter

        # 初期モードを線描画に設定
        self.current_mode = MODE_DRAW_LINE
        self.draw_widget.set_mode(self.current_mode)

    def set_line_mode(self, instance):
        self.current_mode = MODE_DRAW_LINE
        self.draw_widget.set_mode(self.current_mode)
        self.scatter.do_translation = False
        self.scatter.do_scale = False
        print("線描画モードに切り替え")

    def set_rect_mode(self, instance):
        self.current_mode = MODE_DRAW_RECT
        self.draw_widget.set_mode(self.current_mode)
        self.scatter.do_translation = False
        self.scatter.do_scale = False
        print("矩形描画モードに切り替え")

    def set_pan_zoom_mode(self, instance):
        self.current_mode = MODE_PAN_ZOOM
        self.draw_widget.set_mode(self.current_mode)
        self.scatter.do_translation = True
        self.scatter.do_scale = True
        print("パン・ズームモードに切り替え")

    def reset_canvas(self, instance):
        self.scatter.scale = 1
        self.scatter.pos = (0, 0)
        self.draw_widget.canvas.clear()
        print("キャンバスをリセット")

class CanvasApp(App):
    def build(self):
        return RootWidget()

if __name__ == '__main__':
    CanvasApp().run()
