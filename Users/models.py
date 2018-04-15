from application import db
from datetime import datetime, timedelta
import enum
from flask import jsonify


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    mail = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    google_access_token = db.Column(db.String)
    google_renew_token = db.Column(db.String)

    available_decks = db.Column(db.Integer, default=2)

    def to_json(self):
        result = {'id': self.id,
                  'name': self.name,
                  'mail': self.mail,
                  'registration_date': self.registration_date,
                  'available_decks': self.available_decks}
        return result
