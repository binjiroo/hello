# app/utils.py
from typing import Any

def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError, AttributeError):
        return default

def to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError, AttributeError):
        return default

# フォーム/セッション向けの薄いラッパ（任意）
def get_int(mapping: dict, key: str, default: int = 0) -> int:
    return to_int(mapping.get(key), default)

def get_float(mapping: dict, key: str, default: float = 0.0) -> float:
    return to_float(mapping.get(key), default)

def fmt2(n) -> str:
    """コード類を2桁ゼロ詰めで文字列化（安全にint化してから）"""
    try:
        return f"{int(str(n).strip()):02d}"
    except Exception:
        return "00"  # 好みで: 失敗時のデフォルト
