from flask import Blueprint

bp = Blueprint(
    "gusset_web_plate",
    __name__,
    url_prefix="/cad/gusset_web_plate",
    template_folder="templates",
)

__all__ = ["bp"]
