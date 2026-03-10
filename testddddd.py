from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Line, Ellipse, Color
from scipy.interpolate import splprep, splev
import numpy as np
from math import cos, sin, pi, sqrt, atan2, degrees


class DrawWidget(Widget):
    SNAP_THRESHOLD = 50

    def __init__(self, info_label, **kwargs):
        super().__init__(**kwargs)
        self.num_points = 3
        self.radius = 100
        self.points = []
        self.is_polygon_mode = False
        self.line_width = 1
        self.mode = "point"
        self.flattening = 1
        self.info_label = info_label
        self.current_line = None
        self.current_rectangle = None
        self.current_ellipse = None
        self.all_points = []  # すべての図形の点を保持

        # Arc drawing attributes
        self.center_point = None
        self.start_angle = None
        self.end_angle = None
        self.dragging = False
        self.temp_line = None
        self.temp_arc = None
        self.selected_shape = None
        self.is_select_mode = False

    def set_num_points(self, value):
        self.num_points = int(value)
        self.display_info(self.points)

    def set_radius(self, value):
        try:
            self.radius = float(value)
        except ValueError:
            pass
        self.display_info(self.points)

    def set_polygon_mode(self, value):
        self.is_polygon_mode = value

    def set_line_width(self, value):
        self.line_width = value

    def set_flattening(self, value):
        try:
            self.flattening = float(value)
        except ValueError:
            pass

    def calculate_length(self, point1, point2):
        return sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

    def calculate_area(self, points):
        n = len(points)
        area = 0
        for i in range(n):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        return abs(area) / 2.0

    def draw_polygon(self, center_x, center_y):
        if self.num_points < 1:
            return

        with self.canvas:
            self.canvas.clear()
            Color(0, 1, 0)
            angle_step = 2 * pi / self.num_points
            self.points = [
                (center_x + self.radius * cos(i * angle_step), center_y + self.radius * sin(i * angle_step))
                for i in range(self.num_points)
            ]

            for i in range(self.num_points):
                Line(points=[self.points[i][0], self.points[i][1], self.points[(i + 1) % self.num_points][0], self.points[(i + 1) % self.num_points][1]], width=self.line_width)

            self.display_info(self.points)

    def on_touch_down(self, touch):
        x, y = self.snap_to_nearest_point(touch.x, touch.y)

        if self.mode == "select":
            self.select_shape(x, y, touch)
        else:
            if self.mode == "point":
                self.draw_point(x, y)
            elif self.mode == "line":
                self.points.append((x, y))
                self.current_line = Line(points=(x, y, x, y), width=self.line_width)
                self.canvas.add(self.current_line)
            elif self.mode == "rectangle":
                self.points.append((x, y))
                self.current_rectangle = Line(rectangle=(x, y, 0, 0), width=self.line_width)
                self.canvas.add(self.current_rectangle)
            elif self.mode == "ellipse":
                self.points.append((x, y))
                self.current_ellipse = Ellipse(pos=(x, y), size=(0, 0))
                self.canvas.add(self.current_ellipse)
            elif self.mode == "text":
                self.draw_text(touch)
            elif self.mode == "polygon":
                self.draw_polygon(x, y)
            elif self.mode == "free_draw":
                self.draw_free(touch)
            elif self.mode == "clear":
                self.clear_canvas()
            elif self.mode == "arc":
                self.arc_on_touch_down(touch)

        # Call the superclass's on_touch_down method for any additional default behavior
        super().on_touch_down(touch)

    def on_touch_move(self, touch):
        x, y = self.snap_to_nearest_point(touch.x, touch.y)

        if self.mode == "select" and self.selected_shape:
            # 移動中の処理
            dx = touch.x - touch.ud['start_x']
            dy = touch.y - touch.ud['start_y']
            if self.selected_shape:
                self.move_shape(dx, dy)
                touch.ud['start_x'] = touch.x
                touch.ud['start_y'] = touch.y
        else:
            if self.mode == "free_draw" and 'line' in touch.ud:
                touch.ud['line'].points += [x, y]
            elif self.mode == "line" and self.current_line:
                self.current_line.points = [self.points[0][0], self.points[0][1], x, y]
            elif self.mode == "rectangle" and self.current_rectangle:
                if 'shift' in Window.modifiers:
                    x0, y0 = self.points[0]
                    width = x - x0
                    height = y - y0
                    self.current_rectangle.rectangle = (x0 - width / 2, y0 - height / 2, width, height)
                else:
                    x0, y0 = self.points[0]
                    self.current_rectangle.rectangle = (x0, y0, x - x0, y - y0)
            elif self.mode == "ellipse" and self.current_ellipse:
                if 'shift' in Window.modifiers:
                    x0, y0 = self.points[0]
                    w, h = x - x0, y - y0
                    self.current_ellipse.pos = (x0 - w / 2, y0 - h / 2)
                    self.current_ellipse.size = (abs(w), abs(h * (self.flattening if self.mode == "ellipse" else 1)))
                else:
                    x0, y0 = self.points[0]
                    w, h = x - x0, y - y0
                    self.current_ellipse.pos = (min(x0, x), min(y0, y))
                    self.current_ellipse.size = (abs(w), abs(h * (self.flattening if self.mode == "ellipse" else 1)))
            elif self.mode == "arc":
                self.arc_on_touch_move(touch)

        # Call the superclass's on_touch_move method for any additional default behavior
        super().on_touch_move(touch)

    def on_touch_up(self, touch):
        x, y = self.snap_to_nearest_point(touch.x, touch.y)

        if self.mode == "select" and self.selected_shape:
            # 選択した図形の選択を解除
            self.selected_shape = None
        else:
            if self.mode == "line" and self.current_line:
                self.canvas.remove(self.current_line)
                self.points.append((x, y))
                self.all_points.extend(self.points)
                with self.canvas:
                    Color(0, 1, 0)
                    Line(points=[self.points[0][0], self.points[0][1], self.points[1][0], self.points[1][1]], width=self.line_width)
                self.points = []
                self.current_line = None
            elif self.mode == "rectangle" and self.current_rectangle:
                self.canvas.remove(self.current_rectangle)
                x0, y0 = self.points[0]
                if 'shift' in Window.modifiers:
                    width = x - x0
                    height = y - y0
                    self.all_points.extend([(x0 - width / 2, y0 - height / 2), (x0 + width / 2, y0 + height / 2)])
                    with self.canvas:
                        Color(0, 1, 0)
                        Line(rectangle=(x0 - width / 2, y0 - height / 2, width, height), width=self.line_width)
                else:
                    self.all_points.extend([(x0, y0), (x, y)])
                    with self.canvas:
                        Color(0, 1, 0)
                        Line(rectangle=(x0, y0, x - x0, y - y0), width=self.line_width)
                self.points = []
                self.current_rectangle = None
            elif (self.mode == "ellipse") and self.current_ellipse:
                self.canvas.remove(self.current_ellipse)
                x0, y0 = self.points[0]
                if 'shift' in Window.modifiers:
                    w, h = x - x0, y - y0
                    with self.canvas:
                        Color(0, 1, 0)
                        Ellipse(pos=(x0 - w / 2, y0 - h / 2), size=(abs(w), abs(h * (self.flattening if self.mode == "ellipse" else 1))), width=self.line_width)
                else:
                    w, h = x - x0, y - y0
                    with self.canvas:
                        Color(0, 1, 0)
                        Ellipse(pos=(min(x0, x), min(y0, y)), size=(abs(w), abs(h * (self.flattening if self.mode == "ellipse" else 1))), width=self.line_width)
                self.points = []
                self.current_ellipse = None
            elif self.mode == "arc":
                self.arc_on_touch_up(touch)

        # Call the superclass's on_touch_up method for any additional default behavior
        super().on_touch_up(touch)

    def snap_to_nearest_point(self, x, y):
        for point in self.all_points:
            if self.calculate_length((x, y), point) < self.SNAP_THRESHOLD:
                return point
        return x, y

    def draw_point(self, x, y):
        with self.canvas:
            Color(0, 1, 0)
            d = 10
            Ellipse(pos=(x - d / 2, y - d / 2), size=(d, d))
        self.points.append((x, y))
        self.all_points.append((x, y))
        self.display_info(self.points)

    def draw_free(self, touch):
        with self.canvas:
            Color(0, 1, 0)
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=self.line_width)
            self.all_points.append((touch.x, touch.y))
        self.display_info(self.all_points)

    def draw_text(self, touch):
        text = "Sample Text"
        with self.canvas:
            Color(0, 1, 0)
            Label(text=text, center=(touch.x, touch.y))
        self.points.append((touch.x, touch.y))
        self.all_points.append((touch.x, touch.y))
        self.display_info(self.points)

    def display_info(self, points):
        info = f"Points: {points}\n"
        info += f"Length: {self.calculate_total_length(points):.2f}\n"
        info += f"Area: {self.calculate_area(points):.2f}\n"
        self.info_label.text = info

    def calculate_total_length(self, points):
        return sum(self.calculate_length(points[i], points[i + 1]) for i in range(len(points) - 1))

    def arc_on_touch_down(self, touch):
        x, y = self.snap_to_nearest_point(touch.x, touch.y)
        if not self.dragging:
            if self.center_point is None:
                self.center_point = (x, y)
                with self.canvas:
                    Color(1, 0, 0)
                    self.temp_arc = Line(circle=(self.center_point[0], self.center_point[1], 0), width=self.line_width)
                    self.dragging = True
            elif self.start_angle is None:
                self.start_angle = self.calculate_angle(self.center_point, (x, y))
                with self.canvas:
                    Color(1, 0, 0)
                    self.temp_line = Line(points=[self.center_point[0], self.center_point[1], x, y], width=self.line_width)
            elif self.end_angle is None:
                self.end_angle = self.calculate_angle(self.center_point, (x, y))
                self.draw_arc(self.center_point, self.start_angle, self.end_angle)
                self.center_point = None
                self.start_angle = None
                self.end_angle = None
                self.dragging = False
        else:
            self.arc_on_touch_move(touch)

    def arc_on_touch_move(self, touch):
        if self.dragging and self.temp_arc:
            x, y = self.snap_to_nearest_point(touch.x, touch.y)
            self.canvas.remove(self.temp_arc)
            self.temp_arc = Line(circle=(self.center_point[0], self.center_point[1], self.calculate_length(self.center_point, (x, y))), width=self.line_width)
            self.canvas.add(self.temp_arc)

    def arc_on_touch_up(self, touch):
        x, y = self.snap_to_nearest_point(touch.x, touch.y)
        self.canvas.remove(self.temp_arc)
        self.temp_arc = None
        if self.center_point and self.start_angle is None:
            self.start_angle = self.calculate_angle(self.center_point, (x, y))
            self.temp_line = Line(points=[self.center_point[0], self.center_point[1], x, y], width=self.line_width)
            self.canvas.add(self.temp_line)
        elif self.center_point and self.start_angle:
            self.end_angle = self.calculate_angle(self.center_point, (x, y))
            self.canvas.remove(self.temp_line)
            self.temp_line = None
            self.draw_arc(self.center_point, self.start_angle, self.end_angle)
            self.center_point = None
            self.start_angle = None
            self.end_angle = None
            self.dragging = False

    def calculate_angle(self, center, point):
        return degrees(atan2(point[1] - center[1], point[0] - center[0]))

    def draw_arc(self, center, start_angle, end_angle):
        with self.canvas:
            Color(1, 0, 0)
            Line(circle=(center[0], center[1], self.calculate_length(center, (center[0] + cos(start_angle), center[1] + sin(start_angle))), start_angle, end_angle), width=self.line_width)

    def clear_canvas(self):
        self.canvas.clear()
        self.points = []
        self.all_points = []
        self.info_label.text = ""

    def draw_bezier_curve(self, points):
        if len(points) < 2:
            return

        def bezier(t, p0, p1, p2, p3):
            return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3

        with self.canvas:
            Color(1, 0, 0)
            step = 0.01
            curve_points = []

            for t in range(0, 100):
                t /= 100
                x = bezier(t, points[0][0], points[1][0], points[2][0], points[3][0])
                y = bezier(t, points[0][1], points[1][1], points[2][1], points[3][1])
                curve_points.extend([x, y])

            Line(points=curve_points, width=self.line_width)

    def draw_spline_curve(self, points):
        if len(points) < 2:
            return

        x = [p[0] for p in points]
        y = [p[1] for p in points]

        tck, u = splprep([x, y], s=0)
        u_fine = np.linspace(0, 1, 100)
        x_fine, y_fine = splev(u_fine, tck)

        with self.canvas:
            Color(0, 0, 1)
            Line(points=[(x_fine[i], y_fine[i]) for i in range(len(x_fine))], width=self.line_width)

    def select_shape(self, x, y, touch):
        self.selected_shape = None
        for shape in self.canvas.children:
            if hasattr(shape, 'rectangle'):
                if shape.rectangle[0] <= x <= shape.rectangle[0] + shape.rectangle[2] and \
                shape.rectangle[1] <= y <= shape.rectangle[1] + shape.rectangle[3]:
                    self.selected_shape = shape
                    print(f"Selected shape with rectangle: {shape.rectangle}")
                    break
            elif hasattr(shape, 'pos'):
                if (shape.pos[0] <= x <= shape.pos[0] + shape.size[0]) and \
                (shape.pos[1] <= y <= shape.pos[1] + shape.size[1]):
                    self.selected_shape = shape
                    print(f"Selected shape with pos: {shape.pos} and size: {shape.size}")
                    break

        if self.selected_shape:
            touch.ud['start_x'] = x
            touch.ud['start_y'] = y
            print(f"Shape selected at: ({x}, {y})")
        else:
            print(f"No shape selected at: ({x}, {y})")

    def move_shape(self, dx, dy):
        if not self.selected_shape:
            return

        if hasattr(self.selected_shape, 'rectangle'):
            x, y, w, h = self.selected_shape.rectangle
            self.selected_shape.rectangle = (x + dx, y + dy, w, h)
        elif hasattr(self.selected_shape, 'pos'):
            x, y = self.selected_shape.pos
            self.selected_shape.pos = (x + dx, y + dy)

        # 曲線の更新
        self.update_curves()

    def update_curves(self):
        # すべての曲線を再描画するための処理
        self.canvas.clear()
        for shape in self.canvas.children:
            if hasattr(shape, 'rectangle'):
                Color(0, 1, 0)
                Line(rectangle=shape.rectangle, width=self.line_width)
            elif hasattr(shape, 'pos'):
                if hasattr(shape, 'size'):
                    Color(0, 1, 0)
                    Ellipse(pos=shape.pos, size=shape.size)
                elif hasattr(shape, 'circle'):
                    Color(1, 0, 0)
                    Line(circle=shape.circle, width=self.line_width)
        self.display_info(self.all_points)

class DrawingApp(App):
    def build(self):
        self.title = "Drawing App"
        layout = BoxLayout(orientation='vertical')

        self.info_label = Label(size_hint=(1, 0.1), text="Point coordinates, line length, and area will be displayed here")
        layout.add_widget(self.info_label)

        self.drawing_widget = DrawWidget(info_label=self.info_label)
        layout.add_widget(self.drawing_widget)

        control_panel = BoxLayout(size_hint=(1, 0.1))

        self.point_button = ToggleButton(text="Point")
        self.point_button.bind(on_release=self.set_point_mode)
        control_panel.add_widget(self.point_button)

        self.line_button = ToggleButton(text="Line")
        self.line_button.bind(on_release=self.set_line_mode)
        control_panel.add_widget(self.line_button)

        self.rectangle_button = ToggleButton(text="Rectangle")
        self.rectangle_button.bind(on_release=self.set_rectangle_mode)
        control_panel.add_widget(self.rectangle_button)

        self.ellipse_button = ToggleButton(text="Ellipse")
        self.ellipse_button.bind(on_release=self.set_ellipse_mode)
        control_panel.add_widget(self.ellipse_button)

        self.arc_button = ToggleButton(text="Arc")
        self.arc_button.bind(on_release=self.set_arc_mode)
        control_panel.add_widget(self.arc_button)

        self.polygon_button = ToggleButton(text="Polygon")
        self.polygon_button.bind(on_release=self.set_polygon_mode)
        control_panel.add_widget(self.polygon_button)

        self.free_draw_button = ToggleButton(text="Free Draw")
        self.free_draw_button.bind(on_release=self.set_free_draw_mode)
        control_panel.add_widget(self.free_draw_button)

        self.text_button = ToggleButton(text="Text")
        self.text_button.bind(on_release=self.set_text_mode)
        control_panel.add_widget(self.text_button)

        self.clear_button = ToggleButton(text="Clear")
        self.clear_button.bind(on_release=self.set_clear_mode)
        control_panel.add_widget(self.clear_button)

        self.bezier_button = ToggleButton(text="Bézier")
        self.bezier_button.bind(on_release=self.set_bezier_mode)
        control_panel.add_widget(self.bezier_button)

        self.spline_button = ToggleButton(text="Spline")
        self.spline_button.bind(on_release=self.set_spline_mode)
        control_panel.add_widget(self.spline_button)

        self.select_button = ToggleButton(text="Select")
        self.select_button.bind(on_release=self.set_select_mode)
        control_panel.add_widget(self.select_button)

        layout.add_widget(control_panel)

        return layout

    def set_point_mode(self, instance):
        self.drawing_widget.mode = "point"
        self.deselect_buttons(instance)

    def set_line_mode(self, instance):
        self.drawing_widget.mode = "line"
        self.deselect_buttons(instance)

    def set_rectangle_mode(self, instance):
        self.drawing_widget.mode = "rectangle"
        self.deselect_buttons(instance)

    def set_ellipse_mode(self, instance):
        self.drawing_widget.mode = "ellipse"
        self.deselect_buttons(instance)

    def set_arc_mode(self, instance):
        self.drawing_widget.mode = "arc"
        self.deselect_buttons(instance)

    def set_polygon_mode(self, instance):
        self.drawing_widget.mode = "polygon"
        self.deselect_buttons(instance)

    def set_free_draw_mode(self, instance):
        self.drawing_widget.mode = "free_draw"
        self.deselect_buttons(instance)

    def set_text_mode(self, instance):
        self.drawing_widget.mode = "text"
        self.deselect_buttons(instance)

    def set_clear_mode(self, instance):
        self.drawing_widget.mode = "clear"
        self.deselect_buttons(instance)

    def deselect_buttons(self, active_button):
        buttons = [self.point_button, self.line_button, self.rectangle_button, self.ellipse_button, self.arc_button,
                   self.polygon_button, self.free_draw_button, self.text_button, self.clear_button]
        for button in buttons:
            if button != active_button:
                button.state = "normal"

    def set_bezier_mode(self, instance):
        self.drawing_widget.mode = "bezier"
        self.deselect_buttons(instance)
        self.drawing_widget.draw_bezier_curve(self.drawing_widget.points)

    def set_spline_mode(self, instance):
        self.drawing_widget.mode = "spline"
        self.deselect_buttons(instance)
        self.drawing_widget.draw_spline_curve(self.drawing_widget.points)

    def set_select_mode(self, instance):
        self.drawing_widget.mode = "select"
        self.deselect_buttons(instance)

if __name__ == "__main__":
    DrawingApp().run()