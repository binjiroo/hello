from flask import Blueprint, render_template

bp = Blueprint("channel", __name__, url_prefix="/channel")

@bp.route("/")
def index():
    return render_template("channel.html")
