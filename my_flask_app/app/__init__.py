import logging
import os
from importlib import import_module
from pathlib import Path

from dotenv import load_dotenv
from flask import Blueprint, Flask, render_template
from jinja2 import ChoiceLoader, FileSystemLoader


BLUEPRINT_LABELS = {
    "column": "コラム断面",
    "shs": "□パイプ断面",
    "chs": "〇パイプ断面",
    "h_section": "H型鋼断面",
    "angle": "山形鋼断面",
    "channel": "溝形鋼断面",
    "ibeam": "Iビーム断面",
    "lipchannel": "リップ溝形鋼",
    "gusset_flange": "ガセットプレート(伏)",
    "gusset_web": "ガセットプレート(軸)",
    "gusset_type": "ガセットプレート(型)",
    "h_flange_steel": "H型鋼大梁継手フランジ面",
    "h_flange_pin": "H型鋼小梁継手フランジ面",
    "h_web_steel": "H型鋼大梁継手ウェブ面",
    "h_web_pin": "H型鋼小梁継手ウェブ面",
    "steel_materials_order": "鋼材注文書",
    "splice_plate_order": "スプライスプレート制作指示書",
    "estimate_document": "鉄骨建築用見積書作成",
}

BLUEPRINT_ORDER = [
    "column",
    "shs",
    "chs",
    "h_section",
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
    module_prefix = f"{__name__}.blueprints"
    registered = 0

    for routes_path in sorted(root.glob("**/routes.py")):
        rel_parts = routes_path.relative_to(root).with_suffix("").parts
        module_name = ".".join([module_prefix, *rel_parts])

        module = import_module(module_name)
        bp = getattr(module, "bp", None)
        if not isinstance(bp, Blueprint):
            app.logger.warning("Skip %s: 'bp' が Blueprint ではありません。", module_name)
            continue
        app.register_blueprint(bp)
        registered += 1

    if registered == 0:
        raise RuntimeError("Blueprint が 1 件も登録されませんでした。")
    app.logger.info("Blueprint 自動登録: %d 件", registered)


def _build_home_pages(app: Flask) -> list[tuple[str, str]]:
    pages: list[tuple[str, str]] = []

    for bp_name in BLUEPRINT_ORDER:
        bp = app.blueprints.get(bp_name)
        if not bp or not bp.url_prefix:
            continue
        label = BLUEPRINT_LABELS.get(bp_name, bp_name)
        pages.append((label, f"{bp.url_prefix.rstrip('/')}/"))

    pages.append(("説明スライドを確認", "/slides/"))
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
        return render_template("home.html", pages=_build_home_pages(app))

    return app
