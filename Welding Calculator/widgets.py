import os
import json
import string
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.core.clipboard import Clipboard
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionGroup, ActionButton
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
import math
import win32ui
import win32print
import win32con
import ctypes
from ctypes import create_string_buffer, cast, POINTER, Structure, c_wchar, c_ushort, c_ulong, c_short

def load_save_info():
    """保存情報をJSONファイルから読み込み、(last_save_dir, last_save_filename) を返す"""
    info_file = "save_info.json"
    if os.path.exists(info_file):
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('last_save_dir'), data.get('last_save_filename')
        except Exception as e:
            print("保存情報の読み込みエラー:", e)
    return None, None

def save_save_info(last_save_dir, last_save_filename):
    """保存情報をJSONファイルに書き込む"""
    info_file = "save_info.json"
    data = {
        'last_save_dir': last_save_dir,
        'last_save_filename': last_save_filename
    }
    try:
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except Exception as e:
        print("保存情報の書き込みエラー:", e)

def open_print_dialog():
    # 現在のデフォルトプリンタを取得
    default_printer = win32print.GetDefaultPrinter()
    
    # 印刷ダイアログを作成
    dlg = win32ui.CreatePrintDialog(0)
    dlg.GetDefaults()
    # デフォルトプリンタ名を設定（必要に応じて）
    dlg.SetDeviceName(default_printer)
    
    # ダイアログをモーダル表示
    if dlg.DoModal() == win32con.IDOK:
        # ユーザーが「OK」を押した場合、印刷設定情報が取得可能
        devmode = dlg.GetDevMode()
        # ここで、devmodeから用紙サイズや印刷部数などを取得し、
        # 印刷ジョブの実行（例：win32print.StartDocPrinterなど）に利用します。
        print("印刷設定が完了しました。")
    else:
        print("印刷がキャンセルされました。")

def get_printer_list():
    """Windows環境で利用可能なプリンターのリストを返す"""
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
    # プリンタ情報のタプルの3番目の要素がプリンタ名
    return [printer[2] for printer in printers]

def execute_print_job(printer_name, document_text, paper_size, copies, orientation):
    # 1. プリンタを開く
    hPrinter = win32print.OpenPrinter(printer_name)
    
    # 2. 読み取り専用の DEVMODE を取得する
    properties = win32print.GetPrinter(hPrinter, 2)
    read_only_devmode = properties['pDevMode']  # これは読み取り専用の PyDEVMODEW
    
    # 3. DocumentProperties() を呼び出して必要なバッファサイズを取得する
    dm_size = win32print.DocumentProperties(0, hPrinter, printer_name, None, None, 0)
    
    # 4. dm_size 分のバッファを確保する
    buffer = create_string_buffer(dm_size)
    
    # 5. DM_OUT_BUFFER | DM_IN_BUFFER フラグを指定して、読み取り専用の devmode を入力、mutableなバッファを出力に渡す
    flags = win32con.DM_OUT_BUFFER | win32con.DM_IN_BUFFER
    result = win32print.DocumentProperties(0, hPrinter, printer_name, buffer, read_only_devmode, flags)
    if result < 0:
        raise Exception("DocumentProperties failed")
    
    # 6. ctypes を使ってバッファを DEVMODE 構造体にキャストする
    class DEVMODE(Structure):
        _fields_ = [
            ("dmDeviceName", c_wchar * 32),
            ("dmSpecVersion", c_ushort),
            ("dmDriverVersion", c_ushort),
            ("dmSize", c_ushort),
            ("dmDriverExtra", c_ushort),
            ("dmFields", c_ulong),
            ("dmOrientation", c_short),
            ("dmPaperSize", c_short),
            ("dmPaperLength", c_short),
            ("dmPaperWidth", c_short),
            # 必要に応じて他のフィールドを追加
        ]
    devmode_mutable = cast(buffer, POINTER(DEVMODE)).contents

    # 7. mutableな DEVMODE の属性を変更する
    if paper_size == "A4":
        devmode_mutable.dmPaperSize = 9
    elif paper_size == "Letter":
        devmode_mutable.dmPaperSize = 1

    devmode_mutable.dmCopies = int(copies)
    devmode_mutable.dmOrientation = 1 if orientation == "縦" else 2

    # 8. 印刷ジョブを開始する
    doc_info = {"DocName": "Welding Calculator Document", "OutputFile": None, "Datatype": "RAW"}
    job_id = win32print.StartDocPrinter(hPrinter, 1, doc_info)
    win32print.StartPagePrinter(hPrinter)
    win32print.WritePrinter(hPrinter, document_text.encode('utf-8'))
    win32print.EndPagePrinter(hPrinter)
    win32print.EndDocPrinter(hPrinter)
    win32print.ClosePrinter(hPrinter)

def get_drives():
    """Windows環境で利用可能なドライブ（例：C:\, D:\, ...）をリストで返す"""
    drives = []
    for drive in string.ascii_uppercase:
        if os.path.exists(f"{drive}:\\"):
            drives.append(f"{drive}:\\")
    return drives

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

            if additional_key is not None:
                additional_spinner.bind(text=lambda spinner, value: self.update_input_field(value, additional_key))
                self.inputs[f"{additional_key}_spinner"] = additional_spinner
            else:
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
                    self.selected_steel_size = text
                    if text in self.spinner_to_perimeter:
                        result = self.spinner_to_perimeter[text]()
                        self.inputs["weld_length"].text = f"{result:.2f}"
                elif spinner_instance == additional_spinner:
                    print(f"新しいスピナーで選択: {text}")
                    
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
            additional_key="wire_weight_key"
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
                    self.selected_steel_size = text
                    result = self.spinner_to_perimeter[text]()
                    self.inputs["weld_length"].text = f"{result:.2f}"
                    calc_method(None)
            spinner = Spinner(text=spinner_values[0], values=spinner_values, size_hint_x=None, width=200, font_size=18)
            spinner.bind(text=on_spinner_select)
            self.add_widget(spinner)

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
            ["リップ鋼"],
            self.calculate_wire_efficiency_weight,
            "wire_weight"
        )

        self.wire_weight_title_label = Label(text="使用ワイヤー重量[kg]:", size_hint_x=None, width=250, font_size=18)
        self.add_widget(self.wire_weight_title_label)

        self.wire_weight_value_label = Label(text="0", size_hint_x=None, width=80, font_size=18)
        self.add_widget(self.wire_weight_value_label)

        copy_button = Button(text="コピー", size_hint_x=None, width=160, font_size=18)
        copy_button.bind(on_press=self.copy_to_clipboard)
        self.add_widget(copy_button)

        self.add_widget(Spinner(text="ガセットプレート", values=["ガセットプレート"], size_hint_x=None, width=200, font_size=18))

        self.setwire_weight_title_label = Label(text="ワイヤー使用率[%]:", size_hint_x=None, width=250, font_size=18)
        self.add_widget(self.setwire_weight_title_label)

        wire_ratio_label = Label(text="0", size_hint_x=None, width=80, font_size=18)
        self.results["wire_ratio"] = wire_ratio_label
        self.add_widget(wire_ratio_label)

        setwire_button = Button(text="計算", size_hint_x=None, width=160, font_size=18)
        setwire_button.bind(on_press=self.setwire_to_weight)
        self.add_widget(setwire_button)

        self.add_widget(Spinner(text="リブプレート", values=["リブプレート"], size_hint_x=None, width=200, font_size=18))

    def update_input_field(self, value, input_key):
        if input_key in self.inputs:
            input_field = self.inputs[input_key]
            input_field.text = value

        if input_key == "wire_weight_key":
            self.wire_weight_value_label.text = f"{value}"

    def calculate_beed_area(self, instance):
        w = float(self.inputs["beed_width"].text)
        h = float(self.inputs["beed_height"].text)
        area = 0.5 * w * h
        self.results["beed_area"].text = f"{round(area, 2):.2f}"

    def calculate_beed_volume(self, instance):
        area = float(self.results["beed_area"].text)
        length = float(self.inputs["weld_length"].text)
        volume = area * length
        self.results["beed_volume"].text = f"{round(volume, 2):.2f}"

    def calculate_wire_area(self, instance):
        d = float(self.inputs["wire_diameter"].text) / 2
        area = math.pi * d ** 2
        self.results["wire_area"].text = f"{round(area, 2):.2f}"

    def calculate_wire_length(self, instance):
        volume = float(self.results["beed_volume"].text)
        wire_area = float(self.results["wire_area"].text)
        if wire_area > 0:
            wire_length = volume / wire_area
            self.results["wire_length"].text = f"{round(wire_length, 2):.2f}"
        else:
            self.results["wire_length"].text = "Error"

    def calculate_wire_efficiency_length(self, instance):
        wire_length = float(self.results["wire_length"].text)
        efficiency = float(self.inputs["efficiency"].text) / 100
        if efficiency > 0:
            efficient_length = wire_length / efficiency
            self.results["efficient_length"].text = f"{round(efficient_length, 2):.2f}"
        else:
            self.results["efficient_length"].text = "Error"

    def calculate_wire_efficiency_weight(self, instance):
        try:
            lw_eff = float(self.results["efficient_length"].text)
            wire_area_val = float(self.results["wire_area"].text)
            volume = lw_eff * wire_area_val
            density_steel_kg_per_mm3 = 7.85e-6
            mass_kg = volume * density_steel_kg_per_mm3
            self.results["wire_weight"].text = f"{mass_kg:.2f}"
        except ValueError:
            self.results["wire_weight"].text = "Error"

    def calculate_perimeter(self, h, w, t1, t2, r):
        perimeter = (w * 2) + ((h - (t2 * 2 + r * 2)) * 2) + (((w - (t1 + r * 2)) / 2) * 4) + (t2 * 4) + (2 * math.pi * r)
        return round(perimeter, 2)
    
    def calculate_coulme_perimeter(self, h, w, t, r):
        perimeter = (((h - r * 2) + (w - r * 2)) * 2) + (2 * math.pi * r)
        return round(perimeter, 2)

    def setwire_to_weight(self, instance):
        try:
            spinner_val = float(self.inputs["wire_weight_key_spinner"].text)
            calc_val = float(self.results["wire_weight"].text)
            if calc_val <= 0:
                self.wire_weight_value_label.text = "Error"
                return
            ratio = calc_val / spinner_val * 100
            self.results["wire_ratio"].text = f"{ratio:.2f}"
        except ValueError:
            self.wire_weight_value_label.text = "Error"

    def copy_to_clipboard(self, instance):
        copy_text = (
            f"{self.selected_steel_size}\n"
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
        print("クリップボードにコピーしました。")

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # 前回保存した情報を読み込む
        last_dir, last_filename = load_save_info()
        self.last_save_dir = last_dir if last_dir is not None else (get_drives()[0] if get_drives() else "C:\\")
        self.last_save_filename = last_filename if last_filename is not None else "welding_calculator.txt"
        # 現在編集中のファイルのパス。まだ保存されていなければ None
        self.current_file = None
        
        # メニューバー部分（ActionBar）を作成
        self.action_bar = ActionBar(size_hint=(1, None), height=50)
        self.action_view = ActionView()
        self.action_prev = ActionPrevious(title="Welding Calculator", with_previous=False)
        self.action_view.add_widget(self.action_prev)
        
        # [ファイル]メニュー
        file_menu = ActionGroup(text="ファイル", mode='spinner')
        file_menu.add_widget(ActionButton(text="新規", on_press=self.menu_new))
        file_menu.add_widget(ActionButton(text="開く", on_press=self.menu_open))
        file_menu.add_widget(ActionButton(text="上書保存", on_press=self.menu_save))
        file_menu.add_widget(ActionButton(text="名付て保存", on_press=self.menu_save_as))
        file_menu.add_widget(ActionButton(text="印刷", on_press=self.menu_print))
        file_menu.add_widget(ActionButton(text="プリンタ設定", on_press=self.menu_printer_settings))
        file_menu.add_widget(ActionButton(text="オプション", on_press=self.menu_options))
        file_menu.add_widget(ActionButton(text="終了", on_press=self.menu_exit))
        
        # [編集]メニュー
        edit_menu = ActionGroup(text="編集", mode='spinner')
        edit_menu.add_widget(ActionButton(text="戻る", on_press=self.menu_undo))
        edit_menu.add_widget(ActionButton(text="進む", on_press=self.menu_redo))
        edit_menu.add_widget(ActionButton(text="切取り", on_press=self.menu_cut))
        edit_menu.add_widget(ActionButton(text="コピー", on_press=self.menu_copy))
        edit_menu.add_widget(ActionButton(text="貼付け", on_press=self.menu_paste))
        edit_menu.add_widget(ActionButton(text="削除", on_press=self.menu_delete))
        
        # [設定]メニュー
        settings_menu = ActionGroup(text="設定", mode='spinner')
        settings_menu.add_widget(ActionButton(text="基本設定", on_press=self.menu_basic_settings))
        settings_menu.add_widget(ActionButton(text="環境設定", on_press=self.menu_env_settings))
        
        # [ヘルプ]メニュー
        help_menu = ActionGroup(text="ヘルプ", mode='spinner')
        help_menu.add_widget(ActionButton(text="トピック検索", on_press=self.menu_topic_search))
        help_menu.add_widget(ActionButton(text="バージョン情報", on_press=self.menu_version_info))
        
        self.action_view.add_widget(file_menu)
        self.action_view.add_widget(edit_menu)
        self.action_view.add_widget(settings_menu)
        self.action_view.add_widget(help_menu)
        self.action_bar.add_widget(self.action_view)
        
        self.add_widget(self.action_bar)
        
        # 既存のWeldingCalculatorを追加
        self.calculator = WeldingCalculator()
        self.add_widget(self.calculator)
    
    # 以下、各メニュー項目選択時のコールバック
    def menu_new(self, instance):
        print("新規が選択されました")
    def menu_open(self, instance):
        # ファイルを開くためのダイアログを表示
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        drives = get_drives()
        drive_spinner = Spinner(
            text=self.last_save_dir,
            values=drives,
            size_hint_y=None,
            height=40,
            font_size=16
        )
        content.add_widget(drive_spinner)
        
        # *.txt ファイルのみ表示するようにフィルタ設定
        filechooser = FileChooserListView(path=self.last_save_dir, filters=['*.txt'])
        content.add_widget(filechooser)
        
        # ドライブスピナーの選択で FileChooser のパスを更新
        drive_spinner.bind(text=lambda spinner, text: setattr(filechooser, 'path', text))
        
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        open_btn = Button(text="開く")
        cancel_btn = Button(text="キャンセル")
        btn_layout.add_widget(open_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title="ファイルを開く", content=content, size_hint=(0.9, 0.9))
        open_btn.bind(on_release=lambda x: self.do_open(filechooser, popup))
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()
        print("開くが選択されました")
        
    def menu_save(self, instance):
        print("上書保存が選択されました")

    def menu_save(self, instance):
        # 既にファイルが存在する場合はダイアログを表示せずに直接上書き保存する
        if self.current_file:
            full_path = self.current_file
            data = (
                f"{self.calculator.selected_steel_size}\n"
                f"ワイヤー直径(d)[mm]:{self.calculator.inputs['wire_diameter'].text}φ\n"
                f"ビード高さ(h)[mm]:{self.calculator.inputs['beed_height'].text}mm\n"
                f"ビード幅(w)[mm]:{self.calculator.inputs['beed_width'].text}mm\n"
                f"溶着率(η)[%]:{self.calculator.inputs['efficiency'].text}%\n"
                f"溶接長さ(L)[mm]:{self.calculator.inputs['weld_length'].text}mm\n"
                f"ビード断面積(A):{self.calculator.results['beed_area'].text}A\n"
                f"ビード体積(V):{self.calculator.results['beed_volume'].text}V\n"
                f"ワイヤー断面積(a):{self.calculator.results['wire_area'].text}φ\n"
                f"必要ワイヤー長さⅠ(Lw):{self.calculator.results['wire_length'].text}mm\n"
                f"必要ワイヤー長さⅡ(Lwη):{self.calculator.results['efficient_length'].text}mm\n"
                f"必要ワイヤー重量 (Wwη) [kg]:{self.calculator.results['wire_weight'].text}kg\n"
                f"使用ワイヤー重量 [kg]:{self.calculator.inputs['wire_weight_key_spinner'].text}kg\n"
                f"ワイヤー使用率 [%]:{self.calculator.results['wire_ratio'].text}%"
            )
            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(data)
                print(f"{full_path} に上書保存しました。")
            except Exception as e:
                print(f"上書保存エラー: {e}")
        else:
            # current_file が設定されていない場合は名付け保存を実施
            self.menu_save_as(instance)

    # MainLayout内のmenu_save_asの修正例
    def menu_save_as(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # 利用可能なドライブ一覧を取得し、前回の保存先を初期値として設定
        drives = get_drives()
        drive_spinner = Spinner(
            text=self.last_save_dir,
            values=drives,
            size_hint_y=None,
            height=40,
            font_size=16
        )
        content.add_widget(drive_spinner)
        
        # FileChooserListViewの初期パスを前回の保存先に設定（テキストファイルのみ表示）
        filechooser = FileChooserListView(path=self.last_save_dir, filters=['*.txt'])
        content.add_widget(filechooser)
        
        # ドライブスピナーで選択が変わったら FileChooser のパスを更新
        drive_spinner.bind(text=lambda spinner, text: setattr(filechooser, 'path', text))
        
        # 前回保存したファイル名を初期値として入力フォームにセット
        file_name_input = TextInput(text=self.last_save_filename, hint_text="ファイル名を入力", size_hint_y=None, height=40)
        content.add_widget(file_name_input)
        
        # ④ 保存／キャンセル用のボタンを配置
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        save_btn = Button(text="保存")
        cancel_btn = Button(text="キャンセル")
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title="名付て保存", content=content, size_hint=(0.9, 0.9))
        save_btn.bind(on_release=lambda x: self.do_save_as(filechooser, file_name_input, popup))
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def do_save_as(self, filechooser, file_name_input, popup):
        selected_path = filechooser.path
        file_name = file_name_input.text.strip()
        if not file_name:
            print("ファイル名が入力されていません。")
            return
        # 拡張子が .txt でなければ追加
        if not file_name.lower().endswith('.txt'):
            file_name += '.txt'
        full_path = os.path.join(selected_path, file_name)
        
        data = (
            f"{self.calculator.selected_steel_size}\n"
            f"ワイヤー直径(d)[mm]:{self.calculator.inputs['wire_diameter'].text}φ\n"
            f"ビード高さ(h)[mm]:{self.calculator.inputs['beed_height'].text}mm\n"
            f"ビード幅(w)[mm]:{self.calculator.inputs['beed_width'].text}mm\n"
            f"溶着率(η)[%]:{self.calculator.inputs['efficiency'].text}%\n"
            f"溶接長さ(L)[mm]:{self.calculator.inputs['weld_length'].text}mm\n"
            f"ビード断面積(A):{self.calculator.results['beed_area'].text}A\n"
            f"ビード体積(V):{self.calculator.results['beed_volume'].text}V\n"
            f"ワイヤー断面積(a):{self.calculator.results['wire_area'].text}φ\n"
            f"必要ワイヤー長さⅠ(Lw):{self.calculator.results['wire_length'].text}mm\n"
            f"必要ワイヤー長さⅡ(Lwη):{self.calculator.results['efficient_length'].text}mm\n"
            f"必要ワイヤー重量 (Wwη) [kg]:{self.calculator.results['wire_weight'].text}kg\n"
            f"使用ワイヤー重量 [kg]:{self.calculator.inputs['wire_weight_key_spinner'].text}kg\n"
            f"ワイヤー使用率 [%]:{self.calculator.results['wire_ratio'].text}%"
        )
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"{full_path} に保存しました。")
            # 最新の保存先情報を更新し、永続化
            self.last_save_dir = selected_path
            self.last_save_filename = file_name
            save_save_info(self.last_save_dir, self.last_save_filename)
            # ★ここで現在編集中のファイルのパスを更新
            self.current_file = full_path
        except Exception as e:
            print(f"保存エラー: {e}")
        popup.dismiss()
        
    def do_open(self, filechooser, popup):
        # FileChooserListView の selection プロパティから選択されたファイルを取得
        if not filechooser.selection:
            print("ファイルが選択されていません。")
            return
        full_path = filechooser.selection[0]
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            lines = content.splitlines()
            # ファイルのフォーマットが想定通りか簡易チェック（最低14行以上）
            if len(lines) < 14:
                print("ファイルの形式が不正です。")
                popup.dismiss()
                return
            # 1行目は鋼材サイズ
            self.calculator.selected_steel_size = lines[0]
            # 以下、各行から値を抽出してウィジェットに設定
            # ※各行は「項目名:値＋単位」の形式になっている前提です。
            if "ワイヤー直径" in lines[1]:
                value = lines[1].split(':')[1].replace('φ', '').strip()
                self.calculator.inputs["wire_diameter"].text = value
            if "ビード高さ" in lines[2]:
                value = lines[2].split(':')[1].replace('mm', '').strip()
                self.calculator.inputs["beed_height"].text = value
            if "ビード幅" in lines[3]:
                value = lines[3].split(':')[1].replace('mm', '').strip()
                self.calculator.inputs["beed_width"].text = value
            if "溶着率" in lines[4]:
                value = lines[4].split(':')[1].replace('%', '').strip()
                self.calculator.inputs["efficiency"].text = value
            if "溶接長さ" in lines[5]:
                value = lines[5].split(':')[1].replace('mm', '').strip()
                self.calculator.inputs["weld_length"].text = value

            # 結果項目
            if "ビード断面積" in lines[6]:
                value = lines[6].split(':')[1].replace('A', '').strip()
                self.calculator.results["beed_area"].text = value
            if "ビード体積" in lines[7]:
                value = lines[7].split(':')[1].replace('V', '').strip()
                self.calculator.results["beed_volume"].text = value
            if "ワイヤー断面積" in lines[8]:
                value = lines[8].split(':')[1].replace('φ', '').strip()
                self.calculator.results["wire_area"].text = value
            if "必要ワイヤー長さⅠ" in lines[9]:
                value = lines[9].split(':')[1].replace('mm', '').strip()
                self.calculator.results["wire_length"].text = value
            if "必要ワイヤー長さⅡ" in lines[10]:
                value = lines[10].split(':')[1].replace('mm', '').strip()
                self.calculator.results["efficient_length"].text = value
            if "必要ワイヤー重量" in lines[11]:
                value = lines[11].split(':')[1].replace('kg', '').strip()
                self.calculator.results["wire_weight"].text = value
            if "使用ワイヤー重量" in lines[12]:
                value = lines[12].split(':')[1].replace('kg', '').strip()
                # 入力フォームのスピナー（wire_weight_key_spinner）に設定
                self.calculator.inputs["wire_weight_key_spinner"].text = value
            if "ワイヤー使用率" in lines[13]:
                value = lines[13].split(':')[1].replace('%', '').strip()
                self.calculator.results["wire_ratio"].text = value
            
            # 読み込んだファイルを current_file に設定
            self.current_file = full_path
            print(f"{full_path} を開きました。")
        except Exception as e:
            print(f"ファイルを開く際のエラー: {e}")
        popup.dismiss()

     
    def menu_print(self, instance):
        print("印刷が選択されました")

    def menu_printer_settings(self, instance):
        # プリンター一覧を取得し、プリンター選択のSpinnerなどを配置する
        printers = get_printer_list()  # グローバルな関数として定義しておく
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="プリンタを選択してください", font_size=16))
        printer_spinner = Spinner(
            text=printers[0] if printers else "プリンタが見つかりません",
            values=printers,
            size_hint_y=None,
            height=40,
            font_size=16
        )
        content.add_widget(printer_spinner)
        
        # 「印刷設定を変更する」ボタンを追加（このボタンでshow_print_settings_popupを開く）
        btn_open_print_settings = Button(text="印刷設定を変更する", size_hint_y=None, height=40)
        btn_open_print_settings.bind(on_release=lambda inst: self.show_print_settings_popup())
        content.add_widget(btn_open_print_settings)
        
        # キャンセル・適用ボタンも配置
        button_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        btn_apply = Button(text="適用", font_size=16)
        btn_cancel = Button(text="キャンセル", font_size=16)
        button_box.add_widget(btn_apply)
        button_box.add_widget(btn_cancel)
        content.add_widget(button_box)
        
        popup = Popup(title="プリンタ設定", content=content, size_hint=(0.8, 0.5))
        
        btn_cancel.bind(on_release=lambda inst: popup.dismiss())
        btn_apply.bind(on_release=lambda inst: self.apply_printer_settings(printer_spinner.text, popup))
        
        popup.open()
        print("プリンタ設定が選択されました")

    def apply_printer_settings(self, selected_printer, popup):
        # 選択されたプリンタをアプリ内で保持するなどの処理を実施
        print("選択されたプリンタ:", selected_printer)
        self.current_printer = selected_printer  # 例として保存
        popup.dismiss()

    def execute_print(self, paper_size, copies, orientation, popup):
        # 印刷する内容を文字列として作成（例：計算結果のまとめ）
        document_text = (
            f"{self.calculator.selected_steel_size}\n"
            f"ワイヤー直径(d)[mm]:{self.calculator.inputs['wire_diameter'].text}φ\n"
            f"ビード高さ(h)[mm]:{self.calculator.inputs['beed_height'].text}mm\n"
            f"ビード幅(w)[mm]:{self.calculator.inputs['beed_width'].text}mm\n"
            f"溶着率(η)[%]:{self.calculator.inputs['efficiency'].text}%\n"
            f"溶接長さ(L)[mm]:{self.calculator.inputs['weld_length'].text}mm\n"
            f"ビード断面積(A):{self.calculator.results['beed_area'].text}A\n"
            f"ビード体積(V):{self.calculator.results['beed_volume'].text}V\n"
            f"ワイヤー断面積(a):{self.calculator.results['wire_area'].text}φ\n"
            f"必要ワイヤー長さⅠ(Lw):{self.calculator.results['wire_length'].text}mm\n"
            f"必要ワイヤー長さⅡ(Lwη):{self.calculator.results['efficient_length'].text}mm\n"
            f"必要ワイヤー重量 (Wwη) [kg]:{self.calculator.results['wire_weight'].text}kg\n"
            f"使用ワイヤー重量 [kg]:{self.calculator.inputs['wire_weight_key_spinner'].text}kg\n"
            f"ワイヤー使用率 [%]:{self.calculator.results['wire_ratio'].text}%"
        )
        # ここで、選択された印刷設定（用紙サイズ、部数、印刷方向）をもとに、pywin32を利用して印刷ジョブを実行します。
        # 例えば、execute_print_job(printer_name, document_text, paper_size, copies, orientation) のような関数を呼び出す。
        # ※ printer_name は、あらかじめプリンタ設定で選択されたself.current_printerなどを利用
        import win32print
        printer_name = self.current_printer if hasattr(self, "current_printer") else win32print.GetDefaultPrinter()
        
        execute_print_job(printer_name, document_text, paper_size, copies, orientation)
        popup.dismiss()

    def show_print_settings_popup(self):
        # 印刷設定用のPopupの内容
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="用紙サイズ:", font_size=16))
        paper_size_spinner = Spinner(
            text="A4",
            values=["A4", "Letter"],
            size_hint_y=None,
            height=40
        )
        content.add_widget(paper_size_spinner)
        
        content.add_widget(Label(text="部数:", font_size=16))
        copies_input = TextInput(text="1", multiline=False, size_hint_y=None, height=40)
        content.add_widget(copies_input)
        
        content.add_widget(Label(text="印刷方向:", font_size=16))
        orientation_spinner = Spinner(
            text="縦",
            values=["縦", "横"],
            size_hint_y=None,
            height=40
        )
        content.add_widget(orientation_spinner)
        
        # 印刷実行ボタンとキャンセルボタン
        btn_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        btn_apply = Button(text="印刷実行", font_size=16)
        btn_cancel = Button(text="キャンセル", font_size=16)
        btn_box.add_widget(btn_apply)
        btn_box.add_widget(btn_cancel)
        content.add_widget(btn_box)
        
        popup = Popup(title="印刷設定", content=content, size_hint=(0.8, 0.6))
        
        btn_cancel.bind(on_release=lambda inst: popup.dismiss())
        btn_apply.bind(on_release=lambda inst: self.execute_print(
            paper_size_spinner.text,
            copies_input.text,
            orientation_spinner.text,
            popup
        ))
        popup.open()

    def menu_options(self, instance):
        print("オプションが選択されました")
    def menu_exit(self, instance):
        print("終了が選択されました")
    def menu_undo(self, instance):
        print("戻るが選択されました")
    def menu_redo(self, instance):
        print("進むが選択されました")
    def menu_cut(self, instance):
        print("切取りが選択されました")
    def menu_copy(self, instance):
        print("コピーが選択されました")
    def menu_paste(self, instance):
        print("貼付けが選択されました")
    def menu_delete(self, instance):
        print("削除が選択されました")
    def menu_basic_settings(self, instance):
        print("基本設定が選択されました")
    def menu_env_settings(self, instance):
        print("環境設定が選択されました")
    def menu_topic_search(self, instance):
        print("トピック検索が選択されました")
    def menu_version_info(self, instance):
        print("バージョン情報が選択されました")

class WeldingApp(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    WeldingApp().run()
