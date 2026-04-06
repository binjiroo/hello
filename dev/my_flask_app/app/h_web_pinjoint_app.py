from flask import Blueprint, render_template, request, session
from .config import (
    h_steel_r_mapping,
    H_STEEL_SIZES_BY_GROUP,
)

h_web_pinjoint_bp = Blueprint(
    "h_web_pinjoint", __name__, template_folder="templates/h_web_pinjoint"
)


def get_steel_sizes_for_width_group(width_group: str) -> list[str]:
    if width_group in H_STEEL_SIZES_BY_GROUP:
        lst = H_STEEL_SIZES_BY_GROUP[width_group]
        if lst:
            return lst

    narrow = H_STEEL_SIZES_BY_GROUP.get("narrow", [])
    if narrow:
        return narrow

    return list(h_steel_r_mapping.keys())


def get_defaults() -> dict:
    all_narrow = H_STEEL_SIZES_BY_GROUP.get("narrow") or list(h_steel_r_mapping.keys())
    default_steel = session.get("steel_size", all_narrow[0])

    from .config import H_STEEL_MASTER

    master_info = H_STEEL_MASTER.get(default_steel, {})
    default_width_group = master_info.get("width_group", "narrow")

    flange_width_pattern = session.get("flange_width_pattern", default_width_group)

    return {
        "steel_size": session.get("steel_size", default_steel),
        "hole_column_x": session.get("hole_column_x", "1"),
        "hole_row_y": session.get("hole_row_y", "1"),
        "hole_pitch_x": session.get("hole_pitch_x", "60"),
        "hole_pitch_y": str(session.get("hole_pitch_y", "60")),
        "hole_endpitch_x": session.get("hole_endpitch_x", "40"),
        "clearance": session.get("clearance", "10"),
        "hole_size": session.get("hole_size", "18"),
        "s1": session.get("s1", "01"),
        "s2": session.get("s2", "01"),
        "off_choice": session.get("off_choice", "5"),
        "lc": session.get("lc", "1"),
        "lt": session.get("lt", "1"),
        "ly": session.get("ly", "0"),
        "members": session.get("members", "1"),
        "separator": session.get("separator", "999"),
        "scale": session.get("scale", "1"),
        "actual_size": session.get("actual_size", "800"),
        "command": session.get("command", "1"),
        "flange_width_pattern": flange_width_pattern,
    }


@h_web_pinjoint_bp.route("/", methods=["GET", "POST"])
def index():
    filenames = [
        "JW_OPT1.DAT",
        "JW_OPT1B.DAT",
        "JW_OPT1C.DAT",
        "JW_OPT1D.DAT",
        "JW_OPT1E.DAT",
        "JW_OPT1F.DAT",
        "JW_OPT1G.DAT",
        "JW_OPT1H.DAT",
        "JW_OPT1I.DAT",
        "JW_OPT1J.DAT",
        "JW_OPT1K.DAT",
        "JW_OPT1L.DAT",
        "JW_OPT1M.DAT",
        "JW_OPT1N.DAT",
        "JW_OPT1O.DAT",
        "JW_OPT1P.DAT",
        "JW_OPT1Q.DAT",
        "JW_OPT1R.DAT",
        "JW_OPT1S.DAT",
        "JW_OPT1T.DAT",
        "JW_OPT1U.DAT",
        "JW_OPT1V.DAT",
        "JW_OPT1W.DAT",
        "JW_OPT1X.DAT",
        "JW_OPT1Y.DAT",
        "JW_OPT1Z.DAT",
    ]

    defaults = get_defaults()
    flange_width_pattern = request.form.get(
        "flange_width_pattern", session.get("flange_width_pattern", "narrow")
    )

    steel_sizes = get_steel_sizes_for_width_group(flange_width_pattern)

    current_steel = session.get("steel_size", defaults["steel_size"])
    if current_steel not in steel_sizes and steel_sizes:
        current_steel = steel_sizes[0]
        session["steel_size"] = current_steel
        defaults["steel_size"] = current_steel

    raw = request.form.get("hole_pitch_y", session.get("hole_pitch_y", defaults["hole_pitch_y"]))
    try:
        hole_pitch_y = float(raw)
    except (TypeError, ValueError):
        hole_pitch_y = 60.0

    session["flange_width_pattern"] = flange_width_pattern
    session["hole_pitch_y"] = hole_pitch_y

    result_str = ""
    error_msg = ""

    if request.method == "POST":
        defaults = get_defaults()
        action = request.form.get("action", "new")
        prev_result = request.form.get("prev_result", "")

        if action == "clear":
            session.clear()
            defaults = get_defaults()
            return render_template(
                "h_web_pinjoint/index.html",
                filenames=filenames,
                steel_sizes=steel_sizes,
                h_steel_sizes_by_group=H_STEEL_SIZES_BY_GROUP,
                defaults=defaults,
                result_str=result_str,
                error_msg=error_msg,
            )

        for key in defaults:
            session[key] = request.form.get(key, defaults[key])

        steel_size = session["steel_size"]
        hole_column_x = int(session["hole_column_x"])
        hole_row_y = int(session["hole_row_y"])
        hole_pitch_x = float(session["hole_pitch_x"])
        hole_endpitch_x = float(session["hole_endpitch_x"])
        clearance = float(session["clearance"])
        hole_size = float(session["hole_size"])
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

        steel_size_vals = steel_size.split("x")
        steel_size_filtered = [v for i, v in enumerate(steel_size_vals) if i not in (1, 2)]
        h_flg, h_t1 = map(float, steel_size_filtered)

        offs = {
            1: (0, -h_flg / 2),
            2: (0, 0),
            3: (0, h_flg / 2),
        }
        choice = int(off_choice) if off_choice.isdigit() else 5
        x_offset, y_offset = offs.get(choice, (0, 0))

        w1 = h_flg / 2
        w3 = 0.0
        w4 = clearance
        h1 = h_flg / 2
        h2 = h_flg / 2 - h_t1

        hole_list = []
        hole_list2 = []

        for i in range(hole_row_y):
            y = (i - (hole_row_y - 1) / 2) * hole_pitch_y
            for j in range(hole_column_x):
                x1 = w4 + (hole_endpitch_x + j * hole_pitch_x)
                x2 = w3 - (hole_endpitch_x + j * hole_pitch_x)
                zx1 = x1 + hole_size / 2
                zx2 = x1 - hole_size / 2
                zy1 = y + hole_size / 2
                zy2 = y - hole_size / 2
                hole_list.extend(
                    [
                        [1, 1, zx1, y + y_offset, zx2, y + y_offset, lc, lt, ly],
                        [1, 1, x1, zy1 + y_offset, x1, zy2 + y_offset, lc, lt, ly],
                        [1, 1, x1, y + y_offset, zx1, y + y_offset, lc, lt, ly, "E", 360, 0],
                    ]
                )

        for i in range(hole_row_y):
            y = (i - (hole_row_y - 1) / 2) * hole_pitch_y
            for j in range(hole_column_x):
                x1 = w4 + (hole_endpitch_x + j * hole_pitch_x)
                x2 = w3 - (hole_endpitch_x + j * hole_pitch_x)
                zx1 = x1 + hole_size / 2
                zx2 = x1 - hole_size / 2
                zy1 = y + hole_size / 2
                zy2 = y - hole_size / 2
                hole_list2.extend(
                    [
                        [2, 2, -zx1, y + y_offset, -zx2, y + y_offset, lc, lt, ly],
                        [2, 2, -x1, zy1 + y_offset, -x1, zy2 + y_offset, lc, lt, ly],
                        [2, 2, -x1, y + y_offset, -zx1, y + y_offset, lc, lt, ly, "E", 360, 0],
                    ]
                )

        shape_list = []

        if action != "append" or not prev_result.strip():
            shape_list.extend([
                ["#H_PINJOINT"],
                [members],
                [999],
            ])

        shape_list.extend([
            [2, "H-" + steel_size],
            ["S", 100, 50],
            ["W", 0],
        ])

        shape_list.extend(hole_list)
        shape_list.extend(hole_list2)

        shape_list.extend(
            [
                [1, 1, w4, -h1 + y_offset, w4, h1 + y_offset, lc, 1, ly],
                [2, 2, -w4, -h1 + y_offset, -w4, h1 + y_offset, lc, 1, ly],
                [1, 2, w4, h1 + y_offset, -w4, h1 + y_offset, lc, 1, ly],
                [1, 2, w4, -h1 + y_offset, -w4, -h1 + y_offset, lc, 1, ly],
                [1, 2, w4, h2 + y_offset, -w4, h2 + y_offset, lc, 1, ly],
                [1, 2, w4, -h2 + y_offset, -w4, -h2 + y_offset, lc, 1, ly],
            ]
        )

        shape_list.append([999, 100, 50])

        lines = [" ".join(str(e) for e in row) for row in shape_list]
        new_result = "\n".join(lines)

        result_str = (
            (prev_result + "\n" + new_result).strip() if action == "append" else new_result
        )

        defaults = get_defaults()

        return render_template(
            "h_web_pinjoint/index.html",
            filenames=filenames,
            steel_sizes=steel_sizes,
            h_steel_sizes_by_group=H_STEEL_SIZES_BY_GROUP,
            defaults=defaults,
            result_str=result_str,
            error_msg=error_msg,
        )

    return render_template(
        "h_web_pinjoint/index.html",
        filenames=filenames,
        steel_sizes=steel_sizes,
        h_steel_sizes_by_group=H_STEEL_SIZES_BY_GROUP,
        defaults=defaults,
        result_str=result_str,
        error_msg=error_msg,
    )
