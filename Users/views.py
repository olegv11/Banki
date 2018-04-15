from Users.application import app, db
from Users.models import User
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import werkzeug.exceptions


def encrypt(unencrypted):
    return generate_password_hash(unencrypted)


@app.route('/user', methods=['POST'])
def create_user():
    user = User()
    unencrypted_password = request.values['password']

    user.name = request.values['name']
    user.password = encrypt(unencrypted_password)
    user.mail = request.values['mail']

    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id})

@app.route('/user_google', methods=['POST'])
def create_user_google():
    user = User()

    user.name = request.values['name']
    user.mail = request.values['mail']
    user.google_access_token = request.values['access_token']
    user.google_renew_token = request.values['renew_token']

    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id})

@app.route('/user_google/tokens', methods=['POST'])
def update_user_google():
    user = User.query.get_or_404(request.values['id'])

    user.google_access_token = request.values['access_token']
    user.google_renew_token = request.values['renew_token']

    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id})


@app.route('/login', methods=['POST'])
def login():
    name = request.values['name']
    unencrypted_password = request.values['password']

    user = User.query.filter_by(name=name).first_or_404()
    if check_password_hash(user.password, unencrypted_password):
        return jsonify({'id': user.id})

    raise werkzeug.exceptions.Unauthorized(description="Could not login")

