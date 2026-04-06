import logging
import os
from importlib import import_module
from pathlib import Path

from dotenv import load_dotenv
from flask import Blueprint, Flask, make_response, render_template
from jinja2 import ChoiceLoader, FileSystemLoader


BLUEPRINT_LABELS = {
    "column": "\u30b3\u30e9\u30e0\u65ad\u9762",
    "shs": "\u25a1\u30d1\u30a4\u30d7\u65ad\u9762",
    "chs": "\u3007\u30d1\u30a4\u30d7\u65ad\u9762",
    "h_size": "H\u578b\u92fc\u65ad\u9762",
    "angle": "\u5c71\u5f62\u92fc\u65ad\u9762",
    "channel": "\u6e9d\u5f62\u92fc\u65ad\u9762",
    "ibeam": "I\u30d3\u30fc\u30e0\u65ad\u9762",
    "lipchannel": "\u30ea\u30c3\u30d7\u578b\u6e9d\u5f62\u92fc\u65ad\u9762",
    "gusset_flange": "\u30ac\u30bb\u30c3\u30c8\u30d7\u30ec\u30fc\u30c8(\u30d5\u30e9\u30f3\u30b8\u9762)",
    "gusset_web": "\u30ac\u30bb\u30c3\u30c8\u30d7\u30ec\u30fc\u30c8(\u30a6\u30a7\u30d6\u9762)",
    "gusset_type": "\u30ac\u30bb\u30c3\u30c8\u30d7\u30ec\u30fc\u30c8(\u578b)",
    "h_flange_steel": "\u5927\u6881\u30d5\u30e9\u30f3\u30b8\u9762\u751f\u6210(\u30d6\u30e9\u30b1\u30c3\u30c8\u4ed8\u304d)",
    "h_flange_pin": "\u5c0f\u6881\u30d5\u30e9\u30f3\u30b8\u9762\u751f\u6210",
    "h_web_steel": "\u5927\u6881\u30a6\u30a7\u30d6\u9762\u751f\u6210(\u30d6\u30e9\u30b1\u30c3\u30c8\u4ed8\u304d)",
    "h_web_pin": "\u5c0f\u6881\u30a6\u30a7\u30d6\u9762\u751f\u6210",
    "steel_materials_order": "\u92fc\u6750\u6ce8\u6587\u66f8\u4f5c\u6210",
    "splice_plate_order": "\u30b9\u30d7\u30e9\u30a4\u30b9\u6ce8\u6587\u66f8\u4f5c\u6210",
    "estimate_document": "\u898b\u7a4d\u66f8\u4f5c\u6210",
}

BLUEPRINT_ORDER = [
    "column",
    "shs",
    "chs",
    "h_size",
    "angle",
    "channel",
    "ibeam",
    "lipchannel",
    "gusset_flange",
    "gusset_web",
    "gusset_type",
    "h_flange_steel",
    "h_flange_pin",
    "h_web_steel",
    "h_web_pin",
    "steel_materials_order",
    "splice_plate_order",
    "estimate_document",
]


def _configure_logging(app: Flask) -> None:
    if app.logger.handlers:
        return

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)


def _add_blueprint_template_paths(app: Flask, app_dir: Path) -> None:
    template_dirs = sorted(
        {str(path.parent) for path in app_dir.glob("blueprints/**/templates/*.html")}
    )
    if not template_dirs:
        return

    current_loader = app.jinja_loader
    extra_loader = FileSystemLoader(template_dirs)
    app.jinja_loader = (
        ChoiceLoader([extra_loader, current_loader])
        if current_loader
        else ChoiceLoader([extra_loader])
    )


def _register_blueprints(app: Flask, app_dir: Path) -> None:
    root = app_dir / "blueprints"
    excluded_prefixes = [
        root / "cad" / "plates",
        root / "cad" / "beams",
        root / "documents",
    ]
    module_prefix = f"{__name__}.blueprints"
    registered = 0

    for routes_path in sorted(root.glob("**/routes.py")):
        if any(prefix in routes_path.parents for prefix in excluded_prefixes):
            continue
        rel_parts = routes_path.relative_to(root).with_suffix("").parts
        module_name = ".".join([module_prefix, *rel_parts])

        module = import_module(module_name)
        bp = getattr(module, "bp", None)
        if not isinstance(bp, Blueprint):
            app.logger.warning("Skip %s: 'bp' is not a Blueprint", module_name)
            continue
        app.register_blueprint(bp)
        registered += 1

    if registered == 0:
        raise RuntimeError("No blueprints registered")
    app.logger.info("Blueprint registered: %d", registered)


def _build_home_pages(app: Flask) -> list[tuple[str, str]]:
    pages: list[tuple[str, str]] = []

    for bp_name in BLUEPRINT_ORDER:
        bp = app.blueprints.get(bp_name)
        if not bp or not bp.url_prefix:
            continue
        label = BLUEPRINT_LABELS.get(bp_name, bp_name)
        pages.append((label, f"{bp.url_prefix.rstrip('/')}/"))

    pages.append(("Slides", "/slides/"))
    return pages


def create_app() -> Flask:
    app_dir = Path(__file__).resolve().parent
    load_dotenv(app_dir.parent / ".env")

    app = Flask(__name__)
    _configure_logging(app)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(24))
    app.config["PPT_EMBED_BASE"] = os.environ.get(
        "PPT_EMBED_BASE",
        "https://onedrive.live.com/embed?resid=REPLACE_ME&em=2&wdAr=1.7777",
    )
    app.config["SLIDES_TOTAL"] = int(os.environ.get("SLIDES_TOTAL", "20"))

    _add_blueprint_template_paths(app, app_dir)
    _register_blueprints(app, app_dir)

    @app.route("/slides/", defaults={"index": 1})
    @app.route("/slides/<int:index>")
    def slides(index: int):
        total = app.config["SLIDES_TOTAL"]
        if total and (index < 1 or index > total):
            index = 1
        return render_template(
            "slides_embed.html",
            index=index,
            total=total,
            ppt_embed_base=app.config["PPT_EMBED_BASE"],
        )

    @app.route("/", endpoint="home")
    def home():
        response = make_response(render_template("home.html", pages=_build_home_pages(app)))
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        return response

    return app

