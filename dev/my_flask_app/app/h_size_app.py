# app/h_size_app.py
from flask import Blueprint, render_template, request, session

from .config import H_STEEL_SIZES_BY_GROUP, h_steel_r_mapping as steel_r_mapping

CATEGORY_OPTIONS = [
    ("light", "軽量H"),
    ("narrow", "細幅H"),
    ("middle", "中幅H"),
    ("wide", "広幅H"),
]

LEADER_FOLLOW_ROWS = [
    ["10", "10", "-1", "0", "1", "0"],
    ["20", "20", "0", "-1", "0", "1"],
]

h_size_bp = Blueprint("h_size", __name__, template_folder="templates/h_size")


def get_sizes_for_category(category):
    return H_STEEL_SIZES_BY_GROUP.get(category, [])


def normalize_category(category):
    return category if category in H_STEEL_SIZES_BY_GROUP else "light"


def normalize_steel_name(category, steel_name):
    sizes = get_sizes_for_category(category)
    if steel_name in sizes:
        return steel_name
    return sizes[0] if sizes else ""


def build_dat_line(row):
    return " ".join(str(item) for item in row)


def is_checked(value):
    return str(value).strip().lower() in {"1", "on", "true", "yes"}


def insert_leader_follow_rows(drawing_rows, enabled):
    if not enabled:
        return drawing_rows

    leader_follow_lines = [build_dat_line(row) for row in LEADER_FOLLOW_ROWS]
    drawing_lines = [build_dat_line(row) for row in drawing_rows]
    if drawing_lines[: len(leader_follow_lines)] == leader_follow_lines:
        return drawing_rows
    if all(line in drawing_lines for line in leader_follow_lines):
        return drawing_rows
    return LEADER_FOLLOW_ROWS + drawing_rows


def get_defaults():
    steel_category = normalize_category(session.get("steel_category", "light"))
    steel_name = normalize_steel_name(steel_category, session.get("steel_name", ""))
    return {
        "steel_category": steel_category,
        "steel_name": steel_name,
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
        "leader_follow": session.get("leader_follow", ""),
    }


@h_size_bp.route("/", methods=("GET", "POST"))
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
    selected_category = normalize_category(
        request.args.get("steel_category", defaults["steel_category"])
    )
    session["steel_category"] = selected_category
    defaults["steel_category"] = selected_category
    defaults["steel_name"] = normalize_steel_name(selected_category, defaults["steel_name"])

    steel_sizes = get_sizes_for_category(selected_category)
    result_str = ""
    error_message = ""

    if request.method == "POST":
        action = request.form.get("action", "new")
        selected_category = normalize_category(
            request.form.get("steel_category", defaults["steel_category"])
        )

        if action == "clear":
            session.clear()
            defaults = get_defaults()
            return render_template(
                "h_size/index.html",
                filenames=filenames,
                steel_sizes=get_sizes_for_category(defaults["steel_category"]),
                category_options=CATEGORY_OPTIONS,
                defaults=defaults,
                result_str="",
                error_message="",
            )

        for key in defaults.keys():
            session[key] = request.form.get(key, defaults[key])
        session["steel_category"] = selected_category
        session["steel_name"] = normalize_steel_name(selected_category, session["steel_name"])
        session["leader_follow"] = "1" if is_checked(request.form.get("leader_follow")) else ""

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
        leader_follow = is_checked(session["leader_follow"])
        prev_result = request.form.get("prev_result", "")

        if not steel_name:
            error_message = "選択したカテゴリにH型鋼サイズがありません。"
            defaults = get_defaults()
            return render_template(
                "h_size/index.html",
                filenames=filenames,
                defaults=defaults,
                result_str=result_str,
                error_message=error_message,
                steel_sizes=get_sizes_for_category(defaults["steel_category"]),
                category_options=CATEGORY_OPTIONS,
            )

        r = steel_r_mapping.get(steel_name, 0)
        a, b, c, d = map(float, steel_name.split("x"))

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
        w2 = c / 2 + r
        w3 = c / 2
        h1 = a / 2
        h2 = a / 2 - d
        h3 = a / 2 - (d + r)

        header_rows = [
            ["#H型鋼断面"],
            [members],
            [separator, scale],
        ]
        section_header_rows = [
            [command, "H-" + steel_name],
            [actual_size, scale],
        ]
        drawing_rows = [
            [s1, s2, 0 + x_off, h1 + y_off, 0 + x_off, -h1 + y_off, lc, lt, ly],
            [s1, s2, -w1 + x_off, 0 + y_off, w1 + x_off, 0 + y_off, lc, lt, ly],
            [s1, s2, -w1 + x_off, h1 + y_off, w1 + x_off, h1 + y_off, lc, lt, ly],
            [s1, s2, -w1 + x_off, -h1 + y_off, w1 + x_off, -h1 + y_off, lc, lt, ly],
            [s1, s2, -w1 + x_off, h2 + y_off, -w2 + x_off, h2 + y_off, lc, lt, ly],
            [s1, s2, w1 + x_off, h2 + y_off, w2 + x_off, h2 + y_off, lc, lt, ly],
            [s1, s2, -w1 + x_off, -h2 + y_off, -w2 + x_off, -h2 + y_off, lc, lt, ly],
            [s1, s2, w1 + x_off, -h2 + y_off, w2 + x_off, -h2 + y_off, lc, lt, ly],
            [s1, s2, -w3 + x_off, h3 + y_off, -w3 + x_off, -h3 + y_off, lc, lt, ly],
            [s1, s2, w3 + x_off, h3 + y_off, w3 + x_off, -h3 + y_off, lc, lt, ly],
            [s1, s2, -w1 + x_off, h1 + y_off, -w1 + x_off, h2 + y_off, lc, lt, ly],
            [s1, s2, w1 + x_off, h1 + y_off, w1 + x_off, h2 + y_off, lc, lt, ly],
            [s1, s2, -w1 + x_off, -h1 + y_off, -w1 + x_off, -h2 + y_off, lc, lt, ly],
            [s1, s2, w1 + x_off, -h1 + y_off, w1 + x_off, -h2 + y_off, lc, lt, ly],
            [s1, s2, -w2 + x_off, h3 + y_off, 0, 90, lc, lt, ly, "E", r],
            [s1, s2, w2 + x_off, h3 + y_off, 90, 180, lc, lt, ly, "E", r],
            [s1, s2, -w2 + x_off, -h3 + y_off, 270, 0, lc, lt, ly, "E", r],
            [s1, s2, w2 + x_off, -h3 + y_off, 180, 270, lc, lt, ly, "E", r],
        ]
        footer_rows = [
            [separator, scale],
        ]

        drawing_rows = insert_leader_follow_rows(drawing_rows, leader_follow)
        list_for_output = (
            section_header_rows + drawing_rows + footer_rows
            if action == "append"
            else header_rows + section_header_rows + drawing_rows + footer_rows
        )
        new_lines = [build_dat_line(row) for row in list_for_output]
        new_result = "\n".join(new_lines)

        result_str = (
            (prev_result + "\n" + new_result).strip()
            if action == "append"
            else new_result
        )

    defaults = get_defaults()

    return render_template(
        "h_size/index.html",
        filenames=filenames,
        defaults=defaults,
        result_str=result_str,
        error_message=error_message,
        steel_sizes=get_sizes_for_category(defaults["steel_category"]),
        category_options=CATEGORY_OPTIONS,
    )
