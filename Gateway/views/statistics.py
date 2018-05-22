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
    return redirect(url_for('index'))