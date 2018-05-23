from Users.application import db
from datetime import datetime, timedelta
import enum
from flask import jsonify


class User(db.Model):
    __tablename__ = 'user'
    mail = db.Column(db.String, primary_key=False, unique=True)
    name = db.Column(db.String, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String)
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    role = db.Column(db.String, nullable=False, default='user')

    google_access_token = db.Column(db.String)

    available_decks = db.Column(db.Integer, default=2)

    def to_json(self):
        result = {'id': self.id,
                  'name': self.name,
                  'mail': self.mail,
                  'registration_date': self.registration_date,
                  'available_decks': self.available_decks,
                  'access_token': self.google_access_token,
                  'role': self.role}
        return result


class UserBill(db.Model):
    __tablename__ = 'userbills'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bill_id = db.Column(db.Integer, nullable=False)

    def to_json(self):
        result = {'id': self.id,
                  'user_id': self.user_id,
                  'bill_id': self.bill_id}
        return result
