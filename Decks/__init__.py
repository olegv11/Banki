from Decks import app, db, redis, inject
from models import Card, Deck, LearningSession


if __name__ == '__main__':
    db.create_all()
    inject.map(db=db)
    inject.map(redis=redis)
    app.run()
