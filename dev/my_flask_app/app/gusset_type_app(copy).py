# my_flask_app/app/gusset_type_app.py
import math
from flask import Blueprint, render_template, request, session, current_app
from .config import h_steel_r_mapping as steel_r_mapping

steel_sizes = list(steel_r_mapping.keys())

gusset_type_bp = Blueprint(
    'gusset_type',
    __name__,
    template_folder='templates/gusset_type'
)

def get_defaults():
    return {
        "steel_name":       session.get("steel_name", ""),
        "sub_steel_name":   session.get("sub_steel_name", ""),
        "s1":               session.get("s1", "01"),
        "s2":               session.get("s2", "01"),
        "lc":              session.get("lc", "1"),
        "lt":              session.get("lt", "1"),
        "ly":              session.get("ly", "1"),
        "b_set":            session.get("b_set", "1"),
        "y_set":            session.get("y_set", "0"),
        "offset_choice":    session.get("offset_choice", "5"),
        "t":                session.get("t", "0"),
        "hole_column_x":    session.get("hole_column_x", "0"),
        "hole_row_y":       session.get("hole_row_y", "0"),
        "hole_pitch_x":     session.get("hole_pitch_x", "0"),
        "hole_pitch_y":     session.get("hole_pitch_y", "0"),
        "hole_endpitch_x":  session.get("hole_endpitch_x", "0"),
        "hole_size":        session.get("hole_size", "0"),
        "mode":             session.get("mode", "1"),
    }

@gusset_type_bp.route('/', methods=['GET', 'POST'])
def index():
    steel_options = steel_sizes
    defaults      = get_defaults()
    result_str    = ""
    error_message = ""

    if request.method == 'POST':
        action = request.form.get('action', 'new')
        # --- クリア処理 ---
        if action == 'clear':
            session.clear()
            defaults = get_defaults()
            return render_template('gusset_type/index.html',
                                steel_sizes=steel_options,
                                defaults=defaults,
                                result_str="",
                                error_message="")
            
        steel_name      = session['steel_name']
        sub_steel_name  = session['sub_steel_name']
        s1              = int(session['s1'])
        s2              = int(session['s2'])
        w1              = (b / 2 - 10) + x_offset
        w2              = (c / 2) + x_offset
        w3              = (c / 2 + r) + x_offset
        w4              = (b / 2 + 50) + x_offset
        w5              = (b / 2 + 1) + x_offset
        w6              = (b / 2) + x_offset
        h1              = (a / 2 - d) + y_offset
        h2              = -(a / 2 - (d + 2)) + y_offset
        h3              = (a / 2 - (d + r)) + y_offset
        h4              = -(a / 2 - (d + r + 2)) + y_offset
        h5              = (a / 2) + y_set + y_offset
        h6              = (a / 2) - e + y_set + y_offset
        h7              = ((a - e) / 2) + (e / 2) + y_set
        h8              = (a - e) - (d + 2)
        h9              = (a / 2 - (d + 2))
        lc              = int(session['lc'])
        lt              = int(session['lt'])
        ly              = int(session['ly'])
        b_set           = int(session['b_set'])
        y_set           = int(session['y_set'])
        offset_choice   = int(session['offset_choice'])
        t               = int(session['t'])
        hole_column_x   = int(session['hole_column_x'])
        hole_row_y      = int(session['hole_row_y'])
        hole_pitch_x    = int(session['hole_pitch_x'])
        hole_pitch_y    = int(session['hole_pitch_y'])
        hole_endpitch_x = int(session['hole_endpitch_x'])
        hole_size       = int(session['hole_size'])
        mode            = int(session['mode'])
        include_header  = int(session['include_header'])

        # --- フォーム値をセッションに保存 ---
        for key, val in defaults.items():
            session[key] = request.form.get(key, val)

        # --- パラメータ取得 ---
        steel_name      = session['steel_name']
        sub_steel_name  = session['sub_steel_name']
        s1              = session['s1']
        s2              = session['s2']
        w1              = session['w1']
        w2              = session['w2']
        w3              = session['w3']
        w4              = session['w4']
        w5              = session['w5']
        w6              = session['w6']
        h1              = session['h1']
        h2              = session['h2']
        h3              = session['h3']
        h4              = session['h4']
        h5              = session['h5']
        h6              = session['h6']
        h7              = session['h7']
        h8              = session['h8']
        h9              = session['h9']
        lc              = session['lc']
        lt              = session['lt']
        ly              = session['ly']
        b_set           = session['b_set']
        y_set           = session['y_set']
        offset_choice   = session['offset_choice']
        t               = session['t']
        hole_column_x   = session['hole_column_x']
        hole_row_y      = session['hole_row_y']
        hole_pitch_x    = session['hole_pitch_x']
        hole_pitch_y    = session['hole_pitch_y']
        hole_endpitch_x = session['hole_endpitch_x']
        hole_size       = session['hole_size']
        mode            = session['mode']
        include_header  = session['include_header']
        prev_result     = request.form.get('prev_result', '')

        # --- 入力チェック ---
        try:
            b_set          = int(b_set)
            y_set          = int(y_set)
            offset_choice  = int(offset_choice)
            t              = int(t)
            hole_column_x  = int(hole_column_x)
            hole_row_y     = int(hole_row_y)
            hole_pitch_x   = int(hole_pitch_x)
            hole_pitch_y   = int(hole_pitch_y)
            hole_endpitch_x= int(hole_endpitch_x)
            hole_size      = int(hole_size)
            mode           = int(mode)
            include_header = int(include_header)
        except ValueError as e:
            error_message = f"数値変換エラー: {e}"

        if not error_message:
            if steel_name not in steel_r_mapping or sub_steel_name not in steel_r_mapping:
                error_message = "指定されたサイズが存在しません。"
        
        # --- 計算ロジック ---
        if not error_message:
            # 環境変数・フォーム値から取得した steel_name, sub_steel_name
            r = steel_r_mapping[steel_name]
            main_vals = [float(v) for v in steel_name.split("x")]
            sub_vals  = [float(v) for v in sub_steel_name.split("x")]
            a, b, c, d = main_vals
            e, f, g, h = sub_vals

            x_offset, y_offset = offsets[choice-1] if 1 <= choice <= 9 else (0, 0)

            # 8. 基準座標の計算（孔の配置に利用）
            x_first = ((b / 2) + hole_endpitch_x) + x_offset
            x_last = ((b / 2) + hole_endpitch_x + (hole_column_x - 1) * hole_pitch_x) + x_offset

            y_first = (((0 - (hole_row_y - 1) / 2) * hole_pitch_y) + (a / 2 - e / 2)) + y_offset + y_set
            y_last = ((((hole_row_y - 1) - (hole_row_y - 1) / 2) * hole_pitch_y) + (a / 2 - e / 2)) + y_offset + y_set

            # オフセットリスト
            offsets = [
                (b/2, -a/2),(0,-a/2),(-b/2,-a/2),
                (b/2,0),(0,0),(-b/2,0),
                (b/2,a/2),(0,a/2),(-b/2,a/2),
            ]
            choice = int(offset_choice) if offset_choice.isdigit() else 5

        # 7. 動的に生成される孔の情報をリストへ追加
        hole_list = []
        for i in range(hole_row_y):
            # 中央基準の y 座標計算
            y = (((i - (hole_row_y - 1) / 2) * hole_pitch_y) + (a / 2 - e / 2)) + y_offset + y_set
            for j in range(hole_column_x):
                # 各列の x 座標計算（親フランジ端点からのオフセットを加味）
                x = ((b / 2) + hole_endpitch_x + j * hole_pitch_x) + x_offset
                zx1 = x + hole_size / 2
                zx2 = x - hole_size / 2
                zy1 = y + hole_size / 2
                zy2 = y - hole_size / 2
                ep = hole_size / 2
                # 元コードと同様、3行分のリストを追加
                hole_list.append([s1, s2, zx1, y, zx2, y, lc, lt, ly])
                hole_list.append([s1, s2, x, zy1, x, zy2, lc, lt, ly])
                hole_list.append([s1, s2, x, y, 0, 360, lc, lt, ly, "E", ep, 0])

                defaults = get_defaults()

    # リスト生成用の共通関数
    def create_shape_list(template, hole_list, new_lines):
        shape_list = [row[:] for row in template]  # テンプレートをコピー
        shape_list.extend(hole_list)
        shape_list.extend(new_lines)
        shape_list.append([999, 100, 50])
        return shape_list

    # 最終形状リストの決定
    if (h1 - (y_last + 40)) <= 0 and ((h9 + y_first) - 40) <= 0:
        final_shape_type = "shape_list4"
        current_app.logger.debug("shape_list4を選択。")
    elif (h1 - (y_last + 40)) >= 0 and ((h9 + y_first) - 40) < 0:
        final_shape_type = "shape_list3"
        current_app.logger.debug("shape_list3を選択。")
    elif (h1 - (y_last + 40)) < 0 and ((h9 + y_first) - 40) >= 0:
        final_shape_type = "shape_list2"
        current_app.logger.debug("shape_list2を選択。")
    else:
        final_shape_type = "shape_list"
        current_app.logger.debug("shape_listを選択。")

    # 使用するmodeを入力
    mode = int(request.form.get("モードを選択（mood1=1、mood2=2、mood3=3）: "))

    # modeとshapeごとの設定テンプレートを定義（各shapeで異なる要素のみ変更）
    mode_templates = {
        1: {
            "shape_list": [
                [s1, s2, w3, h1, w1, h1, lc, lt, ly],
                [s1, s2, w3, h2, w1, h2, lc, lt, ly],
                [s1, s2, w1, h1, w1, y_last + 50, lc, lt, ly],
                [s1, s2, w1, h2, w1, y_first - 50, lc, lt, ly],
                [s1, s2, w2, h3, w2, h4, lc, lt, ly],
                [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
                [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
                [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
                [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
                [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
                [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
                [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
                [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
            ],
            "shape_list2": [
                [s1, s2, w3, h1, w5, h1, lc, lt, ly],
                [s1, s2, w3, h2, w1, h2, lc, lt, ly],
                [s1, s2, w5, h1, w5, y_last + 40, lc, lt, ly],
                [s1, s2, w1, h2, w1, y_first - 50, lc, lt, ly],
                [s1, s2, w2, h3, w2, h4, lc, lt, ly],
                [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
                [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
                [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
                [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
                [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
                [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
                [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
                [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
            ],
            "shape_list3": [
                [s1, s2, w3, h1, w1, h1, lc, lt, ly],
                [s1, s2, w3, h2, w5, h2, lc, lt, ly],
                [s1, s2, w1, h1, w1, y_last + 50, lc, lt, ly],
                [s1, s2, w5, h2, w5, y_first - 40, lc, lt, ly],
                [s1, s2, w2, h3, w2, h4, lc, lt, ly],
                [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
                [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
                [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
                [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
                [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
                [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
                [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
                [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
            ],
            "shape_list4": [
                [s1, s2, w3, h1, w5, h1, lc, lt, ly],
                [s1, s2, w3, h2, w5, h2, lc, lt, ly],
                [s1, s2, w5, h1, w5, y_last + 40, lc, lt, ly],
                [s1, s2, w5, h2, w5, y_first - 40, lc, lt, ly],
                [s1, s2, w2, h3, w2, h4, lc, lt, ly],
                [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
                [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
                [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
                [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
                [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
                [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
                [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
                [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
            ]
        },
        2: {  # mode2では異なる設定を指定可能（現状は例として同じ設定を使用）
            # mode2独自の設定に書き換え可能
            "shape_list": [
                [s1, s2, w3, h1, w6, h1, lc, lt, ly],
                [s1, s2, w3, h2, w6, h2, lc, lt, ly],
                [s1, s2, w2, h3, w2, h4, lc, lt, ly],
                [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
                [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
                [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
                [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
                [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
                [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
                [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
                [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
            ],
            "shape_list2": [
                [s1, s2, w3, h1, w5, h1, lc, lt, ly],
                [s1, s2, w3, h2, w6, h2, lc, lt, ly],
                [s1, s2, w5, h1, w5, y_last + 40, lc, lt, ly],
                [s1, s2, w2, h3, w2, h4, lc, lt, ly],
                [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
                [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
                [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
                [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
                [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
                [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
                [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
                [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
            ],
            "shape_list3": [
                [s1, s2, w3, h1, w6, h1, lc, lt, ly],
                [s1, s2, w3, h2, w5, h2, lc, lt, ly],
                [s1, s2, w5, h2, w5, y_first - 40, lc, lt, ly],
                [s1, s2, w2, h3, w2, h4, lc, lt, ly],
                [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
                [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
                [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
                [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
                [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
                [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
                [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
                [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
            ],
            "shape_list4": [
                [s1, s2, w3, h1, w5, h1, lc, lt, ly],
                [s1, s2, w3, h2, w5, h2, lc, lt, ly],
                [s1, s2, w5, h1, w5, y_last + 40, lc, lt, ly],
                [s1, s2, w5, h2, w5, y_first - 40, lc, lt, ly],
                [s1, s2, w2, h3, w2, h4, lc, lt, ly],
                [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
                [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
                [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
                [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
                [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
                [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
                [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
                [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
            ]
        },
        3: {  # mode2では異なる設定を指定可能（現状は例として同じ設定を使用）
            # mode2独自の設定に書き換え可能
            "shape_list": [
                [s1, s2, w3, h1, w6, h1, lc, lt, ly],
                [s1, s2, w3, h2, w6, h2, lc, lt, ly],
                [s1, s2, w2, h3, w2, h4, lc, lt, ly],
                [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
                [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
                [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
                [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
                [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
                [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
                [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
                [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
            ],
            "shape_list2": [
                [s1, s2, w3, h1, w5, h1, lc, lt, ly],
                [s1, s2, w3, h2, w6, h2, lc, lt, ly],
                [s1, s2, w2, h3, w2, h4, lc, lt, ly],
                [s1, s2, w5, h1, w5, y_last + 40, lc, lt, ly],
                [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
                [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
                [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
                [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
                [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
                [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
                [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
                [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
            ],
            "shape_list3": [
                [s1, s2, w3, h1, w6, h1, lc, lt, ly],
                [s1, s2, w3, h2, w5, h2, lc, lt, ly],
                [s1, s2, w2, h3, w2, h4, lc, lt, ly],
                [s1, s2, w5, h2, w5, y_first - 40, lc, lt, ly],
                [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
                [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
                [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
                [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
                [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
                [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
                [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
                [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
            ],
            "shape_list4": [
                [s1, s2, w3, h1, w5, h1, lc, lt, ly],
                [s1, s2, w3, h2, w5, h2, lc, lt, ly],
                [s1, s2, w2, h3, w2, h4, lc, lt, ly],
                [s1, s2, w5, h1, w5, y_last + 40, lc, lt, ly],
                [s1, s2, w5, h2, w5, y_first - 40, lc, lt, ly],
                [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
                [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
                [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
                [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
                [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
                [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
                [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
                [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
            ],
        }
    }

    new_lines = []

    if mode == 1:
        # 元々の条件 (mode 1用)
        if (h1 - (y_last + 40)) > 0:
            current_app.logger.debug("mood1:上面切欠き")
            current_app.logger.debug((h1 - (y_last + 40)) > 0)
            current_app.logger.debug(h1 - (y_last + 40))
            top_horizontal_line = [
                s1, s2, w6, y_last + 40, x_last + 25, y_last + 40, lc, lt, ly
            ]
        else:
            current_app.logger.debug("mood1:上面突出し。")
            current_app.logger.debug((h1 - (y_last + 40)) > 0)
            current_app.logger.debug(h1 - (y_last + 40))
            top_horizontal_line = [
                s1, s2, w5, y_last + 40, x_last + 25, y_last + 40, lc, lt, ly
            ]
        new_lines.append(top_horizontal_line)

        if ((h9 + y_first) - 40) > 0:
            current_app.logger.debug("mood1:下面切欠き。")
            current_app.logger.debug((h9 + y_first) - 40 > 0)
            current_app.logger.debug((h9 + y_first) - 40)
            bottom_horizontal_line = [
                s1, s2, w6, y_first - 40, x_last + 40, y_first - 40, lc, lt, ly
            ]
        else:
            current_app.logger.debug("mood1:下面突出し。")
            current_app.logger.debug((h9 + y_first) - 40 > 0)
            current_app.logger.debug((h9 + y_first) - 40)
            bottom_horizontal_line = [
                s1, s2, w5, y_first - 40, x_last + 40, y_first - 40, lc, lt, ly
            ]
        new_lines.append(bottom_horizontal_line)

        right_vertical_line = [
            s1, s2, x_last + 40, y_first - 40, x_last + 40, y_last + 25, lc, lt, ly
        ]
        new_lines.append(right_vertical_line)

        cut_line = [
            s1, s2, x_last + 25, y_last + 40, x_last + 40, y_last + 25, lc, lt, ly
        ]
        new_lines.append(cut_line)

        # 角丸線の追加条件をフラグに基づいて行う
        if final_shape_type in ["shape_list", "shape_list3"]:
            current_app.logger.debug("top_corner_lineが選択されました。")
            top_corner_line = [s1, s2, w6, y_last + 50, 180, 270, lc, lt, ly, "E", 10, 0]
            new_lines.append(top_corner_line)
            
        if final_shape_type in ["shape_list", "shape_list2"]:
            current_app.logger.debug("bottom_corner_lineが選択されました。")
            bottom_corner_line = [s1, s2, w6, y_first - 50, 90, 180, lc, lt, ly, "E", 10, 0]
            new_lines.append(bottom_corner_line)

    elif mode == 2:
        # top_horizontal_line (mode2用)
        if (- d - y_set + y_offset) > 0:
            current_app.logger.debug("mood2:上面斜め。")
            current_app.logger.debug((- d - y_set + y_offset) - (r + 10))
            top_horizontal_line = [
                s1, s2, w6, h1, x_last + 40, h5, lc, lt, ly
            ]
            new_lines.append(top_horizontal_line)
        else:
            current_app.logger.debug("mood2:上面突出し。")
            current_app.logger.debug(- d - y_set + y_offset)
            top_horizontal_line = [
                s1, s2, w5, y_last + 40, x_last + 25, y_last + 40, lc, lt, ly
            ]
            cut_line = [
                s1, s2, x_last + 25, y_last + 40, x_last + 40, y_last + 25, lc, lt, ly
            ]
            new_lines.append(top_horizontal_line)
            new_lines.append(cut_line)

        # bottom_horizontal_lineとright_vertical_line (mode2用)
        if (h8 + y_set + y_offset) > 0:
            current_app.logger.debug("mood2:下面斜め。")
            current_app.logger.debug((h8 + y_set + y_offset) - (r + 10))
            bottom_horizontal_line = [
                s1, s2, w6, h2, x_last + 40, h6, lc, lt, ly
            ]
            new_lines.append(bottom_horizontal_line)
        else:
            current_app.logger.debug("mood2:下面突出し。")
            current_app.logger.debug(h8 + y_set + y_offset)
            bottom_horizontal_line = [
                s1, s2, w5, y_first - 40, x_last + 40, y_first - 40, lc, lt, ly
            ]
            new_lines.append(bottom_horizontal_line)

        #mode = int(request.form.get("モードを選択（元々の条件=1、新しい条件=2）: "))

        # 条件フラグを設定
        cond1 = (- d - y_set + y_offset) < 0
        cond2 = (h8 + y_set + y_offset) < 0

        # 4通りのケースで分岐
        if cond1 and cond2:
            # 両方とも True の場合
            # この場合の right_vertical_line の設定を（例として）行う
            right_vertical_line = [s1, s2, x_last + 40, y_last + 25, x_last + 40, y_first - 40, lc, lt, ly]
            new_lines.append(right_vertical_line)
            current_app.logger.debug("両方とも True")
        elif (not cond1) and (not cond2):
            # 両方とも False の場合
            right_vertical_line = [s1, s2, x_last + 40, h7, x_last + 40, y_first - 40, lc, lt, ly]
            new_lines.append(right_vertical_line)
            current_app.logger.debug("両方とも False")
        elif cond1 and (not cond2):
            # 条件1のみ True の場合
            right_vertical_line = [s1, s2, x_last + 40, y_last + 25, x_last + 40, h6, lc, lt, ly]
            new_lines.append(right_vertical_line)
            current_app.logger.debug("条件1のみ True")
        elif (not cond1) and cond2:
            # 条件2のみ True の場合
            right_vertical_line = [s1, s2, x_last + 40, h5, x_last + 40, y_first - 40, lc, lt, ly]
            new_lines.append(right_vertical_line)
            current_app.logger.debug("条件2のみ True")
        else:
            # 万が一のためのデフォルト値
            right_vertical_line = []
            new_lines.append(right_vertical_line)

    elif mode == 3:
        # 元々の条件 (mode 3用)
        if (- d - y_set + y_offset) > 0:
            current_app.logger.debug("mood3:上面斜め。")
            current_app.logger.debug(h1 - (y_last + 40))
            current_app.logger.debug(- d - y_set + y_offset)
            top_horizontal_line = [
                s1, s2, w6, h1, x_last + 40, h5, lc, lt, ly
            ]
            new_lines.append(top_horizontal_line)
        else:
            current_app.logger.debug("mood3:上面切欠き。")
            current_app.logger.debug(h1 - (y_last + 40))
            current_app.logger.debug(- d - y_set + y_offset)
            top_horizontal_line = [
                s1, s2, w5, y_last + 40, x_last + 25, y_last + 40, lc, lt, ly
            ]
            new_lines.append(top_horizontal_line)

        # 元々の条件 (mode 3用)
        if (h8 + y_set + y_offset) > 0:
            current_app.logger.debug("mood3:下面斜め。")
            current_app.logger.debug(h1 - (y_last + 40))
            current_app.logger.debug(- d - y_set + y_offset)
            bottom_horizontal_line = [
                s1, s2, w6, h2, x_last + 40, h6, lc, lt, ly
            ]
            new_lines.append(bottom_horizontal_line)
        else:
            current_app.logger.debug("mood3:下面切欠き。")
            current_app.logger.debug(h1 - (y_last + 40))
            current_app.logger.debug(- d - y_set + y_offset)
            bottom_horizontal_line = [
                s1, s2, w5, y_first - 40, x_last + 40, y_first - 40, lc, lt, ly
            ]
            new_lines.append(bottom_horizontal_line)

        # 条件フラグを設定
        cond1 = (- d - y_set + y_offset) < 0
        cond2 = (h8 + y_set + y_offset) < 0

        if include_header:
            base_template = [
                ["#ガセットプレート"],
                [b_set],
                [999, 100, 50],
                [2, "H",a,"-H",e, y_set, hole_column_x, "x", hole_row_y, hole_size, "φ"],
                ["S", 100, 50],
                [800, 1],
            ]
        else:
            base_template = [
                [2, "H",a,"-H",e, y_set, hole_column_x, "x", hole_row_y, hole_size, "φ"],
                ["S", 100, 50],
                [800, 1],
            ]

        selected_template = base_template + mode_templates[mode][final_shape_type]
        # リスト作成関数を呼び出す
        final_shape_list = create_shape_list(selected_template, hole_list, new_lines)

        result_str = "\n".join(
        " ".join(str(item) for item in row)
        for row in final_shape_list
        )

        return render_template('gusset_type/index.html',
                            steel_sizes=steel_options,
                            defaults=defaults,
                            result_str=result_str,
                            error_message=error_message)
