from app import app, admin, logger, api
from flask_admin.contrib.sqla import ModelView
from flask import render_template, redirect, jsonify, url_for, request, session, flash, send_from_directory

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
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            success = APIUser.validate_creds(username, password)
            if success:
                flash('Successful Login')
                return redirect(url_for('index'))
            else:
                flash('Username and/or password do not match')

        else:
            flash('Registration failed')


    return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            
            user = APIUser.create(username, password)
            if user:
                session['user'] = True
                session['username'] = username
                flash('Successful registration')
                return redirect(url_for('index'))
            else:
                flash('Registration failed, try another username')
        else:
            flash('Registration failed')  
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/search', methods=['POST'])
def search():
    text = request.form.get('text')
    # search = f'%{text}%'
    # results = APIUser.query.filter(APIUser.username.like(search)).all()
    # return jsonify(results)

    return jsonify(({'object': 'result1'}, {'object': 'result2'}, {'object': 'result3'}, {'object': 'result3'}, {'object': 'result4'}))

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'img/favicon.ico', mimetype='image/vnd.microsoft.icon')