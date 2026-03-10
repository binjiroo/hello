from flask import Blueprint, render_template

bp = Blueprint("estimate_document", __name__, url_prefix="/estimate_document")

@bp.route("/")
def index():
    return render_template("estimate_document.html")
