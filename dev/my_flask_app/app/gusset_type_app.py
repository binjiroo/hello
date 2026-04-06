# my_flask_app/app/gusset_type_app.py
import math
from flask import (
    Flask,
    Blueprint,
    render_template,
    request,
    session,
    current_app,
)
from .utils import to_int, to_float, get_int, get_float, fmt2
from .config import h_steel_r_mapping as steel_r_mapping
from .size_dat_utils import build_dat_line, insert_leader_follow_rows, is_checked


steel_sizes = list(steel_r_mapping.keys())

gusset_type_bp = Blueprint(
    "gusset_type", __name__, template_folder="templates/gusset_type"
)


def get_defaults():
    return {
        "steel_name": session.get("steel_name", ""),
        "sub_steel_name": session.get("sub_steel_name", ""),
        "s1": session.get("s1", "01"),
        "s2": session.get("s2", "01"),
        "lc": session.get("lc", "1"),
        "lt": session.get("lt", "1"),
        "ly": session.get("ly", "1"),
        "b_set": session.get("b_set", "1"),
        "y_set": session.get("y_set", "0"),
        "offset_choice": session.get("offset_choice", "5"),
        "t": session.get("t", "0"),
        # ▼ 新フィールド名
        "hole_column_x": session.get("hole_column_x", "1"),
        "hole_row_y": session.get("hole_row_y", "1"),
        "hole_pitch": session.get("hole_pitch", "0"),            # 列ピッチ
        "row_hole_pitch": session.get("row_hole_pitch", "0"),    # 行ピッチ
        "end_hole_pitch": session.get("end_hole_pitch", "0"),    # 終端ピッチ
        "clearance": session.get("clearance", "0"),              # クリアランス
        "hole_size": session.get("hole_size", "0"),
        "mode": session.get("mode", "1"),
        # ★ 追加: y_set を水平処理にする許容範囲（絶対値）
        # 0 → 高さ0のときだけ水平処理 / 50 → ±50 まで水平処理 など
        "yset_limit": session.get("yset_limit", "0"),
        "leader_follow": session.get("leader_follow", ""),
    }


@gusset_type_bp.route("/", methods=["GET", "POST"])
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
    steel_options = steel_sizes
    result_str = ""
    error_message = ""

    if request.method == "POST":
        # フォームの生データをログに出す
        current_app.logger.debug(
            f"[フォーム] mode={request.form.get('mode')}, action={request.form.get('action')}"
        )
        # セッションに格納した直後にもログ
        for key in request.form.keys():
            session[key] = request.form[key]
        session["leader_follow"] = "1" if is_checked(request.form.get("leader_follow")) else ""
        current_app.logger.debug(f"[セッション格納] mode={session.get('mode')}")
        action = request.form.get("action", "new")

        # --- クリア処理 ---
        if action == "clear":
            session.clear()
            defaults = get_defaults()
            return render_template(
                "gusset_type/index.html",
                filenames=filenames,
                steel_sizes=steel_options,
                defaults=defaults,
                result_str="",
                error_message="",
            )

        action = request.form.get("action", "new")
        include_header = action == "new"

        # ② セッションから取り出し（生の文字列の取得）
        prev_results = session.get("results", "")

        # --- セッションから再取得＆型変換 ---
        try:
            # 3) ★ここから正規化（型変換して計算用の統一名に詰める）
            steel_name = session.get("steel_name", "")
            sub_steel_name = session.get("sub_steel_name", "")

            # 必要ならここでサイズ存在チェック
            if (steel_name not in steel_r_mapping) or (sub_steel_name not in steel_r_mapping):
                raise ValueError("指定されたサイズが存在しません。")

            s1 = get_int(session, "s1", 1)
            s2 = get_int(session, "s2", 1)
            lc = get_int(session, "lc", 1)
            lt = get_int(session, "lt", 1)
            ly = session.get("ly", "1")  # ← ここは文字列のまま扱う（レイヤーなので）

            b_set = get_int(session, "b_set", 1)
            y_set = get_int(session, "y_set", 0)
            offset_choice = get_int(session, "offset_choice", 5)
            t = get_float(session, "t", 0.0)

            # フォーム名→計算用名（フォールバック不要ならそのまま）
            hole_column_x = get_int(session, "hole_column_x", 0)
            hole_row_y = get_int(session, "hole_row_y", 0)
            hole_pitch_x = get_int(session, "hole_pitch", 0)            # 列ピッチ
            hole_pitch_y = get_int(session, "row_hole_pitch", 0)        # 行ピッチ
            hole_endpitch_x = get_int(session, "end_hole_pitch", 0)
            clearance = get_int(session, "clearance", 0)
            hole_size = get_int(session, "hole_size", 0)
            mode = get_int(session, "mode", 1)
            leader_follow = is_checked(session["leader_follow"])

            # ここを追加（安全ガード）
            if mode not in (1, 2):
                mode = 1  # もしくは ValueError を投げてもOK

            # --- 値を変数に展開 ---
            main_vals = [float(v) for v in steel_name.split("x")]
            sub_vals = [float(v) for v in sub_steel_name.split("x")]

            a, b, c, d = main_vals
            e, f, g, h = sub_vals
            r = steel_r_mapping[steel_name]

            # ★ 修正: yset_limit の正規化（符号無視＋フランジ厚を下限にする）
            raw_yset_limit = get_int(session, "yset_limit", 0)
            yset_limit_abs = abs(raw_yset_limit)

            # 親梁フランジ厚 d を下限とする（物理的に意味のある最小値）
            min_yset_limit = int(math.ceil(d))  # 例: 12.7 → 13

            if yset_limit_abs < min_yset_limit:
                yset_limit = min_yset_limit
            else:
                yset_limit = yset_limit_abs

            current_app.logger.debug(
                f"[yset_limit正規化] raw={raw_yset_limit}, "
                f"abs={yset_limit_abs}, min={min_yset_limit}, used={yset_limit}"
            )

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

            if not (1 <= offset_choice <= 9):
                offset_choice = 5  # default

            x_offset, y_offset = offsets[offset_choice - 1]

            # --- ここで初めて計算開始 ---
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

            # 親梁フランジ/ガセット周りの高さ
            h1 = (a / 2 - d) + y_offset
            h2 = -(a / 2 - (d + 2)) + y_offset
            h3 = (a / 2 - (d + r)) + y_offset
            h4 = -(a / 2 - (d + r + 2)) + y_offset
            h5 = (a / 2) + y_set + y_offset
            h6 = (a / 2) - e + y_set + y_offset
            h7 = ((a - e) / 2) + (e / 2) + y_set
            h8 = (a - e) - (d + 2)
            h9 = a / 2 - (d + 2)

            # （ここから下の再キャストは元コードのまま残しています）
            lc = int(session["lc"])
            lt = int(session["lt"])
            ly = int(session["ly"])
            b_set = int(session["b_set"])
            y_set = int(session["y_set"])
            offset_choice = int(session["offset_choice"])
            t = float(session["t"])
            hole_column_x = int(session["hole_column_x"])
            hole_row_y = int(session["hole_row_y"])
            hole_size = int(session["hole_size"])
            mode = int(session["mode"])

            # 孔座標
            x_first = (b / 2) + hole_endpitch_x + clearance + x_offset
            x_last = (
                (b / 2) + hole_endpitch_x + clearance + (hole_column_x - 1) * hole_pitch_x
            ) + x_offset

            y_first = (
                (((0 - (hole_row_y - 1) / 2) * hole_pitch_y) + (a / 2 - e / 2))
                + y_offset
                + y_set
            )
            y_last = (
                (
                    (((hole_row_y - 1) - (hole_row_y - 1) / 2) * hole_pitch_y)
                    + (a / 2 - e / 2)
                )
                + y_offset
                + y_set
            )

            # ─────────────────────────────────────────
            # ★ 判定は mode 共通で一本化（mode=1 の基準に統一）
            # ─────────────────────────────────────────
            TOP_MARGIN = 40
            BOTTOM_MARGIN = 40

            # 安全線から subcut までのクリアランス
            top_clear = h1 - (y_last + TOP_MARGIN)          # >0: 上側に余裕あり
            bot_clear = (y_first - BOTTOM_MARGIN) - h2      # >0: 下側に余裕あり

            # ログ用差分
            current_app.logger.debug(
                f"[差分] 上面Δ={top_clear:.2f}, 下面Δ={bot_clear:.2f} "
                f"(h1={h1:.2f}, h2={h2:.2f}, y_last+40={y_last+TOP_MARGIN:.2f}, "
                f"y_first-40={y_first-BOTTOM_MARGIN:.2f})"
            )

            # 上下当たりフラグ（<=0 なら安全線に到達 or 超え）
            hit_top = top_clear <= 0
            hit_bottom = bot_clear <= 0

            # shape_list1〜4 の決定（単一ソース・オブ・トゥルース）
            if hit_top and hit_bottom:
                final_shape_type = "shape_list4"
            elif hit_top and not hit_bottom:
                final_shape_type = "shape_list2"
            elif (not hit_top) and hit_bottom:
                final_shape_type = "shape_list3"
            else:
                final_shape_type = "shape_list"

            current_app.logger.debug(
                f"[孔芯検証] b/2={b/2:.2f}, x_offset={x_offset:.2f}, "
                f"w6_r={w6_r:.2f}, x_first={x_first:.2f}, "
                f"from_flange={x_first - w6_r:.2f}  (期待= {hole_endpitch_x + clearance})"
            )
            current_app.logger.debug(
                f"[分岐結果] {final_shape_type} (hit_top={hit_top}, hit_bottom={hit_bottom})"
            )

            # 7. 動的に生成される孔の情報をリストへ追加
            hole_list = []
            for i in range(hole_row_y):
                # 中央基準の y 座標計算
                y = (
                    (((i - (hole_row_y - 1) / 2) * hole_pitch_y) + (a / 2 - e / 2))
                    + y_offset
                    + y_set
                )
                for j in range(hole_column_x):
                    # 各列の x 座標計算（親フランジ端点からのオフセットを加味）
                    x = ((b / 2) + hole_endpitch_x + clearance + j * hole_pitch_x) + x_offset
                    zx1 = x + hole_size / 2
                    zx2 = x - hole_size / 2
                    zy1 = y + hole_size / 2
                    zy2 = y - hole_size / 2
                    ep = hole_size / 2
                    # 元コードと同様、3行分のリストを追加
                    hole_list.append([fmt2(s1), fmt2(s2), zx1, y, zx2, y, lc, lt, ly])
                    hole_list.append([fmt2(s1), fmt2(s2), x, zy1, x, zy2, lc, lt, ly])
                    hole_list.append([fmt2(s1), fmt2(s2), x, y, 0, 360, lc, lt, ly, "E", ep, 0])

            # リスト生成用の共通関数
            def create_shape_list(template, hole_list, new_lines):
                shape_list = [row[:] for row in template]  # テンプレートをコピー
                shape_list.extend(hole_list)
                shape_list.extend(new_lines)
                shape_list.append([999, 100, 50])
                return shape_list

            # modeとshapeごとの設定テンプレートを定義（各shapeで異なる要素のみ変更）
            mode_templates = {
                1: {
                    "shape_list": [
                        [fmt2(s1), fmt2(s2), w3_r, h1, w1_r, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h2, w1_r, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w1_r, h1, w1_r, y_last + 50, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w1_r, h2, w1_r, y_first - 50, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
                    ],
                    "shape_list2": [
                        [fmt2(s1), fmt2(s2), w3_r, h1, w5_r, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h2, w1_r, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w5_r, h1, w5_r, y_last + 40, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w1_r, h2, w1_r, y_first - 50, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
                    ],
                    "shape_list3": [
                        [fmt2(s1), fmt2(s2), w3_r, h1, w1_r, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h2, w5_r, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w1_r, h1, w1_r, y_last + 50, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w5_r, h2, w5_r, y_first - 40, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
                    ],
                    "shape_list4": [
                        [fmt2(s1), fmt2(s2), w3_r, h1, w5_r, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h2, w5_r, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w5_r, h1, w5_r, y_last + 40, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w5_r, h2, w5_r, y_first - 40, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
                    ],
                },
                2: {
                    "shape_list": [
                        [fmt2(s1), fmt2(s2), w3_r, h1, w6_r, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h2, w6_r, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
                    ],
                    "shape_list2": [
                        [fmt2(s1), fmt2(s2), w3_r, h1, w5_r, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h2, w6_r, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w5_r, h1, w5_r, y_last + 40, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
                    ],
                    "shape_list3": [
                        [fmt2(s1), fmt2(s2), w3_r, h1, w6_r, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h2, w5_r, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w5_r, h2, w5_r, y_first - 40, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
                    ],
                    "shape_list4": [
                        [fmt2(s1), fmt2(s2), w3_r, h1, w5_r, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h2, w5_r, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w5_r, h1, w5_r, y_last + 40, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w5_r, h2, w5_r, y_first - 40, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_r, h3, w2_r, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_r, h3, 90, 180, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_r, h4, 180, 270, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h1, w1_l, h1, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h2, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w1_l, h1, w1_l, h2, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w2_l, h3, w2_l, h4, lc, lt, ly],
                        [fmt2(s1), fmt2(s2), w3_l, h3, 0, 90, lc, lt, ly, "E", r],
                        [fmt2(s1), fmt2(s2), w3_l, h4, 270, 0, lc, lt, ly, "E", r],
                    ],
                },
            }

            selected_tpl = mode_templates[mode][final_shape_type]
            current_app.logger.debug(
                f"[テンプレ適用] mode={mode}, final_shape_type={final_shape_type}, "
                f"行数={len(selected_tpl)}, サンプル={selected_tpl[:2]}…"
            )

            new_lines = []

            # 角丸用の共通半径
            R_FILLET = 10.0

            # ──────────────────────────────
            # mode 別：比較演算子は mode=1 の基準に統一
            # ──────────────────────────────
            if mode == 1:
                # 1) 角丸を描く／描かない判定
                #   - 上側: shape_list / shape_list3 のときだけ候補
                #   - 下側: shape_list / shape_list2 のときだけ候補
                allow_top_fillet = (
                    final_shape_type in ["shape_list", "shape_list3"]
                    and top_clear >= R_FILLET
                )
                allow_bottom_fillet = (
                    final_shape_type in ["shape_list", "shape_list2"]
                    and bot_clear >= R_FILLET
                )

                current_app.logger.debug(
                    f"[mode1角丸判定] allow_top={allow_top_fillet}, allow_bottom={allow_bottom_fillet}, "
                    f"top_clear={top_clear:.2f}, bot_clear={bot_clear:.2f}"
                )

                # 2) 上フランジ下からガセット上 subcut までの水平ライン
                if top_clear > 0:
                    if allow_top_fillet:
                        # 角丸あり: 従来どおり w6_r から出す
                        start_x_top = w6_r
                    else:
                        # 角丸なし: 垂直線(w1_r)と直結させる
                        start_x_top = w1_r
                    top_horizontal_line = [
                        fmt2(s1), fmt2(s2),
                        start_x_top, y_last + TOP_MARGIN,
                        x_last + 25, y_last + TOP_MARGIN,
                        lc, lt, ly,
                    ]
                else:
                    # 上側に余裕がないときは従来どおり
                    top_horizontal_line = [
                        fmt2(s1), fmt2(s2),
                        w5_r, y_last + TOP_MARGIN,
                        x_last + 25, y_last + TOP_MARGIN,
                        lc, lt, ly,
                    ]
                new_lines.append(top_horizontal_line)

                # 3) 下フランジ上面-2 からガセット下 subcut までの水平ライン
                if bot_clear > 0:
                    if allow_bottom_fillet:
                        # 角丸あり: 従来どおり w6_r から出す
                        start_x_bottom = w6_r
                    else:
                        # 角丸なし: 垂直線(w1_r)と直結させる
                        start_x_bottom = w1_r
                    bottom_horizontal_line = [
                        fmt2(s1), fmt2(s2),
                        start_x_bottom, y_first - BOTTOM_MARGIN,
                        x_last + 40,     y_first - BOTTOM_MARGIN,
                        lc, lt, ly,
                    ]
                else:
                    bottom_horizontal_line = [
                        fmt2(s1), fmt2(s2),
                        w5_r, y_first - BOTTOM_MARGIN,
                        x_last + 40, y_first - BOTTOM_MARGIN,
                        lc, lt, ly,
                    ]
                new_lines.append(bottom_horizontal_line)

                # 4) 継手先端の垂直線とカットライン（これは mode1 では固定でOK）
                right_vertical_line = [
                    fmt2(s1), fmt2(s2),
                    x_last + 40, y_first - BOTTOM_MARGIN,
                    x_last + 40, y_last + 25,
                    lc, lt, ly,
                ]
                new_lines.append(right_vertical_line)

                cut_line = [
                    fmt2(s1), fmt2(s2),
                    x_last + 25, y_last + TOP_MARGIN,
                    x_last + 40, y_last + 25,
                    lc, lt, ly,
                ]
                new_lines.append(cut_line)

                # 5) 角丸（フィレット）を描く場合だけ追加
                #    allow_* が False のときは円弧を一切描かない
                if allow_top_fillet:
                    top_corner_line = [
                        fmt2(s1), fmt2(s2),
                        w6_r, y_last + TOP_MARGIN + R_FILLET,  # = y_last+50
                        180, 270,
                        lc, lt, ly, "E", R_FILLET, 0,
                    ]
                    new_lines.append(top_corner_line)

                if allow_bottom_fillet:
                    bottom_corner_line = [
                        fmt2(s1), fmt2(s2),
                        w6_r, y_first - BOTTOM_MARGIN - R_FILLET,  # = y_first-50
                        90, 180,
                        lc, lt, ly, "E", R_FILLET, 0,
                    ]
                    new_lines.append(bottom_corner_line)

            elif mode == 2:
                # （ここから下は、いま貼っていただいた mode==2 のコードをそのまま残してください）
                # 親梁フランジラインと子梁フランジラインのずれ量で許容判定
                top_gap = abs(h5 - h1)
                bottom_gap = abs(h6 - h2)

                top_tolerant = (top_clear > 0 and top_gap <= yset_limit)
                bottom_tolerant = (bot_clear > 0 and bottom_gap <= yset_limit)

                # ★ 下側だけ拡張許容
                bottom_tolerant_ext = (bot_clear > 0 and bottom_gap <= (yset_limit + d))

                current_app.logger.debug(
                    f"[許容判定] top_gap={top_gap:.2f}, bottom_gap={bottom_gap:.2f}, "
                    f"yset_limit={yset_limit}, bottom_tolerant_ext={bottom_tolerant_ext}"
                )

                # ── 上側 ───────────────────────────────
                if top_clear > 0:
                    if top_tolerant:
                        corner_x = w6_r
                        corner_y = y_last + TOP_MARGIN
                        r_fillet = 10

                        arc_cx = corner_x + r_fillet
                        arc_cy = corner_y + r_fillet

                        flange_vertical = [
                            fmt2(s1), fmt2(s2),
                            corner_x, h1,
                            corner_x, arc_cy,
                            lc, lt, ly,
                        ]
                        new_lines.append(flange_vertical)

                        top_horizontal_line = [
                            fmt2(s1), fmt2(s2),
                            arc_cx,   corner_y,
                            x_last + 25, corner_y,
                            lc, lt, ly,
                        ]
                        new_lines.append(top_horizontal_line)

                        corner_arc = [
                            fmt2(s1), fmt2(s2),
                            arc_cx, arc_cy,
                            180, 270,
                            lc, lt, ly,
                            "E", r_fillet, 0,
                        ]
                        new_lines.append(corner_arc)

                        cut_line = [
                            fmt2(s1), fmt2(s2),
                            x_last + 25, corner_y,
                            x_last + 40, corner_y - 15,
                            lc, lt, ly,
                        ]
                        new_lines.append(cut_line)

                    else:
                        top_horizontal_line = [
                            fmt2(s1), fmt2(s2),
                            w6_r, h1,
                            x_last + 40, h5,
                            lc, lt, ly,
                        ]
                        new_lines.append(top_horizontal_line)

                else:
                    top_horizontal_line = [
                        fmt2(s1), fmt2(s2),
                        w5_r, y_last + TOP_MARGIN,
                        x_last + 25, y_last + TOP_MARGIN,
                        lc, lt, ly,
                    ]
                    cut_line = [
                        fmt2(s1), fmt2(s2),
                        x_last + 25, y_last + TOP_MARGIN,
                        x_last + 40, y_last + 25,
                        lc, lt, ly,
                    ]
                    new_lines.append(top_horizontal_line)
                    new_lines.append(cut_line)

                # ── 下側 ───────────────────────────────
                if bot_clear > 0:
                    if bottom_tolerant_ext:
                        corner_bx = w6_r
                        corner_by = y_first - BOTTOM_MARGIN

                        r_fillet = 10
                        arc_bcx = corner_bx + r_fillet
                        arc_bcy = corner_by - r_fillet

                        flange_vertical_bottom = [
                            fmt2(s1), fmt2(s2),
                            corner_bx, h2,
                            corner_bx, arc_bcy,
                            lc, lt, ly,
                        ]
                        new_lines.append(flange_vertical_bottom)

                        bottom_horizontal_line = [
                            fmt2(s1), fmt2(s2),
                            arc_bcx, corner_by,
                            x_last + 40, corner_by,
                            lc, lt, ly,
                        ]
                        new_lines.append(bottom_horizontal_line)

                        bottom_corner_arc = [
                            fmt2(s1), fmt2(s2),
                            arc_bcx, arc_bcy,
                            90, 180,
                            lc, lt, ly,
                            "E", r_fillet, 0,
                        ]
                        new_lines.append(bottom_corner_arc)

                    else:
                        bottom_horizontal_line = [
                            fmt2(s1), fmt2(s2),
                            w6_r, h2,
                            x_last + 40, h6,
                            lc, lt, ly,
                        ]
                        new_lines.append(bottom_horizontal_line)

                else:
                    bottom_horizontal_line = [
                        fmt2(s1), fmt2(s2),
                        w5_r, y_first - BOTTOM_MARGIN,
                        x_last + 40, y_first - BOTTOM_MARGIN,
                        lc, lt, ly,
                    ]
                    new_lines.append(bottom_horizontal_line)

                cond1 = (top_clear <= 0)
                cond2 = (bot_clear <= 0)

                if top_tolerant:
                    y_top = y_last + 25
                else:
                    if cond1:
                        y_top = y_last + 25
                    else:
                        y_top = h5

                if bottom_tolerant:
                    y_bottom = y_first - BOTTOM_MARGIN
                else:
                    if cond2:
                        y_bottom = y_first - BOTTOM_MARGIN
                    else:
                        y_bottom = h6

                current_app.logger.debug(
                    f"[縦線終端] y_top={y_top:.2f}, y_bottom={y_bottom:.2f}, "
                    f"top_tol={top_tolerant}, bottom_tol={bottom_tolerant}, "
                    f"cond1={cond1}, cond2={cond2}"
                )

                right_vertical_line = [
                    fmt2(s1), fmt2(s2),
                    x_last + 40, y_top,
                    x_last + 40, y_bottom,
                    lc, lt, ly,
                ]
                new_lines.append(right_vertical_line)

            # ヘッダー有無
            if include_header:
                base_template = [
                    ["#ガセットプレート"],
                    [b_set],
                    [999, 100, 50],
                    [
                        2, "H", a, "-H", e, y_set,
                        hole_column_x, "x", hole_row_y, hole_size, "φ",
                    ],
                    ["S", 100, 50],
                    [800, 1],
                ]
            else:
                base_template = [
                    [
                        2, "H", a, "-H", e, y_set,
                        hole_column_x, "x", hole_row_y, hole_size, "φ",
                    ],
                    ["S", 100, 50],
                    [800, 1],
                ]

            # ★ mode1 のときだけ、テンプレート中の垂直線の終点を補正する
            if mode == 1:
                # 元テンプレを丸ごとコピー
                shape_core = [row[:] for row in mode_templates[1][final_shape_type]]

                # 上側の垂直線（index=2）が角丸と接している:
                #   shape_list / shape_list3 で、かつ角丸を描かない場合だけ、
                #   終点 y を「円弧接点(y_last+50) → 水平線の高さ(y_last+40)」に落とす
                if final_shape_type in ["shape_list", "shape_list3"] and not allow_top_fillet:
                    # shape_core[2] = [s1, s2, x1, y1, x2, y2, lc, lt, ly]
                    shape_core[2][5] = y_last + TOP_MARGIN  # y2 を y_last+40 に補正

                # 下側の垂直線（index=3）が角丸と接している:
                #   shape_list / shape_list2 で、かつ角丸を描かない場合だけ、
                #   終点 y を「円弧接点(y_first-50) → 水平線の高さ(y_first-40)」に上げる
                if final_shape_type in ["shape_list", "shape_list2"] and not allow_bottom_fillet:
                    shape_core[3][5] = y_first - BOTTOM_MARGIN  # y2 を y_first-40 に補正

                drawing_rows = shape_core

            else:
                # mode2 などはテンプレそのまま利用
                drawing_rows = [row[:] for row in mode_templates[mode][final_shape_type]]

            drawing_rows = insert_leader_follow_rows(drawing_rows, leader_follow)
            selected_template = base_template + drawing_rows

            # リスト作成関数を呼び出す
            final_shape_list = create_shape_list(
                selected_template, hole_list, new_lines
            )

            result_str = "\n".join(build_dat_line(row) for row in final_shape_list)

            # ──③ action に応じた結果の保持──
            if action == "append":
                # 過去のテキストの末尾に、新しい result_str を追記
                combined = prev_results + ("\n" if prev_results else "") + result_str
                session["results"] = combined
                result_str = combined  # 表示用も上書き
            elif action == "new":
                session["results"] = result_str
            elif action == "clear":
                session.clear()
                result_str = ""

        except ValueError as ve:
            error_message = f"入力エラー: {ve}"
            result_str = ""  # エラー時のresult_strを空に設定

        defaults = get_defaults()
        return render_template(
            "gusset_type/index.html",
            filenames=filenames,
            steel_sizes=steel_options,
            defaults=defaults,
            result_str=result_str,
            error_message=error_message,
        )

    # 最終的なフォーム描画
    defaults = get_defaults()
    return render_template(
        "gusset_type/index.html",
        filenames=filenames,
        steel_sizes=steel_options,
        defaults=defaults,
        result_str=result_str,
        error_message=error_message,
    )
