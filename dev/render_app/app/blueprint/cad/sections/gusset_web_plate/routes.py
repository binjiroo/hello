from pathlib import Path

from flask import render_template_string, request, session

from . import bp
from app.blueprint.api.gusset_web_plate.routes import (
    DEFAULT_VALUES,
    FILENAMES,
    STEEL_SIZES,
    build_gusset_web_plate_result,
)

TEMPLATE_SOURCE = (Path(__file__).with_name("templates") / "index.html").read_text(
    encoding="utf-8"
)


def _render_screen(**context):
    # Keep each blueprint on its own index.html while matching the Phase2 path rule.
    return render_template_string(TEMPLATE_SOURCE, **context)


def _get_defaults():
    return {key: session.get(key, value) for key, value in DEFAULT_VALUES.items()}


@bp.route("/", methods=("GET", "POST"))
def index():
    defaults = _get_defaults()
    result_str = ""
    error_msg = ""

    if request.method == "POST":
        action = request.form.get("action", "new")
        previous_result = request.form.get("prev_result", "")

        if action == "clear":
            session.clear()
            return _render_screen(
                filenames=FILENAMES,
                steel_sizes=STEEL_SIZES,
                defaults=_get_defaults(),
                result_str="",
                error_msg="",
            )

        for key, default in DEFAULT_VALUES.items():
            if key == "leader_follow":
                continue
            session[key] = request.form.get(key, defaults.get(key, default))
        session["leader_follow"] = (
            "1" if str(request.form.get("leader_follow", "")).lower() in {"1", "on", "true", "yes"} else ""
        )

        result_str, error_msg = build_gusset_web_plate_result(
            session,
            action=action,
            previous_result=previous_result,
        )
        defaults = _get_defaults()

    return _render_screen(
        filenames=FILENAMES,
        steel_sizes=STEEL_SIZES,
        defaults=defaults,
        result_str=result_str,
        error_msg=error_msg,
    )
