import logging
from importlib import import_module
from pathlib import Path

from dotenv import load_dotenv
from flask import Blueprint, Flask, render_template
from jinja2 import ChoiceLoader, FileSystemLoader
from app.config import Config


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
    app.logger.setLevel(logging.INFO)


def _load_config(app: Flask) -> None:
    # Centralized config object for future environment-specific settings.
    app.config.from_object(Config)


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
    if not root.exists():
        app.logger.info("Blueprint directory not found: %s", root)
        return

    module_prefix = f"{__name__}.blueprints"
    registered = 0

    for routes_path in sorted(root.glob("**/routes.py")):
        rel_parts = routes_path.relative_to(root).with_suffix("").parts
        module_name = ".".join([module_prefix, *rel_parts])

        try:
            module = import_module(module_name)
        except Exception:
            app.logger.exception("Failed to import %s", module_name)
            continue

        bp = getattr(module, "bp", None)
        if not isinstance(bp, Blueprint):
            app.logger.warning("Skip %s: Blueprint instance 'bp' not found", module_name)
            continue

        app.register_blueprint(bp)
        registered += 1

    if registered == 0:
        app.logger.info("No blueprints were registered.")
    else:
        app.logger.info("Blueprint registered: %d", registered)


def _build_home_pages(app: Flask) -> list[tuple[str, str]]:
    pages: list[tuple[str, str]] = []

    for name, bp in app.blueprints.items():
        if not bp.url_prefix:
            continue
        pages.append((name, f"{bp.url_prefix.rstrip('/')}/"))

    pages.sort(key=lambda item: item[0])
    return pages


def _register_default_routes(app: Flask) -> None:
    if "home" in app.view_functions:
        return

    templates_dir = Path(app.root_path) / "templates"
    has_slides_template = (templates_dir / "slides_embed.html").exists()
    has_home_template = (templates_dir / "home.html").exists()

    if has_slides_template:

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

    if has_home_template:

        @app.route("/", endpoint="home")
        def home():
            return render_template("home.html", pages=_build_home_pages(app))


def create_app() -> Flask:
    app_dir = Path(__file__).resolve().parent
    load_dotenv(app_dir.parent / ".env")

    app = Flask(__name__)
    _configure_logging(app)
    _load_config(app)
    try:
        from app.routes import register_routes

        register_routes(app)
    except Exception:
        app.logger.exception("Failed to register app.routes")
    _add_blueprint_template_paths(app, app_dir)
    _register_blueprints(app, app_dir)
    _register_default_routes(app)
    return app
