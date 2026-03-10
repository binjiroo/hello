from flask import Blueprint, render_template

bp = Blueprint("chs", __name__, url_prefix="/chs")

@bp.route("/")
def index():
    return render_template("chs.html")
