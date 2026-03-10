from flask import Blueprint, render_template

bp = Blueprint("column", __name__, url_prefix="/column")

@bp.route("/")
def index():
    return render_template("column.html")
