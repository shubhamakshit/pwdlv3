from flask import Blueprint, request, jsonify, render_template

from mainLogic.utils.glv import Global

template_blueprint = Blueprint('template_blueprint', __name__)

@template_blueprint.route('/')
def index():
    return render_template('index.html')

@template_blueprint.route('/util')
def util():
    return render_template('index.html')

@template_blueprint.route('/prefs')
def prefs():
    return render_template('index.html')

@template_blueprint.route('/help')
def help():
    return render_template('index.html')

@template_blueprint.route('/sessions')
def sessions():
    return render_template('index.html')

@template_blueprint.route('/admin')
def admin():
    return render_template('index.html')

@template_blueprint.route('/boss')
def boss():
    return render_template('index.html')

@template_blueprint.route('/login')
def login():
    return render_template('index.html')

@template_blueprint.route('/profile')
def profile():
    return render_template('index.html')

# @template_blueprint.route('/manifest.json')
# def manifest():
#     return render_template('manifest.json')