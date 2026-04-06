from flask import Blueprint, render_template

bp = Blueprint("h_flange_pin", __name__, url_prefix="/h_flange_pin")

@bp.route("/")
def index():
    return render_template("h_flange_pin.html")
