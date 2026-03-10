from flask import Blueprint, render_template

bp = Blueprint("gusset_flange", __name__, url_prefix="/gusset_flange")

@bp.route("/")
def index():
    return render_template("gusset_flange.html")
