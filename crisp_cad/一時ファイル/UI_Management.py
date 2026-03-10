class UI_Management():
    def build(self):
        # ルートレイアウトを水平方向のBoxLayoutに設定
        root = BoxLayout(orientation='horizontal')
        self.drawer = ShapeDrawer()

        # メインパネルとレイヤーパネルを作成
        main_panel = BoxLayout(orientation='vertical', size_hint=(0.9, 1))
        layer_panel = BoxLayout(orientation='vertical', size_hint=(0.1, 1))

        # メニューバーの作成
        menu_bar = BoxLayout(size_hint=(1, None), height=30, orientation='horizontal')

        # ファイルメニューのドロップダウンを作成
        file_dropdown = DropDown()

        # ファイルメニューの項目を追加
        file_items = [
            '新規作成', '開く', '上書き保存', '名前を付けて保存',
            '印刷', 'プリンタ設定', '---',
            '最近のファイル', '---',
            '再起動', '保存して再起動', '閉じる'
        ]

        for item in file_items:
            if item == '---':
                # 区切り線としてラベルを追加
                separator = Label(text='----------------', size_hint_y=None, height=20)
                file_dropdown.add_widget(separator)
            elif item == '最近のファイル':
                # 最近のファイルのサブメニューを作成
                recent_files_dropdown = DropDown()
                self.recent_files = self.load_recent_files()  # 最近のファイルをロード

                if self.recent_files:
                    for filename in self.recent_files:
                        btn = Button(text=filename, size_hint_y=None, height=30)
                        btn.bind(on_release=lambda btn: recent_files_dropdown.select(btn.text))
                        recent_files_dropdown.add_widget(btn)
                else:
                    btn = Button(text='最近のファイルはありません', size_hint_y=None, height=30)
                    btn.disabled = True
                    recent_files_dropdown.add_widget(btn)

                # 「最近のファイル」ボタンを作成し、サブメニューをバインド
                recent_files_btn = Button(text='最近のファイル', size_hint_y=None, height=30)
                recent_files_btn.bind(on_release=recent_files_dropdown.open)
                recent_files_dropdown.bind(on_select=lambda instance, x: self.on_recent_file_select(x))
                file_dropdown.add_widget(recent_files_btn)
            else:
                btn = Button(text=item, size_hint_y=None, height=30)
                btn.bind(on_release=lambda btn: file_dropdown.select(btn.text))
                file_dropdown.add_widget(btn)

        # ファイルボタンを作成し、ドロップダウンをバインド
        file_btn = Button(text='ファイル', size_hint=(None, 1), width=80)
        file_btn.bind(on_release=file_dropdown.open)
        file_dropdown.bind(on_select=lambda instance, x: self.on_file_menu_select(x))
        menu_bar.add_widget(file_btn)

        # メニュー項目の追加
        menu_items = ['編集', '表示', '作図', '設定', 'レイヤー', '開発', '操作', 'その他', 'ヘルプ']
        for item in menu_items:
            btn = Button(text=item, size_hint=(None, 1), width=80)
            btn.bind(on_press=self.on_menu_button)
            menu_bar.add_widget(btn)

        # コントロールパネル（描画モードとクリアボタン）
        control_panel = BoxLayout(size_hint=(1, None), height=50, orientation='horizontal')

        # 描画モードボタン
        modes = ['点', '線', '矩形', '円', '円弧', '選択', '回転']
        for mode_name in modes:
            btn = Button(text=mode_name, size_hint=(0.1, 1))
            btn.bind(on_press=self.on_mode_button)
            control_panel.add_widget(btn)

        # 戻るボタン
        back_button = Button(text='戻る', size_hint=(0.1, 1))
        back_button.bind(on_press=self.on_back_button)
        control_panel.add_widget(back_button)

        # 進むボタン
        forward_button = Button(text='進む', size_hint=(0.1, 1))
        forward_button.bind(on_press=self.on_forward_button)
        control_panel.add_widget(forward_button)

        # クリアボタン
        clear_button = Button(text='クリア', size_hint=(0.1, 1))
        clear_button.bind(on_press=self.on_clear_button)
        control_panel.add_widget(clear_button)

        # スナップモードトグルボタン
        self.snap_toggle = ToggleButton(text='スナップOFF', size_hint=(0.1, 1))
        self.snap_toggle.bind(on_press=self.on_snap_toggle)
        control_panel.add_widget(self.snap_toggle)

        # 下部のコントロールパネル（線幅、扁平率、塗りモード）
        line_width_panel = BoxLayout(size_hint=(1, None), height=40, orientation='horizontal')

        # 線幅ラベル
        line_width_label = Label(text='線幅:', size_hint=(0.1, 1))
        line_width_panel.add_widget(line_width_label)

        # 線幅スライダー
        line_width_slider = Slider(min=1, max=20, value=1, step=1, size_hint=(0.5, 1))
        line_width_slider.bind(value=self.on_line_width_slider)
        line_width_panel.add_widget(line_width_slider)

        # 線幅入力
        line_width_input = TextInput(text='1', multiline=False, size_hint=(0.1, 1))
        line_width_input.bind(text=self.on_line_width_input)
        line_width_panel.add_widget(line_width_input)

        # 線幅スピナー
        line_width_spinner = Spinner(
            text='1',
            values=[str(i) for i in range(1, 21)],
            size_hint=(0.1, 1)
        )
        line_width_spinner.bind(text=self.on_line_width_spinner)
        line_width_panel.add_widget(line_width_spinner)

        # 扁平率入力
        flattening_input = TextInput(text='0.0', multiline=False, size_hint=(0.1, 1))
        flattening_input.bind(text=self.on_flattening_input)
        line_width_panel.add_widget(flattening_input)

        # 扁平率スピナー
        flattening_spinner = Spinner(
            text='扁平率',
            values=('0.0', '0.1', '0.2', '0.3', '0.4', '0.5'),
            size_hint=(0.1, 1)
        )
        flattening_spinner.bind(text=self.on_flattening_spinner)
        line_width_panel.add_widget(flattening_spinner)

        # 塗りモードトグルボタン
        self.fill_toggle = ToggleButton(text='塗り', size_hint=(0.1, 1))
        self.fill_toggle.bind(on_press=self.on_fill_toggle)
        line_width_panel.add_widget(self.fill_toggle)

        # スナップモードトグルボタンを追加
        self.snap_toggle = ToggleButton(text='スナップOFF', size_hint=(0.1, 1))
        self.snap_toggle.bind(on_press=self.on_snap_toggle)
        line_width_panel.add_widget(self.snap_toggle)

        # 色コントロールパネル
        color_panel = BoxLayout(size_hint=(1, None), height=40, orientation='horizontal')

        # 色ラベル
        color_label = Label(text='色:', size_hint=(0.1, 1))
        color_panel.add_widget(color_label)

        # 色スライダー
        color_slider = Slider(min=0, max=11, value=0, step=1, size_hint=(0.5, 1))
        color_slider.bind(value=self.on_color_slider)
        color_panel.add_widget(color_slider)

        # 色入力
        color_input = TextInput(text='0', multiline=False, size_hint=(0.1, 1))
        color_input.bind(text=self.on_color_input)
        color_panel.add_widget(color_input)

        # 色スピナー
        color_spinner = Spinner(
            text='0',
            values=[str(i) for i in range(12)],
            size_hint=(0.1, 1)
        )
        color_spinner.bind(text=self.on_color_spinner)
        color_panel.add_widget(color_spinner)

        # 色見本表示（Widgetを使用）
        color_sample = Widget(size_hint=(0.1, 1))
        color_panel.add_widget(color_sample)

        # カラーモードスピナー
        color_mode_spinner = Spinner(
            text='RGB',
            values=('RGB', 'CMYK', 'グレースケール'),
            size_hint=(0.1, 1)
        )
        color_mode_spinner.bind(text=self.on_color_mode_spinner)
        color_panel.add_widget(color_mode_spinner)

        # 角度入力フォームを追加
        angle_input = TextInput(text='', multiline=False, size_hint=(0.1, 1))
        angle_input.bind(text=self.on_angle_input)
        color_panel.add_widget(angle_input)

        # 回転ステップスピナーを追加
        rotation_step_spinner = Spinner(
            text='フリー',
            values=('フリー', '15度', '30度', '45度', '90度'),
            size_hint=(0.1, 1)
        )
        rotation_step_spinner.bind(text=self.on_rotation_step_spinner)
        color_panel.add_widget(rotation_step_spinner)

        # ウィジェットへの参照を保存
        self.line_width_slider = line_width_slider
        self.line_width_input = line_width_input
        self.line_width_spinner = line_width_spinner
        self.color_slider = color_slider
        self.color_input = color_input
        self.color_spinner = color_spinner
        self.color_sample = color_sample
        self.color_mode_spinner = color_mode_spinner

        # 録画制御パネル
        record_panel = BoxLayout(size_hint=(1, None), height=40, orientation='horizontal')

        # 録画開始ボタン
        self.record_button = ToggleButton(text='録画開始', size_hint=(0.1, 1))
        self.record_button.bind(on_press=self.on_record_toggle)
        record_panel.add_widget(self.record_button)

        # 再生ボタン
        replay_button = Button(text='再生', size_hint=(0.1, 1))
        replay_button.bind(on_press=self.on_replay_button)
        record_panel.add_widget(replay_button)

        # 色設定を初期化
        self.color_value = 0  # 0から11まで
        self.color_mode = 'RGB'  # 'RGB', 'CMYK', 'グレースケール'

        # RGBモードの色を定義
        self.colors_rgb = [
            (0, 0, 0),       # 0 黒
            (1, 0, 0),       # 1 赤
            (0, 1, 0),       # 2 緑
            (0, 0, 1),       # 3 青
            (1, 1, 0),       # 4 黄色
            (0, 1, 1),       # 5 シアン
            (1, 0, 1),       # 6 マゼンタ
            (1, 1, 1),       # 7 白
            (1, 0.5, 0),     # 8 オレンジ
            (0.5, 0, 0.5),   # 9 紫
            (0.6, 0.3, 0),   # 10 茶色
            (0.5, 0.5, 0.5)  # 11 グレー
        ]

        # CMYKの値を定義
        self.colors_cmyk_values = [
            (0, 0, 0, 1),       # 0 黒
            (1, 0, 0, 0),       # 1 シアン
            (0, 1, 0, 0),       # 2 マゼンタ
            (0, 0, 1, 0),       # 3 イエロー
            (1, 1, 0, 0),       # 4 ブルー
            (0, 1, 1, 0),       # 5 レッド
            (1, 0, 1, 0),       # 6 グリーン
            (0, 0, 0, 0),       # 7 白
            (0, 0.5, 1, 0),     # 8 オリーブ
            (0.5, 1, 0, 0),     # 9 パープル
            (1, 0.5, 0, 0),     # 10 ティール
            (0, 0, 0, 0.5)      # 11 グレー
        ]

        # 既存のウィジェットをメインパネルに追加
        main_panel.add_widget(menu_bar)
        main_panel.add_widget(control_panel)
        main_panel.add_widget(line_width_panel)
        main_panel.add_widget(color_panel)
        main_panel.add_widget(record_panel)
        main_panel.add_widget(self.drawer)

        # レイヤーパネルを構築
        layer_grid = GridLayout(cols=2, rows=10, size_hint=(1, None), height=400)  # 20個のレイヤーボタンを配置
        self.layer_buttons = []
        for i in range(20):  # 20個のメインレイヤーボタンを作成
            btn = ToggleButton(text=f' {i+1}', size_hint=(None, None), width=40, height=40)
            btn.bind(on_press=self.on_layer_toggle)
            self.layer_buttons.append(btn)
            layer_grid.add_widget(btn)
        layer_panel.add_widget(layer_grid)

        # レイヤー切換えボタンを追加
        self.layer_switch_button = ToggleButton(text='メイン', size_hint=(None, None), width=80, height=40)
        self.layer_switch_button.bind(on_press=self.on_layer_switch_toggle)
        layer_panel.add_widget(self.layer_switch_button)

        # パネルをルートに追加
        root.add_widget(main_panel)
        root.add_widget(layer_panel)

        # 初期設定
        self.is_main_layer_mode = True
        self.current_main_layer = 0
        self.current_sub_layer = 0
        self.layer_buttons[self.current_main_layer].state = 'down'

        # 初期線幅設定
        self.line_width = 1

        # 初期色を設定
        self.drawer.set_current_color(self.get_current_color())
        self.update_color_sample()

        return root

    def build_ui(self):
        layer_selector = Spinner(
            text='Select Layer',
            values=[f"Main {i+1}" for i in range(num_main_layers)],
            size_hint=(None, None),
            size=(100, 44),
            pos=(10, 10)
        )
        layer_selector.bind(text=self.on_layer_selected)
        return layer_selector
    
    def on_menu_button(self, instance):
        # メニューボタンが押されたときの処理
        if instance.text == 'ファイル':
            # ファイルメニューの処理を実装
            pass
        elif instance.text == '編集':
            # 編集メニューの処理を実装
            pass
        elif instance.text == '表示':
            # 表示メニューの処理を実装
            pass
        elif instance.text == '作図':
            # 表示メニューの処理を実装
            pass
        elif instance.text == '設定':
            # 表示メニューの処理を実装
            pass
        elif instance.text == 'レイヤー':
            # 表示メニューの処理を実装
            pass
        elif instance.text == '開発':
            # 表示メニューの処理を実装
            pass
        elif instance.text == '操作':
            # 表示メニューの処理を実装
            pass
        elif instance.text == 'その他':
            # 表示メニューの処理を実装
            pass
        elif instance.text == 'ヘルプ':
            # ヘルプメニューの処理を実装
            pass
    
    def on_angle_input(self, instance, value):
        self.drawer.set_rotation_angle(value)

    def on_rotation_step_spinner(self, spinner, text):
        self.drawer.set_rotation_step(text)

    def on_mode_button(self, instance):
        mode_dict = {'点': 'point', '線': 'line', '矩形': 'rectangle',
                    '円': 'circle', '円弧': 'arc', '選択': 'select', '回転': 'rotate'}
        mode = mode_dict.get(instance.text, 'point')
        self.drawer.set_drawing_mode(mode)

    def on_clear_button(self, instance):
        self.drawer.clear_canvas()

    def on_flattening_input(self, instance, value):
        self.drawer.set_flattening_rate(value)

    def on_flattening_spinner(self, spinner, text):
        self.drawer.set_flattening_rate(text)

    def on_fill_toggle(self, instance):
        if instance.state == 'down':
            self.drawer.set_fill_mode('fill')
            instance.text = '線'
        else:
            self.drawer.set_fill_mode('stroke')
            instance.text = '塗り'

    def on_snap_toggle(self, instance):
        if instance.state == 'down':
            self.drawer.set_snap_mode(True)
            instance.text = 'スナップON'
        else:
            self.drawer.set_snap_mode(False)
            instance.text = 'スナップOFF'

    def on_line_width_slider(self, instance, value):
        self.line_width = int(value)
        self.line_width_input.text = str(self.line_width)
        self.line_width_spinner.text = str(self.line_width)
        self.drawer.set_line_width(self.line_width)

    def on_line_width_input(self, instance, value):
        try:
            val = int(value)
            if 1 <= val <= 20:
                self.line_width = val
                self.line_width_slider.value = val
                self.line_width_spinner.text = str(val)
                self.drawer.set_line_width(self.line_width)
            else:
                instance.text = str(self.line_width)
        except ValueError:
            instance.text = str(self.line_width)

    def on_line_width_spinner(self, instance, text):
        val = int(text)
        self.line_width = val
        self.line_width_slider.value = val
        self.line_width_input.text = str(val)
        self.drawer.set_line_width(self.line_width)

    def on_color_slider(self, instance, value):
        self.color_value = int(value)
        self.color_input.text = str(self.color_value)
        self.color_spinner.text = str(self.color_value)
        self.update_color_sample()
        self.drawer.set_current_color(self.get_current_color())

    def on_color_input(self, instance, value):
        try:
            val = int(value)
            if 0 <= val <= 11:
                self.color_value = val
                self.color_slider.value = val
                self.color_spinner.text = str(val)
                self.update_color_sample()
                self.drawer.set_current_color(self.get_current_color())
            else:
                instance.text = str(self.color_value)
        except ValueError:
            instance.text = str(self.color_value)

    def on_color_spinner(self, spinner, text):
        val = int(text)
        self.color_value = val
        self.color_slider.value = val
        self.color_input.text = str(val)
        self.update_color_sample()
        self.drawer.set_current_color(self.get_current_color())

    def on_color_mode_spinner(self, spinner, text):
        self.color_mode = text
        self.update_color_sample()
        self.drawer.set_current_color(self.get_current_color())

    def update_color_sample(self):
        color = self.get_current_color()
        # 色見本の背景色を更新
        self.color_sample.canvas.before.clear()
        with self.color_sample.canvas.before:
            Color(*color)
            Rectangle(pos=self.color_sample.pos, size=self.color_sample.size)

if __name__ == '__main__':
    ShapeApp().run()