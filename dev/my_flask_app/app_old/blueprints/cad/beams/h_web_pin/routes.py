from flask import Blueprint, render_template

bp = Blueprint("h_web_pin", __name__, url_prefix="/h_web_pin")

@bp.route("/")
def index():
    return render_template("h_web_pin.html")
