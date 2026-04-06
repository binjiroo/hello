from flask import Blueprint

import sys
from pathlib import Path

app_root = Path(__file__).resolve().parents[5]
if str(app_root) not in sys.path:
    sys.path.insert(0, str(app_root))

from app import splice_plate_order_app as splice_plate_order_app_module

bp = Blueprint("splice_plate_order", __name__, url_prefix="/splice_plate_order")


@bp.route("/", methods=["GET", "POST"])
def index():
    return splice_plate_order_app_module.splice_plate_order_index()
