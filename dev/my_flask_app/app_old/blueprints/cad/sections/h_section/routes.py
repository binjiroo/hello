from flask import Blueprint, redirect, url_for

bp = Blueprint("h_section", __name__, url_prefix="/h_section")

@bp.route("/")
def index():
    return redirect(url_for("h_size.index"))
