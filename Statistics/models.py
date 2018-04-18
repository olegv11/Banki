from Statistics.application import db
from datetime import datetime
import enum

class ItemType(enum.Enum):
    UNKNOWN = 0,
    USER_REGISTERED = 1,
    USER_BOUGHT_DECK = 2,
    USER_LOGGED_IN = 3,
    USER_MODIFIED_DECK = 4


class StatisticsItem(db.Model):
    __tablename__ = 'statistics_item'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type = db.Column(db.Integer, nullable=False, default=ItemType.UNKNOWN)
    data = db.Column(db.String, nullable=True)


