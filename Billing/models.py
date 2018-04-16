from Billing.application import db
from datetime import datetime, timedelta
from flask import jsonify

class Bill(db.Model):
    __tablename__ = 'bill'
    id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    card_number = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {'id':self.id,
                'amount': self.amount,
                'date': self.date.timestamp(),
                'card_number': self.card_number,
                'description': self.description}
