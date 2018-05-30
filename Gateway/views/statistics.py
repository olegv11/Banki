from Gateway.application import app, j
from flask import request, jsonify, g, redirect, url_for, render_template
import werkzeug.exceptions
import requests
from Gateway.views.common import *
from Gateway.exceptions import BankiException, RemoteBankiException
from datetime import datetime


@app.route('/stat')
@j.should_have_role(role='admin')
def get_stat():
    stats = requests.get(make_statistics_url('/data'),
                         params={'type': 'LOGIN'})
    if stats.status_code != 200:
        stats = []
    else:
        stats = stats.json()

    google = [datum for datum in stats if datum['data'] == 'GOOGLE']
    site = [datum for datum in stats if datum['data'] == 'SITE']
    return render_template('statistics', google=len(google), site=len(site))
