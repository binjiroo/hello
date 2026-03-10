from flask import Blueprint, render_template

bp = Blueprint("ibeam", __name__, url_prefix="/ibeam")

@bp.route("/")
def index():
    return render_template("ibeam.html")
