from flask import Flask, render_template, request, session
import math

app = Flask(__name__)
# セッション利用に必要なシークレットキーを設定
app.secret_key = 'your_secret_key'  # 実運用時はランダムな文字列を設定

# 各鋼材のサイズと対応する r 値の辞書
steel_r_mapping = {
    "75x40x5x7": (4, 8),
    "100x50x5x7.5": (4, 8),
    "125x65x6x8": (4, 8),
    "150x75x6.5x10": (5, 10),
    "150x75x9x12.5": (7.5, 15),
    "200x80x7.5x11": (6, 12),
    "200x90x8x13.5": (7, 14),
    "250x90x9x13": (7, 14),
    "250x90x11x14.5": (8.5, 17),
    "300x90x9x13": (7, 14),
    "300x90x10x15.5": (9.5, 19),
    "300x90x12x16": (9.5, 19),
    "380x100x10.5x16": (9, 18),
    "380x100x13x16.5": (9, 18),
    "380x100x13x20": (12, 24),
}

@app.route("/", methods=["GET", "POST"])
def index():
    result_str = ""
    error_message = ""
    steel_sizes = list(steel_r_mapping.keys())

    if request.method == "POST":
        prev_result = request.form.get("prev_result", "")
        # POST時: セッション保存
        session["steel_name"] = request.form.get("steel_name")
        session["s1"] = request.form.get("s1")
        session["s2"] = request.form.get("s2")
        session["offset_choice"] = request.form.get("offset_choice")
        session["lc"] = request.form.get("lc")
        session["lt"] = request.form.get("lt")
        session["ly"] = request.form.get("ly")
        session["members"] = request.form.get("members")
        session["separator"] = request.form.get("separator")
        session["scale"] = request.form.get("scale")
        session["command"] = request.form.get("command")

        action = request.form.get("action", "new")

        steel_name = request.form.get("steel_name")
        s1 = request.form.get("s1")
        s2 = request.form.get("s2")
        s1 = request.form.get("s1")
        s2 = request.form.get("s2")
        offset_choice = request.form.get("offset_choice")
        lc = request.form.get("lc")
        lt = request.form.get("lt")
        ly = request.form.get("ly")
        members = request.form.get("members")
        separator = request.form.get("separator")
        scale = request.form.get("scale")
        command = request.form.get("command")
        
        # 座標計算
        angle_deg = 95
        angle_rad = math.radians(angle_deg)
        x_coord = math.cos(angle_rad)
        y_coord = math.sin(angle_rad)
        y_tan = math.tan(math.radians(5))
        
        if steel_name not in steel_r_mapping:
            error_message = "指定されたサイズが存在しません。"
        else:
            r1, r2 = steel_r_mapping[steel_name]
            try:
                values_str = steel_name.split("x")
                values = [float(val) for val in values_str]
                a, b, c, d = values
            except Exception as e:
                error_message = f"数値変換エラー: {e}"
            
            # 中間変数の計算
            ff = ((b - c) / 2) - (r2 + (r2 * x_coord))
            gg = ((b - c) / 2) - (r1 + (r1 * x_coord))
            hh = ((a / 2) - d) - ff * y_tan
            ii = ((a / 2) - d) + gg * y_tan
            
            # オフセットの候補
            offsets = {
                1: (b / 2, -a / 2), 2: (0, -a / 2), 3: (-b / 2, -a / 2),
                4: (b / 2, 0),      5: (0, 0),      6: (-b / 2, 0),
                7: (b / 2, a / 2),  8: (0, a / 2),  9: (-b / 2, a / 2)
            }
            choice = int(offset_choice) if offset_choice.isdigit() else 5
            x_offset, y_offset = offsets.get(choice, (0, 0))
            
            # 各変数の計算
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
            
            # shape_list の作成（ここでは header なしで shape_list のリストのみ出力）
            shape_list = [
                ["#溝型鋼断面"],
                [members],
                [separator, scale],
                [command, "[-" + steel_name],
                [800, 1],
                # 基準線
                [s1, s2, 0 + x_offset, h1 + y_offset, 0 + x_offset, -h1 + y_offset, lc, lt, ly],
                [s1, s2, -w1 + x_offset, 0 + y_offset, w1 + x_offset, 0 + y_offset, lc, lt, ly],
                # 外フランジ上下
                [s1, s2, -w1 + x_offset, h1 + y_offset, w1 + x_offset, h1 + y_offset, lc, lt, ly],
                [s1, s2, -w1 + x_offset, -h1 + y_offset, w1 + x_offset, -h1 + y_offset, lc, lt, ly],
                # 内フランジ上下
                [s1, s2, -w3 + x_offset, h3 + y_offset, w4 + x_offset, h5 + y_offset, lc, lt, ly],
                [s1, s2, -w3 + x_offset, -h3 + y_offset, w4 + x_offset, -h5 + y_offset, lc, lt, ly],
                # ウェーブ
                [s1, s2, -w1 + x_offset, h1 + y_offset, -w1 + x_offset, -h1 + y_offset, lc, lt, ly],
                [s1, s2, -w2 + x_offset, h2 + y_offset, -w2 + x_offset, -h2 + y_offset, lc, lt, ly],
                # フランジエッジ
                [s1, s2, w1 + x_offset, h1 + y_offset, w1 + x_offset, h4 + y_offset, lc, lt, ly],
                [s1, s2, w1 + x_offset, -h1 + y_offset, w1 + x_offset, -h4 + y_offset, lc, lt, ly],
                # r 指定
                [s1, s2, -w5 + x_offset, h2 + y_offset, 95, 180, lc, lt, ly, "E", r2],
                [s1, s2, -w5 + x_offset, -h2 + y_offset, 180, 265, lc, lt, ly, "E", r2],
                [s1, s2, w6 + x_offset, h4 + y_offset, 275, 0, lc, lt, ly, "E", r1],
                [s1, s2, w6 + x_offset, -h4 + y_offset, 0, 85, lc, lt, ly, "E", r1],
                [separator, scale],
            ]

            list_for_output = shape_list[3:] if action == "append" else shape_list
            new_lines = [" ".join(str(item) for item in row) for row in list_for_output]
            new_result = "\n".join(new_lines)

            result_str = (prev_result + "\n" + new_result).strip() if action == "append" else new_result

        # 重要！POST送信処理の最後に再取得する
        default_values = {
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

    if action == "clear":
        session.clear()
        result_str = ""

        # クリアだけしてすぐ返す
        default_values = {
            "steel_name": "",
            "s1": "01",  # etc...
            # 他の defaults も一律デフォルトに
        }

        return render_template(
            "index.html",
            result_str=result_str,
            error_message=error_message,
            steel_sizes=steel_sizes,
            defaults=default_values
        )

    # GETのとき（初期表示または再読み込み時）
    default_values = {
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

    return render_template(
        "index.html",
        result_str=result_str,
        error_message=error_message,
        steel_sizes=steel_sizes,
        defaults=default_values
    )

if __name__ == "__main__":
    app.run(debug=True)
