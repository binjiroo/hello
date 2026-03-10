# labels.py
from kivy.uix.treeview import TreeViewLabel
from kivy.graphics import Rectangle, Line, Color
from kivy.properties import ColorProperty, NumericProperty

class CustomTreeViewLabel(TreeViewLabel):
    background_color = ColorProperty((1, 1, 1, 1))
    border_color = ColorProperty((0, 0, 0, 1))
    border_width = NumericProperty(1)
    
    def __init__(self, **kwargs):
        super(CustomTreeViewLabel, self).__init__(**kwargs)
        with self.canvas.before:
            # 背景色の設定
            self.bg_color_instruction = Color(rgba=self.background_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            # 枠線色の設定
            self.border_color_instruction = Color(rgba=self.border_color)
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=self.border_width)
        
        # プロパティの更新に合わせて描画を更新
        self.bind(pos=self.update_graphics, size=self.update_graphics,
                  background_color=self.update_graphics,
                  border_color=self.update_graphics,
                  border_width=self.update_graphics)

    def update_graphics(self, *args):
        # 背景色の更新
        self.bg_color_instruction.rgba = self.background_color
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        
        # 枠線の更新
        self.border_color_instruction.rgba = self.border_color
        self.border.rectangle = (self.x, self.y, self.width, self.height)
        self.border.width = self.border_width
