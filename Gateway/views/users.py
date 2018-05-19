from Gateway.application import app, j
from flask import request, jsonify, g, redirect, url_for, render_template
import werkzeug.exceptions
import requests
from Gateway.views.common import *
from Gateway.exceptions import BankiException, RemoteBankiException
from datetime import datetime

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('users/login.html')