from flask import Blueprint

bp = Blueprint(
    "gusset_type",
    __name__,
    url_prefix="/cad/gusset_type",
    template_folder="templates",
)

__all__ = ["bp"]
