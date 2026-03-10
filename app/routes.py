from flask import Flask, render_template


BLUEPRINT_ORDER = [
    "column",
    "shs",
    "chs",
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

LABEL_OVERRIDES = {
    "h_section": "h_size",
}

HIDDEN_BLUEPRINTS = {
    "h_section",
}


def register_routes(app: Flask) -> None:
    @app.route("/", endpoint="home")
    def home() -> str:
        pages = []
        seen = set()

        for name in BLUEPRINT_ORDER:
            if name in HIDDEN_BLUEPRINTS:
                continue
            bp = app.blueprints.get(name)
            if not bp or not bp.url_prefix:
                continue
            label = LABEL_OVERRIDES.get(name, name)
            pages.append((label, f"{bp.url_prefix.rstrip('/')}/"))
            seen.add(name)

        for name in sorted(app.blueprints):
            if name in seen or name in HIDDEN_BLUEPRINTS:
                continue
            bp = app.blueprints.get(name)
            if not bp or not bp.url_prefix:
                continue
            label = LABEL_OVERRIDES.get(name, name)
            pages.append((label, f"{bp.url_prefix.rstrip('/')}/"))
        return render_template("home.html", pages=pages)
