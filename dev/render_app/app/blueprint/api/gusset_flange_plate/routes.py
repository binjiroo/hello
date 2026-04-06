from flask import jsonify, request

from . import bp
from app.data.steel_mappings import gusset_flange_plate_mapping as steel_r_mapping

DEFAULT_VALUES = {
    "h_type": "",
    "sub_h_type": "",
    "hole_column": "1",
    "hole_pitch": "0",
    "gusset_name": "",
    "t": "6",
    "s1": "01",
    "s2": "01",
    "off_choice": "5",
    "lc": "1",
    "lt": "1",
    "ly": "0",
    "members": "5",
    "separator": "999",
    "scale": "1",
    "actual_size": "800",
    "command": "1",
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


def _normalize(values):
    state = {key: str(values.get(key, default)) for key, default in DEFAULT_VALUES.items()}
    state["leader_follow"] = "1" if _is_checked(values.get("leader_follow")) else ""
    return state


def build_gusset_flange_plate_result(values, action="new", previous_result=""):
    if action == "clear":
        return "", ""

    state = _normalize(values)

    try:
        h_type = state["h_type"]
        sub_h_type = state["sub_h_type"]
        if h_type not in steel_r_mapping or sub_h_type not in steel_r_mapping:
            raise ValueError("主材または副材のH形鋼サイズを選択してください。")

        hole_column = int(state["hole_column"])
        hole_pitch = int(state["hole_pitch"])
        gusset_name = state["gusset_name"].strip()
        if not gusset_name:
            raise ValueError("ガセット名を入力してください。")

        t = float(state["t"])
        s1 = state["s1"]
        s2 = state["s2"]
        lc = state["lc"]
        lt = state["lt"]
        ly = state["ly"]
        members = state["members"]
        separator = state["separator"]
        scale = state["scale"]
        actual_size = state["actual_size"]
        command = state["command"]
        leader_follow = _is_checked(state["leader_follow"])

        vals = h_type.split("x") + sub_h_type.split("x")
        filtered = [value for index, value in enumerate(vals) if index not in (0, 3, 4, 5, 7)]
        a, b, c = map(float, filtered)
    except ValueError as exc:
        return previous_result, f"入力エラー: {exc}"

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
    choice = int(state["off_choice"]) if state["off_choice"].isdigit() else 5
    x_off, y_off = offsets.get(choice, (0, 0))

    w1, w2 = c / 2, c / 2 + t
    w3, w4 = -c / 2 - 20, c / 2 + t + 20
    h1, h2 = b / 2, a / 2
    h3, h4 = a / 2 + 90, a / 2 + 50
    extension = (hole_column - 1) * hole_pitch
    h3_end = h3 + extension

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

    for index in range(hole_column):
        y_bolt = h4 + index * hole_pitch
        shape_list.append(
            [s1, s2, w3 + x_off, y_bolt + y_off, w4 + x_off, y_bolt + y_off, lc, lt, ly]
        )

    shape_list.append([s1, s2, w1 + x_off, h3_end + y_off, w2 + x_off, h3_end + y_off, lc, lt, ly])
    shape_list.extend(
        [
            [s1, s2, w1 + x_off, -h1 + y_off, w2 + x_off, -h1 + y_off, lc, lt, ly],
            [s1, s2, w1 + x_off, -h2 + 10 + y_off, w2 + x_off, -h2 + 10 + y_off, lc, lt, ly],
            [s1, s2, w1 + x_off, -h1 + y_off, w1 + x_off, -h2 + 10 + y_off, lc, lt, ly],
            [s1, s2, w2 + x_off, -h1 + y_off, w2 + x_off, -h2 + 10 + y_off, lc, lt, ly],
            [999, 100, 50],
        ]
    )

    drawing_rows = _insert_leader_follow_rows(shape_list[5:-1], leader_follow)
    shape_list = shape_list[:5] + drawing_rows + shape_list[-1:]

    new_result = "\n".join(_build_dat_line(row) for row in shape_list)
    result = f"{previous_result}\n{new_result}".strip() if action == "append" else new_result
    return result, ""


@bp.route("/generate", methods=("POST",))
def generate():
    payload = request.get_json(silent=True) or request.form.to_dict()
    action = payload.get("action", "new")
    previous_result = payload.get("prev_result", "")
    result, error_msg = build_gusset_flange_plate_result(
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
