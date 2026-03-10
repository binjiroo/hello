from flask import Blueprint, render_template, request, session
import math
from .config import (
    ibeam_steel_r_mapping as steel_r_mapping,
)  # ← これで定義済みマッピングを読み込む


steel_sizes = list(steel_r_mapping.keys())
ibeam_size_bp = Blueprint(
    "ibeam_size", __name__, template_folder="templates/ibeam_size"
)


# セッションからデフォルト値をまとめて取ってくるヘルパー
def get_defaults():
    return {
        "steel_name": session.get("steel_name", ""),
        "s1": session.get("s1", "01"),
        "s2": session.get("s2", "01"),
        "offset_choice": session.get("offset_choice", "5"),
        "lc": session.get("lc", "1"),
        "lt": session.get("lt", "1"),
        "ly": session.get("ly", "0"),
        "members": session.get("members", "1"),
        "separator": session.get("separator", "999"),
        "scale": session.get("scale", ""),
        "command": session.get("command", "1"),
    }


@ibeam_size_bp.route("/", methods=["GET", "POST"])
def index():
    filenames = [
        "JW_OPT4.DAT",
        "JW_OPT4B.DAT",
        "JW_OPT4C.DAT",
        "JW_OPT4D.DAT",
        "JW_OPT4E.DAT",
        "JW_OPT4F.DAT",
        "JW_OPT4G.DAT",
        "JW_OPT4H.DAT",
        "JW_OPT4I.DAT",
        "JW_OPT4J.DAT",
        "JW_OPT4K.DAT",
        "JW_OPT4L.DAT",
        "JW_OPT4M.DAT",
        "JW_OPT4N.DAT",
        "JW_OPT4O.DAT",
        "JW_OPT4P.DAT",
        "JW_OPT4Q.DAT",
        "JW_OPT4R.DAT",
        "JW_OPT4S.DAT",
        "JW_OPT4T.DAT",
        "JW_OPT4U.DAT",
        "JW_OPT4V.DAT",
        "JW_OPT4W.DAT",
        "JW_OPT4X.DAT",
        "JW_OPT4Y.DAT",
        "JW_OPT4Z.DAT",
    ]
    steel_sizes = list(steel_r_mapping.keys())
    defaults = get_defaults()
    result_str = ""
    error_message = ""

    if request.method == "POST":
        action = request.form.get("action", "new")

        # 「クリア」処理
        if action == "clear":
            session.clear()
            defaults = get_defaults()
            return render_template(
                "ibeam_size/index.html",
                filenames=filenames,
                steel_sizes=steel_sizes,
                defaults=defaults,
                result_str="",
                error_message="",
            )

        # 1) フォーム値 → セッション
        for key in defaults.keys():
            session[key] = request.form.get(key, defaults[key])

        # 2) パラメータ取得
        steel_name = session["steel_name"]
        s1 = session["s1"]
        s2 = session["s2"]
        offset_choice = session["offset_choice"]
        lc = session["lc"]
        lt = session["lt"]
        ly = session["ly"]
        members = session["members"]
        separator = session["separator"]
        scale = session["scale"]
        command = session["command"]
        prev_result = request.form.get("prev_result", "")

        # 3) 座標計算ロジック（もとの app.py からコピペして組み込む）
        # 座標計算
        flange_taper_angle = 8
        angle_deg = 90 + flange_taper_angle
        angle_rad = math.radians(angle_deg)
        x_coord = math.cos(angle_rad)
        y_coord = math.sin(angle_rad)
        y_tan = math.tan(math.radians(8))

        if steel_name not in steel_r_mapping:
            error_message = "指定されたサイズが存在しません。"
        else:
            r1, r2 = steel_r_mapping[steel_name]
            try:
                values_str = steel_name.split("x")
                values = [float(val) for val in values_str]
                a, b, c, d = values
            except Exception as e:
                error_message = f"数値変換エラー: {e}"

            # 中間変数の計算
            mid = (b / 2 - c / 2) / 2
            ff = mid - (r2 * x_coord)
            gg = mid - (r1 * x_coord)
            base_y = (a / 2) - d
            hh = base_y - ff * y_tan
            ii = base_y + gg * y_tan

            # オフセットの候補
            offsets = {
                1: (b / 2, -a / 2),
                2: (0, -a / 2),
                3: (-b / 2, -a / 2),
                4: (b / 2, 0),
                5: (0, 0),
                6: (-b / 2, 0),
                7: (b / 2, a / 2),
                8: (0, a / 2),
                9: (-b / 2, a / 2),
            }
            choice = int(offset_choice) if offset_choice.isdigit() else 5
            x_offset, y_offset = offsets.get(choice, (0, 0))

            # 各変数の計算
            w1 = b / 2
            w2 = c / 2
            w3 = w2 + (r2 * x_coord) + r2
            w4 = w1 - (r1 * x_coord) - r1
            w5 = w2 + r2
            w6 = w1 - r1
            h1 = a / 2
            h2 = (hh) - (r2 * y_coord)
            h3 = hh
            h4 = (ii) + (r1 * y_coord)
            h5 = ii

            # shape_list の作成（ここでは header なしで shape_list のリストのみ出力）
            shape_list = [
                ["#溝型鋼断面"],
                [members],
                [separator, scale],
                [command, "[-" + steel_name],
                [800, scale],
                # 基準線
                [
                    s1,
                    s2,
                    0 + x_offset,
                    h1 + y_offset,
                    0 + x_offset,
                    -h1 + y_offset,
                    lc,
                    lt,
                    ly,
                ],
                [
                    s1,
                    s2,
                    -w1 + x_offset,
                    0 + y_offset,
                    w1 + x_offset,
                    0 + y_offset,
                    lc,
                    lt,
                    ly,
                ],
                # 外フランジ上下
                [
                    s1,
                    s2,
                    -w1 + x_offset,
                    h1 + y_offset,
                    w1 + x_offset,
                    h1 + y_offset,
                    lc,
                    lt,
                    ly,
                ],
                [
                    s1,
                    s2,
                    -w1 + x_offset,
                    -h1 + y_offset,
                    w1 + x_offset,
                    -h1 + y_offset,
                    lc,
                    lt,
                    ly,
                ],
                # 内フランジ上下
                [
                    s1,
                    s2,
                    -w3 + x_offset,
                    h3 + y_offset,
                    -w4 + x_offset,
                    h5 + y_offset,
                    lc,
                    lt,
                    ly,
                ],
                [
                    s1,
                    s2,
                    w3 + x_offset,
                    h3 + y_offset,
                    w4 + x_offset,
                    h5 + y_offset,
                    lc,
                    lt,
                    ly,
                ],
                [
                    s1,
                    s2,
                    -w3 + x_offset,
                    -h3 + y_offset,
                    -w4 + x_offset,
                    -h5 + y_offset,
                    lc,
                    lt,
                    ly,
                ],
                [
                    s1,
                    s2,
                    w3 + x_offset,
                    -h3 + y_offset,
                    w4 + x_offset,
                    -h5 + y_offset,
                    lc,
                    lt,
                    ly,
                ],
                # ウェーブ
                [
                    s1,
                    s2,
                    -w2 + x_offset,
                    h2 + y_offset,
                    -w2 + x_offset,
                    -h2 + y_offset,
                    lc,
                    lt,
                    ly,
                ],
                [
                    s1,
                    s2,
                    w2 + x_offset,
                    h2 + y_offset,
                    w2 + x_offset,
                    -h2 + y_offset,
                    lc,
                    lt,
                    ly,
                ],
                # フランジエッジ
                [
                    s1,
                    s2,
                    w1 + x_offset,
                    h1 + y_offset,
                    w1 + x_offset,
                    h4 + y_offset,
                    lc,
                    lt,
                    ly,
                ],
                [
                    s1,
                    s2,
                    -w1 + x_offset,
                    h1 + y_offset,
                    -w1 + x_offset,
                    h4 + y_offset,
                    lc,
                    lt,
                    ly,
                ],
                [
                    s1,
                    s2,
                    w1 + x_offset,
                    -h1 + y_offset,
                    w1 + x_offset,
                    -h4 + y_offset,
                    lc,
                    lt,
                    ly,
                ],
                [
                    s1,
                    s2,
                    -w1 + x_offset,
                    -h1 + y_offset,
                    -w1 + x_offset,
                    -h4 + y_offset,
                    lc,
                    lt,
                    ly,
                ],
                # r 指定
                [s1, s2, -w5 + x_offset, h2 + y_offset, 0, 82, lc, lt, ly, "E", r2],
                [s1, s2, w5 + x_offset, h2 + y_offset, 98, 180, lc, lt, ly, "E", r2],
                [s1, s2, -w5 + x_offset, -h2 + y_offset, 278, 0, lc, lt, ly, "E", r2],
                [s1, s2, w5 + x_offset, -h2 + y_offset, 180, 262, lc, lt, ly, "E", r2],
                [s1, s2, w6 + x_offset, h4 + y_offset, 278, 0, lc, lt, ly, "E", r1],
                [s1, s2, -w6 + x_offset, h4 + y_offset, 180, 262, lc, lt, ly, "E", r1],
                [s1, s2, w6 + x_offset, -h4 + y_offset, 0, 82, lc, lt, ly, "E", r1],
                [s1, s2, -w6 + x_offset, -h4 + y_offset, 98, 180, lc, lt, ly, "E", r1],
                [separator, scale],
            ]

            list_for_output = shape_list[3:] if action == "append" else shape_list
            new_lines = [" ".join(str(item) for item in row) for row in list_for_output]
            new_result = "\n".join(new_lines)

            result_str = (
                (prev_result + "\n" + new_result).strip()
                if action == "append"
                else new_result
            )

        # 4) 計算後、再度 defaults 更新
        defaults = get_defaults()

    # GET または POST後に必ず描画
    return render_template(
        "ibeam_size/index.html",
        filenames=filenames,
        steel_sizes=steel_sizes,
        defaults=defaults,
        result_str=result_str,
        error_message=error_message,
    )
