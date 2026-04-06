from flask import Blueprint, render_template

bp = Blueprint("steel_materials_order", __name__, url_prefix="/steel_materials_order")

@bp.route("/")
def index():
    return render_template("steel_materials_order.html")
