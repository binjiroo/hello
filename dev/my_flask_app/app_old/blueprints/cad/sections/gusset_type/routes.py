from flask import Blueprint

import sys
from pathlib import Path

app_root = Path(__file__).resolve().parents[5]
if str(app_root) not in sys.path:
    sys.path.insert(0, str(app_root))

from app import gusset_type_app as gusset_type_app_module

bp = Blueprint("gusset_type", __name__, url_prefix="/gusset_type")


@bp.route("/", methods=["GET", "POST"])
def index():
    return gusset_type_app_module.index()
