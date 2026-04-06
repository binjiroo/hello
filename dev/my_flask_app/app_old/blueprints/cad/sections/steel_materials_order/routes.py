from flask import Blueprint

import sys
from pathlib import Path

app_root = Path(__file__).resolve().parents[5]
if str(app_root) not in sys.path:
    sys.path.insert(0, str(app_root))

from app import steel_materials_order_app as steel_materials_order_app_module

bp = Blueprint("steel_materials_order", __name__, url_prefix="/steel_materials_order")


@bp.route("/", methods=["GET", "POST"])
def index():
    return steel_materials_order_app_module.index()
