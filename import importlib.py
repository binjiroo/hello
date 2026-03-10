import importlib
import pkgutil


def register_blueprints(app):

    package = "app.blueprints"

    for importer, module_name, ispkg in pkgutil.walk_packages(
        path=["app/blueprints"],
        prefix=package + "."
    ):

        if module_name.endswith("routes"):

            module = importlib.import_module(module_name)

            if hasattr(module, "bp"):
                app.register_blueprint(module.bp)