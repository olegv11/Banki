from Decks.application import db
from datetime import datetime, timedelta
import enum
from flask import jsonify


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
    current_interval = db.Column(db.DateTime, nullable=False,
                                 default=datetime.utcfromtimestamp(timedelta(days=1).total_seconds()))

    def __repr__(self):
        return '<Card: %r | %r>' % (self.front, self.back)

    def to_json(self):
        result = {'id': self.id,
                  'front': self.front,
                  'back': self.back,
                  'learned': self.learned,
                  'level': self.level,
                  'ef': self.easing_factor}
        return result



class Deck(db.Model):
    __tablename__ = 'deck'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False,
                              default=datetime.utcnow)
    cards = db.relationship('Card', backref=db.backref('deck', lazy=True))

    session_id = db.Column(db.Integer, db.ForeignKey('learning_session.id'))
    session = db.relationship('LearningSession', backref=db.backref('deck', uselist=False))

    owner_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Deck: %r>' % self.name

    def to_json(self):
        result = {'id': self.id,
                  'name': self.name,
                  'description': self.description,
                  'session': self.session_id,
                  'owner_id': self.owner_id,
                  'creation_date': self.creation_date.timestamp()}
        return result



class LearningSession(db.Model):
    __tablename__ = 'learning_session'
    id = db.Column(db.Integer, primary_key=True)
    last_activity = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
