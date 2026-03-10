import os

# ==========================
# アプリ定義
# ==========================

sections = [
    "column",
    "shs",
    "chs",
    "angle",
    "channel",
    "ibeam",
    "lipchannel",
    "h_section"
]

plates = [
    "gusset_flange",
    "gusset_web",
    "gusset_type"
]

beams = [
    "h_flange_steel",
    "h_flange_pin",
    "h_web_steel",
    "h_web_pin"
]

documents = [
    "steel_materials_order",
    "splice_plate_order",
    "estimate_document"
]


# ==========================
# 共通ファイル
# ==========================

ROUTES_TEMPLATE = """from flask import Blueprint, render_template

bp = Blueprint("{name}", __name__, url_prefix="/{name}")

@bp.route("/")
def index():
    return render_template("{name}.html")
"""

LOGIC_TEMPLATE = """# business logic here
"""


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<title>{name}</title>
</head>
<body>
<h1>{name}</h1>
</body>
</html>
"""


# ==========================
# 作成関数
# ==========================

def create_app(path, name):

    os.makedirs(path + "/templates", exist_ok=True)

    with open(f"{path}/routes.py", "w") as f:
        f.write(ROUTES_TEMPLATE.format(name=name))

    with open(f"{path}/logic.py", "w") as f:
        f.write(LOGIC_TEMPLATE)

    with open(f"{path}/templates/{name}.html", "w") as f:
        f.write(HTML_TEMPLATE.format(name=name))


# ==========================
# ディレクトリ生成
# ==========================

base = "app/blueprints"

for name in sections:
    create_app(f"{base}/cad/sections/{name}", name)

for name in plates:
    create_app(f"{base}/cad/plates/{name}", name)

for name in beams:
    create_app(f"{base}/cad/beams/{name}", name)

for name in documents:
    create_app(f"{base}/documents/{name}", name)


# その他ディレクトリ

dirs = [
    "app/api",
    "app/data",
    "app/errors",
    "app/extensions",
    "app/logic",
    "app/models",
    "app/services",
    "app/utils",
    "app/templates",
    "app/static/css",
    "app/static/img",
    "instance",
    "logs",
    "migrations"
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

print("Project structure created!")