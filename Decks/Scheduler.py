from Decks.application import cron
from Decks.models import LearningSession
from Decks.CardQueues import CardQueues
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime


def update_due_cards():
    sessions = LearningSession.query.all()
    for s in sessions:
        if s.deck is not None:
            q = CardQueues(s)
            q.populate_due_queue(datetime.now())
            q.populate_new_queue(10)


cron.add_job(
    func=update_due_cards,
    trigger=IntervalTrigger(seconds=10),
    id='card_update_job',
    name='Update due cards',
    replace_existing=True)