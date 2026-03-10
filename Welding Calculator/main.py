from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.core.clipboard import Clipboard
import math

class WeldingCalculator(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_steel_size = ""  # 選択された鋼材サイズを保存
        self.cols = 4  # ラベル、空ウィジェット、入力、スピナーの4列
        self.spacing = 2
        self.padding = 1

        # 入力データ保持用
        self.inputs = {}

        # スピナーと全周計算のマッピング
        self.spinner_to_perimeter = {
            "H-100x50x5x7": lambda: self.calculate_perimeter(100, 50, 5, 7, 8),
            "H-175x90x5x8": lambda: self.calculate_perimeter(175, 90, 5, 8, 8),
            "H-198x99x4.5x7": lambda: self.calculate_perimeter(198, 99, 4.5, 7, 8),
            "H-200x100x5.5x8": lambda: self.calculate_perimeter(200, 100, 5.5, 8, 8),
            "H-248x124x5x8": lambda: self.calculate_perimeter(248, 124, 5, 8, 8),
            "H-250x125x6x9": lambda: self.calculate_perimeter(250, 125, 6, 9, 8),
            "H-298x149x5.5x8": lambda: self.calculate_perimeter(298, 149, 5.5, 8, 13),
            "H-300x150x6.5x9": lambda: self.calculate_perimeter(300, 150, 6.5, 9, 13),
            "H-346x174x6x9": lambda: self.calculate_perimeter(346, 174, 6, 9, 13),
            "H-350x175x7x11": lambda: self.calculate_perimeter(350, 175, 7, 11, 13),
            "H-396x199x7x11": lambda: self.calculate_perimeter(396, 199, 7, 11, 13),
            "H-400x200x8x13": lambda: self.calculate_perimeter(400, 200, 8, 13, 13),
            "H-148x100x6x9": lambda: self.calculate_perimeter(148, 100, 6, 9, 8),
            "H-194x150x6x9": lambda: self.calculate_perimeter(194, 150, 6, 9, 8),
            "H-244x175x7x11": lambda: self.calculate_perimeter(244, 175, 7, 11, 13),
            "H-294x200x8x12": lambda: self.calculate_perimeter(294, 200, 8, 12, 13),
            "H-340x250x9x14": lambda: self.calculate_perimeter(340, 250, 9, 14, 13),
            "H-100x100x6x8": lambda: self.calculate_perimeter(100, 100, 6, 8, 8),
            "H-125x125x6.5x9": lambda: self.calculate_perimeter(125, 125, 6.5, 9, 8),
            "H-150x150x7x10": lambda: self.calculate_perimeter(150, 150, 7, 10, 8),
            "H-175x175x7.5x11": lambda: self.calculate_perimeter(175, 175, 7.5, 11, 13),
            "H-200x200x8x12": lambda: self.calculate_perimeter(200, 200, 8, 12, 13),
            "H-250x250x9x14": lambda: self.calculate_perimeter(250, 250, 9, 14, 13),
            "H-300x300x10x15": lambda: self.calculate_perimeter(300, 300, 10, 15, 13),
            "□-200x200x9": lambda: self.calculate_coulme_perimeter(200, 200, 9, 22.5),
            "□-200x200x12": lambda: self.calculate_coulme_perimeter(200, 200, 12, 30),
            "□-200x200x16": lambda: self.calculate_coulme_perimeter(200, 200, 16, 40),
            "□-250x250x9": lambda: self.calculate_coulme_perimeter(250, 250, 9, 22.5),
            "□-250x250x12": lambda: self.calculate_coulme_perimeter(250, 250, 12, 30),
            "□-250x250x16": lambda: self.calculate_coulme_perimeter(250, 250, 16, 40),
            "□-250x250x19": lambda: self.calculate_coulme_perimeter(250, 250, 19, 47.5),
            "□-300x300x9": lambda: self.calculate_coulme_perimeter(300, 300, 9, 22.5),
            "□-300x300x12": lambda: self.calculate_coulme_perimeter(300, 300, 12, 30),
            "□-300x300x16": lambda: self.calculate_coulme_perimeter(300, 300, 16, 40),
            "□-300x300x19": lambda: self.calculate_coulme_perimeter(300, 300, 19, 47.5),
            "□-300x300x22": lambda: self.calculate_coulme_perimeter(300, 300, 22, 55),
            "□-350x350x9": lambda: self.calculate_coulme_perimeter(300, 300, 10, 15, 13),
            "□-350x350x12": lambda: self.calculate_coulme_perimeter(300, 300, 10, 15, 13),
            "□-350x350x16": lambda: self.calculate_coulme_perimeter(300, 300, 10, 15, 13),
            "□-350x350x19": lambda: self.calculate_coulme_perimeter(300, 300, 10, 15, 13),
            "□-350x350x22": lambda: self.calculate_coulme_perimeter(300, 300, 10, 15, 13),
            "□-400x400x9": lambda: self.calculate_coulme_perimeter(300, 300, 10, 15, 13),
            "□-400x400x12": lambda: self.calculate_coulme_perimeter(300, 300, 10, 15, 13),
            "□-400x400x16": lambda: self.calculate_coulme_perimeter(300, 300, 10, 15, 13),
            "□-400x400x19": lambda: self.calculate_coulme_perimeter(300, 300, 10, 15, 13),
            "□-400x400x22": lambda: self.calculate_coulme_perimeter(300, 300, 10, 15, 13),
        }

        # 行を追加するヘルパーメソッド
        def add_row_with_spinner(label_text, spinner_values, input_key, additional_spinner_values, additional_key=None):
            self.add_widget(Label(text=label_text, size_hint_x=None, width=250, font_size=18))
            input_field = TextInput(text="0", multiline=False, size_hint_x=None, width=80, halign="center", font_size=18)
            self.add_widget(input_field)
            self.inputs[input_key] = input_field  # 入力フィールドを辞書に保存
            
            # 2つ目スピナー追加
            additional_spinner = Spinner(
                text=additional_spinner_values[0],
                values=additional_spinner_values,
                size_hint_x=None,
                width=160,
                font_size=18
            )

            # 2つ目が呼び出されるときのbind
            if additional_key is not None:
                # 2つ目のスピナーは additional_key で管理
                additional_spinner.bind(text=lambda spinner, value: self.update_input_field(value, additional_key))
                # 何かしら辞書に登録するなら
                self.inputs[f"{additional_key}_spinner"] = additional_spinner
            else:
                # 2つ目のスピナーも従来通り input_key で扱う
                additional_spinner.bind(text=lambda spinner, value: self.update_input_field(value, input_key))
                self.inputs[f"{input_key}_additional_spinner"] = additional_spinner

            self.add_widget(additional_spinner)


            # 元々のスピナーの追加
            spinner = Spinner(
                text=spinner_values[0],
                values=spinner_values,
                size_hint_x=None,
                width=200,
                font_size=18
            )
            self.add_widget(spinner)
            self.inputs[f"{input_key}_spinner"] = spinner  # スピナーを辞書で管理

            # スピナーの選択時イベント
            def on_spinner_select(spinner_instance, text):
                if spinner_instance == spinner:
                    # スピナーで選択されたサイズを保存
                    self.selected_steel_size = text
                    # 元のスピナーの選択時
                    if text in self.spinner_to_perimeter:
                        result = self.spinner_to_perimeter[text]()
                        self.inputs["weld_length"].text = f"{result:.2f}"
                elif spinner_instance == additional_spinner:
                    # 新しいスピナーの選択時
                    print(f"新しいスピナーで選択: {text}")
                    

            # スピナーにイベントをバインド
            spinner.bind(text=on_spinner_select)
            additional_spinner.bind(text=on_spinner_select)

        # 入力行を追加
        add_row_with_spinner(
            "ワイヤー直径 (d) [mm]:",
            [
                "H型鋼(広幅)", "H-100x100x6x8", "H-125x125x6.5x9", "H-150x150x7x10",
                "H-175x175x7.5x11", "H-200x200x8x12", "H-250x250x9x14", "H-300x300x10x15"
            ],
            "wire_diameter",
            ["ワイヤー直径(d)", "0.6", "0.8", "1.0", "1.2", "1.4", "1.8", "2.0", "2.4", "3.0", "3.2"]
            )
        add_row_with_spinner(
            "ビード高さ (h) [mm]:",
            [
                "H型鋼(中幅)", "H-148x100x6x9", "H-194x150x6x9", 
                "H-244x175x7x11", "H-294x200x8x12", "H-340x250x9x14"
            ],
            "beed_height",
            ["ビード高さ(h)", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
             )
        add_row_with_spinner(
            "ビード幅 (w) [mm]:",
            [
                "H型鋼(細幅)", "H-100x50x5x7", "H-175x90x5x8", "H-198x99x4.5x7",
                "H-200x100x5.5x8", "H-248x124x5x8", "H-250x125x6x9",
                "H-298x149x5.5x8", "H-300x150x6.5x9", "H-346x174x6x9",
                "H-350x175x7x11", "H-396x199x7x11", "H-400x200x8x13"
            ],
            "beed_width",
            ["ビード幅(w)", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
            )
        add_row_with_spinner(
            "溶着率 (η) [%]:", 
            [
                "H型鋼(広幅)レ型溶接", "H-100x100x6x8", "H-125x125x6.5x9", "H-150x150x7x10",
                "H-175x175x7.5x11", "H-200x200x8x12", "H-250x250x9x14", "H-300x300x10x15"
            ],
            "efficiency",
            ["溶着率(η)", "50", "55", "60", "65", "70", "75", "80", "85", "90", "95", "100"]
            )
        add_row_with_spinner(
            "溶接長さ (L) [mm]:", 
            [
                "H型鋼(中幅)レ型溶接", "H-148x100x6x9", "H-194x150x6x9", "H-244x175x7x11",
                "H-294x200x8x12", "H-340x250x9x14"
            ], 
            "weld_length",
            ["ワイヤー重量", "5", "15", "20", "25", "300"],
            additional_key="wire_weight_key"  # ← 任意のキー名
             )

        # 計算結果保持用
        self.results = {}

        # 計算ボタンと結果表示を配置するヘルパーメソッド
        def add_calculation_row(label_text, button_text, spinner_values, calc_method, result_key):
            self.add_widget(Label(text=label_text, size_hint_x=None, width=250, font_size=18))
            result_label = Label(text="0", size_hint_x=None, width=80, font_size=18)
            self.results[result_key] = result_label  # 計算結果ラベルを辞書に保存
            self.add_widget(result_label)
            calc_button = Button(text=button_text, size_hint_x=None, width=160, font_size=18)
            calc_button.bind(on_press=calc_method)  # ボタンに計算メソッドをバインド
            self.add_widget(calc_button)
            
            def on_spinner_select(spinner_instance, text):
                if text in self.spinner_to_perimeter:
                    # スピナーで選択されたサイズを保存
                    self.selected_steel_size = text
                    # H型鋼の全周計算結果をweld_lengthに表示
                    result = self.spinner_to_perimeter[text]()
                    self.inputs["weld_length"].text = f"{result:.2f}"  # 少数2桁に四捨五入して表示
                    # ここで対応する計算メソッドを呼び出す
                    calc_method(None)  # Noneを渡してインスタンスをシミュレートする

            spinner = Spinner(text=spinner_values[0], values=spinner_values, size_hint_x=None, width=200, font_size=18)
            spinner.bind(text=on_spinner_select)
            self.add_widget(spinner)

        # 計算行を追加
        add_calculation_row("ビード断面積 (A):", "計算", [
            "H型鋼(細幅)レ型溶接", "H-100x50x5x7", "H-175x90x5x8", "H-198x99x4.5x7",
            "H-200x100x5.5x8", "H-248x124x5x8", "H-250x125x6x9",
            "H-298x149x5.5x8", "H-300x150x6.5x9", "H-346x174x6x9",
            "H-350x175x7x11", "H-396x199x7x11", "H-400x200x8x13"
        ], self.calculate_beed_area, "beed_area")
        add_calculation_row("ビード体積 (V):", "計算", [
            "コラムレ型溶接", "□-200x200x9", "□-200x200x12", "□-200x200x16", 
            "□-250x250x9", "□-250x250x12", "□-250x250x16",  "□-250x250x19",
            "□-300x300x9", "□-300x300x12", "□-300x300x16",  "□-300x300x19",  "□-300x300x22", 
            "□-350x350x9", "□-350x350x12", "□-350x350x16",  "□-350x350x19",  "□-350x350x22",
            "□-400x400x9", "□-400x400x12", "□-400x400x16",  "□-400x400x19",  "□-400x400x22"
            ], self.calculate_beed_volume, "beed_volume")
        add_calculation_row("ワイヤー断面積 (a):", "計算", ["チャンネル"], self.calculate_wire_area, "wire_area")
        add_calculation_row("必要ワイヤー長さⅠ (Lw):", "計算", ["アングル"], self.calculate_wire_length, "wire_length")
        add_calculation_row("必要ワイヤー長さⅡ (Lwη):", "計算", ["角パイプ"], self.calculate_wire_efficiency_length, "efficient_length")
        add_calculation_row(
            "必要ワイヤー重量 (Wwη):",
            "計算",
            ["リップ鋼"],  # スピナー未使用でもOKなので適当なリストを入れておく
            self.calculate_wire_efficiency_weight,
            "wire_weight"
        )

        # 空の最後の行を修正
        self.wire_weight_title_label = Label(text="使用ワイヤー重量[kg]:", size_hint_x=None, width=250, font_size=18)
        self.add_widget(self.wire_weight_title_label)

        self.wire_weight_value_label = Label(text="0", size_hint_x=None, width=80, font_size=18)
        self.add_widget(self.wire_weight_value_label)

        copy_button = Button(text="コピー", size_hint_x=None, width=160, font_size=18)
        copy_button.bind(on_press=self.copy_to_clipboard)
        self.add_widget(copy_button)

        self.add_widget(Spinner(text="ガセットプレート", values=["ガセットプレート"], size_hint_x=None, width=200, font_size=18))

        # 空の最後の行
        self.setwire_weight_title_label = Label(text="ワイヤー使用率[%]:", size_hint_x=None, width=250, font_size=18)
        self.add_widget(self.setwire_weight_title_label)

        wire_ratio_label = Label(text="0", size_hint_x=None, width=80, font_size=18)
        self.results["wire_ratio"] = wire_ratio_label
        self.add_widget(wire_ratio_label)

        setwire_button = Button(text="計算", size_hint_x=None, width=160, font_size=18)
        setwire_button.bind(on_press=self.setwire_to_weight)
        self.add_widget(setwire_button)

        self.add_widget(Spinner(text="リブプレート", values=["リブプレート"], size_hint_x=None, width=200, font_size=18))

    # スピナーで選択された値を入力フィールドに反映させるメソッド
    def update_input_field(self, value, input_key):
        if input_key in self.inputs:
            # 入力欄があればそちらに反映
            input_field = self.inputs[input_key]
            input_field.text = value

        # wire_weight_key のときだけ「使用ワイヤー重量ラベル」を更新
        if input_key == "wire_weight_key":
            self.wire_weight_value_label.text = f"{value}"

    # 計算メソッド
    def calculate_beed_area(self, instance):
        w = float(self.inputs["beed_width"].text)
        h = float(self.inputs["beed_height"].text)
        area = 0.5 * w * h
        self.results["beed_area"].text = f"{round(area, 2):.2f}"  # 少数2桁に四捨五入して表示

    def calculate_beed_volume(self, instance):
        area = float(self.results["beed_area"].text)
        length = float(self.inputs["weld_length"].text)
        volume = area * length
        self.results["beed_volume"].text = f"{round(volume, 2):.2f}"  # 少数2桁に四捨五入して表示

    def calculate_wire_area(self, instance):
        d = float(self.inputs["wire_diameter"].text) / 2
        area = math.pi * d ** 2
        self.results["wire_area"].text = f"{round(area, 2):.2f}"  # 少数2桁に四捨五入して表示

    def calculate_wire_length(self, instance):
        volume = float(self.results["beed_volume"].text)
        wire_area = float(self.results["wire_area"].text)
        if wire_area > 0:
            wire_length = volume / wire_area
            self.results["wire_length"].text = f"{round(wire_length, 2):.2f}"  # 少数2桁に四捨五入して表示
        else:
            self.results["wire_length"].text = "Error"

    def calculate_wire_efficiency_length(self, instance):
        wire_length = float(self.results["wire_length"].text)
        efficiency = float(self.inputs["efficiency"].text) / 100
        if efficiency > 0:
            efficient_length = wire_length / efficiency
            self.results["efficient_length"].text = f"{round(efficient_length, 2):.2f}"  # 少数2桁に四捨五入して表示
        else:
            self.results["efficient_length"].text = "Error"

    def calculate_wire_efficiency_weight(self, instance):
        try:
            lw_eff = float(self.results["efficient_length"].text)       # mm
            wire_area_val = float(self.results["wire_area"].text)       # mm^2
            volume = lw_eff * wire_area_val                             # mm^3
            density_steel_kg_per_mm3 = 7.85e-6                          # kg/mm^3
            mass_kg = volume * density_steel_kg_per_mm3
            self.results["wire_weight"].text = f"{mass_kg:.2f}"
        except ValueError:
            self.results["wire_weight"].text = "Error"

    # H型鋼の全周計算メソッド
    def calculate_perimeter(self, h, w, t1, t2, r):
        perimeter = (w * 2) + ((h - (t2 * 2 + r * 2)) * 2) + (((w - (t1 + r * 2)) / 2) * 4) + (t2 * 4) + (2 * math.pi * r)
        return round(perimeter, 2)  # 少数2桁に四捨五入して返す
    
    def calculate_coulme_perimeter(selh, h, w, t, r):
        perimeter = (((h - r * 2) + (w - r * 2)) * 2) + (2 * math.pi * r)
        return round(perimeter, 2)  # 少数2桁に四捨五入して返す

    def setwire_to_weight(self, instance):
        """
        使用ワイヤー重量(wire_weight_key_spinner) と 必要ワイヤー重量(self.results["wire_weight"])
        の割合を計算し、self.wire_weight_value_label に表示するメソッド
        """
        try:
            # 1. ユーザーがスピナーで選択した使用ワイヤー重量 [kg]
            spinner_val = float(self.inputs["wire_weight_key_spinner"].text)  # 例: "5", "15" etc.

            # 2. 必要ワイヤー重量 (Wwη) [kg] (計算済み)
            calc_val = float(self.results["wire_weight"].text)  # 例: "12.34" etc.

            # 3. 0除算対策
            if calc_val <= 0:
                self.wire_weight_value_label.text = "Error"
                return
            
            # 4. 割合(%) = (使用ワイヤー重量 / 必要ワイヤー重量)
            ratio = calc_val / spinner_val * 100

            # 5. 結果を小数2桁に丸めて表示
            self.results["wire_ratio"].text = f"{ratio:.2f}"

        except ValueError:
            # もし文字列が"Error"や空欄など、float変換できない場合
            self.wire_weight_value_label.text = "Error"

    def copy_to_clipboard(self, instance):
        """
        「コピー」ボタンが押されたときに呼び出されるメソッド
        指定された形式でまとめてクリップボードにコピーする
        """
        copy_text = (
            f"{self.selected_steel_size}\n"  # ← 先頭に選択された鋼材サイズを追加
            f"ワイヤー直径(d)[mm]:{self.inputs['wire_diameter'].text}φ\n"
            f"ビード高さ(h)[mm]:{self.inputs['beed_height'].text}mm\n"
            f"ビード幅(w)[mm]:{self.inputs['beed_width'].text}mm\n"
            f"溶着率(η)[%]:{self.inputs['efficiency'].text}%\n"
            f"溶接長さ(L)[mm]:{self.inputs['weld_length'].text}mm\n"
            f"ビード断面積(A):{self.results['beed_area'].text}A\n"
            f"ビード体積(V):{self.results['beed_volume'].text}V\n"
            f"ワイヤー断面積(a):{self.results['wire_area'].text}φ\n"
            f"必要ワイヤー長さⅠ(Lw):{self.results['wire_length'].text}mm\n"
            f"必要ワイヤー長さⅡ(Lwη):{self.results['efficient_length'].text}mm\n"
            f"必要ワイヤー重量 (Wwη) [kg]:{self.results['wire_weight'].text}kg\n"
            f"使用ワイヤー重量 [kg]:{self.inputs['wire_weight_key_spinner'].text}kg\n"
            f"ワイヤー使用率 [%]:{self.results['wire_ratio'].text}%"
        )
        Clipboard.copy(copy_text)
        # 必要に応じて完了通知用のダイアログ表示やprintなどを入れてもよい
        print("クリップボードにコピーしました。")

class WeldingApp(App):
    def build(self):
        return WeldingCalculator()

if __name__ == "__main__":
    WeldingApp().run()