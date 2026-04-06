from flask import Blueprint

import sys
from pathlib import Path

app_root = Path(__file__).resolve().parents[5]
if str(app_root) not in sys.path:
    sys.path.insert(0, str(app_root))

from app import estimate_document_app as estimate_document_app_module

bp = Blueprint("estimate_document", __name__, url_prefix="/estimate_document")


@bp.route("/", methods=["GET", "POST"])
def index():
    return estimate_document_app_module.index()
