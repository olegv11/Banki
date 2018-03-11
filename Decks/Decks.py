from flask import Flask, jsonify, request, abort
from werkzeug.exceptions import HTTPException, default_exceptions
from flask_sqlalchemy import SQLAlchemy


def JsonApp(app):
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


app = JsonApp(Flask(__name__))
app.config.from_object('config')
db = SQLAlchemy(app)


@app.errorhandler(500)
def error500(error):
    return jsonify({'Error:', str(error)}, 500)


@app.route('/api')
def my_microservice():
    return jsonify({'Hello':'World'})


@app.route('/api/person/<int:person_id>')
def person(person_id):
    response = jsonify({'Hello': person_id})
    return response


if __name__ == '__main__':
    app.run()
