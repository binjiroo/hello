import os

from flask import Flask, render_template


def _register_blueprints(app: Flask) -> None:
    from importlib import import_module
    from pathlib import Path

    root = Path(__file__).resolve().parent / "blueprints"
    if not root.exists():
        return

    for routes_path in sorted(root.glob("**/routes.py")):
        rel_parts = routes_path.relative_to(root).with_suffix("").parts
        module_name = ".".join(["app", "blueprints", *rel_parts])
        module = import_module(module_name)
        bp = getattr(module, "bp", None)
        if bp is not None:
            app.register_blueprint(bp)


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
            pages.append((name, f"{bp.url_prefix.rstrip('/')}/"))
        pages.sort(key=lambda item: item[0])
        return render_template("home.html", pages=pages)

    return app
