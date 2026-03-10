from flask import Blueprint, render_template

bp = Blueprint("shs", __name__, url_prefix="/shs")

@bp.route("/")
def index():
    return render_template("shs.html")
