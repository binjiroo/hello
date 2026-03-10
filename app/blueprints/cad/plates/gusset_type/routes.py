from flask import Blueprint, render_template

bp = Blueprint("gusset_type", __name__, url_prefix="/gusset_type")

@bp.route("/")
def index():
    return render_template("gusset_type.html")
