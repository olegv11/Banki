from Gateway.application import app, j
from flask import request, make_response, jsonify, g, redirect, url_for, render_template
import werkzeug.exceptions
import requests
from Gateway.views.common import *
from Gateway.exceptions import BankiException, RemoteBankiException
from datetime import datetime
from flask_oauth import OAuth


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
    return render_template('users/register.html')


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

    login_attempt = requests.post(make_users_url('/login'),
                                  data={'name': name, 'password': password})
    if login_attempt.status_code == 401:
        return render_template('users/login.html', error='Попробуйте ещё раз')
    elif login_attempt.status_code != 200:
        handle_request_exception(login_attempt.status_code, login_attempt, 'Не получилось войти!')

    l = login_attempt.json()
    resp = make_response(redirect(url_for('user_page', user_id=l['id'])))
    j.set_token(resp, l['id'], l['name'], l['mail'],l['role'])
    return resp


@app.route('/user/<int:user_id>', methods=['GET'])
@j.should_have_login
def user_page(user_id):
    if not is_own_page(user_id):
        raise BankiException(code=403, description='No rights to see the user page')
    user = requests.get(make_users_url('/user/{0}', user_id))
    if user.status_code != 200:
        handle_request_exception(user.status_code, user, 'Could not get user!')

    bills = requests.get(make_bills_url('/user/{0}/bill', user_id))
    if bills.status_code != 200:
        handle_request_exception(bills.status_code, bills, 'Could not get bills for user!')

    return render_template('users/user.html', user=user.json(), bills = bills.json())


@app.route('/user/<int:user_id>/buy', methods=['GET'])
@j.should_have_login
def user_buy(user_id):
    return render_template('users/buy.html', user_id=user_id)

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
                          consumer_key=app.config['GOOGLE_CLIENT_ID'],
                          consumer_secret=app.config['GOOGLE_CLIENT_SECRET'])


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
        j.set_token(resp, userJson['id'], userJson['name'], userJson['mail'], userJson['role'])
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
