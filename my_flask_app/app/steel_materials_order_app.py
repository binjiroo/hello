# my_flask_app/app/steel_materials_order_app.py
from flask import Flask, Blueprint, render_template, request, jsonify
import json
import os

steel_order_bp = Blueprint('steel_order', __name__, template_folder='templates/steel_materials_order')

@steel_order_bp.route('/steel_materials_order')
def show_order_form():
    basedir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(basedir, 'data', 'steel_lists.json'), encoding='utf-8') as f:
        steel_data = json.load(f)

    return render_template(
        'steel_materials_order/index.html',
        steel_data=steel_data,
        print_mode=False
    )

@steel_order_bp.route('/steel_materials_order/print')
def print_order_form():
    basedir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(basedir, 'data', 'steel_lists.json'), encoding='utf-8') as f:
        steel_data = json.load(f)

    return render_template(
        'steel_materials_order/index.html',
        steel_data=steel_data,
        print_mode=True
    )

@steel_order_bp.route('/', methods=['GET', 'POST'])
def index():
    basedir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(basedir, 'data', 'steel_lists.json'), encoding='utf-8') as f:
        steel_data = json.load(f)

    if request.method == 'POST':
        form_data = {
            'project_name': request.form.get('project_name', ''),
            'order_date': request.form.get('order_date', ''),
            'delivery_date': request.form.get('delivery_date', ''),
            'chief_date': request.form.get('chief_date', ''),
            'company_name': request.form.get('company_name', ''),
            'tel': request.form.get('tel', ''),
            'fax': request.form.get('fax', ''),
            'email': request.form.get('email', '')
        }
        return render_template(
            'steel_materials_order/index.html',
            steel_data=steel_data,
            print_mode=False,
            **form_data
        )

    return render_template('steel_materials_order/index.html', steel_data=steel_data, print_mode=False)