from Decks import db
from datetime import datetime, timedelta
import enum


class CardTypeEnum(enum.Enum):
    new = 1,
    learned = 2,
    due = 3,


class Card(db.Model):
    __tablename__ = 'card'
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
    __tablename__ = 'deck'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False,
                              default=datetime.utcnow)
    cards = db.relationship('card', backref=db.backref('deck', lazy=True))

    session_id = db.Column(db.Integer, db.ForeignKey('learning_session.id'))
    session = db.relationship('session', backref=db.backref('deck', uselist=False))

    def __repr__(self):
        return '<Deck: %r>' % self.name


class LearningSession(db.Model):
    __tablename__ = 'learning_session'
    id = db.Column(db.Integer, primary_key=True)
    last_activity = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

