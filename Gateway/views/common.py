from Gateway.application import app, j
from Gateway.exceptions import BankiException, RemoteBankiException
import requests
from flask import request, jsonify, g, redirect, url_for, render_template


def make_decks_url(p, *args):
    return app.config['DECKS_URL'] + p.format(*args)


def make_users_url(p, *args):
    return app.config['USERS_URL'] + p.format(*args)


def make_bills_url(p, *args):
    return app.config['BILLING_URL'] + p.format(*args)


def make_statistics_url(p, *args):
    return app.config['STAT_URL'] + p.format(*args)


def send_statistics(type, data=''):
    try:
        requests.post(make_statistics_url('/data'), data={'type': type, 'data': data})
    except:
        pass

def handle_request_exception(status_code, request_object, description):
    if status_code == 404:
        raise BankiException(status_code, description)
    else:
        inner = BankiException(status_code, description)
        raise RemoteBankiException(inner, request_object)


@app.route('/')
def index():
    return render_template('index.html')