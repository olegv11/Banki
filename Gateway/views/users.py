from Gateway.application import app, j
from flask import request, make_response, jsonify, g, redirect, url_for, render_template
import werkzeug.exceptions
import requests
from Gateway.views.common import *
from Gateway.exceptions import BankiException, RemoteBankiException
from datetime import datetime
from flask_oauth import OAuth
import os


def get_user_id():
    return g.user_data['user_id']

def get_role():
    return g.user_data['role']

def is_own_page(user_id):
    return get_user_id() == user_id or 'admin' == get_role()


@app.route('/user/register', methods=['GET'])
def register_page():
    return render_template('users/register.html')


@app.route('/user/register', methods=['POST'])
def register():
    name = request.values['name']
    mail = request.values['mail']
    password = request.values['password']
    reg_request = requests.post(make_users_url('/user'),
                                data={'name': name, 'mail': mail, 'password': password})
    if reg_request.status_code != 200:
        handle_request_exception(reg_request.status_code, reg_request, 'Could not create user!')

    reg_json = reg_request.json()
    if 'id' not in reg_json:
        return render_template('users/register.html', error='Пользователь с такой почтой уже существует!')

    send_statistics('REGISTERED', 'SITE')

    user = requests.get(make_users_url('/user/mail/{0}', mail))
    if user.status_code != 200:
        handle_request_exception(user.status_code, user, 'Something happened')
    userJson = user.json()
    newResponse = make_response(redirect(url_for('user_page', user_id=userJson['id'])))
    j.set_token(newResponse, userJson['id'], userJson['name'], userJson['mail'], userJson['role'])

    return newResponse


@app.route('/user/logout', methods=['GET'])
@j.should_have_login
def logout():
    resp = make_response(redirect(url_for('index')))
    j.erase_token(resp)
    return resp

@app.route('/user/login', methods=['GET'])
def login_page():
    return render_template('users/login.html')

@app.route('/user/login', methods=['POST'])
def login():
    name = request.values['name']
    password = request.values['password']
    print('LOGGING IN:' + make_users_url('/logjn'))
    login_attempt = requests.post(make_users_url('/login'),
                                  data={'name': name, 'password': password})
    if login_attempt.status_code == 401:
        return render_template('users/login.html', error='Попробуйте ещё раз')
    elif login_attempt.status_code != 200:
        handle_request_exception(login_attempt.status_code, login_attempt, 'Не получилось войти!')

    l = login_attempt.json()
    resp = make_response(redirect(url_for('user_page', user_id=l['id'])))
    j.set_token(resp, l['id'], l['name'], l['mail'], l['role'])
    send_statistics('LOGIN', 'SITE')
    return resp


@app.route('/user/<int:user_id>', methods=['GET'])
@j.should_have_login
def user_page(user_id):
    if not is_own_page(user_id):
        raise werkzeug.exceptions.Forbidden('No rights to see the user page')
    user = requests.get(make_users_url('/user/{0}', user_id))
    if user.status_code != 200:
        handle_request_exception(user.status_code, user, 'Could not get user!')
    user_json = user.json()

    bills = []

    bill_ids = requests.get(make_users_url('/user/{0}/bill', user_id))
    if bill_ids.status_code == 200:
        bills_ids_json = bill_ids.json()
        bills_req = requests.get(make_bills_url('/bills'), params={'ids': bill_ids})
        if bills_req.status_code == 200:
            bills = bills_req.json()
            for b in bills:
                b['date'] = datetime.utcfromtimestamp(b['date'])

    decks = requests.get(make_decks_url('/decks/{0}', user_id))
    if decks.status_code == 200:
        json_decks = decks.json()
        print(json_decks)
        user_json['decks_number'] = str(len(json_decks))
    else:
        user_json['decks_number'] = 'N/A'

    return render_template('users/user.html', user=user_json, bills=bills)


@app.route('/user/<int:user_id>/buy', methods=['GET'])
@j.should_have_login
def buy_deck_page(user_id):
    if not is_own_page(user_id):
        raise werkzeug.exceptions.Forbidden('No rights to see the user page')
    return render_template('users/buy.html', user_id=user_id)

@app.route('/user/<int:user_id>/buy', methods=['POST'])
@j.should_have_login
def buy_deck(user_id):
    amount = 100
    card_number = request.values['card_number']
    bought_req = requests.post(make_bills_url('/bill'),
                  data={'amount': amount, 'card_number': card_number,
                        'description': 'Покупка колоды'})
    if bought_req.status_code != 200:
        handle_request_exception(bought_req.status_code, bought_req, 'Could not buy deck')

    bill_id = bought_req.json()['id']
    try:
        users_req = requests.post(make_users_url('/user/{0}/bill', g.user_data['user_id']),
                                  data={'bill_id': bill_id})
        if users_req.status_code != 200:
            requests.delete(make_bills_url('/bill/{0}', bill_id))
    except requests.ConnectionError:
        requests.delete(make_bills_url('/bill/{0}', bill_id))
    return redirect(url_for('user_page', user_id=g.user_data['user_id']))


oauth = OAuth()
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=os.getenv('GOOGLE_CLIENT_ID'),
                          consumer_secret=os.getenv('GOOGLE_CLIENT_SECRET'))


@app.route('/logingoogle')
def googlelogin():
    callback = url_for('oauthCallback', _external=True)
    return google.authorize(callback=callback)


@app.route('/oauth2callback')
@google.authorized_handler
def oauthCallback(resp):
    access_token = resp['access_token']
    headers = {'Authorization': 'OAuth ' + access_token}
    req = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', headers=headers)
    reqJson = req.json()
    name = reqJson['name']
    mail = reqJson['email']

    user_existsreq = requests.get(make_users_url('/user_exists'), params={'mail': mail})
    if user_existsreq.status_code != 200:
        handle_request_exception(user_existsreq.status_code, user_existsreq, 'Something happened!')

    if user_existsreq.json()['result']:
        user = requests.get(make_users_url('/user/mail/{0}', mail))
        if user.status_code != 200:
            handle_request_exception(user.status_code, user, 'Something happened')
        userJson = user.json()
        newResponse = make_response(redirect(url_for('user_page', user_id=userJson['id'])))
        j.set_token(newResponse, userJson['id'], userJson['name'], userJson['mail'], userJson['role'])
        send_statistics('LOGIN', 'GOOGLE')
        return newResponse
    else:
        reg = requests.post(make_users_url('/user_google'),
                            data={'name': name, 'mail': mail, 'access_token': access_token})
        if reg.status_code != 200:
            handle_request_exception(reg.status_code, reg, 'Something happened')

        user = requests.get(make_users_url('/user/mail/{0}', mail))
        if user.status_code != 200:
            handle_request_exception(user.status_code, user, 'Something happened')
        userJson = user.json()
        newResponse = make_response(redirect(url_for('user_page', user_id=userJson['id'])))
        j.set_token(newResponse, userJson['id'], userJson['name'], userJson['mail'], userJson['role'])
        send_statistics('REGISTERED', 'GOOGLE')
        return newResponse


@google.tokengetter
def get_access_token():
    if g.user_data is not None:
        user = requests.get(make_users_url('/user/{0}', g.user_data['user_id']))
        if user.status_code != 200:
            return None
        user_json = user.json()
        return user_json['access_token'], user_json['secret_token']
    return None
