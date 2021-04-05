from app import app, admin, logger, api
from flask_admin.contrib.sqla import ModelView
from flask import render_template, redirect, url_for, request, session, flash, send_from_directory

from functools import wraps
from models import APIUser, APIKey, db
from forms import LoginForm, RegistrationForm

import os


class AdminModelView(ModelView):
    # def is_accessible(self):
    #     return 'admin' in session
    pass


def login_required(f):
    @wraps
    def inner(*args, **kwargs):
        user_key = session.get('user_key')
        if user_key and APIUser.query.filter_by(user_key=user_key).first():
            return f(*args, **kwargs)

        return redirect(url_for('index'))

    return inner


@app.route('/example')
def example():
    return render_template('example.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        form = RegistrationForm()
        return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        form = LoginForm()
        return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_key', None)
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'img/favicon.ico', mimetype='image/vnd.microsoft.icon')