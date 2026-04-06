import os
from flask import Flask
from app.config import cannel_steel_r_mapping
from app.config import h_steel_r_mapping
from app import create_app

def create_app():
    app = Flask(__name__)
    secret = os.environ.get('SECRET_KEY')
    if not secret:
        # ローカル開発用に一時的なキーを生成
        secret = os.urandom(24)
    app.secret_key = secret
    #…
    return app

if __name__ == '__main__':
    app.run(debug=True)
