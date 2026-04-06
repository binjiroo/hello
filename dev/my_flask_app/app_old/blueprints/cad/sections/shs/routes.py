from flask import Blueprint, render_template, request, session

import sys
from pathlib import Path

app_root = Path(__file__).resolve().parents[5]
if str(app_root) not in sys.path:
    sys.path.insert(0, str(app_root))

from app.config import shs_steel_r_mapping as steel_r_mapping

bp = Blueprint("shs", __name__, url_prefix="/shs", template_folder="templates")


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
        "actual_size": session.get("actual_size", ""),
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
    defaults = get_defaults()
    result_str = ""
    error_message = ""

    if request.method == "POST":
        action = request.form.get("action", "new")

        if action == "clear":
            session.clear()
            defaults = get_defaults()
            return render_template(
                "shs_size/index.html",
                filenames=filenames,
                steel_sizes=list(steel_r_mapping.keys()),
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
        actual_size = session["actual_size"]
        command = session["command"]
        prev_result = request.form.get("prev_result", "")

        r1, r2 = steel_r_mapping.get(steel_name)
        a, b, c = map(float, steel_name.split("x"))

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
        x_off, y_off = offsets.get(choice, (0, 0))

        w1 = b / 2
        w2 = (b / 2) - c
        w3 = (b / 2) - r1
        h1 = a / 2
        h2 = (a / 2) - c
        h3 = (a / 2) - r1

        shape_list = [
            ["#隗貞ｽ｢驪ｼ邂｡譁ｭ髱｢"],
            [members],
            [separator, scale],
            [command, "笆｡-" + steel_name],
            [actual_size, scale],
            [s1, s2, 0 + x_off, h1 + y_off, 0 + x_off, -h1 + y_off, lc, lt, ly],
            [s1, s2, -w1 + x_off, 0 + y_off, w1 + x_off, 0 + y_off, lc, lt, ly],
            [s1, s2, -w1 + x_off, h1 + y_off, w1 + x_off, h1 + y_off, lc, lt, ly],
            [s1, s2, -w1 + x_off, -h1 + y_off, w1 + x_off, -h1 + y_off, lc, lt, ly],
            [s1, s2, w1 + x_off, h1 + y_off, w1 + x_off, -h1 + y_off, lc, lt, ly],
            [s1, s2, -w1 + x_off, h1 + y_off, -w1 + x_off, -h1 + y_off, lc, lt, ly],
            [s1, s2, -w3 + x_off, h2 + y_off, w3 + x_off, h2 + y_off, lc, lt, ly],
            [s1, s2, -w3 + x_off, -h2 + y_off, w3 + x_off, -h2 + y_off, lc, lt, ly],
            [s1, s2, w2 + x_off, h3 + y_off, w2 + x_off, -h3 + y_off, lc, lt, ly],
            [s1, s2, -w2 + x_off, h3 + y_off, -w2 + x_off, -h3 + y_off, lc, lt, ly],
            [s1, s2, -w3 + x_off, h3 + y_off, 90, 180, lc, lt, ly, "E", r1],
            [s1, s2, w3 + x_off, h3 + y_off, 0, 90, lc, lt, ly, "E", r1],
            [s1, s2, -w3 + x_off, -h3 + y_off, 180, 270, lc, lt, ly, "E", r1],
            [s1, s2, w3 + x_off, -h3 + y_off, 270, 0, lc, lt, ly, "E", r1],
            [s1, s2, -w3 + x_off, h3 + y_off, 90, 180, lc, lt, ly, "E", r2],
            [s1, s2, w3 + x_off, h3 + y_off, 0, 90, lc, lt, ly, "E", r2],
            [s1, s2, -w3 + x_off, -h3 + y_off, 180, 270, lc, lt, ly, "E", r2],
            [s1, s2, w3 + x_off, -h3 + y_off, 270, 0, lc, lt, ly, "E", r2],
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
        "shs_size/index.html",
        filenames=filenames,
        defaults=defaults,
        result_str=result_str,
        error_message=error_message,
        steel_sizes=list(steel_r_mapping.keys()),
    )
