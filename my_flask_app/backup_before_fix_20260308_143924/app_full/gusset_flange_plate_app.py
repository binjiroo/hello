import math
from flask import Blueprint, render_template, request, session
from .config import (
    gusset_flange_plate_mapping as steel_r_mapping,
)  # ← これで定義済みマッピングを読み込む

steel_sizes = list(steel_r_mapping.keys())

gusset_flange_plate_bp = Blueprint(
    "gusset_flange_plate", __name__, template_folder="templates/gusset_flange_plate"
)


# セッションからデフォルト値をまとめて取ってくるヘルパー
def get_defaults():
    return {
        "h_type": session.get("h_type", ""),
        "sub_h_type": session.get("sub_h_type", ""),
        "hole_column": session.get("hole_column", "1"),
        "hole_pitch": session.get("hole_pitch", "0"),
        "gusset_name": session.get("gusset_name", ""),
        "t": session.get("t", "6"),
        "s1": session.get("s1", "01"),
        "s2": session.get("s2", "01"),
        "off_choice": session.get("off_choice", "5"),
        "lc": session.get("lc", "1"),
        "lt": session.get("lt", "1"),
        "ly": session.get("ly", "0"),
        "members": session.get("members", "5"),
        "separator": session.get("separator", "999"),
        "scale": session.get("scale", "1"),
        "actual_size": session.get("actual_size", "800"),
        "command": session.get("command", "1"),
    }


@gusset_flange_plate_bp.route("/", methods=["GET", "POST"])
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
    error_msg = ""

    if request.method == "POST":
        action = request.form.get("action", "new")
        prev_result = request.form.get("prev_result", "")

        # クリア
        if action == "clear":
            session.clear()
            defaults = get_defaults()
            return render_template(
                "gusset_flange_plate/index.html",
                filenames=filenames,
                steel_sizes=list(steel_r_mapping.keys()),
                defaults=defaults,
                result_str="",
                error_msg="",
            )

        # セッションに保存
        for key in defaults.keys():
            session[key] = request.form.get(key, defaults[key])

        # セッションから読み出し
        h_type = session["h_type"]
        sub_h_type = session["sub_h_type"]
        hole_column = int(session["hole_column"])
        hole_pitch = int(session["hole_pitch"])
        gusset_name = session["gusset_name"]
        t = float(session["t"])
        s1 = session["s1"]
        s2 = session["s2"]
        off_choice = session["off_choice"]
        lc = session["lc"]
        lt = session["lt"]
        ly = session["ly"]
        members = session["members"]
        separator = session["separator"]
        scale = session["scale"]
        actual_size = session["actual_size"]
        command = session["command"]

        # a,b,c の抽出
        vals = h_type.split("x") + sub_h_type.split("x")
        filtered = [v for i, v in enumerate(vals) if i not in (0, 3, 4, 5, 7)]
        a, b, c = map(float, filtered)

        # オフセットの候補
        offs = {
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
        choice = int(off_choice) if off_choice.isdigit() else 5
        x_off, y_off = offs.get(choice, (0, 0))

        # 寸法計算
        w1, w2 = c / 2, c / 2 + t
        w3, w4 = -c / 2 - 20, c / 2 + t + 20
        h1, h2 = b / 2, a / 2
        h3, h4 = a / 2 + 90, a / 2 + 50
        extension = (hole_column - 1) * hole_pitch
        h3_end = h3 + extension

        # shape_list 組み立て
        shape_list = [
            ["#ガセットプレート"],
            [members],
            [separator, scale],
            [command, gusset_name],
            [actual_size, scale],
            [s1, s2, w1 + x_off, h1 + y_off, w2 + x_off, h1 + y_off, lc, lt, ly],
            [s1, s2, w1 + x_off, h2 + y_off, w2 + x_off, h2 + y_off, lc, lt, ly],
            [s1, s2, w1 + x_off, h1 + y_off, w1 + x_off, h3_end + y_off, lc, lt, ly],
            [s1, s2, w2 + x_off, h1 + y_off, w2 + x_off, h3_end + y_off, lc, lt, ly],
        ]
        for i in range(hole_column):
            y_bolt = h4 + i * hole_pitch
            shape_list.append(
                [
                    s1,
                    s2,
                    w3 + x_off,
                    y_bolt + y_off,
                    w4 + x_off,
                    y_bolt + y_off,
                    lc,
                    lt,
                    ly,
                ]
            )
        shape_list.append(
            [s1, s2, w1 + x_off, h3_end + y_off, w2 + x_off, h3_end + y_off, lc, lt, ly]
        )
        shape_list.extend(
            [
                [s1, s2, w1 + x_off, -h1 + y_off, w2 + x_off, -h1 + y_off, lc, lt, ly],
                [
                    s1,
                    s2,
                    w1 + x_off,
                    -h2 + 10 + y_off,
                    w2 + x_off,
                    -h2 + 10 + y_off,
                    lc,
                    lt,
                    ly,
                ],
                [
                    s1,
                    s2,
                    w1 + x_off,
                    -h1 + y_off,
                    w1 + x_off,
                    -h2 + 10 + y_off,
                    lc,
                    lt,
                    ly,
                ],
                [
                    s1,
                    s2,
                    w2 + x_off,
                    -h1 + y_off,
                    w2 + x_off,
                    -h2 + 10 + y_off,
                    lc,
                    lt,
                    ly,
                ],
                [999, 100, 50],
            ]
        )

        lines = [" ".join(str(e) for e in row) for row in shape_list]
        new_result = "\n".join(lines)

        # 新規 or 追加
        result_str = (
            (prev_result + "\n" + new_result).strip()
            if action == "append"
            else new_result
        )
        defaults = get_defaults()

    return render_template(
        "gusset_flange_plate/index.html",
        filenames=filenames,
        steel_sizes=list(steel_r_mapping.keys()),
        defaults=defaults,
        result_str=result_str,
        error_msg=error_msg,
    )
