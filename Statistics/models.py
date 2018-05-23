from Statistics.application import db
from datetime import datetime
import enum


class StatisticsItem(db.Model):
    __tablename__ = 'statistics_item'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String, nullable=False, default="UNKNOWN")
    data = db.Column(db.String, nullable=True)


