from flask import Blueprint, render_template, request, session
import math
from .config import (
    chs_steel_r_mapping as steel_r_mapping,
)  # 竊・縺薙ｌ縺ｧ螳夂ｾｩ貂医∩繝槭ャ繝斐Φ繧ｰ繧定ｪｭ縺ｿ霎ｼ繧

from .size_dat_utils import build_dat_line, insert_leader_follow_rows, is_checked
steel_sizes = list(steel_r_mapping.keys())

chs_size_bp = Blueprint("chs_size", __name__, template_folder="templates/chs_size")


# 繧ｻ繝・す繝ｧ繝ｳ縺九ｉ繝・ヵ繧ｩ繝ｫ繝亥､繧偵∪縺ｨ繧√※蜿悶▲縺ｦ縺上ｋ繝倥Ν繝代・
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
        "leader_follow": session.get("leader_follow", ""),
    }


@chs_size_bp.route("/", methods=["GET", "POST"])
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

        # 縲後け繝ｪ繧｢縲榊・逅・
        if action == "clear":
            session.clear()
            defaults = get_defaults()
            return render_template(
                "chs_size/index.html",
                filenames=filenames,
                steel_sizes=list(steel_r_mapping.keys()),
                defaults=defaults,
                result_str="",
                error_message="",
            )

        # 譁ｰ隕・or 霑ｽ蜉 險育ｮ・
        # 1) 繝輔か繝ｼ繝蛟､ 竊・繧ｻ繝・す繝ｧ繝ｳ
        for key in defaults.keys():
            session[key] = request.form.get(key, defaults[key])
        session["leader_follow"] = "1" if is_checked(request.form.get("leader_follow")) else ""

        # 繝輔か繝ｼ繝縺九ｉ蛟､繧貞叙蠕・
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

        # r 繧貞叙蠕・
        chs_name = steel_r_mapping.get(steel_name)
        # 蝙句錐縺九ｉ謨ｰ蛟､繝ｪ繧ｹ繝医ｒ逕滓・
        a, b = map(float, steel_name.split("x"))

        # 繧ｪ繝輔そ繝・ヨ縺ｮ蛟呵｣・
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

        # 蜷・ｨｮ蟇ｸ豕戊ｨ育ｮ・
        cx1 = a / 2
        cx2 = (a / 2) - b
        cy1 = a / 2
        cy2 = (a / 2) - b

        # shape_list 繧堤ｵ・∩遶九※
        shape_list = [
            ["#驪ｼ邂｡譁ｭ髱｢"],
            [members],
            [separator, scale],
            [command, chs_name + steel_name],
            [actual_size, scale],
            # 蝓ｺ貅也ｷ・
            [s1, s2, 0 + x_off, cy1 + y_off, 0 + x_off, -cy1 + y_off, lc, lt, ly],
            [s1, s2, -cx1 + x_off, 0 + y_off, cx1 + x_off, 0 + y_off, lc, lt, ly],
            # 蜊雁ｾ・欠螳・
            [s1, s2, 0 + x_off, 0 + y_off, 0, 360, lc, lt, ly, "E", cx1],
            [s1, s2, 0 + x_off, 0 + y_off, 0, 360, lc, lt, ly, "E", cx2],
            [separator, scale],
        ]
        drawing_rows = insert_leader_follow_rows(shape_list[5:-1], leader_follow)
        shape_list = shape_list[:5] + drawing_rows + shape_list[-1:]

        list_for_output = shape_list[3:] if action == "append" else shape_list
        new_lines = [build_dat_line(row) for row in list_for_output]
        new_result = "\n".join(new_lines)

        result_str = (
            (prev_result + "\n" + new_result).strip()
            if action == "append"
            else new_result
        )

    # 4) 險育ｮ怜ｾ後∝・蠎ｦ defaults 譖ｴ譁ｰ
    defaults = get_defaults()

    return render_template(
        "chs_size/index.html",
        filenames=filenames,
        defaults=defaults,
        result_str=result_str,
        error_message=error_message,
        steel_sizes=list(steel_r_mapping.keys()),
    )
