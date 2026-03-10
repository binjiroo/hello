# my_flask_app/app/__init__.py
import os
import logging
from flask import Flask, render_template
from dotenv import load_dotenv

def create_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(basedir, '..', '.env'))
    app = Flask(__name__)

    # ログ設定: 標準出力にDEBUG以上を出力
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)

    # ① 環境変数から読み込む（本番運用向け）
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))

    # 各モジュール（Blueprint）の登録
    from .column_size_app import column_size_bp
    from .shs_size_app import shs_size_bp
    from .chs_size_app import chs_size_bp
    from .angle_size_app import angle_size_bp
    from .cannel_size_app import cannel_size_bp
    from .ibeam_size_app import ibeam_size_bp
    from .lipcannel_size_app import lipcannel_size_bp
    from .gusset_flange_plate_app import gusset_flange_plate_bp
    from .gusset_web_plate_app import gusset_web_plate_bp
    from .gusset_type_app import gusset_type_bp
    from .h_size_app import h_size_bp
    from .h_flange_steeljoint_app import h_flange_steeljoint_bp
    from .h_flange_pinjoint_app import h_flange_pinjoint_bp
    from .h_web_steeljoint_app import h_web_steeljoint_bp
    from .h_web_pinjoint_app import h_web_pinjoint_bp
    from .steel_materials_order_app import steel_order_bp
    from .splice_plate_order_app import splice_plate_order_bp
    from .estimate_document_app import estimate_document_bp

    app.register_blueprint(column_size_bp,      url_prefix='/column_size')
    app.register_blueprint(shs_size_bp,      url_prefix='/shs_size')
    app.register_blueprint(chs_size_bp,      url_prefix='/chs_size')
    app.register_blueprint(h_size_bp,           url_prefix='/h_size')
    app.register_blueprint(angle_size_bp,      url_prefix='/angle_size')
    app.register_blueprint(cannel_size_bp,      url_prefix='/cannel_size')
    app.register_blueprint(ibeam_size_bp,      url_prefix='/ibeam_size')
    app.register_blueprint(lipcannel_size_bp,      url_prefix='/lipcannel_size')
    app.register_blueprint(gusset_flange_plate_bp,     url_prefix='/gusset_flange_plate')
    app.register_blueprint(gusset_web_plate_bp,     url_prefix='/gusset_web_plate')
    app.register_blueprint(gusset_type_bp,     url_prefix='/gusset_type')
    app.register_blueprint(h_flange_steeljoint_bp, url_prefix='/h_flange_steeljoint')
    app.register_blueprint(h_flange_pinjoint_bp,   url_prefix='/h_flange_pinjoint')
    app.register_blueprint(h_web_steeljoint_bp, url_prefix='/h_web_steeljoint')
    app.register_blueprint(h_web_pinjoint_bp,   url_prefix='/h_web_pinjoint')
    app.register_blueprint(steel_order_bp, url_prefix='/steel_materials_order')
    app.register_blueprint(splice_plate_order_bp, url_prefix='/splice_plate_order')
    app.register_blueprint(estimate_document_bp, url_prefix='/estimate_document')
    ppt_base = os.environ.get('PPT_EMBED_BASE')
    if not ppt_base:
        app.logger.warning("PPT_EMBED_BASE が未設定です。開発用ダミーURLを使用します。")
        ppt_base = 'https://onedrive.live.com/embed?resid=REPLACE_ME&em=2&wdAr=1.7777'
    app.config['PPT_EMBED_BASE'] = ppt_base

    @app.route('/slides/', defaults={'index': 1})
    @app.route('/slides/<int:index>')
    def slides(index):
        # 総スライド数（任意）: 不明なら None のままでOK。あるなら入力チェックに使う
        total = 20  # 分かっていれば正しい枚数に
        if total and (index < 1 or index > total):
            index = 1
        ppt_embed_base = app.config['PPT_EMBED_BASE']
        # PowerPoint Online は 1 始まり
        return render_template('slides_embed.html',
                               index=index,
                               total=total,
                               ppt_embed_base=ppt_embed_base)

    @app.route('/', endpoint='home')
    def home():
        # 各ページ名とURLパスのリスト
        pages = [
            ("コラム断面", "/column_size/"),
            ("□パイプ断面", "/shs_size/"),
            ("〇パイプ断面", "/chs_size/"),
            ("H型鋼断面", "/h_size/"),
            ("山形鋼断面", "/angle_size/"),
            ("溝形鋼断面", "/cannel_size/"),
            ("Iビーム断面", "/ibeam_size/"),
            ("リップ溝形鋼", "/lipcannel_size/"),
            ("ガセットプレート(伏)", "/gusset_flange_plate/"),
            ("ガセットプレート(軸)", "/gusset_web_plate/"),
            ("ガセットプレート(型)", "/gusset_type/"),
            ("H型鋼大梁継手フランジ面", "/h_flange_steeljoint/"),
            ("H型鋼小梁継手フランジ面", "/h_flange_pinjoint/"),
            ("H型鋼大梁継手ウェーブ面", "/h_web_steeljoint/"),
            ("H型鋼小梁継手ウェーブ面", "/h_web_pinjoint/"),
            ("鋼材注文書", "/steel_materials_order/"),
            ("スプライスプレート制作指示書", "/splice_plate_order/"),
            ("鉄骨建築用見積書作成", "/estimate_document/"),
            ("説明スライドを確認", "/slides/1"),
        ]
        return render_template('home.html', pages=pages)

    return app
