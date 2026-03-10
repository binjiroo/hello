# spinner_layout.py
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label

class SpinnerLayout(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.spacing = 5
        self.padding = 10

        self.steel_data = {
            "H型鋼(広幅)": "H-200x100x5.5x8",
            "H型鋼(中幅)": "H-150x75x5.0x7",
            "H型鋼(細幅)": "H-100x50x4.5x6",
            "H型鋼(広幅)レ型溶接": "H-200x100x5.5x8",
            "H型鋼(中幅)レ型溶接": "H-150x75x5.0x7",
            "H型鋼(細幅)レ型溶接": "H-100x50x4.5x6",
            "コラムレ型溶接": "□-250x250x9",
            "チャンネル": "C-150x75x9",
            "アングル": "L-100x100x10",
            "角パイプ": "R-100x100x10",
            "リップ鋼": "L-100x100x10",
        }

        for name in self.steel_data:
            spinner = Spinner(text=name, values=[self.steel_data[name]], size_hint_x=None, width=200)
            spinner.bind(text=self.on_spinner_select)  # 自身のメソッドを呼び出し
            self.add_widget(spinner)

    def on_spinner_select(self, spinner, text):
        # スピナーが選択されたときの処理
        if text in self.steel_data:
            self.parent.set_weld_length(self.steel_data[text])  # 親ウィジェットのメソッドを呼び出し
