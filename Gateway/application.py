from flask import Flask, jsonify, request, abort, render_template, url_for, redirect
from werkzeug.exceptions import HTTPException, default_exceptions
from flask_inject import Inject
from flask_migrate import Migrate
from Gateway.auth import Jwt
from Gateway.exceptions import BankiException, RemoteBankiException
import requests
import json

app = Flask(__name__)
app.config.from_object('Gateway.config')
inject = Inject(app)
j = Jwt(app)


@app.errorhandler(Exception)
def handle_exception(error):
    print(error)
    return render_template('error.html')


@app.errorhandler(401)
def handle_401(error):
    print(error)
    return redirect(url_for('login'))

@app.errorhandler(403)
def handle_403(error):
    print(error)
    return render_template('403.html')

@app.errorhandler(404)
def handle_404(error):
    print(error)
    return render_template('404.html')

@app.errorhandler(BankiException)
def handle_exception(error: BankiException):
    app.logger.error('Exception\nCode: {0}\nDescription: {1}'.format(error.code, error.description))
    if error.code == 404:
        return render_template('404.html')
    return render_template('error.html')

@app.errorhandler(requests.RequestException)
def handle_exception(error):
    return render_template('error.html')



@app.errorhandler(RemoteBankiException)
def handle_remote_exception(error: RemoteBankiException):
    app.logger.error('Remote exception\nCode: {0}\nDescription: {1}\nURL {2}'
                     .format(error.inner_exception.code,
                             error.inner_exception.description,
                             error.request_object.url))
    return jsonify(error.to_dict())
