from flask import Blueprint

bp = Blueprint(
    "gusset_flange_plate_api",
    __name__,
    url_prefix="/api/gusset_flange_plate",
)

__all__ = ["bp"]
