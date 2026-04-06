import math

from flask import jsonify, request

from . import bp
from app.data.steel_mappings import h_steel_r_mapping as steel_r_mapping

DEFAULT_VALUES = {
    "steel_name": "",
    "sub_steel_name": "",
    "s1": "01",
    "s2": "01",
    "lc": "1",
    "lt": "1",
    "ly": "1",
    "b_set": "1",
    "y_set": "0",
    "offset_choice": "5",
    "t": "0",
    "hole_column_x": "1",
    "hole_row_y": "1",
    "hole_pitch": "0",
    "row_hole_pitch": "0",
    "end_hole_pitch": "0",
    "clearance": "0",
    "hole_size": "0",
    "mode": "1",
    "yset_limit": "0",
    "leader_follow": "",
}

STEEL_SIZES = list(steel_r_mapping.keys())
LEADER_FOLLOW_ROWS = [
    ["10", "10", "-1", "0", "1", "0"],
    ["20", "20", "0", "-1", "0", "1"],
]
FILENAMES = ["JW_OPT4.DAT"] + [f"JW_OPT4{suffix}.DAT" for suffix in "BCDEFGHIJKLMNOPQRSTUVWXYZ"]


def _build_dat_line(row):
    return " ".join(str(item) for item in row)


def _is_checked(value):
    return str(value).strip().lower() in {"1", "on", "true", "yes"}


def _insert_leader_follow_rows(drawing_rows, enabled):
    if not enabled:
        return drawing_rows

    leader_follow_lines = [_build_dat_line(row) for row in LEADER_FOLLOW_ROWS]
    drawing_lines = [_build_dat_line(row) for row in drawing_rows]
    if drawing_lines[: len(leader_follow_lines)] == leader_follow_lines:
        return drawing_rows
    if all(line in drawing_lines for line in leader_follow_lines):
        return drawing_rows
    return LEADER_FOLLOW_ROWS + drawing_rows


def _to_int(value, default=0):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError, AttributeError):
        return default


def _to_float(value, default=0.0):
    try:
        return float(str(value).strip())
    except (TypeError, ValueError, AttributeError):
        return default


def _get_int(mapping, key, default=0):
    return _to_int(mapping.get(key), default)


def _get_float(mapping, key, default=0.0):
    return _to_float(mapping.get(key), default)


def _fmt2(value):
    try:
        return f"{int(str(value).strip()):02d}"
    except Exception:
        return "00"


def _normalize(values):
    state = {key: str(values.get(key, default)) for key, default in DEFAULT_VALUES.items()}
    state["leader_follow"] = "1" if _is_checked(values.get("leader_follow")) else ""
    return state


def _build_mode1_templates(ctx):
    s1 = ctx["s1"]
    s2 = ctx["s2"]
    lc = ctx["lc"]
    lt = ctx["lt"]
    ly = ctx["ly"]
    w1_r = ctx["w1_r"]
    w2_r = ctx["w2_r"]
    w3_r = ctx["w3_r"]
    w5_r = ctx["w5_r"]
    w1_l = ctx["w1_l"]
    w2_l = ctx["w2_l"]
    w3_l = ctx["w3_l"]
    h1 = ctx["h1"]
    h2 = ctx["h2"]
    h3 = ctx["h3"]
    h4 = ctx["h4"]
    y_last = ctx["y_last"]
    y_first = ctx["y_first"]
    r = ctx["r"]

    return {
        "shape_list": [
            [_fmt2(s1), _fmt2(s2), w3_r, h1, w1_r, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h2, w1_r, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w1_r, h1, w1_r, y_last + 50, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w1_r, h2, w1_r, y_first - 50, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
        ],
        "shape_list2": [
            [_fmt2(s1), _fmt2(s2), w3_r, h1, w5_r, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h2, w1_r, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w5_r, h1, w5_r, y_last + 40, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w1_r, h2, w1_r, y_first - 50, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
        ],
        "shape_list3": [
            [_fmt2(s1), _fmt2(s2), w3_r, h1, w1_r, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h2, w5_r, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w1_r, h1, w1_r, y_last + 50, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w5_r, h2, w5_r, y_first - 40, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
        ],
        "shape_list4": [
            [_fmt2(s1), _fmt2(s2), w3_r, h1, w5_r, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h2, w5_r, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w5_r, h1, w5_r, y_last + 40, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w5_r, h2, w5_r, y_first - 40, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
        ],
    }


def _build_mode2_templates(ctx):
    s1 = ctx["s1"]
    s2 = ctx["s2"]
    lc = ctx["lc"]
    lt = ctx["lt"]
    ly = ctx["ly"]
    w1_l = ctx["w1_l"]
    w2_r = ctx["w2_r"]
    w2_l = ctx["w2_l"]
    w3_l = ctx["w3_l"]
    w3_r = ctx["w3_r"]
    w5_r = ctx["w5_r"]
    w6_r = ctx["w6_r"]
    h1 = ctx["h1"]
    h2 = ctx["h2"]
    h3 = ctx["h3"]
    h4 = ctx["h4"]
    y_last = ctx["y_last"]
    y_first = ctx["y_first"]
    r = ctx["r"]

    return {
        "shape_list": [
            [_fmt2(s1), _fmt2(s2), w3_r, h1, w6_r, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h2, w6_r, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
        ],
        "shape_list2": [
            [_fmt2(s1), _fmt2(s2), w3_r, h1, w5_r, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h2, w6_r, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w5_r, h1, w5_r, y_last + 40, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
        ],
        "shape_list3": [
            [_fmt2(s1), _fmt2(s2), w3_r, h1, w6_r, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h2, w5_r, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w5_r, h2, w5_r, y_first - 40, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
        ],
        "shape_list4": [
            [_fmt2(s1), _fmt2(s2), w3_r, h1, w5_r, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h2, w5_r, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w5_r, h1, w5_r, y_last + 40, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w5_r, h2, w5_r, y_first - 40, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
            [_fmt2(s1), _fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
            [_fmt2(s1), _fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
        ],
    }


def build_gusset_type_result(values, action="new", previous_result=""):
    if action == "clear":
        return "", ""

    state = _normalize(values)

    try:
        steel_name = state["steel_name"]
        sub_steel_name = state["sub_steel_name"]
        if steel_name not in steel_r_mapping or sub_steel_name not in steel_r_mapping:
            raise ValueError("主材または副材のH形鋼サイズを選択してください。")

        s1 = _get_int(state, "s1", 1)
        s2 = _get_int(state, "s2", 1)
        lc = _get_int(state, "lc", 1)
        lt = _get_int(state, "lt", 1)
        ly = state.get("ly", "1")

        b_set = _get_int(state, "b_set", 1)
        y_set = _get_int(state, "y_set", 0)
        offset_choice = _get_int(state, "offset_choice", 5)
        _t = _get_float(state, "t", 0.0)

        hole_column_x = _get_int(state, "hole_column_x", 0)
        hole_row_y = _get_int(state, "hole_row_y", 0)
        hole_pitch_x = _get_int(state, "hole_pitch", 0)
        hole_pitch_y = _get_int(state, "row_hole_pitch", 0)
        hole_endpitch_x = _get_int(state, "end_hole_pitch", 0)
        clearance = _get_int(state, "clearance", 0)
        hole_size = _get_int(state, "hole_size", 0)
        mode = _get_int(state, "mode", 1)
        leader_follow = _is_checked(state["leader_follow"])

        if mode not in (1, 2):
            mode = 1

        main_vals = [float(value) for value in steel_name.split("x")]
        sub_vals = [float(value) for value in sub_steel_name.split("x")]
        if len(main_vals) != 4 or len(sub_vals) != 4:
            raise ValueError("H形鋼サイズの形式が不正です。")

        a, b, c, d = main_vals
        e, _f, _g, _h = sub_vals
        r = steel_r_mapping[steel_name]

        raw_yset_limit = _get_int(state, "yset_limit", 0)
        yset_limit_abs = abs(raw_yset_limit)
        min_yset_limit = int(math.ceil(d))
        yset_limit = max(yset_limit_abs, min_yset_limit)

        offsets = [
            (b / 2, -a / 2),
            (0, -a / 2),
            (-b / 2, -a / 2),
            (b / 2, 0),
            (0, 0),
            (-b / 2, 0),
            (b / 2, a / 2),
            (0, a / 2),
            (-b / 2, a / 2),
        ]
        if not 1 <= offset_choice <= 9:
            offset_choice = 5
        x_offset, y_offset = offsets[offset_choice - 1]

        w1_r = (b / 2 - 10) + x_offset
        w2_r = (c / 2) + x_offset
        w3_r = (c / 2 + r) + x_offset
        w4_r = (b / 2 + 50) + x_offset
        w5_r = (b / 2 + 1) + x_offset
        w6_r = (b / 2) + x_offset
        w1_l = -(b / 2 - 10) + x_offset
        w2_l = -(c / 2) + x_offset
        w3_l = -(c / 2 + r) + x_offset
        w4_l = -(b / 2 + 50) + x_offset
        w5_l = -(b / 2 + 1) + x_offset
        w6_l = -(b / 2) + x_offset

        h1 = (a / 2 - d) + y_offset
        h2 = -(a / 2 - (d + 2)) + y_offset
        h3 = (a / 2 - (d + r)) + y_offset
        h4 = -(a / 2 - (d + r + 2)) + y_offset
        h5 = (a / 2) + y_set + y_offset
        h6 = (a / 2) - e + y_set + y_offset
        h7 = ((a - e) / 2) + (e / 2) + y_set
        h8 = (a - e) - (d + 2)
        h9 = a / 2 - (d + 2)

        x_first = (b / 2) + hole_endpitch_x + clearance + x_offset
        x_last = (b / 2) + hole_endpitch_x + clearance + (hole_column_x - 1) * hole_pitch_x + x_offset
        y_first = (((0 - (hole_row_y - 1) / 2) * hole_pitch_y) + (a / 2 - e / 2)) + y_offset + y_set
        y_last = ((((hole_row_y - 1) - (hole_row_y - 1) / 2) * hole_pitch_y) + (a / 2 - e / 2)) + y_offset + y_set

        top_margin = 40
        bottom_margin = 40
        top_clear = h1 - (y_last + top_margin)
        bot_clear = (y_first - bottom_margin) - h2

        hit_top = top_clear <= 0
        hit_bottom = bot_clear <= 0
        if hit_top and hit_bottom:
            final_shape_type = "shape_list4"
        elif hit_top and not hit_bottom:
            final_shape_type = "shape_list2"
        elif (not hit_top) and hit_bottom:
            final_shape_type = "shape_list3"
        else:
            final_shape_type = "shape_list"

        hole_list = []
        for row_index in range(hole_row_y):
            y = (((row_index - (hole_row_y - 1) / 2) * hole_pitch_y) + (a / 2 - e / 2)) + y_offset + y_set
            for column_index in range(hole_column_x):
                x = ((b / 2) + hole_endpitch_x + clearance + column_index * hole_pitch_x) + x_offset
                zx1 = x + hole_size / 2
                zx2 = x - hole_size / 2
                zy1 = y + hole_size / 2
                zy2 = y - hole_size / 2
                ep = hole_size / 2
                hole_list.append([_fmt2(s1), _fmt2(s2), zx1, y, zx2, y, lc, lt, ly])
                hole_list.append([_fmt2(s1), _fmt2(s2), x, zy1, x, zy2, lc, lt, ly])
                hole_list.append([_fmt2(s1), _fmt2(s2), x, y, 0, 360, lc, lt, ly, "E", ep, 0])

        def create_shape_list(template, holes, new_lines):
            shape_list = [row[:] for row in template]
            shape_list.extend(holes)
            shape_list.extend(new_lines)
            shape_list.append([999, 100, 50])
            return shape_list

        template_context = {
            "s1": s1,
            "s2": s2,
            "lc": lc,
            "lt": lt,
            "ly": ly,
            "w1_r": w1_r,
            "w2_r": w2_r,
            "w3_r": w3_r,
            "w5_r": w5_r,
            "w6_r": w6_r,
            "w1_l": w1_l,
            "w2_l": w2_l,
            "w3_l": w3_l,
            "h1": h1,
            "h2": h2,
            "h3": h3,
            "h4": h4,
            "y_last": y_last,
            "y_first": y_first,
            "top_margin": top_margin,
            "bottom_margin": bottom_margin,
            "r": r,
        }
        mode_templates = _build_mode1_templates(template_context) if mode == 1 else _build_mode2_templates(template_context)
        selected_tpl = mode_templates[final_shape_type]

        new_lines = []
        r_fillet = 10.0

        if mode == 1:
            allow_top_fillet = final_shape_type in ["shape_list", "shape_list3"] and top_clear >= r_fillet
            allow_bottom_fillet = final_shape_type in ["shape_list", "shape_list2"] and bot_clear >= r_fillet

            if top_clear > 0:
                start_x_top = w6_r if allow_top_fillet else w1_r
                top_horizontal_line = [_fmt2(s1), _fmt2(s2), start_x_top, y_last + top_margin, x_last + 25, y_last + top_margin, lc, lt, ly]
            else:
                top_horizontal_line = [_fmt2(s1), _fmt2(s2), w5_r, y_last + top_margin, x_last + 25, y_last + top_margin, lc, lt, ly]
            new_lines.append(top_horizontal_line)

            if bot_clear > 0:
                start_x_bottom = w6_r if allow_bottom_fillet else w1_r
                bottom_horizontal_line = [_fmt2(s1), _fmt2(s2), start_x_bottom, y_first - bottom_margin, x_last + 40, y_first - bottom_margin, lc, lt, ly]
            else:
                bottom_horizontal_line = [_fmt2(s1), _fmt2(s2), w5_r, y_first - bottom_margin, x_last + 40, y_first - bottom_margin, lc, lt, ly]
            new_lines.append(bottom_horizontal_line)

            right_vertical_line = [_fmt2(s1), _fmt2(s2), x_last + 40, y_first - bottom_margin, x_last + 40, y_last + 25, lc, lt, ly]
            new_lines.append(right_vertical_line)

            cut_line = [_fmt2(s1), _fmt2(s2), x_last + 25, y_last + top_margin, x_last + 40, y_last + 25, lc, lt, ly]
            new_lines.append(cut_line)

            if allow_top_fillet:
                new_lines.append([_fmt2(s1), _fmt2(s2), w6_r, y_last + top_margin + r_fillet, 180, 270, lc, lt, ly, "E", r_fillet, 0])
            if allow_bottom_fillet:
                new_lines.append([_fmt2(s1), _fmt2(s2), w6_r, y_first - bottom_margin - r_fillet, 90, 180, lc, lt, ly, "E", r_fillet, 0])
        else:
            top_gap = abs(h5 - h1)
            bottom_gap = abs(h6 - h2)
            top_tolerant = top_clear > 0 and top_gap <= yset_limit
            bottom_tolerant = bot_clear > 0 and bottom_gap <= yset_limit
            bottom_tolerant_ext = bot_clear > 0 and bottom_gap <= (yset_limit + d)

            if top_clear > 0:
                if top_tolerant:
                    corner_x = w6_r
                    corner_y = y_last + top_margin
                    arc_cx = corner_x + r_fillet
                    arc_cy = corner_y + r_fillet
                    new_lines.append([_fmt2(s1), _fmt2(s2), corner_x, h1, corner_x, arc_cy, lc, lt, ly])
                    new_lines.append([_fmt2(s1), _fmt2(s2), arc_cx, corner_y, x_last + 25, corner_y, lc, lt, ly])
                    new_lines.append([_fmt2(s1), _fmt2(s2), arc_cx, arc_cy, 180, 270, lc, lt, ly, "E", r_fillet, 0])
                    new_lines.append([_fmt2(s1), _fmt2(s2), x_last + 25, corner_y, x_last + 40, corner_y - 15, lc, lt, ly])
                else:
                    new_lines.append([_fmt2(s1), _fmt2(s2), w6_r, h1, x_last + 40, h5, lc, lt, ly])
            else:
                new_lines.append([_fmt2(s1), _fmt2(s2), w5_r, y_last + top_margin, x_last + 25, y_last + top_margin, lc, lt, ly])
                new_lines.append([_fmt2(s1), _fmt2(s2), x_last + 25, y_last + top_margin, x_last + 40, y_last + 25, lc, lt, ly])

            if bot_clear > 0:
                if bottom_tolerant_ext:
                    corner_bx = w6_r
                    corner_by = y_first - bottom_margin
                    arc_bcx = corner_bx + r_fillet
                    arc_bcy = corner_by - r_fillet
                    new_lines.append([_fmt2(s1), _fmt2(s2), corner_bx, h2, corner_bx, arc_bcy, lc, lt, ly])
                    new_lines.append([_fmt2(s1), _fmt2(s2), arc_bcx, corner_by, x_last + 40, corner_by, lc, lt, ly])
                    new_lines.append([_fmt2(s1), _fmt2(s2), arc_bcx, arc_bcy, 90, 180, lc, lt, ly, "E", r_fillet, 0])
                else:
                    new_lines.append([_fmt2(s1), _fmt2(s2), w6_r, h2, x_last + 40, h6, lc, lt, ly])
            else:
                new_lines.append([_fmt2(s1), _fmt2(s2), w5_r, y_first - bottom_margin, x_last + 40, y_first - bottom_margin, lc, lt, ly])

            y_top = y_last + 25 if top_tolerant or top_clear <= 0 else h5
            y_bottom = y_first - bottom_margin if bottom_tolerant or bot_clear <= 0 else h6
            new_lines.append([_fmt2(s1), _fmt2(s2), x_last + 40, y_top, x_last + 40, y_bottom, lc, lt, ly])

        include_header = action == "new"
        if include_header:
            base_template = [
                ["#ガセットプレート"],
                [b_set],
                [999, 100, 50],
                [2, "H", a, "-H", e, y_set, hole_column_x, "x", hole_row_y, hole_size, "ﾏ"],
                ["S", 100, 50],
                [800, 1],
            ]
        else:
            base_template = [
                [2, "H", a, "-H", e, y_set, hole_column_x, "x", hole_row_y, hole_size, "ﾏ"],
                ["S", 100, 50],
                [800, 1],
            ]

        if mode == 1:
            shape_core = [row[:] for row in mode_templates[final_shape_type]]
            allow_top_fillet = final_shape_type in ["shape_list", "shape_list3"] and top_clear >= r_fillet
            allow_bottom_fillet = final_shape_type in ["shape_list", "shape_list2"] and bot_clear >= r_fillet
            if final_shape_type in ["shape_list", "shape_list3"] and not allow_top_fillet:
                shape_core[2][5] = y_last + top_margin
            if final_shape_type in ["shape_list", "shape_list2"] and not allow_bottom_fillet:
                shape_core[3][5] = y_first - bottom_margin
            drawing_rows = shape_core
        else:
            drawing_rows = [row[:] for row in selected_tpl]

        drawing_rows = _insert_leader_follow_rows(drawing_rows, leader_follow)
        selected_template = base_template + drawing_rows
        final_shape_list = create_shape_list(selected_template, hole_list, new_lines)

        result_text = "\n".join(_build_dat_line(row) for row in final_shape_list)
        result = f"{previous_result}\n{result_text}".strip() if action == "append" else result_text
        return result, ""
    except ValueError as exc:
        return previous_result, f"入力エラー: {exc}"


@bp.route("/generate", methods=("POST",))
def generate():
    payload = request.get_json(silent=True) or request.form.to_dict()
    action = payload.get("action", "new")
    previous_result = payload.get("prev_result", "")
    result, error_msg = build_gusset_type_result(
        payload,
        action=action,
        previous_result=previous_result,
    )
    return jsonify(
        {
            "result": result,
            "error_msg": error_msg,
            "filenames": FILENAMES,
            "steel_sizes": STEEL_SIZES,
            "defaults": _normalize(payload),
        }
    )
