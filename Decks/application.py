from flask import Flask, jsonify, request, abort
from werkzeug.exceptions import HTTPException, default_exceptions
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_inject import Inject
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

def json_app(app):
    def error_handling(error):
        if isinstance(error, HTTPException):
            result = {'code': error.code, 'description': error.description,
                      'message': str(error)}
        else:
            description = abort.mapping[500].description
            result = {'code': 500, 'description': description,
                      'message': str(error)}
        resp = jsonify(result)
        resp.status_code = result['code']
        return resp

    for code in default_exceptions.keys():
        app.register_error_handler(code, error_handling)

    return app


app = json_app(Flask(__name__))
app.config.from_object('Decks.config')
db = SQLAlchemy(app)
redis = FlaskRedis(app)
inject = Inject(app)
migrate = Migrate(app, db)

cron = BackgroundScheduler()
cron.start()
atexit.register(lambda: cron.shutdown())