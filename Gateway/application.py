from flask import Flask, jsonify, request, abort
from werkzeug.exceptions import HTTPException, default_exceptions
from flask_inject import Inject
from flask_migrate import Migrate
from Gateway.auth import Jwt


app = Flask(__name__)
app.config.from_object('Gateway.config')
inject = Inject(app)
j = Jwt(app)



