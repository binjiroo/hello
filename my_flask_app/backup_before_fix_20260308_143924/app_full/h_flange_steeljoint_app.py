import math
from flask import Blueprint, render_template, request, session
from .config import (
    h_steel_r_mapping,              # ← これは統合マスタから自動生成されたものになる
    H_STEEL_SIZES_BY_GROUP,         # ★ 追加
    column_steel_r_mapping,
    diaphragm_sizes_mapping,
    bracket_lengths_mapping,
    regular_flange_pitch_mapping,
    staggered_flange_pitch_mapping,
    regular_flange_pitch_narrow_mapping,
    regular_flange_pitch_middle_mapping,
    regular_flange_pitch_wide_mapping,
    staggered_flange_pitch_narrow_mapping,
    staggered_flange_pitch_middle_mapping,
    staggered_flange_pitch_wide_mapping,
)

column_sizes = list(column_steel_r_mapping.keys())
diaphragm_sizes = list(diaphragm_sizes_mapping.keys())
bracket_lengths = list(bracket_lengths_mapping.keys())

h_flange_steeljoint_bp = Blueprint(
    "h_flange_steeljoint", __name__, template_folder="templates/h_flange_steeljoint"
)

def get_steel_sizes_for_width_group(width_group: str) -> list[str]:
    """
    幅パターン（narrow/middle/wide）に応じて H 型鋼リストを返す。
    未定義のパターンが来た場合は narrow をフォールバックにする。
    """
    if width_group in H_STEEL_SIZES_BY_GROUP:
        lst = H_STEEL_SIZES_BY_GROUP[width_group]
        if lst:
            return lst

    # wide などが空のときの保険
    # それでも空なら統合マスタ全体を返す
    narrow = H_STEEL_SIZES_BY_GROUP.get("narrow", [])
    if narrow:
        return narrow

    return list(h_steel_r_mapping.keys())

def get_stagger_x_params(
    pattern: str,
    is_outer_row: bool,
    hole_column_x: int,
    hole_pitch_x: float,
) -> tuple[int, float]:
    n = max(hole_column_x, 1)

    # 1) 元の外列基準（外スタート・外エンド）
    if pattern == "outer_base":
        if is_outer_row:
            # 外：E, E+P, E+2P, ...
            return n, 0.0
        else:
            # 内：E+P/2, E+3P/2, ...  (両端が外)
            return max(n - 1, 1), hole_pitch_x / 2.0

    # 2) 外内同数（両方とも E, E+P, ... ベース）
    if pattern == "same_center":
        if is_outer_row:
            # 外：E, E+P, ...
            return n, 0.0
        else:
            # 内：E+P/2, E+3P/2, ...（列数は外と同じ）
            return n, hole_pitch_x / 2.0

    # 3) 内で始まり外で終わる（最初の列だけ内側、最後の列だけ外側…のようなアレンジ）
    if pattern == "same_inner_start":
        if is_outer_row:
            # 外：E+P/2, E+3P/2, ...（内より 1/2P 奥側）
            return n, hole_pitch_x / 2.0
        else:
            # 内：E, E+P, E+2P, ...
            return n, 0.0

    # 4) 外で始まり内で終わる
    if pattern == "same_outer_start":
        if is_outer_row:
            # 外：E, E+P, ...
            return n, 0.0
        else:
            # 内：E+P/2, E+3P/2, ...
            return n, hole_pitch_x / 2.0

    # 5) 内で始まり内で終わる（両端が内）
    if pattern == "same_inner_both":
        if is_outer_row:
            # 外：E+P/2, E+3P/2, ...（内の間だけに入る → 列数は 1 個少ない）
            return max(n - 1, 1), hole_pitch_x / 2.0
        else:
            # 内：E, E+P, E+2P, ...（両端とも内）
            return n, 0.0

    # 想定外は outer_base 相当
    if is_outer_row:
        return n, 0.0
    else:
        return max(n - 1, 1), hole_pitch_x / 2.0

def process_result(prev_result: str, shape_list: list[list], action: str) -> str:
    """
    shape_list からDATファイル用のテキストを生成し、
    action が 'append' なら prev_result に追記、
    そうでなければ新規に返します。
    """

def get_defaults():
    # セッションに steel_size があればそれを使い、なければ narrow の最初を使う
    all_narrow = H_STEEL_SIZES_BY_GROUP.get("narrow") or list(h_steel_r_mapping.keys())
    default_steel = session.get("steel_size", all_narrow[0])

    # width_group は、セッション指定 > 統合マスタの幅グループ > "narrow" の優先順
    from .config import H_STEEL_MASTER  # ループ import が気になる場合はファイル先頭に移しても OK
    master_info = H_STEEL_MASTER.get(default_steel, {})
    default_width_group = master_info.get("width_group", "narrow")

    flange_width_pattern = session.get("flange_width_pattern", default_width_group)

    return {
        "steel_size": session.get("steel_size", default_steel),
        "column_size": session.get("column_size", column_sizes[0]),
        "diaphragm_size": session.get("diaphragm_size", diaphragm_sizes[0]),
        "bracket_length": session.get("bracket_length", bracket_lengths[0]),
        "hole_column_x": session.get("hole_column_x", "1"),
        "hole_row_y": session.get("hole_row_y", "1"),
        "hole_pitch_x": session.get("hole_pitch_x", "60"),
        "hole_endpitch_x": session.get("hole_endpitch_x", "40"),
        "clearance": session.get("clearance", "10"),
        "hole_size": session.get("hole_size", "18"),
        "hole_pattern": session.get("hole_pattern", "0"),
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

        # ★ 幅パターンのデフォルトを統合マスタから
        "flange_width_pattern": flange_width_pattern,

        # ★ 千鳥孔のスタート
        "stagger_col_pattern": session.get("stagger_col_pattern", "outer_base"),
    }

@h_flange_steeljoint_bp.route("/", methods=["GET", "POST"])
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

    regular_keys = list(regular_flange_pitch_mapping.keys())
    staggered_keys = list(staggered_flange_pitch_mapping.keys())
    hole_pattern = request.form.get("hole_pattern", session.get("hole_pattern", "0"))
    flange_width_pattern = request.form.get(
        "flange_width_pattern",
        session.get("flange_width_pattern", "narrow")
    )

    # ★ 幅パターンに応じて H 型鋼リストを決定
    steel_sizes = get_steel_sizes_for_width_group(flange_width_pattern)

    # ★ セッションの steel_size がリストに含まれていなければ、先頭に差し替え
    current_steel = session.get("steel_size", defaults["steel_size"])
    if current_steel not in steel_sizes and steel_sizes:
        current_steel = steel_sizes[0]
        session["steel_size"] = current_steel
        defaults["steel_size"] = current_steel


    raw = request.form.get("hole_pitch_y")
    if raw:
        try:
            hole_pitch_y = float(raw)
        except ValueError:
            hole_pitch_y = 60.0
    else:
        selected = request.form.get("steel_size")

        # ★ 幅パターン & 孔タイプでマッピングを選ぶ
        if hole_pattern == "0":
            # 通常孔
            if flange_width_pattern == "narrow":
                mapping = regular_flange_pitch_narrow_mapping
            elif flange_width_pattern == "middle":
                mapping = regular_flange_pitch_middle_mapping
            elif flange_width_pattern == "wide":
                mapping = regular_flange_pitch_wide_mapping
            else:
                mapping = regular_flange_pitch_mapping  # フォールバック
        else:
            # 千鳥孔
            if flange_width_pattern == "narrow":
                mapping = staggered_flange_pitch_narrow_mapping
            elif flange_width_pattern == "middle":
                mapping = staggered_flange_pitch_middle_mapping
            elif flange_width_pattern == "wide":
                mapping = staggered_flange_pitch_wide_mapping
            else:
                mapping = staggered_flange_pitch_mapping  # フォールバック

        if selected in mapping:
            hole_pitch_y = float(mapping[selected][0])
        else:
            hole_pitch_y = float(session.get("hole_pitch_y", 60))

    session["hole_pattern"] = hole_pattern
    session["flange_width_pattern"] = flange_width_pattern
    session["hole_pitch_y"] = hole_pitch_y

    hole_row_y = defaults["hole_row_y"]
    hole_pattern = defaults["hole_pattern"]
    result_str = ""
    error_msg = ""

    if request.method == "POST":
        defaults = get_defaults()
        action = request.form.get("action", "new")
        prev_result = request.form.get("prev_result", "")
        # 数値系をまとめてキャスト
        try:
            hole_row_y = int(session.get("hole_row_y", defaults["hole_row_y"]))
            hole_column_x = int(session.get("hole_column_x", defaults["hole_column_x"]))
            hole_pitch_x = float(session.get("hole_pitch_x", defaults["hole_pitch_x"]))
            clearance = float(session.get("clearance", defaults["clearance"]))
            hole_size = float(session.get("hole_size", defaults["hole_size"]))
        except ValueError:
            # どれかがキャスト失敗したらフォールバック
            hole_row_y = 1
            hole_column_x = 1
            hole_pitch_x = 60.0
            clearance = 10.0
            hole_size = 18.0
            action = request.form.get("action", "new")
            prev_result = request.form.get("prev_result", "")

        if action == "clear":
            session.clear()
            defaults = get_defaults()
            # GET の初期表示
            return render_template(
                "h_flange_steeljoint/index.html",
                filenames=filenames,
                steel_sizes=steel_sizes,
                column_sizes=column_sizes,
                diaphragm_sizes=diaphragm_sizes,
                bracket_lengths=bracket_lengths,
                h_steel_sizes_by_group=H_STEEL_SIZES_BY_GROUP,
                # ★ ここ追加：細・中・広＋互換ビュー
                regular_flange_pitch_mapping=regular_flange_pitch_mapping,
                staggered_flange_pitch_mapping=staggered_flange_pitch_mapping,
                regular_flange_pitch_narrow_mapping=regular_flange_pitch_narrow_mapping,
                regular_flange_pitch_middle_mapping=regular_flange_pitch_middle_mapping,
                regular_flange_pitch_wide_mapping=regular_flange_pitch_wide_mapping,
                staggered_flange_pitch_narrow_mapping=staggered_flange_pitch_narrow_mapping,
                staggered_flange_pitch_middle_mapping=staggered_flange_pitch_middle_mapping,
                staggered_flange_pitch_wide_mapping=staggered_flange_pitch_wide_mapping,
                defaults=defaults,
                result_str=result_str,
                error_msg=error_msg,
            )

        # ★★★ ここから inner_pitch_y を取得（try と clear の「後」） ★★★
        inner_pitch_y = None
        if str(session.get("hole_pattern", "0")) == "1":
            steel_size = session.get("steel_size", defaults["steel_size"])
            flange_width_pattern = session.get(
                "flange_width_pattern",
                defaults["flange_width_pattern"],
            )

            # 幅パターンごとに千鳥用マッピングを選択
            if flange_width_pattern == "narrow":
                stagger_mapping = staggered_flange_pitch_narrow_mapping
            elif flange_width_pattern == "middle":
                stagger_mapping = staggered_flange_pitch_middle_mapping
            elif flange_width_pattern == "wide":
                stagger_mapping = staggered_flange_pitch_wide_mapping
            else:
                stagger_mapping = staggered_flange_pitch_mapping  # フォールバック

            tup = stagger_mapping.get(steel_size)
            if tup and len(tup) >= 2:
                # tup = (外外ピッチ, 外→内ピッチ)
                inner_pitch_y = float(tup[1])
        # ★★★ inner_pitch_y ブロックはここまで ★★★

        session["hole_row_y"] = request.form.get("hole_row_y", defaults["hole_row_y"])

        # ★ ここで列パターンも保存
        session["stagger_col_pattern"] = request.form.get(
            "stagger_col_pattern",
            defaults["stagger_col_pattern"],
        )
        stagger_col_pattern = session["stagger_col_pattern"]

        # フォームデータ保存
        for key in defaults:
            session[key] = request.form.get(key, defaults[key])

        steel_size = session["steel_size"]
        column_size = session["column_size"]
        diaphragm_size = session["diaphragm_size"]
        bracket_length = session["bracket_length"]
        hole_column_x = int(session["hole_column_x"])
        hole_row_y = int(session["hole_row_y"])
        hole_pitch_x = float(session["hole_pitch_x"])
        hole_endpitch_x = float(session["hole_endpitch_x"])
        clearance = float(session["clearance"])
        hole_size = float(session["hole_size"])
        hole_pattern = int(session["hole_pattern"])
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

        # a,b,c の抽出
        steel_size_vals = steel_size.split("x")
        column_size_vals = column_size.split("x")
        diaphragm_size_vals = diaphragm_size.split("x")
        bracket_length_vals = bracket_length.split("x")
        steel_size_filtered = [
            v for i, v in enumerate(steel_size_vals) if i not in (0, 3)
        ]
        column_size_filtered = [
            v for i, v in enumerate(column_size_vals) if i not in (2,)
        ]
        diaphragm_size_filtered = [
            v for i, v in enumerate(diaphragm_size_vals) if i not in (2,)
        ]
        bracket_length_filtered = [v for i, v in enumerate(bracket_length_vals)]
        brk_leng_list = list(map(float, bracket_length_filtered))
        h_flg, h_t1 = map(float, steel_size_filtered)
        col_width, col_height = map(float, column_size_filtered)
        dia_width_1, dia_width_2 = map(float, diaphragm_size_filtered)
        brk_leng = brk_leng_list[0]

        # オフセットの候補high
        offs = {
            1: (0, -h_flg / 2),
            2: (0, 0),
            3: (0, h_flg / 2),
        }
        choice = int(off_choice) if off_choice.isdigit() else 5
        x_offset, y_offset = offs.get(choice, (0, 0))

        # 各変数の計算
        w1 = col_width / 2
        w2 = dia_width_1 / 2
        w3 = brk_leng
        w4 = brk_leng + clearance
        h1 = h_flg / 2  # 200
        h2 = h_t1 / 2  # 8

        # 標準孔パターン用リスト
        hole_list = []  # ブロック1用
        hole_list2 = []  # ブロック2用

        # 千鳥孔パターン用リスト
        row_holes_list_1 = []  # ブロック1用（千鳥）
        row_holes_list_2 = []  # ブロック2用（千鳥）

        if hole_pattern == 0:
            # 標準配置の処理
            for i in range(hole_row_y):
                y = (i - (hole_row_y - 1) / 2) * hole_pitch_y
                for j in range(hole_column_x):
                    x1 = w4 + (hole_endpitch_x + j * hole_pitch_x)
                    x2 = w3 - (hole_endpitch_x + j * hole_pitch_x)
                    zx1 = x1 + hole_size / 2
                    zx2 = x1 - hole_size / 2
                    zx3 = x2 + hole_size / 2
                    zx4 = x2 - hole_size / 2
                    zy1 = y + hole_size / 2
                    zy2 = y - hole_size / 2
                    hole_list.extend(
                        [
                            [1, 1, zx1, y + y_offset, zx2, y + y_offset, lc, lt, ly],
                            [1, 1, x1, zy1 + y_offset, x1, zy2 + y_offset, lc, lt, ly],
                            [ 1, 1, x1, y + y_offset, zx1, y + y_offset, lc, lt, ly, "E", 360, 0, ],
                            [1, 1, zx3, y + y_offset, zx4, y + y_offset, lc, lt, ly],
                            [1, 1, x2, zy1 + y_offset, x2, zy2 + y_offset, lc, lt, ly],
                            [ 1, 1, x2, y + y_offset, zx3, y + y_offset, lc, lt, ly, "E", 360, 0, ],
                        ]
                    )

            for i in range(hole_row_y):
                y = (i - (hole_row_y - 1) / 2) * hole_pitch_y
                for j in range(hole_column_x):
                    x1 = w4 + (hole_endpitch_x + j * hole_pitch_x)
                    x2 = w3 - (hole_endpitch_x + j * hole_pitch_x)
                    zx1 = x1 + hole_size / 2
                    zx2 = x1 - hole_size / 2
                    zx3 = x2 + hole_size / 2
                    zx4 = x2 - hole_size / 2
                    zy1 = y + hole_size / 2
                    zy2 = y - hole_size / 2
                    hole_list2.extend(
                        [
                            [2, 2, -zx1, y + y_offset, -zx2, y + y_offset, lc, lt, ly],
                            [ 2, 2, -x1, zy1 + y_offset, -x1, zy2 + y_offset, lc, lt, ly, ],
                            [ 2, 2, -x1, y + y_offset, -zx1, y + y_offset, lc, lt, ly, "E", 360, 0, ],
                            [2, 2, -zx3, y + y_offset, -zx4, y + y_offset, lc, lt, ly],
                            [ 2, 2, -x2, zy1 + y_offset, -x2, zy2 + y_offset, lc, lt, ly, ],
                            [ 2, 2, -x2, y + y_offset, -zx3, y + y_offset, lc, lt, ly, "E", 360, 0, ],
                        ]
                    )

        elif hole_pattern == 1:
            # 千鳥配置
            row_holes_list_1 = []  # ブロック1用（千鳥）
            row_holes_list_2 = []  # ブロック2用（千鳥）

            outer_rows = hole_row_y          # 外側配列の段数
            actual_rows = outer_rows * 2     # 実際の行数（外＋内）

            # -----------------------------
            # 1) y 方向の行位置を決定
            # -----------------------------
            if actual_rows <= 1:
                # 行が 1(=外側1行だけ) のときは 0 に集約
                y_positions = [0.0]

            elif actual_rows == 4 and inner_pitch_y is not None:
                # 外側2行・内側2行（合計4行）の典型ケース
                #   hole_pitch_y = 外側⇔外側 の距離
                #   inner_pitch_y = 外側⇔内側 の距離
                half_outer = hole_pitch_y / 2.0

                y_bottom_outer = -half_outer      # 下側外
                y_top_outer    =  half_outer      # 上側外

                y_bottom_inner = y_bottom_outer + inner_pitch_y  # 下側内
                y_top_inner    = y_top_outer    - inner_pitch_y  # 上側内

                # 下外 → 下内 → 上内 → 上外 の順
                y_positions = [
                    y_bottom_outer,
                    y_bottom_inner,
                    y_top_inner,
                    y_top_outer,
                ]

            else:
                # それ以外（行数が4でない、inner_pitch_y が無いなど）は等分割
                y_top = -hole_pitch_y / 2.0
                y_bottom = hole_pitch_y / 2.0
                if actual_rows <= 1:
                    y_positions = [0.0]
                else:
                    interval = (y_bottom - y_top) / (actual_rows - 1)
                    y_positions = [y_top + interval * i for i in range(actual_rows)]

            # -----------------------------
            # 2) 各行について X 方向の孔配置を決定
            # -----------------------------
            for i in range(actual_rows):
                y = y_positions[i]

                is_outer_row = (i == 0 or i == actual_rows - 1)

                # ★ モードに応じて孔数とオフセットを取得
                num_cols, extra_x_offset = get_stagger_x_params(
                    stagger_col_pattern,
                    is_outer_row,
                    hole_column_x,
                    hole_pitch_x,
                )

                row_1 = []
                row_2 = []

                for j in range(num_cols):
                    # 大梁側・ブラケット側で対称になるように距離 d を定義
                    d = hole_endpitch_x + j * hole_pitch_x + extra_x_offset

                    # 大梁側（w4 側）: プラス方向
                    x1 = w4 + d
                    # ブラケット側（w3 側）: マイナス方向へ d だけ戻る
                    x2 = w3 - d

                    # 大梁側孔の周囲
                    zx1 = x1 + hole_size / 2.0
                    zx2 = x1 - hole_size / 2.0
                    # ブラケット側孔の周囲
                    zx3 = x2 + hole_size / 2.0
                    zx4 = x2 - hole_size / 2.0

                    zy1 = y + hole_size / 2.0
                    zy2 = y - hole_size / 2.0

                    # --- ブロック1側（正側） ---

                    # 大梁側孔
                    row_1.extend(
                        [
                            [1, 1, zx1, y + y_offset, zx2, y + y_offset, lc, lt, ly],
                            [1, 1, x1,  zy1 + y_offset, x1,  zy2 + y_offset, lc, lt, ly],
                            [
                                1, 1,
                                x1,  y + y_offset,
                                zx1, y + y_offset,
                                lc, lt, ly, "E", 360, 0,
                            ],
                        ]
                    )

                    # ブラケット側孔
                    row_1.extend(
                        [
                            [1, 1, zx3, y + y_offset, zx4, y + y_offset, lc, lt, ly],
                            [1, 1, x2,  zy1 + y_offset, x2,  zy2 + y_offset, lc, lt, ly],
                            [
                                1, 1,
                                x2,  y + y_offset,
                                zx3, y + y_offset,
                                lc, lt, ly, "E", 360, 0,
                            ],
                        ]
                    )

                    # --- ブロック2側（鏡像：X だけ符号反転） ---

                    # 大梁側孔（鏡像）
                    row_2.extend(
                        [
                            [2, 2, -zx1, y + y_offset, -zx2, y + y_offset, lc, lt, ly],
                            [2, 2, -x1,  zy1 + y_offset, -x1,  zy2 + y_offset, lc, lt, ly],
                            [
                                2, 2,
                                -x1,  y + y_offset,
                                -zx1, y + y_offset,
                                lc, lt, ly, "E", 360, 0,
                            ],
                        ]
                    )

                    # ブラケット側孔（鏡像）
                    row_2.extend(
                        [
                            [2, 2, -zx3, y + y_offset, -zx4, y + y_offset, lc, lt, ly],
                            [2, 2, -x2,  zy1 + y_offset, -x2,  zy2 + y_offset, lc, lt, ly],
                            [
                                2, 2,
                                -x2,  y + y_offset,
                                -zx3, y + y_offset,
                                lc, lt, ly, "E", 360, 0,
                            ],
                        ]
                    )

                row_holes_list_1.append(row_1)
                row_holes_list_2.append(row_2)

        else:
            print("無効なパターン選択です。標準配置として処理します。")
            for i in range(hole_row_y):
                y = (i - (hole_row_y - 1) / 2) * hole_pitch_y
                for j in range(hole_column_x):
                    x1 = w4 + (hole_endpitch_x + j * hole_pitch_x)
                    x2 = w3 - (hole_endpitch_x + j * hole_pitch_x)
                    zx1 = x1 + hole_size / 2
                    zx2 = x1 - hole_size / 2
                    zx3 = x2 + hole_size / 2
                    zx4 = x2 - hole_size / 2
                    zy1 = y + hole_size / 2
                    zy2 = y - hole_size / 2
                    hole_list.extend(
                        [
                            [1, 1, zx1, y + y_offset, zx2, y + y_offset, lc, lt, ly],
                            [1, 1, x1, zy1 + y_offset, x1, zy2 + y_offset, lc, lt, ly],
                            [ 1, 1, x1, y + y_offset, zx1, y + y_offset, lc, lt, ly, "E", 360, 0, ],
                        ]
                    )
                    hole_list2.extend(
                        [
                            [2, 2, -zx1, y + y_offset, -zx2, y + y_offset, lc, lt, ly],
                            [ 2, 2, -x1, zy1 + y_offset, -x1, zy2 + y_offset, lc, lt, ly, ],
                            [ 2, 2, -x1, y + y_offset, -zx1, y + y_offset, lc, lt, ly, "E", 360, 0, ],
                        ]
                    )

        # -----------------------------
        # shape_list の組み立て
        # -----------------------------
        shape_list = []

        # ★ 追加計算ではヘッダを付けない
        #   - action != "append"（新規） のとき
        #   - または prev_result が空のとき（初回 append 対応）
        if action != "append" or not prev_result.strip():
            shape_list.extend([
                ["#H型鋼断面"],
                [members],
                [999],
            ])

        # ここから下は元の中身をそのまま移動
        shape_list.extend([
            [2, "H-" + steel_size],
            ["S", 100, 50],
            ["W", 0],
            # ブロック1ブラケット切端
            [1, 1, w1, 0 + y_offset, w3, 0 + y_offset, lc, 5, ly],
            [1, 1, w3, h1 + y_offset, w3, -h1 + y_offset, lc, lt, ly],
            [1, 1, w1, h1 + y_offset, w3, h1 + y_offset, lc, lt, ly],
            [1, 1, w1, -h1 + y_offset, w3, -h1 + y_offset, lc, lt, ly],
            [1, 1, w1, h2 + y_offset, w3, h2 + y_offset, lc, 5, ly],
            [1, 1, w1, -h2 + y_offset, w3, -h2 + y_offset, lc, 5, ly],
            # ブロック1大梁切端
            [1, 1, w4, h1 + y_offset, w4, -h1 + y_offset, lc, lt, ly],
        ])


        if hole_pattern == 0:
            shape_list.extend(hole_list)
            shape_list.extend(hole_list2)

        elif hole_pattern == 1:
            for row in row_holes_list_1:
                shape_list.extend(row)
            for row in row_holes_list_2:
                shape_list.extend(row)
        # ブロック間
        shape_list.extend(
            [
                [1, 2, w4, 0 + y_offset, -w4, 0 + y_offset, lc, 5, ly],
                [1, 2, w4, h1 + y_offset, -w4, h1 + y_offset, lc, lt, ly],
                [1, 2, w4, -h1 + y_offset, -w4, -h1 + y_offset, lc, lt, ly],
                [1, 2, w4, h2 + y_offset, -w4, h2 + y_offset, lc, 5, ly],
                [1, 2, w4, -h2 + y_offset, -w4, -h2 + y_offset, lc, 5, ly],
            ]
        )

        shape_list.extend(
            [
                # ブロック2ブラケット切端
                [2, 2, -w1, 0 + y_offset, -w3, 0 + y_offset, lc, 5, ly],
                [2, 2, -w3, h1 + y_offset, -w3, -h1 + y_offset, lc, lt, ly],
                [2, 2, -w1, h1 + y_offset, -w3, h1 + y_offset, lc, lt, ly],
                [2, 2, -w1, -h1 + y_offset, -w3, -h1 + y_offset, lc, lt, ly],
                [2, 2, -w1, h2 + y_offset, -w3, h2 + y_offset, lc, 5, ly],
                [2, 2, -w1, -h2 + y_offset, -w3, -h2 + y_offset, lc, 5, ly],
                # ブロック2大梁切端
                [2, 2, -w4, h1 + y_offset, -w4, -h1 + y_offset, lc, lt, ly],
            ]
        )

        shape_list.append([999, 100, 50])

        result_str = process_result(prev_result, shape_list, action)

        lines = [" ".join(str(e) for e in row) for row in shape_list]
        new_result = "\n".join(lines)

        result_str = (
            (prev_result + "\n" + new_result).strip()
            if action == "append"
            else new_result
        )

        defaults = get_defaults()

        return render_template(
            "h_flange_steeljoint/index.html",
            filenames=filenames,
            steel_sizes=steel_sizes,
            column_sizes=column_sizes,
            diaphragm_sizes=diaphragm_sizes,
            bracket_lengths=bracket_lengths,
            h_steel_sizes_by_group=H_STEEL_SIZES_BY_GROUP,
            # マッピング両方を渡す
            regular_flange_pitch_mapping=regular_flange_pitch_mapping,
            staggered_flange_pitch_mapping=staggered_flange_pitch_mapping,
            regular_flange_pitch_narrow_mapping=regular_flange_pitch_narrow_mapping,
            regular_flange_pitch_middle_mapping=regular_flange_pitch_middle_mapping,
            regular_flange_pitch_wide_mapping=regular_flange_pitch_wide_mapping,
            staggered_flange_pitch_narrow_mapping=staggered_flange_pitch_narrow_mapping,
            staggered_flange_pitch_middle_mapping=staggered_flange_pitch_middle_mapping,
            staggered_flange_pitch_wide_mapping=staggered_flange_pitch_wide_mapping,
            defaults=defaults,
            result_str=result_str,
            error_msg=error_msg,
        )
    # GET の初期表示
    return render_template(
        "h_flange_steeljoint/index.html",
        filenames=filenames,
        steel_sizes=steel_sizes,
        column_sizes=column_sizes,
        diaphragm_sizes=diaphragm_sizes,
        bracket_lengths=bracket_lengths,
        h_steel_sizes_by_group=H_STEEL_SIZES_BY_GROUP,
        # ★ ここ追加：細・中・広＋互換ビュー
        regular_flange_pitch_mapping=regular_flange_pitch_mapping,
        staggered_flange_pitch_mapping=staggered_flange_pitch_mapping,
        regular_flange_pitch_narrow_mapping=regular_flange_pitch_narrow_mapping,
        regular_flange_pitch_middle_mapping=regular_flange_pitch_middle_mapping,
        regular_flange_pitch_wide_mapping=regular_flange_pitch_wide_mapping,
        staggered_flange_pitch_narrow_mapping=staggered_flange_pitch_narrow_mapping,
        staggered_flange_pitch_middle_mapping=staggered_flange_pitch_middle_mapping,
        staggered_flange_pitch_wide_mapping=staggered_flange_pitch_wide_mapping,
        defaults=defaults,
        result_str=result_str,
        error_msg=error_msg,
    )

