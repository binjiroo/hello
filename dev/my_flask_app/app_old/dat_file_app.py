# app/dat_file_app.py
from flask import Blueprint, request, make_response
import io

dat_bp = Blueprint('download_dat', __name__)

@dat_bp.route('/download_dat', methods=['POST'])
def download_dat():
    # フォームから選択されたファイル名を取得
    name = request.form['dat_name']
    # ここでDATファイルの中身を生成／読み込み。
    # 例として空ファイルを返しますが、
    # 実際にはshape_listをまとめた文字列などを入れてください。
    content = ""  # ← ここを your_dat_string に置き換え

    # レスポンスを組み立て
    buf = io.BytesIO(content.encode('utf-8'))
    resp = make_response(buf.getvalue())
    resp.headers['Content-Type'] = 'application/octet-stream'
    # ブラウザ側に「名前を付けて保存」ダイアログを出させる
    resp.headers['Content-Disposition'] = f'attachment; filename="{name}"'
    return resp
