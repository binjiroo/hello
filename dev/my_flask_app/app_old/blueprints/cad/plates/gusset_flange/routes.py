from flask import Blueprint, render_template

bp = Blueprint("gusset_flange_legacy", __name__, url_prefix="/gusset_flange_legacy")

@bp.route("/")
def index():
    return render_template("gusset_flange.html")
