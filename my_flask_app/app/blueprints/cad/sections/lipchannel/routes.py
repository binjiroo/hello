from flask import Blueprint, render_template

bp = Blueprint("lipchannel", __name__, url_prefix="/lipchannel")

@bp.route("/")
def index():
    return render_template("lipchannel.html")
