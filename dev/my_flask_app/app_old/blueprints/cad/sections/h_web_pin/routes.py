from flask import Blueprint

import sys
from pathlib import Path

app_root = Path(__file__).resolve().parents[5]
if str(app_root) not in sys.path:
    sys.path.insert(0, str(app_root))

from app import h_web_pinjoint_app as h_web_pinjoint_app_module

bp = Blueprint("h_web_pin", __name__, url_prefix="/h_web_pin")


@bp.route("/", methods=["GET", "POST"])
def index():
    return h_web_pinjoint_app_module.index()
