from flask import Blueprint

bp = Blueprint(
    "gusset_flange_plate",
    __name__,
    url_prefix="/cad/gusset_flange_plate",
    template_folder="templates",
)

__all__ = ["bp"]
