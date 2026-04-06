from flask import Blueprint, render_template

bp = Blueprint("h_flange_steel", __name__, url_prefix="/h_flange_steel")

@bp.route("/")
def index():
    return render_template("h_flange_steel.html")
