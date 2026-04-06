from flask import Blueprint

bp = Blueprint(
    "gusset_web_plate_api",
    __name__,
    url_prefix="/api/gusset_web_plate",
)

__all__ = ["bp"]
