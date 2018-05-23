from Users.application import app, db
from Users.models import User, UserBill
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
    user.role = 'user'
    if 'role' in request.values:
        user.role = request.values['role']

    if User.query.filter_by(name=user.name).first() is not None:
        return jsonify({'status': 'Name exists'})

    if User.query.filter_by(mail=user.mail).first() is not None:
        return jsonify({'status': 'Name exists'})

    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id})

@app.route('/user_exists', methods=['GET'])
def has_user():
    mail = request.args.get('mail')
    if mail is not None:
        if User.query.filter_by(mail=mail).first() is not None:
            return jsonify({'result': True})
        else:
            return jsonify({'result': False})

    name = request.args.get('name')
    if name is not None:
        if User.query.filter_by(name=name).first() is not None:
            return jsonify({'result': True})
        else:
            return jsonify({'result': False})
    raise werkzeug.exceptions.BadRequest('Should have mail or name')

@app.route('/user_google', methods=['POST'])
def create_user_google():
    user = User()

    user.name = request.values['name']
    user.mail = request.values['mail']
    user.google_access_token = request.values['access_token']

    if User.query.filter_by(mail=user.mail).first() is not None:
        return jsonify({'status': 'Name exists'})

    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id})


@app.route('/user/<int:user_id>')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_json())

@app.route('/user/mail/<string:mail>')
def get_user_mail(mail):
    user = User.query.filter_by(mail=mail).first_or_404()
    return jsonify(user.to_json())

@app.route('/user_google/tokens', methods=['POST'])
def update_user_google():
    user = User.query.get_or_404(request.values['id'])

    user.google_access_token = request.values['access_token']

    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id})

@app.route('/user/<int:user_id>/bill', methods=['POST'])
def user_bought(user_id):
    bill_id = request.values['bill_id']

    ub = UserBill()
    ub.user_id = user_id
    ub.bill_id = bill_id

    user = User.query.get_or_404(user_id)
    user.available_decks += 1

    db.session.add(ub)
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': ub.id})


@app.route('/user/<int:user_id>/bill', methods=['GET'])
def user_bills(user_id):
    result = UserBill.query.filter_by(user_id=user_id).all()
    result_json = list(map(lambda x: x.to_json()['bill_id'], result))
    return jsonify(result_json)


@app.route('/login', methods=['POST'])
def login():
    name = request.values['name']
    unencrypted_password = request.values['password']

    user = User.query.filter_by(name=name).first()

    if user is not None and check_password_hash(user.password, unencrypted_password):
        return jsonify({'id': user.id, 'name': user.name, 'mail': user.mail,
                        'role': user.role})

    raise werkzeug.exceptions.Unauthorized(description="Could not login")

