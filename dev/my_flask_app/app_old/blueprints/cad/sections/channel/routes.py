from flask import Blueprint, render_template, request, session

import math
import sys
from pathlib import Path

app_root = Path(__file__).resolve().parents[5]
if str(app_root) not in sys.path:
    sys.path.insert(0, str(app_root))

from app.config import cannel_steel_r_mapping as steel_r_mapping

bp = Blueprint("channel", __name__, url_prefix="/channel", template_folder="templates")


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


@bp.route("/", methods=["GET", "POST"])
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

        if action == "clear":
            session.clear()
            defaults = get_defaults()
            return render_template(
                "cannel_size/index.html",
                filenames=filenames,
                steel_sizes=steel_sizes,
                defaults=defaults,
                result_str="",
                error_message="",
            )

        for key in defaults.keys():
            session[key] = request.form.get(key, defaults[key])

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

        angle_deg = 95
        angle_rad = math.radians(angle_deg)
        x_coord = math.cos(angle_rad)
        y_coord = math.sin(angle_rad)
        y_tan = math.tan(math.radians(5))

        if steel_name not in steel_r_mapping:
            error_message = "サイズが不正です。"
        else:
            r1, r2 = steel_r_mapping[steel_name]
            try:
                values_str = steel_name.split("x")
                values = [float(val) for val in values_str]
                a, b, c, d = values
            except Exception as e:
                error_message = f"サイズ解析に失敗しました: {e}"
            else:
                ff = ((b - c) / 2) - (r2 + (r2 * x_coord))
                gg = ((b - c) / 2) - (r1 + (r1 * x_coord))
                hh = ((a / 2) - d) - ff * y_tan
                ii = ((a / 2) - d) + gg * y_tan

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

                w1 = b / 2
                w2 = b / 2 - c
                w3 = (((b - c) / 2) - (r2 + (r2 * x_coord))) - (c / 2)
                w4 = (((b - c) / 2) - (r1 + (r1 * x_coord))) + (c / 2)
                w5 = b / 2 - (c + r2)
                w6 = b / 2 - r1
                h1 = a / 2
                h2 = (((a / 2) - d) - ff * y_tan) - (r2 * y_coord)
                h3 = ((a / 2) - d) - ff * y_tan
                h4 = (((a / 2) - d) + gg * y_tan) + (r1 * y_coord)
                h5 = ((a / 2) - d) + gg * y_tan

                shape_list = [
                    ["#貅晏梛驪ｼ譁ｭ髱｢"],
                    [members],
                    [separator, scale],
                    [command, "[-" + steel_name],
                    [800, scale],
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
                    [
                        s1,
                        s2,
                        -w3 + x_offset,
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
                        w4 + x_offset,
                        -h5 + y_offset,
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
                        -h1 + y_offset,
                        lc,
                        lt,
                        ly,
                    ],
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
                        w1 + x_offset,
                        -h1 + y_offset,
                        w1 + x_offset,
                        -h4 + y_offset,
                        lc,
                        lt,
                        ly,
                    ],
                    [s1, s2, -w5 + x_offset, h2 + y_offset, 95, 180, lc, lt, ly, "E", r2],
                    [s1, s2, -w5 + x_offset, -h2 + y_offset, 180, 265, lc, lt, ly, "E", r2],
                    [s1, s2, w6 + x_offset, h4 + y_offset, 275, 0, lc, lt, ly, "E", r1],
                    [s1, s2, w6 + x_offset, -h4 + y_offset, 0, 85, lc, lt, ly, "E", r1],
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

        defaults = get_defaults()

    return render_template(
        "cannel_size/index.html",
        filenames=filenames,
        steel_sizes=steel_sizes,
        defaults=defaults,
        result_str=result_str,
        error_message=error_message,
    )
