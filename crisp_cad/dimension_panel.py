# dimension_panel.py

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider

def create_dimension_main_panel():
    main_panel = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)

    # 寸法入力フォーム (Dimension Input Form): 幅比 0.057
    dimension_input = TextInput(size_hint_x=0.057, size_hint_y=None, height=40)

    # 寸法トグルボタン (Dimension Toggle Button): 幅比 0.057
    dimension_toggle = ToggleButton(text='寸法', size_hint_x=0.057, size_hint_y=None, height=40)

    # 角度指定スライダー (Angle Slider): 幅比 0.15
    angle_slider = Slider(min=0, max=360, value=0, size_hint_x=0.15, size_hint_y=None, height=40)

    # 角度指定入力フォーム (Angle Input Form): 幅比 0.057
    angle_input = TextInput(size_hint_x=0.057, size_hint_y=None, height=40)

    # 角度指定トグルボタン (Angle Toggle Button): 幅比 0.057
    angle_toggle = ToggleButton(text='角度', size_hint_x=0.057, size_hint_y=None, height=40)

    # リセットボタン (Reset Button): 幅比 0.057
    reset_button = Button(text='リセット', size_hint_x=0.057, size_hint_y=None, height=40)

    # 線ボタン (Line Button): 幅比 0.057
    line_button = Button(text='線', size_hint_x=0.057, size_hint_y=None, height=40)

    # 半径ボタン (Radius Button): 幅比 0.057
    radius_button = Button(text='半径', size_hint_x=0.057, size_hint_y=None, height=40)

    # 直径ボタン (Diameter Button): 幅比 0.057
    diameter_button = Button(text='直径', size_hint_x=0.057, size_hint_y=None, height=40)

    # 円周ボタン (Circumference Button): 幅比 0.057
    circumference_button = Button(text='円周', size_hint_x=0.057, size_hint_y=None, height=40)

    # 角度ボタン (Angle Button): 幅比 0.057
    angle_button = Button(text='角度', size_hint_x=0.057, size_hint_y=None, height=40)

    # 寸法値ボタン (Dimension Value Button): 幅比 0.057
    dimension_value_button = Button(text='寸法値', size_hint_x=0.057, size_hint_y=None, height=40)

    # 設定ボタン (Settings Button): 幅比 0.057
    settings_button = Button(text='設定', size_hint_x=0.057, size_hint_y=None, height=40)

    # 累進ボタン (Progressive Button): 幅比 0.057
    progressive_button = Button(text='累進', size_hint_x=0.057, size_hint_y=None, height=40)

    # 一括処理ボタン (Batch Processing Button): 幅比 0.057
    batch_button = Button(text='一括', size_hint_x=0.057, size_hint_y=None, height=40)

    # 実行ボタン (Execute Button): 幅比 0.057
    execute_button = Button(text='実行', size_hint_x=0.057, size_hint_y=None, height=40)

    # ウィジェットを追加
    main_panel.add_widget(dimension_input)
    main_panel.add_widget(dimension_toggle)
    main_panel.add_widget(angle_slider)
    main_panel.add_widget(angle_input)
    main_panel.add_widget(angle_toggle)
    main_panel.add_widget(reset_button)
    main_panel.add_widget(line_button)
    main_panel.add_widget(radius_button)
    main_panel.add_widget(diameter_button)
    main_panel.add_widget(circumference_button)
    main_panel.add_widget(angle_button)
    main_panel.add_widget(dimension_value_button)
    main_panel.add_widget(settings_button)
    main_panel.add_widget(progressive_button)
    main_panel.add_widget(batch_button)
    main_panel.add_widget(execute_button)

    return main_panel

def create_dimension_sub_panel():
    sub_panel = BoxLayout(orientation='vertical')

    # 寸法線設定トグルボタン (Dimension Line Setting Toggle Button)
    dimension_line_toggle = ToggleButton(text='寸法線設定')

    # 寸法線設定入力フォーム (Dimension Line Setting Input Form)
    dimension_line_input = TextInput()

    # 少数点入力フォーム (Decimal Point Input Form)
    decimal_input = TextInput()

    # 少数点トグルボタン (Decimal Point Toggle Button)
    decimal_toggle = ToggleButton(text='少数')

    # ウィジェットを追加
    sub_panel.add_widget(dimension_line_toggle)
    sub_panel.add_widget(dimension_line_input)
    sub_panel.add_widget(decimal_input)
    sub_panel.add_widget(decimal_toggle)

    return sub_panel
