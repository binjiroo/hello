from flask import Blueprint, render_template

bp = Blueprint("h_web_steel", __name__, url_prefix="/h_web_steel")

@bp.route("/")
def index():
    return render_template("h_web_steel.html")
