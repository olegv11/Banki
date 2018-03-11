from Decks import db
from datetime import datetime, timedelta
import enum


class CardTypeEnum(enum.Enum):
    new = 1,
    learned = 2,
    due = 3,


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    front = db.Column(db.String, nullable=False)
    back = db.Column(db.String, nullable=False)

    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False)
    number_in_deck = db.Column(db.Integer, nullable=False)

    learned = db.Column(db.Boolean, nullable=False, default=False)
    repetitions = db.Column(db.Integer, nullable=False, default=0)
    easing_factor = db.Column(db.Float, nullable=False, default=2.5)
    level = db.Column(db.Integer, nullable=False, default=1)

    due_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    current_interval = db.Column(db.DateTime, nullable=False, default=timedelta(days=1))

    def __repr__(self):
        return '<Card: %r | %r>' % (self.front, self.back)


class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=false)
    creation_date = db.Column(db.DateTime, nullable=False,
                              default=datetime.utcnow)
    cards = db.relationship('Card', backref='deck', lazy=True)

    def __repr__(self):
        return '<Deck: %r>' % self.name

