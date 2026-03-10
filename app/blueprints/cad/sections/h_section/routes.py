from flask import Blueprint, render_template

bp = Blueprint("h_section", __name__, url_prefix="/h_section")

@bp.route("/")
def index():
    return render_template("h_section.html")
