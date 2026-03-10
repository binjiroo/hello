from kivy.graphics import InstructionGroup
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.properties import (
    BooleanProperty,
    ObjectProperty,
    ListProperty,
    DictProperty,
    NumericProperty,
    StringProperty
)

# Additional imports based on your application's needs
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

# Importing the Drawer class from your custom module
from drawer import Drawer

import os
import sys
# import math  # If needed for mathematical computations

class FileManagement_Drawing_Controls():
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