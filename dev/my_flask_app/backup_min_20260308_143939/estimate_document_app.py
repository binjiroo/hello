from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import datetime
import json
import re
from typing import List

from flask import Blueprint, render_template, request


estimate_document_bp = Blueprint(
    "estimate_document",
    __name__,
    template_folder="templates/estimate_document",
)


DOC_TYPES = [
    ("quotation_submit", "見積書(提出用)"),
    ("quotation_internal", "見積書(社内用)"),
    ("detail_submit", "見積明細書(提出用)"),
    ("detail_internal", "見積明細書(社内用)"),
    ("material_internal", "材料費詳細(社内用)"),
    ("outsource_internal", "外注1次加工費詳細(社内用)"),
    ("factory_labor_internal", "工場加工人工詳細(社内用)"),
    ("site_labor_internal", "現場作業人工詳細(社内用)"),
    ("zinc_internal", "亜鉛メッキ詳細(社内用)"),
]

DEFAULT_DOC_TYPE = DOC_TYPES[0][0]


@dataclass
class EstimateLine:
    description: str = ""
    quantity: str = ""
    unit: str = ""
    unit_price: str = ""
    discount: str = ""
    tax_rate: str = "10"
    line_total: str = ""


@dataclass
class PrintLine:
    no: int
    description: str
    quantity: str
    unit: str
    unit_price: str
    discount: str
    tax_rate: str
    line_total: str


@dataclass
class DetailLine:
    description: str = ""
    quantity: str = ""
    unit: str = ""
    weight_kg: str = ""
    unit_price: str = ""
    amount: str = ""


@dataclass
class DetailPrintLine:
    no: int
    description: str
    quantity: str
    unit: str
    weight_kg: str
    unit_price: str
    amount: str


DETAIL_CONTENT_OPTIONS = [
    "材料費",
    "1次加工費",
    "2次加工費",
    "現場作業費",
    "ベースプレート製作費",
    "ガセットプレート製作費",
    "プレート製作費",
    "ブレース製作費",
    "ボルト代",
    "亜鉛メッキ代",
    "塗装費",
    "タッチアップ代",
    "レッカー代",
    "運搬費",
    "図面製作費",
    "諸経費",
]

DETAIL_UNIT_OPTIONS = [
    "人工",
    "本",
    "個",
    "式",
    "t",
    "kg",
    "日",
    "回",
]

MATERIAL_CONTENT_PRESETS = {
    "H型鋼(細幅)": ["H-200x100x5.5x8"],
    "H型鋼(中幅)": ["H-250x125x6x9"],
    "H型鋼(広幅)": ["H-400x200x8x13"],
    "H型鋼(軽量)": ["LH-150x75x5x7"],
    "コラム": ["C-300x300x10x15"],
    "SHS角形鋼管": ["SHS-150x150x6"],
    "CHS鋼管": ["CHS-139.8x4.5"],
    "山型鋼": ["L-65x65x6"],
    "溝型鋼": ["C-100x50x20x3.2"],
    "Iビーム": ["I-200x100x7x10"],
    "リップ溝型鋼": ["LC-100x50x20x2.3"],
    "ブレース": ["PL-12x75"],
    "プレート": ["PL-9x150x300"],
}

MATERIAL_UNIT_OPTIONS = [
    "数量",
    "個数",
    "本数",
    "枚数",
    "個",
    "本",
    "枚",
]

OUTSOURCE_UNIT_OPTIONS = [
    "本",
    "回",
    "個",
    "孔",
    "ヶ所",
]
OUTSOURCE_CONTENT_OPTIONS = [
    "柱切断",
    "柱開先加工",
    "梁切断",
    "梁開先加工",
    "梁孔加工",
    "ベースプレート作成",
    "ダイヤフラム作成",
    "ガセットプレート作成",
    "ブレース用ガセットプレート作成",
    "プレート作成",
]

FACTORY_CONTENT_OPTIONS = [
    "ベースプレート仮付け",
    "ベースプレート本付け",
    "トッププレート仮付け",
    "トッププレート本付け",
    "ガセットプレート仮付け",
    "ガセットプレート本付け",
    "コラム用裏当仮付け",
    "コラム用裏当本付け",
    "H型鋼用裏当仮付け",
    "H型鋼用裏当本付け",
    "ブレース用ガセットプレート仮付け",
    "ブレース用ガセットプレート本付け",
    "2つ孔ピース仮付け",
    "2つ孔ピース本付け",
    "窓枠ピース仮付け",
    "窓枠ピース本付け",
]

FACTORY_UNIT_OPTIONS = [
    "本",
    "回",
    "個",
    "枚",
    "ヶ所",
]

SITE_CONTENT_OPTIONS = [
    "柱建方",
    "梁建方",
    "ブレース取付",
    "胴縁取付",
    "母屋取付",
    "ボルト本締め",
    "タッチアップ",
    "レッカー使用日数",
    "運搬回数",
    "作業人数",
]

SITE_UNIT_OPTIONS = [
    "本",
    "回",
    "個",
    "枚",
    "ヶ所",
]

ZINC_UNIT_OPTIONS = [
    "本",
    "回",
    "個",
    "枚",
    "ヶ所",
]


@dataclass
class MaterialLine:
    description: str = ""
    quantity: str = ""
    unit: str = ""
    weight_kg: str = ""
    unit_price: str = ""
    amount: str = ""


@dataclass
class MaterialPrintLine:
    no: int
    description: str
    quantity: str
    unit: str
    weight_kg: str
    unit_price: str
    amount: str


@dataclass
class OutsourceLine:
    description: str = ""
    quantity: str = ""
    unit: str = ""
    weight_kg: str = ""
    unit_price: str = ""
    amount: str = ""


@dataclass
class OutsourcePrintLine:
    no: int
    description: str
    quantity: str
    unit: str
    weight_kg: str
    unit_price: str
    amount: str


@dataclass
class FactoryLine:
    description: str = ""
    quantity: str = ""
    unit: str = ""
    time_per_min: str = ""
    time_total_min: str = ""
    man_days: str = ""


@dataclass
class FactoryPrintLine:
    no: int
    description: str
    quantity: str
    unit: str
    time_per_min: str
    time_total_min: str
    man_days: str


@dataclass
class SiteLine:
    description: str = ""
    quantity: str = ""
    unit: str = ""
    time_per_min: str = ""
    time_total_min: str = ""
    man_days: str = ""


@dataclass
class SitePrintLine:
    no: int
    description: str
    quantity: str
    unit: str
    time_per_min: str
    time_total_min: str
    man_days: str


@dataclass
class ZincLine:
    description: str = ""
    quantity: str = ""
    unit: str = ""
    weight_kg: str = ""
    unit_price: str = ""
    amount: str = ""


@dataclass
class ZincPrintLine:
    no: int
    description: str
    quantity: str
    unit: str
    weight_kg: str
    unit_price: str
    amount: str


def _to_decimal(raw: str) -> Decimal:
    s = (raw or "").replace(",", "").strip()
    if not s:
        return Decimal("0")
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _yen_round(value: Decimal) -> Decimal:
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def _fmt_yen(raw: str) -> str:
    value = _to_decimal(raw)
    return f"{int(_yen_round(value)):,}"


def _fmt_number(raw: str) -> str:
    value = _to_decimal(raw)
    if value == value.to_integral():
        return f"{int(value)}"
    return f"{value.normalize()}"


def _fmt_date_ja(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return f"{dt.year}/{dt.month:02d}/{dt.day:02d}"
    except ValueError:
        return s


def _collect_note_lines(prefix: str) -> List[str]:
    if request.method != "POST":
        return ["", "", "", ""]

    pattern = re.compile(rf"^{re.escape(prefix)}_note_(\d+)$")
    indexed = []
    for key in request.form.keys():
        m = pattern.match(key)
        if not m:
            continue
        idx = int(m.group(1))
        indexed.append((idx, request.form.get(key, "")))
    if not indexed:
        return ["", "", "", ""]
    indexed.sort(key=lambda x: x[0])
    return [value for _, value in indexed]


def _build_lines_from_request() -> List[EstimateLine]:
    if request.method != "POST":
        return [EstimateLine()]

    descriptions = request.form.getlist("description[]")
    quantities = request.form.getlist("quantity[]")
    units = request.form.getlist("unit[]")
    unit_prices = request.form.getlist("unit_price[]")
    discounts = request.form.getlist("discount[]")
    tax_rates = request.form.getlist("tax_rate[]")

    max_len = max(
        len(descriptions),
        len(quantities),
        len(units),
        len(unit_prices),
        len(discounts),
        len(tax_rates),
        1,
    )

    lines: List[EstimateLine] = []
    for i in range(max_len):
        description = descriptions[i] if i < len(descriptions) else ""
        quantity = quantities[i] if i < len(quantities) else ""
        unit = units[i] if i < len(units) else ""
        unit_price = unit_prices[i] if i < len(unit_prices) else ""
        discount = discounts[i] if i < len(discounts) else ""
        tax_rate = tax_rates[i] if i < len(tax_rates) else "10"

        qty_dec = _to_decimal(quantity)
        unit_price_dec = _to_decimal(unit_price)
        discount_dec = _to_decimal(discount)
        line_total_dec = _yen_round((qty_dec * unit_price_dec) - discount_dec)
        if line_total_dec < 0:
            line_total_dec = Decimal("0")

        line = EstimateLine(
            description=description,
            quantity=quantity,
            unit=unit,
            unit_price=unit_price,
            discount=discount,
            tax_rate=tax_rate if tax_rate in {"10", "8", "0"} else "10",
            line_total=str(line_total_dec),
        )

        if any(
            [
                line.description,
                line.quantity,
                line.unit,
                line.unit_price,
                line.discount,
            ]
        ):
            lines.append(line)

    if not lines:
        lines.append(EstimateLine())
    return lines


def _calc_totals(lines: List[EstimateLine]) -> dict:
    taxable_10 = Decimal("0")
    taxable_8 = Decimal("0")
    taxable_0 = Decimal("0")

    for line in lines:
        amount = _to_decimal(line.line_total)
        if line.tax_rate == "8":
            taxable_8 += amount
        elif line.tax_rate == "0":
            taxable_0 += amount
        else:
            taxable_10 += amount

    tax_10 = _yen_round(taxable_10 * Decimal("0.10"))
    tax_8 = _yen_round(taxable_8 * Decimal("0.08"))
    consumption_tax = tax_10 + tax_8
    subtotal = taxable_10 + taxable_8 + taxable_0
    total = subtotal + consumption_tax

    return {
        "taxable_10": str(_yen_round(taxable_10)),
        "taxable_8": str(_yen_round(taxable_8)),
        "taxable_0": str(_yen_round(taxable_0)),
        "tax_excluded_amount": str(_yen_round(subtotal)),
        "consumption_tax": str(_yen_round(consumption_tax)),
        "subtotal": str(_yen_round(subtotal)),
        "total": str(_yen_round(total)),
    }


def _build_print_lines(lines: List[EstimateLine]) -> List[PrintLine]:
    result: List[PrintLine] = []
    for idx, line in enumerate(lines, start=1):
        result.append(
            PrintLine(
                no=idx,
                description=line.description,
                quantity=_fmt_number(line.quantity),
                unit=line.unit,
                unit_price=_fmt_yen(line.unit_price),
                discount=_fmt_yen(line.discount),
                tax_rate=line.tax_rate,
                line_total=_fmt_yen(line.line_total),
            )
        )
    return result


def _build_detail_lines_from_request() -> List[DetailLine]:
    if request.method != "POST":
        return [DetailLine()]

    descriptions = request.form.getlist("detail_description[]")
    quantities = request.form.getlist("detail_quantity[]")
    units = request.form.getlist("detail_unit[]")
    weights = request.form.getlist("detail_weight_kg[]")
    unit_prices = request.form.getlist("detail_unit_price[]")

    max_len = max(len(descriptions), len(quantities), len(units), len(weights), len(unit_prices), 1)

    lines: List[DetailLine] = []
    for i in range(max_len):
        description = descriptions[i] if i < len(descriptions) else ""
        quantity = quantities[i] if i < len(quantities) else ""
        unit = units[i] if i < len(units) else ""
        weight_kg = weights[i] if i < len(weights) else ""
        unit_price = unit_prices[i] if i < len(unit_prices) else ""
        amount = str(_yen_round(_to_decimal(weight_kg) * _to_decimal(unit_price)))

        line = DetailLine(
            description=description,
            quantity=quantity,
            unit=unit,
            weight_kg=weight_kg,
            unit_price=unit_price,
            amount=amount,
        )
        if any([line.description, line.quantity, line.unit, line.weight_kg, line.unit_price]):
            lines.append(line)

    if not lines:
        lines.append(DetailLine())
    return lines


def _calc_detail_totals(lines: List[DetailLine], adjustment_raw: str) -> dict:
    subtotal = Decimal("0")
    for line in lines:
        subtotal += _to_decimal(line.amount)
    adjustment = _to_decimal(adjustment_raw)
    total = subtotal + adjustment
    return {
        "detail_subtotal": str(_yen_round(subtotal)),
        "detail_adjustment": str(_yen_round(adjustment)),
        "detail_total": str(_yen_round(total)),
    }


def _build_detail_print_lines(lines: List[DetailLine]) -> List[DetailPrintLine]:
    result: List[DetailPrintLine] = []
    for idx, line in enumerate(lines, start=1):
        result.append(
            DetailPrintLine(
                no=idx,
                description=line.description,
                quantity=_fmt_number(line.quantity),
                unit=line.unit,
                weight_kg=_fmt_number(line.weight_kg),
                unit_price=_fmt_yen(line.unit_price),
                amount=_fmt_yen(line.amount),
            )
        )
    return result


def _build_material_lines_from_request() -> List[MaterialLine]:
    if request.method != "POST":
        return [MaterialLine()]

    descriptions = request.form.getlist("material_description[]")
    quantities = request.form.getlist("material_quantity[]")
    units = request.form.getlist("material_unit[]")
    weights = request.form.getlist("material_weight_kg[]")
    unit_prices = request.form.getlist("material_unit_price[]")

    max_len = max(len(descriptions), len(quantities), len(units), len(weights), len(unit_prices), 1)
    lines: List[MaterialLine] = []
    for i in range(max_len):
        description = descriptions[i] if i < len(descriptions) else ""
        quantity = quantities[i] if i < len(quantities) else ""
        unit = units[i] if i < len(units) else ""
        weight_kg = weights[i] if i < len(weights) else ""
        unit_price = unit_prices[i] if i < len(unit_prices) else ""
        amount = str(_yen_round(_to_decimal(weight_kg) * _to_decimal(unit_price)))

        line = MaterialLine(
            description=description,
            quantity=quantity,
            unit=unit,
            weight_kg=weight_kg,
            unit_price=unit_price,
            amount=amount,
        )
        if any([line.description, line.quantity, line.unit, line.weight_kg, line.unit_price]):
            lines.append(line)

    if not lines:
        lines.append(MaterialLine())
    return lines


def _calc_material_totals(lines: List[MaterialLine], adjustment_raw: str) -> dict:
    subtotal = Decimal("0")
    for line in lines:
        subtotal += _to_decimal(line.amount)
    adjustment = _to_decimal(adjustment_raw)
    total = subtotal + adjustment
    return {
        "material_subtotal": str(_yen_round(subtotal)),
        "material_adjustment": str(_yen_round(adjustment)),
        "material_total": str(_yen_round(total)),
    }


def _build_material_print_lines(lines: List[MaterialLine]) -> List[MaterialPrintLine]:
    result: List[MaterialPrintLine] = []
    for idx, line in enumerate(lines, start=1):
        result.append(
            MaterialPrintLine(
                no=idx,
                description=line.description,
                quantity=_fmt_number(line.quantity),
                unit=line.unit,
                weight_kg=_fmt_number(line.weight_kg),
                unit_price=_fmt_yen(line.unit_price),
                amount=_fmt_yen(line.amount),
            )
        )
    return result


def _build_outsource_lines_from_request() -> List[OutsourceLine]:
    if request.method != "POST":
        return [OutsourceLine()]

    descriptions = request.form.getlist("outsource_description[]")
    quantities = request.form.getlist("outsource_quantity[]")
    units = request.form.getlist("outsource_unit[]")
    weights = request.form.getlist("outsource_weight_kg[]")
    unit_prices = request.form.getlist("outsource_unit_price[]")

    max_len = max(len(descriptions), len(quantities), len(units), len(weights), len(unit_prices), 1)
    lines: List[OutsourceLine] = []
    for i in range(max_len):
        description = descriptions[i] if i < len(descriptions) else ""
        quantity = quantities[i] if i < len(quantities) else ""
        unit = units[i] if i < len(units) else ""
        weight_kg = weights[i] if i < len(weights) else ""
        unit_price = unit_prices[i] if i < len(unit_prices) else ""
        amount = str(_yen_round(_to_decimal(quantity) * _to_decimal(unit_price)))

        line = OutsourceLine(
            description=description,
            quantity=quantity,
            unit=unit,
            weight_kg=weight_kg,
            unit_price=unit_price,
            amount=amount,
        )
        if any([line.description, line.quantity, line.unit, line.weight_kg, line.unit_price]):
            lines.append(line)

    if not lines:
        lines.append(OutsourceLine())
    return lines


def _calc_outsource_totals(lines: List[OutsourceLine], adjustment_raw: str) -> dict:
    subtotal = Decimal("0")
    for line in lines:
        subtotal += _to_decimal(line.amount)
    adjustment = _to_decimal(adjustment_raw)
    total = subtotal + adjustment
    return {
        "outsource_subtotal": str(_yen_round(subtotal)),
        "outsource_adjustment": str(_yen_round(adjustment)),
        "outsource_total": str(_yen_round(total)),
    }


def _build_outsource_print_lines(lines: List[OutsourceLine]) -> List[OutsourcePrintLine]:
    result: List[OutsourcePrintLine] = []
    for idx, line in enumerate(lines, start=1):
        result.append(
            OutsourcePrintLine(
                no=idx,
                description=line.description,
                quantity=_fmt_number(line.quantity),
                unit=line.unit,
                weight_kg=_fmt_number(line.weight_kg),
                unit_price=_fmt_yen(line.unit_price),
                amount=_fmt_yen(line.amount),
            )
        )
    return result


def _build_factory_lines_from_request() -> List[FactoryLine]:
    if request.method != "POST":
        return [FactoryLine()]

    descriptions = request.form.getlist("factory_description[]")
    quantities = request.form.getlist("factory_quantity[]")
    units = request.form.getlist("factory_unit[]")
    time_per_mins = request.form.getlist("factory_time_per_min[]")

    max_len = max(len(descriptions), len(quantities), len(units), len(time_per_mins), 1)
    lines: List[FactoryLine] = []
    for i in range(max_len):
        description = descriptions[i] if i < len(descriptions) else ""
        quantity = quantities[i] if i < len(quantities) else ""
        unit = units[i] if i < len(units) else ""
        time_per_min = time_per_mins[i] if i < len(time_per_mins) else ""
        time_total_min_dec = _to_decimal(quantity) * _to_decimal(time_per_min)
        time_total_min = str(_yen_round(time_total_min_dec))
        man_days = (time_total_min_dec / Decimal("480")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        line = FactoryLine(
            description=description,
            quantity=quantity,
            unit=unit,
            time_per_min=time_per_min,
            time_total_min=time_total_min,
            man_days=str(man_days),
        )
        if any([line.description, line.quantity, line.unit, line.time_per_min]):
            lines.append(line)

    if not lines:
        lines.append(FactoryLine())
    return lines


def _calc_factory_totals(lines: List[FactoryLine]) -> dict:
    total_minutes = Decimal("0")
    for line in lines:
        total_minutes += _to_decimal(line.time_total_min)
    total_hours = total_minutes / Decimal("60")
    total_man_days = total_hours / Decimal("8")
    return {
        "factory_total_minutes": str(_yen_round(total_minutes)),
        "factory_total_hours": str(total_hours.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "factory_total_man_days": str(total_man_days.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
    }


def _build_factory_print_lines(lines: List[FactoryLine]) -> List[FactoryPrintLine]:
    result: List[FactoryPrintLine] = []
    for idx, line in enumerate(lines, start=1):
        result.append(
            FactoryPrintLine(
                no=idx,
                description=line.description,
                quantity=_fmt_number(line.quantity),
                unit=line.unit,
                time_per_min=_fmt_number(line.time_per_min),
                time_total_min=_fmt_number(line.time_total_min),
                man_days=_fmt_number(line.man_days),
            )
        )
    return result


def _build_site_lines_from_request() -> List[SiteLine]:
    if request.method != "POST":
        return [SiteLine()]

    descriptions = request.form.getlist("site_description[]")
    quantities = request.form.getlist("site_quantity[]")
    units = request.form.getlist("site_unit[]")
    time_per_mins = request.form.getlist("site_time_per_min[]")

    max_len = max(len(descriptions), len(quantities), len(units), len(time_per_mins), 1)
    lines: List[SiteLine] = []
    for i in range(max_len):
        description = descriptions[i] if i < len(descriptions) else ""
        quantity = quantities[i] if i < len(quantities) else ""
        unit = units[i] if i < len(units) else ""
        time_per_min = time_per_mins[i] if i < len(time_per_mins) else ""
        time_total_min_dec = _to_decimal(quantity) * _to_decimal(time_per_min)
        time_total_min = str(_yen_round(time_total_min_dec))
        man_days = (time_total_min_dec / Decimal("480")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        line = SiteLine(
            description=description,
            quantity=quantity,
            unit=unit,
            time_per_min=time_per_min,
            time_total_min=time_total_min,
            man_days=str(man_days),
        )
        if any([line.description, line.quantity, line.unit, line.time_per_min]):
            lines.append(line)

    if not lines:
        lines.append(SiteLine())
    return lines


def _calc_site_totals(lines: List[SiteLine]) -> dict:
    total_minutes = Decimal("0")
    for line in lines:
        total_minutes += _to_decimal(line.time_total_min)
    total_hours = total_minutes / Decimal("60")
    total_man_days = total_hours / Decimal("8")
    return {
        "site_total_minutes": str(_yen_round(total_minutes)),
        "site_total_hours": str(total_hours.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "site_total_man_days": str(total_man_days.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
    }


def _build_site_print_lines(lines: List[SiteLine]) -> List[SitePrintLine]:
    result: List[SitePrintLine] = []
    for idx, line in enumerate(lines, start=1):
        result.append(
            SitePrintLine(
                no=idx,
                description=line.description,
                quantity=_fmt_number(line.quantity),
                unit=line.unit,
                time_per_min=_fmt_number(line.time_per_min),
                time_total_min=_fmt_number(line.time_total_min),
                man_days=_fmt_number(line.man_days),
            )
        )
    return result


def _build_zinc_lines_from_request() -> List[ZincLine]:
    if request.method != "POST":
        return [ZincLine()]

    descriptions = request.form.getlist("zinc_description[]")
    quantities = request.form.getlist("zinc_quantity[]")
    units = request.form.getlist("zinc_unit[]")
    weights = request.form.getlist("zinc_weight_kg[]")
    unit_prices = request.form.getlist("zinc_unit_price[]")

    max_len = max(len(descriptions), len(quantities), len(units), len(weights), len(unit_prices), 1)
    lines: List[ZincLine] = []
    for i in range(max_len):
        description = descriptions[i] if i < len(descriptions) else ""
        quantity = quantities[i] if i < len(quantities) else ""
        unit = units[i] if i < len(units) else ""
        weight_kg = weights[i] if i < len(weights) else ""
        unit_price = unit_prices[i] if i < len(unit_prices) else ""
        amount = str(_yen_round(_to_decimal(weight_kg) * _to_decimal(unit_price)))

        line = ZincLine(
            description=description,
            quantity=quantity,
            unit=unit,
            weight_kg=weight_kg,
            unit_price=unit_price,
            amount=amount,
        )
        if any([line.description, line.quantity, line.unit, line.weight_kg, line.unit_price]):
            lines.append(line)

    if not lines:
        lines.append(ZincLine())
    return lines


def _calc_zinc_totals(lines: List[ZincLine]) -> dict:
    total = Decimal("0")
    for line in lines:
        total += _to_decimal(line.amount)
    return {
        "zinc_total": str(_yen_round(total)),
    }


def _build_zinc_print_lines(lines: List[ZincLine]) -> List[ZincPrintLine]:
    result: List[ZincPrintLine] = []
    for idx, line in enumerate(lines, start=1):
        result.append(
            ZincPrintLine(
                no=idx,
                description=line.description,
                quantity=_fmt_number(line.quantity),
                unit=line.unit,
                weight_kg=_fmt_number(line.weight_kg),
                unit_price=_fmt_yen(line.unit_price),
                amount=_fmt_number(line.amount),
            )
        )
    return result


@estimate_document_bp.route("/", methods=["GET", "POST"])
def index():
    action = request.form.get("action", "") if request.method == "POST" else ""
    doc_type = request.form.get("doc_type", request.args.get("doc_type", DEFAULT_DOC_TYPE))
    valid_doc_types = {key for key, _ in DOC_TYPES}
    label_map = dict(DOC_TYPES)
    if doc_type not in valid_doc_types:
        doc_type = DEFAULT_DOC_TYPE

    lines = _build_lines_from_request()
    totals = _calc_totals(lines)
    print_lines = _build_print_lines(lines)
    detail_lines = _build_detail_lines_from_request()
    material_lines = _build_material_lines_from_request()
    outsource_lines = _build_outsource_lines_from_request()
    factory_lines = _build_factory_lines_from_request()
    site_lines = _build_site_lines_from_request()
    zinc_lines = _build_zinc_lines_from_request()

    form = request.form if request.method == "POST" else {}

    def val(name: str, default: str = "") -> str:
        return form.get(name, default)

    paper_orientation = val("paper_orientation", "portrait")
    if paper_orientation not in {"portrait", "landscape"}:
        paper_orientation = "portrait"
    print_page_height_mm = 210 if paper_orientation == "landscape" else 297

    print_mode = action in {"print_preview", "print", "printer_settings"}
    auto_print = action in {"print", "printer_settings"}
    detail_totals = _calc_detail_totals(detail_lines, val("detail_adjustment"))
    detail_print_lines = _build_detail_print_lines(detail_lines)
    material_totals = _calc_material_totals(material_lines, val("material_adjustment"))
    material_print_lines = _build_material_print_lines(material_lines)
    outsource_totals = _calc_outsource_totals(outsource_lines, val("outsource_adjustment"))
    outsource_print_lines = _build_outsource_print_lines(outsource_lines)
    factory_totals = _calc_factory_totals(factory_lines)
    factory_print_lines = _build_factory_print_lines(factory_lines)
    site_totals = _calc_site_totals(site_lines)
    site_print_lines = _build_site_print_lines(site_lines)
    zinc_totals = _calc_zinc_totals(zinc_lines)
    zinc_print_lines = _build_zinc_print_lines(zinc_lines)
    detail_note_lines = _collect_note_lines("detail")
    material_note_lines = _collect_note_lines("material")
    outsource_note_lines = _collect_note_lines("outsource")
    factory_note_lines = _collect_note_lines("factory")
    site_note_lines = _collect_note_lines("site")
    zinc_note_lines = _collect_note_lines("zinc")
    subject_value = (val("subject") or "").strip()
    estimate_no_value = (val("estimate_no") or "").strip()
    estimate_date_value = (val("estimate_date") or "").strip()
    if doc_type in {"detail_submit", "detail_internal", "material_internal", "outsource_internal", "factory_labor_internal", "site_labor_internal", "zinc_internal"} and not subject_value:
        subject_value = (val("detail_subject_fallback") or "").strip()
    if doc_type in {"detail_submit", "detail_internal", "material_internal", "outsource_internal", "factory_labor_internal", "site_labor_internal", "zinc_internal"} and not estimate_no_value:
        estimate_no_value = (val("detail_estimate_no_fallback") or "").strip()
    if doc_type in {"detail_submit", "detail_internal", "material_internal", "outsource_internal", "factory_labor_internal", "site_labor_internal", "zinc_internal"} and not estimate_date_value:
        estimate_date_value = (val("detail_estimate_date_fallback") or "").strip()
    customer_honorific = (val("customer_honorific", "様") or "").strip()
    if customer_honorific not in {"様", "御中"}:
        customer_honorific = "様"

    return render_template(
        "estimate_document/index.html",
        doc_types=DOC_TYPES,
        doc_type=doc_type,
        current_doc_label=label_map.get(doc_type, ""),
        print_mode=print_mode,
        auto_print=auto_print,
        printer_settings_mode=(action == "printer_settings"),
        paper_orientation=paper_orientation,
        print_page_height_mm=print_page_height_mm,
        lines=lines,
        detail_lines=detail_lines,
        detail_content_options=DETAIL_CONTENT_OPTIONS,
        detail_unit_options=DETAIL_UNIT_OPTIONS,
        detail_print_lines=detail_print_lines,
        detail_blank_print_rows=max(0, 12 - len(detail_print_lines)),
        detail_note_lines=detail_note_lines,
        detail_subtotal=detail_totals["detail_subtotal"],
        detail_adjustment=detail_totals["detail_adjustment"],
        detail_total=detail_totals["detail_total"],
        detail_subtotal_fmt=_fmt_yen(detail_totals["detail_subtotal"]),
        detail_adjustment_fmt=_fmt_yen(detail_totals["detail_adjustment"]),
        detail_total_fmt=_fmt_yen(detail_totals["detail_total"]),
        material_lines=material_lines,
        material_content_presets=MATERIAL_CONTENT_PRESETS,
        material_content_presets_json=json.dumps(MATERIAL_CONTENT_PRESETS, ensure_ascii=False),
        material_unit_options=MATERIAL_UNIT_OPTIONS,
        material_print_lines=material_print_lines,
        material_blank_print_rows=max(0, 12 - len(material_print_lines)),
        material_note_lines=material_note_lines,
        material_subtotal=material_totals["material_subtotal"],
        material_adjustment=material_totals["material_adjustment"],
        material_total=material_totals["material_total"],
        material_subtotal_fmt=_fmt_yen(material_totals["material_subtotal"]),
        material_adjustment_fmt=_fmt_yen(material_totals["material_adjustment"]),
        material_total_fmt=_fmt_yen(material_totals["material_total"]),
        outsource_lines=outsource_lines,
        outsource_content_options=OUTSOURCE_CONTENT_OPTIONS,
        outsource_unit_options=OUTSOURCE_UNIT_OPTIONS,
        outsource_print_lines=outsource_print_lines,
        outsource_blank_print_rows=max(0, 12 - len(outsource_print_lines)),
        outsource_note_lines=outsource_note_lines,
        outsource_subtotal=outsource_totals["outsource_subtotal"],
        outsource_adjustment=outsource_totals["outsource_adjustment"],
        outsource_total=outsource_totals["outsource_total"],
        outsource_subtotal_fmt=_fmt_yen(outsource_totals["outsource_subtotal"]),
        outsource_adjustment_fmt=_fmt_yen(outsource_totals["outsource_adjustment"]),
        outsource_total_fmt=_fmt_yen(outsource_totals["outsource_total"]),
        factory_lines=factory_lines,
        factory_content_options=FACTORY_CONTENT_OPTIONS,
        factory_unit_options=FACTORY_UNIT_OPTIONS,
        factory_print_lines=factory_print_lines,
        factory_blank_print_rows=max(0, 12 - len(factory_print_lines)),
        factory_note_lines=factory_note_lines,
        factory_total_minutes=factory_totals["factory_total_minutes"],
        factory_total_hours=factory_totals["factory_total_hours"],
        factory_total_man_days=factory_totals["factory_total_man_days"],
        site_lines=site_lines,
        site_content_options=SITE_CONTENT_OPTIONS,
        site_unit_options=SITE_UNIT_OPTIONS,
        site_print_lines=site_print_lines,
        site_blank_print_rows=max(0, 12 - len(site_print_lines)),
        site_note_lines=site_note_lines,
        site_total_minutes=site_totals["site_total_minutes"],
        site_total_hours=site_totals["site_total_hours"],
        site_total_man_days=site_totals["site_total_man_days"],
        zinc_lines=zinc_lines,
        zinc_content_presets=MATERIAL_CONTENT_PRESETS,
        zinc_content_presets_json=json.dumps(MATERIAL_CONTENT_PRESETS, ensure_ascii=False),
        zinc_unit_options=ZINC_UNIT_OPTIONS,
        zinc_print_lines=zinc_print_lines,
        zinc_blank_print_rows=max(0, 12 - len(zinc_print_lines)),
        zinc_note_lines=zinc_note_lines,
        zinc_total=zinc_totals["zinc_total"],
        print_lines=print_lines,
        blank_print_rows=max(0, (6 if paper_orientation == "landscape" else 8) - len(print_lines)),
        customer_name=val("customer_name"),
        customer_honorific=customer_honorific,
        subject=subject_value,
        delivery_due=val("delivery_due"),
        delivery_due_ja=_fmt_date_ja(val("delivery_due")),
        valid_until=val("valid_until"),
        valid_until_ja=_fmt_date_ja(val("valid_until")),
        payment_terms=val("payment_terms"),
        estimate_no=estimate_no_value,
        estimate_date=estimate_date_value,
        estimate_date_ja=_fmt_date_ja(estimate_date_value),
        company_name=val("company_name"),
        postal_code=val("postal_code"),
        address=val("address"),
        phone=val("phone"),
        fax=val("fax"),
        email=val("email"),
        taxable_10_fmt=_fmt_yen(totals["taxable_10"]),
        taxable_8_fmt=_fmt_yen(totals["taxable_8"]),
        taxable_0_fmt=_fmt_yen(totals["taxable_0"]),
        tax_excluded_amount_fmt=_fmt_yen(totals["tax_excluded_amount"]),
        consumption_tax_fmt=_fmt_yen(totals["consumption_tax"]),
        subtotal_fmt=_fmt_yen(totals["subtotal"]),
        total_fmt=_fmt_yen(totals["total"]),
        **totals,
    )
