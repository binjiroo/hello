from flask import Blueprint, render_template

bp = Blueprint("splice_plate_order", __name__, url_prefix="/splice_plate_order")

@bp.route("/")
def index():
    return render_template("splice_plate_order.html")
