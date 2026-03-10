from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # 各モジュールのBlueprintをインポートして登録する
    from .cannel_size_app import cannel_size_blueprint
    from .gusset_plate_app import gusset_plate_blueprint
    from .h_size_app import h_size_blueprint
    from .h_flange_steeljoint_app import h_flange_steeljoint_blueprint
    from .h_flange_pinjoint_app import h_flange_pinjoint_blueprint
    
    app.register_blueprint(cannel_size_blueprint, url_prefix='/cannel_size')
    app.register_blueprint(gusset_plate_blueprint, url_prefix='/gusset_plate')
    app.register_blueprint(h_size_blueprint, url_prefix='/h_size')
    app.register_blueprint(h_flange_steeljoint_blueprint, url_prefix='/h_flange_steeljoint')
    app.register_blueprint(h_flange_pinjoint_blueprint, url_prefix='/h_flange_pinjoint')
    
    return app
