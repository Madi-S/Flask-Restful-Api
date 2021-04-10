# from jobs import *
from app import app, logger, sio, send, admin, db, api
from flask_admin.contrib.sqla import ModelView
from flask import render_template, redirect, jsonify, url_for, request, session, flash, send_from_directory

from functools import wraps
from models import APIUser, APIKey, Message
from forms import LoginForm, RegistrationForm

import os
import stripe


stripe.api_key = app.config['STRIPE_SECRET_KEY']


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


@app.route('/cancel')
def cancel():
    flash('Payment canceled')
    return redirect(url_for('index'))


@app.route('/thanks')
def thanks():
    flash('Payment successful')
    return redirect(url_for('index'))


@app.route('/stripe-pay')
def stripe_pay():
    stripe_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1IdBuUDUZN97XqaBVd43hUcR',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) +
        '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('cancel', _external=True),
    )
    return {
        'checkout_session_id': stripe_session['id'],
        'checkout_public_key': app.config['STRIP_PUBLIC_KEY']
    }


@app.route('/pricing')
def pricing():
    # stripe_session = stripe.checkout.Session.create(
    #     payment_method_types=['card'],
    #     line_items=[{
    #         'price': 'price_1IdBuUDUZN97XqaBVd43hUcR',
    #         'quantity': 1,
    #     }],
    #     mode='payment',
    #     success_url=url_for('thanks', _external=True) +
    #     '?session_id={CHECKOUT_SESSION_ID}',
    #     cancel_url=url_for('cancel', _external=True),
    # )

    return render_template('pricing.html',
                        #    checkout_session_id=stripe_session['id'],
                        #    checkout_public_key=app.config['STRIP_PUBLIC_KEY']
                           )


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            success, msg = APIUser.validate_creds(username, password)
            if success:
                flash(msg)
                return redirect(url_for('index'))
            else:
                flash(msg)
        else:
            flash('Login failed')

    return render_template('login.html', form=form)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
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

    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/profile/<username>')
def profile(username):
    user_data = {'username': username}
    user = APIUser.query.filter_by(username=username).first()

    if not user:
        flash(f'Sorry, but user {username} does not exist')
        return redirect(url_for('index'))

    if username == session.get('username'):
        user_data['api_key'] = user.api_user_key
    else:
        user_data['api_key'] = user.api_user_key[:10] + '*************'

    return render_template('profile.html', user_data=user_data)


@app.route('/search', methods=['POST'])
def search():
    # return jsonify(({'object': 'result1'}, {'object': 'result2'}, {'object': 'result3'}, {'object': 'result3'}, {'object': 'result4'}))
    
    text = request.form.get('text')
    search = f'%{text}%'
    users = APIUser.query.filter(APIUser.username.like(search)).limit(100).all()
    data = []
    for user in users:
        data.append({
            'username': user.username
        })
    return jsonify(data)



@app.route('/')
def index():
    # sleep_thread()
    # send_email_to()
    msgs = Message.get_last_n_msgs(10)
    return render_template('index.html', msgs=msgs)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'img/favicon.ico', mimetype='image/vnd.microsoft.icon')


bad_words = ('foe', 'bar')

@sio.on('message')
def message_handler(msg):
    logger.debug('Message: %s', msg)
    
    
    if msg.text in bad_words or len(msg.text) < 2 or len(msg.text) > 229:
        flash('Message contains bad words or message length is inappropriate')
        return redirect(url_for('index'))

    else:
        Message.create(
            text=msg.text, 
            sender=msg.sender,
            category=msg.category
        )

        send(msg, broadcast=True)

    # broadcast=False means sending message only to the sender (from whom message originally came from) 
    # broadcast=True means sending message to everyone


