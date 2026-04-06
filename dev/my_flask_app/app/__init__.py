import logging
import os

from dotenv import load_dotenv
from flask import Flask, render_template

logger = logging.getLogger(__name__)


def create_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(basedir, '..', '.env'))

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))

    if not app.logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)

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

    app.register_blueprint(column_size_bp, url_prefix='/column_size')
    app.register_blueprint(shs_size_bp, url_prefix='/shs_size')
    app.register_blueprint(chs_size_bp, url_prefix='/chs_size')
    app.register_blueprint(h_size_bp, url_prefix='/h_size')
    app.register_blueprint(angle_size_bp, url_prefix='/angle_size')
    app.register_blueprint(cannel_size_bp, url_prefix='/cannel_size')
    app.register_blueprint(ibeam_size_bp, url_prefix='/ibeam_size')
    app.register_blueprint(lipcannel_size_bp, url_prefix='/lipcannel_size')
    app.register_blueprint(gusset_flange_plate_bp, url_prefix='/gusset_flange_plate')
    app.register_blueprint(gusset_web_plate_bp, url_prefix='/gusset_web_plate')
    app.register_blueprint(gusset_type_bp, url_prefix='/gusset_type')
    app.register_blueprint(h_flange_steeljoint_bp, url_prefix='/h_flange_steeljoint')
    app.register_blueprint(h_flange_pinjoint_bp, url_prefix='/h_flange_pinjoint')
    app.register_blueprint(h_web_steeljoint_bp, url_prefix='/h_web_steeljoint')
    app.register_blueprint(h_web_pinjoint_bp, url_prefix='/h_web_pinjoint')
    app.register_blueprint(steel_order_bp, url_prefix='/steel_materials_order')
    app.register_blueprint(splice_plate_order_bp, url_prefix='/splice_plate_order')
    app.register_blueprint(estimate_document_bp, url_prefix='/estimate_document')

    ppt_base = os.environ.get('PPT_EMBED_BASE')
    if not ppt_base:
        app.logger.warning('PPT_EMBED_BASE is not set. Using fallback embed URL for development.')
        ppt_base = 'https://onedrive.live.com/embed?resid=REPLACE_ME&em=2&wdAr=1.7777'
    app.config['PPT_EMBED_BASE'] = ppt_base

    @app.route('/slides/', defaults={'index': 1})
    @app.route('/slides/<int:index>')
    def slides(index):
        total = 20
        if total and (index < 1 or index > total):
            index = 1
        return render_template(
            'slides_embed.html',
            index=index,
            total=total,
            ppt_embed_base=app.config['PPT_EMBED_BASE'],
        )

    @app.route('/', endpoint='home')
    def home():
        pages = [
            ('コラム断面', '/column_size/'),
            ('角パイプ断面', '/shs_size/'),
            ('丸パイプ断面', '/chs_size/'),
            ('H形鋼断面', '/h_size/'),
            ('山形鋼断面', '/angle_size/'),
            ('溝形鋼断面', '/cannel_size/'),
            ('Iビーム断面', '/ibeam_size/'),
            ('リップ溝形鋼', '/lipcannel_size/'),
            ('ガセットプレート(柱)', '/gusset_flange_plate/'),
            ('ガセットプレート(梁)', '/gusset_web_plate/'),
            ('ガセットプレート(形状)', '/gusset_type/'),
            ('H形鋼フランジ継手', '/h_flange_steeljoint/'),
            ('H形鋼フランジピン', '/h_flange_pinjoint/'),
            ('H形鋼ウェブ継手', '/h_web_steeljoint/'),
            ('H形鋼ウェブピン', '/h_web_pinjoint/'),
            ('鋼材発注書', '/steel_materials_order/'),
            ('スプライスプレート帳票', '/splice_plate_order/'),
            ('見積書作成', '/estimate_document/'),
            ('説明スライド', '/slides/1'),
        ]
        return render_template('home.html', pages=pages)

    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200

    @app.errorhandler(404)
    def not_found(_error):
        return '404 Not Found', 404

    return app






