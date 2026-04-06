from flask import Blueprint, render_template

bp = Blueprint("gusset_web", __name__, url_prefix="/gusset_web")

@bp.route("/")
def index():
    return render_template("gusset_web.html")
