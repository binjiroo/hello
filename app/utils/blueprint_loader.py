import importlib
import pkgutil
from flask import Blueprint


def register_blueprints(app, package_name="app.blueprints"):
    """
    blueprints ディレクトリを再帰スキャンして
    routes.py 内の Blueprint を自動登録する
    """

    package = importlib.import_module(package_name)

    for finder, name, ispkg in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):

        # routes モジュールのみ対象
        if name.endswith(".routes"):

            module = importlib.import_module(name)

            for item_name in dir(module):

                item = getattr(module, item_name)

                if isinstance(item, Blueprint):
                    app.register_blueprint(item)