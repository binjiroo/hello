from flask import Blueprint

bp = Blueprint(
    "gusset_type_api",
    __name__,
    url_prefix="/api/gusset_type",
)

__all__ = ["bp"]
