import logging
import os

from flask import Flask, render_template

PAGE_LABELS = {
    "angle_size": "山形鋼",
    "chs_size": "丸パイプ",
    "column_size": "コラム断面",
    "h_size": "H形鋼",
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _register_blueprints(app: Flask) -> None:
    from importlib import import_module
    from pathlib import Path

    app_root = Path(__file__).resolve().parent

    for package_root in ("blueprint", "blueprints"):
        root = app_root / package_root
        if not root.exists():
            continue

        for routes_path in sorted(root.glob("**/routes.py")):
            rel_parts = routes_path.relative_to(root).with_suffix("").parts
            module_name = ".".join(["app", package_root, *rel_parts])
            module = import_module(module_name)
            bp = getattr(module, "bp", None)
            if bp is None or bp.name in app.blueprints:
                continue
            app.register_blueprint(bp)
            logger.info("Registered blueprint %s at %s", bp.name, bp.url_prefix)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(24)

    _register_blueprints(app)

    @app.route("/", endpoint="home")
    def home():
        pages = []
        for name, bp in app.blueprints.items():
            if not bp.url_prefix:
                continue
            label = PAGE_LABELS.get(name.removesuffix("_api"), name)
            pages.append((label, f"{bp.url_prefix.rstrip('/')}/"))
        pages.sort(key=lambda item: item[0])
        return render_template("home.html", pages=pages)

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    @app.errorhandler(404)
    def not_found(_error):
        return "404 Not Found", 404

    return app




PAGE_LABELS["ibeam_size"] = "Iビーム断面"
