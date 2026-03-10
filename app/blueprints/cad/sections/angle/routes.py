from flask import Blueprint, render_template

bp = Blueprint("angle", __name__, url_prefix="/angle")

@bp.route("/")
def index():
    return render_template("angle.html")
