from flask import Blueprint, render_template, request, session

from app.data.steel_mappings import H_STEEL_SIZES_BY_GROUP, h_steel_r_mapping as steel_r_mapping

CATEGORY_OPTIONS = [
    ("light", "霆ｽ驥秋"),
    ("narrow", "邏ｰ蟷・"),
    ("middle", "荳ｭ蟷・"),
    ("wide", "蠎・ｹ・"),
]

bp = Blueprint("h_size", __name__, url_prefix="/cad/h_size", template_folder="templates")


def get_sizes_for_category(category):
    return H_STEEL_SIZES_BY_GROUP.get(category, [])


def normalize_category(category):
    return category if category in H_STEEL_SIZES_BY_GROUP else "light"


def normalize_steel_name(category, steel_name):
    sizes = get_sizes_for_category(category)
    if steel_name in sizes:
        return steel_name
    return sizes[0] if sizes else ""


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
    }


@bp.route("/", methods=("GET", "POST"))
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

        if not steel_name:
            error_message = "驕ｸ謚槭＠縺溘き繝・ざ繝ｪ縺ｫH蝙矩蕎繧ｵ繧､繧ｺ縺後≠繧翫∪縺帙ｓ縲・"
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

        shape_list = [
            ["#H蠖｢驪ｼ譁ｭ髱｢蝗ｳ蠖｢"],
            [members],
            [separator, scale],
            [command, "H-" + steel_name],
            [actual_size, scale],
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
        "h_size/index.html",
        filenames=filenames,
        defaults=defaults,
        result_str=result_str,
        error_message=error_message,
        steel_sizes=get_sizes_for_category(defaults["steel_category"]),
        category_options=CATEGORY_OPTIONS,
    )
