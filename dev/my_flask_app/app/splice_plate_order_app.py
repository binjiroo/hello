# my_flask_app/app/splice_plate_order_app.py
import os
import json
from dataclasses import dataclass, asdict
from flask import Blueprint, render_template, request, current_app
from typing import List, Optional

# steel_lists.json への共通パス
BASEDIR = os.path.abspath(os.path.dirname(__file__))
STEEL_LISTS_PATH = os.path.join(BASEDIR, 'data', 'steel_lists.json')

# ★ 共通デフォルト（JS 側の DEFAULT_SP_… と合わせる）
DEFAULT_SP_END_PITCH_MM = 40      # 切端～最初孔芯
DEFAULT_SP_CLEARANCE_MM = 10      # 柱ブラケット～大梁クリアランス

# ★ H型鋼ごとのスプライスプレート初期値マッピング（推奨：板厚＋孔条件＋端ピッチのみ）
# ※ flange_plate_outer / flange_plate_inner / web_plate は「JSが計算して入力欄へ生成する」ので持たせない想定
# ※ hole_count_y や web 側の孔条件は暫定値（必要に応じてAIJ等に合わせて修正）

SPLICE_PRESETS: dict[str, dict] = {

    "H-200x100x5.5x8": {
        # thickness
        "flange_thk_mm": 9,
        "web_thk_mm": 6,

        # common
        "common_flange_end_pitch": "40",
        "common_flangesp_end_pitch": "40",
        "common_web_end_pitch": "40",
        "common_websp_x_end_pitch": "40",
        "common_websp_y_end_pitch": "40",
        "common_clearance": "10",

        # flange
        "flange_hole_dia": "18",
        "flange_hole_count_x": "2",
        "flange_hole_count_y": "2",
        "flange_col_pitch": "60",
        "flange_row_pitch": "60",

        # web
        "web_col_pitch": "60",
        "web_row_pitch": "60",
        "web_hole_count_x": "1",
        "web_hole_count_y": "2",
        "web_hole_dia": "18",
    },

    "H-250x125x6x9": {
        "flange_thk_mm": 9,
        "web_thk_mm": 6,

        # common
        "common_flange_end_pitch": "40",
        "common_flangesp_end_pitch": "40",
        "common_web_end_pitch": "40",
        "common_websp_x_end_pitch": "40",
        "common_websp_y_end_pitch": "40",
        "common_clearance": "10",

        # flange
        "flange_hole_dia": "18",
        "flange_hole_count_x": "3",
        "flange_hole_count_y": "2",
        "flange_col_pitch": "60",
        "flange_row_pitch": "75",

        # web
        "web_col_pitch": "60",
        "web_row_pitch": "60",
        "web_hole_count_x": "1",
        "web_hole_count_y": "2",
        "web_hole_dia": "18",
    },

    "H-300x150x6.5x9": {
        "flange_thk_mm": 12,
        "web_thk_mm": 9,

        # common
        "common_flange_end_pitch": "40",
        "common_flangesp_end_pitch": "40",
        "common_web_end_pitch": "40",
        "common_websp_x_end_pitch": "40",
        "common_websp_y_end_pitch": "40",
        "common_clearance": "10",

        # flange
        "flange_hole_dia": "18",
        "flange_hole_count_x": "3",
        "flange_hole_count_y": "2",
        "flange_col_pitch": "60",
        "flange_row_pitch": "90",

        # web
        "web_col_pitch": "60",
        "web_row_pitch": "60",
        "web_hole_count_x": "1",
        "web_hole_count_y": "3",
        "web_hole_dia": "18",
    },

    "H-400x200x8x13": {
        "flange_thk_mm": 12,
        "web_thk_mm": 9,

        # common
        "common_flange_end_pitch": "40",
        "common_flangesp_end_pitch": "40",
        "common_web_end_pitch": "40",
        "common_websp_x_end_pitch": "40",
        "common_websp_y_end_pitch": "40",
        "common_clearance": "10",

        # flange
        "flange_hole_dia": "22",
        "flange_hole_count_x": "3",
        "flange_hole_count_y": "2",
        "flange_col_pitch": "60",
        "flange_row_pitch": "120",

        # web
        "web_col_pitch": "60",
        "web_row_pitch": "60",
        "web_hole_count_x": "1",
        "web_hole_count_y": "4",
        "web_hole_dia": "22",
    },

    "H-500x200x10x16": {
        "flange_thk_mm": 19,
        "web_thk_mm": 16,

        # common
        "common_flange_end_pitch": "40",
        "common_flangesp_end_pitch": "40",
        "common_web_end_pitch": "40",
        "common_websp_x_end_pitch": "40",
        "common_websp_y_end_pitch": "40",
        "common_clearance": "10",

        # flange
        "flange_hole_dia": "24",
        "flange_hole_count_x": "4",
        "flange_hole_count_y": "2",
        "flange_col_pitch": "70",
        "flange_row_pitch": "120",

        # web
        "web_col_pitch": "70",
        "web_row_pitch": "100",
        "web_hole_count_x": "1",
        "web_hole_count_y": "5",
        "web_hole_dia": "24",
    },
}

def load_steel_lists() -> dict:
    """
    steel_materials_order と同じ data/steel_lists.json を読むヘルパー。
    """
    try:
        with open(STEEL_LISTS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        current_app.logger.error(
            "[splice] steel_lists.json が見つかりません: %s", STEEL_LISTS_PATH
        )
        return {}
    except Exception as e:
        current_app.logger.exception(
            "[splice] steel_lists.json 読み込み失敗: %s", e
        )
        return {}

# =========================
# レイアウトプロファイル定義
# =========================

@dataclass
class LayoutProfile:
    key: str
    label: str
    page_width_mm: float
    page_height_mm: float
    orientation: str          # 'portrait' or 'landscape'
    drawing_ratio: float      # 図面エリア比率（0〜1）
    data_ratio: float         # データエリア比率（0〜1）

    def to_dict(self):
        d = asdict(self)
        d["page_size"] = (self.page_width_mm, self.page_height_mm)
        return d

LAYOUT_PROFILES: dict[str, LayoutProfile] = {
    "A3_landscape_7_3": LayoutProfile(
        key="A3_landscape_7_3",
        label="A3 横 / 図面7 : データ3",
        page_width_mm=420.0,
        page_height_mm=297.0,
        orientation="landscape",
        drawing_ratio=0.7,
        data_ratio=0.3,
    ),
    "A4_portrait_6_4": LayoutProfile(
        key="A4_portrait_6_4",
        label="A4 縦 / 図面6 : データ4",
        page_width_mm=210.0,
        page_height_mm=297.0,
        orientation="portrait",
        drawing_ratio=0.6,
        data_ratio=0.4,
    ),
}

DEFAULT_PROFILE_KEY = "A3_landscape_7_3"

@dataclass
class SplicePlateRow:
    h_size: str = ""
    set_count: Optional[int] = None       # ★ 修正
    flange_plate_outer: str = ""  # "t×B×L"
    flange_plate_inner: str = ""  # "t×B×L"
    web_plate: str = ""           # "t×H×L"
    hole_dia: str = ""
    hole_count_x: Optional[int] = None    # ★ 修正
    hole_count_y: Optional[int] = None
    col_pitch: str = ""
    row_pitch: str = ""
    remarks: str = ""

# =========================
# Blueprint 定義
# =========================

splice_plate_order_bp = Blueprint(
    "splice_plate_order",
    __name__,
    template_folder="templates/splice_plate_order",
)

def _get_layout_profile_from_request() -> dict:
  """
  クエリ ?profile=... からレイアウトプロファイルを取得。
  不正 or 未指定なら DEFAULT_PROFILE_KEY を使う。
  """
  key = request.args.get("profile", DEFAULT_PROFILE_KEY)
  profile = LAYOUT_PROFILES.get(key, LAYOUT_PROFILES[DEFAULT_PROFILE_KEY])
  return profile.to_dict()

def _to_int_or_none(raw: str) -> Optional[int]:
    """
    空文字や不正な数字は None として扱う簡易パーサ。
    """
    s = (raw or "").strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        # ログにだけ残しておくと後で原因追跡しやすい
        current_app.logger.warning("[splice] invalid int value: %r", raw)
        return None

def _build_rows_from_request() -> List[SplicePlateRow]:
    if request.method != "POST":
        return [SplicePlateRow()]  # 初期表示：空1行

    h_sizes      = request.form.getlist("h_size[]")
    set_counts   = request.form.getlist("set_count[]")
    flange_outer_list = request.form.getlist("flange_plate_outer[]")
    flange_inner_list = request.form.getlist("flange_plate_inner[]")
    web_list     = request.form.getlist("web_plate[]")
    hole_dias    = request.form.getlist("hole_dia[]")
    hole_counts_x = request.form.getlist("hole_count_x[]")
    hole_counts_y = request.form.getlist("hole_count_y[]")
    col_pitches  = request.form.getlist("col_pitch[]")
    row_pitches  = request.form.getlist("row_pitch[]")
    remarks_list = request.form.getlist("remarks[]")

    max_len = max(
        len(h_sizes),
        len(set_counts),
        len(flange_outer_list),
        len(flange_inner_list),
        len(web_list),
        len(hole_dias),
        len(hole_counts_x),
        len(hole_counts_y),
        len(col_pitches),
        len(row_pitches),
        len(remarks_list),
    )

    rows: List[SplicePlateRow] = []

    for i in range(max_len):
        def at(lst, idx, default=""):
            return lst[idx] if idx < len(lst) else default

        row = SplicePlateRow(
            h_size      = at(h_sizes, i, ""),
            set_count   = _to_int_or_none(at(set_counts, i, "")),
            flange_plate_outer= at(flange_outer_list, i, ""),
            flange_plate_inner= at(flange_inner_list, i, ""),
            web_plate   = at(web_list, i, ""),
            hole_dia    = at(hole_dias, i, ""),
            hole_count_x= _to_int_or_none(at(hole_counts_x, i, "")),
            hole_count_y= _to_int_or_none(at(hole_counts_y, i, "")),
            col_pitch   = at(col_pitches, i, ""),
            row_pitch   = at(row_pitches, i, ""),
            remarks     = at(remarks_list, i, ""),
        )

        if any([
            row.h_size,
            row.set_count,
            row.flange_plate_outer,
            row.flange_plate_inner,
            row.web_plate,
            row.hole_dia,
            row.hole_count_x,
            row.hole_count_y,
            row.col_pitch,
            row.row_pitch,
            row.remarks,
        ]):
            rows.append(row)

    if not rows:
        rows.append(SplicePlateRow())

    # ついでにデバッグ用ログも
    current_app.logger.debug(
        "[splice] rows count=%d, sample=%r",
        len(rows),
        rows[0] if rows else None,
    )

    return rows

def _build_context(layout_profile: dict) -> dict:
    form = request.form if request.method == "POST" else {}

    def val(name: str, default: str = "") -> str:
        return form.get(name, default)

    rows = _build_rows_from_request()

    steel_lists = load_steel_lists()
    h_steel_sizes: List[str] = []
    # steel_lists["H型鋼"] が dict {"H-100x50x5x7": 26.67, ...} という前提
    h_section = steel_lists.get("H型鋼")
    if isinstance(h_section, dict):
        h_steel_sizes = list(h_section.keys())
    else:
        current_app.logger.warning(
            "[splice] steel_lists.json の 'H型鋼' セクションが dict ではありません"
        )

    ctx = {
        "layout_profile": layout_profile,
        "profile_key": layout_profile["key"],
        # ★ 追加: レイアウト一覧（key → ラベル）
        "layout_profiles": {k: p.label for k, p in LAYOUT_PROFILES.items()},
        "project_name": val("project_name"),
        "order_date": val("order_date"),
        "delivery_date": val("delivery_date"),
        "delivery_place": val("delivery_place"),
        "chief_name": val("chief_name"),
        "company_name": val("company_name"),
        "tel": val("tel"),
        "fax": val("fax"),
        "email": val("email"),
        "web_url": val("web_url"),
        # common / flange / web settings (print_mode 用に保持)
        "h_end_pitch_mm": val("h_end_pitch_mm"),
        "pl_end_pitch_mm": val("pl_end_pitch_mm"),
        "web_end_pitch_mm": val("web_end_pitch_mm"),
        "websp_x_end_pitch_mm": val("websp_x_end_pitch_mm"),
        "websp_y_end_pitch_mm": val("websp_y_end_pitch_mm"),
        "clearance_mm": val("clearance_mm"),
        "flange_hole_dia_mm": val("flange_hole_dia_mm"),
        "flange_col_pitch_mm": val("flange_col_pitch_mm"),
        "flange_hole_count_x": val("flange_hole_count_x"),
        "flange_row_pitch_mm": val("flange_row_pitch_mm"),
        "flange_row_edge_mm": val("flange_row_edge_mm"),
        "flange_hole_count_y": val("flange_hole_count_y"),
        "web_hole_dia_mm": val("web_hole_dia_mm"),
        "web_col_pitch_mm": val("web_col_pitch_mm"),
        "web_hole_count_x": val("web_hole_count_x"),
        "web_row_pitch_mm": val("web_row_pitch_mm"),
        "web_hole_count_y": val("web_hole_count_y"),
        "drag_session_id": val("drag_session_id"),
        "hole_cross_enabled": val("hole_cross_enabled"),
        "dim_font_mm": val("dim_font_mm"),
        "rows": rows,
        "steel_sizes": h_steel_sizes,  # ★ ここでテンプレートへ渡す
        # ★ 追加: JS 用のプリセット JSON
        "splice_presets_json": json.dumps(SPLICE_PRESETS, ensure_ascii=False),
    }
    return ctx

@splice_plate_order_bp.route("/", methods=["GET", "POST"])
def splice_plate_order_index():
    layout_profile = _get_layout_profile_from_request()
    context = _build_context(layout_profile)

    # デフォルトは編集モード
    print_mode = False

    # ★ ベースとなる値（プロファイル側に将来持たせる場合も一旦ここで拾う）
    end_pitch_mm = context.get("end_pitch_mm", DEFAULT_SP_END_PITCH_MM)
    clearance_mm = context.get("clearance_mm", DEFAULT_SP_CLEARANCE_MM)

    if request.method == "POST":
        form = request.form
        action = form.get("action", "")

        current_app.logger.debug(
            "[splice]/ index POST action=%s, rows=%d",
            action, len(context.get("rows", []))
        )

        # ★ フォームから上書き（数値変換に失敗したらデフォルトのまま）
        v = form.get("end_pitch_mm", "").strip()
        if v:
            try:
                end_pitch_mm = int(v)
            except ValueError:
                current_app.logger.warning(
                    "[splice] invalid end_pitch_mm=%r, use default=%d",
                    v, end_pitch_mm,
                )

        v = form.get("clearance_mm", "").strip()
        if v:
            try:
                clearance_mm = int(v)
            except ValueError:
                current_app.logger.warning(
                    "[splice] invalid clearance_mm=%r, use default=%d",
                    v, clearance_mm,
                )

        # 印刷プレビュー用ボタンから来た POST のときだけ印刷モード
        if action == "print_preview":
            print_mode = True

    # ★ テンプレートに渡す
    context["end_pitch_mm"] = end_pitch_mm
    context["clearance_mm"] = clearance_mm

    return render_template(
        "splice_plate_order/index.html",
        **context,
        print_mode=print_mode,
    )
