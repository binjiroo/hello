from flask import Blueprint, render_template, request, session

import sys
from pathlib import Path

app_root = Path(__file__).resolve().parents[5]
if str(app_root) not in sys.path:
    sys.path.insert(0, str(app_root))

from app.config import gusset_web_plate_mapping as steel_r_mapping

bp = Blueprint(
    "gusset_web",
    __name__,
    url_prefix="/gusset_web",
    template_folder="templates",
)


def get_defaults():
    return {
        "h_type": session.get("h_type", ""),
        "sub_h_type": session.get("sub_h_type", ""),
        "hole_column": session.get("hole_column", "1"),
        "hole_pitch": session.get("hole_pitch", "0"),
        "clearance": session.get("clearance", "10"),
        "end_hole_pitch": session.get("end_hole_pitch", "40"),
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
    error_msg = ""

    if request.method == "POST":
        action = request.form.get("action", "new")
        prev_result = request.form.get("prev_result", "")

        if action == "clear":
            session.clear()
            defaults = get_defaults()
            return render_template(
                "gusset_web_plate/index.html",
                filenames=filenames,
                steel_sizes=list(steel_r_mapping.keys()),
                defaults=defaults,
                result_str="",
                error_msg="",
            )

        for key in defaults.keys():
            session[key] = request.form.get(key, defaults[key])

        def to_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        h_type = session["h_type"]
        sub_h_type = session["sub_h_type"]
        hole_column = to_int(session["hole_column"])
        hole_pitch = to_int(session["hole_pitch"])
        clearance = to_int(session.get("clearance", 0) or 0)
        end_hole = to_int(session.get("end_hole_pitch", 40) or 40)
        gusset_name = session["gusset_name"]
        mating_gusset = f'"{gusset_name}'
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

        try:
            vals = h_type.split("x") + sub_h_type.split("x")
            filtered = [v for i, v in enumerate(vals) if i not in (0, 3, 4, 7)]
            a, b, c, d = map(float, filtered)
        except Exception:
            error_msg = "サイズの形式が不正です。"
        else:
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

            w1, w2 = d / 2, d / 2 + t
            w3, w4 = -d / 2 - 20, d / 2 + t + 20
            w5 = a / 2
            h1, h2 = b / 2, a / 2 + 90
            h3, h4 = c / 2 + d / 2, a / 2 + clearance + end_hole
            extension = (hole_column - 1) * hole_pitch
            h3_end = h3 + extension

            header_rows = [
                ["#ガセットプレート"],
                [members],
                [separator, scale],
            ]
            name_rows = [
                [command, gusset_name],
                [actual_size, scale],
            ]
            frame_rows = [
                [s1, s2, w1 + x_off, h1 + y_off, w2 + x_off, h1 + y_off, lc, lt, ly],
                [s1, s2, w1 + x_off, h2 + y_off, w2 + x_off, h2 + y_off, lc, lt, ly],
                [s1, s2, w1 + x_off, h1 + y_off, w1 + x_off, h2 + y_off, lc, lt, ly],
                [s1, s2, w2 + x_off, h1 + y_off, w2 + x_off, h2 + y_off, lc, lt, ly],
                [
                    s1,
                    s2,
                    -w5 + x_off,
                    h2 + y_off,
                    -w5 + x_off,
                    h2 + 10 + y_off,
                    10000,
                    4,
                    ly,
                    mating_gusset,
                ],
            ]

            append_only_rows = name_rows + frame_rows

            bolt_rows = []
            if hole_column >= 1:
                intervals = hole_column - 1
                span = intervals * hole_pitch
                start = -span / 2

                last_bolt_y = None
                for i in range(hole_column):
                    y_bolt = h4 + start + i * hole_pitch
                    last_bolt_y = y_bolt
                    bolt_rows.append(
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

                top_line_y = (
                    last_bolt_y + 40 if last_bolt_y is not None else (h1 + 40)
                )
                top_line_row = [
                    s1,
                    s2,
                    w1 + x_off,
                    top_line_y + y_off,
                    w2 + x_off,
                    top_line_y + y_off,
                    lc,
                    lt,
                    ly,
                ]
            else:
                top_line_row = []

            tail_rows = [[999, 100, 50]]

            if action == "append":
                shape_list = append_only_rows
            else:
                shape_list = header_rows + name_rows + frame_rows + bolt_rows
                if top_line_row:
                    shape_list.append(top_line_row)
                shape_list += tail_rows

            lines = [" ".join(str(e) for e in row) for row in shape_list]
            new_result = "\n".join(lines)

            result_str = (
                (prev_result + "\n" + new_result).strip()
                if action == "append"
                else new_result
            )
            defaults = get_defaults()

    return render_template(
        "gusset_web_plate/index.html",
        filenames=filenames,
        steel_sizes=list(steel_r_mapping.keys()),
        defaults=defaults,
        result_str=result_str,
        error_msg=error_msg,
    )
