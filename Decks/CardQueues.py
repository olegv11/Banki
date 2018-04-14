from application import redis, db
from models import Card, LearningSession
from datetime import datetime


class CardQueues(object):
    def __init__(self, session : LearningSession):
        self.deck = session.deck
        self.newQueue = 'new{}'.format(self.deck.id)
        self.revQueue = 'rev{}'.format(self.deck.id)

    def populate_due_queue(self, now: datetime):
        due_cards = Card.query.filter(Card.deck_id == self.deck.id, Card.learned.is_(True),
                                      now > Card.due_time).first()
        for card in due_cards:
            redis.rpush(self.revQueue, card.id)

    def populate_new_queue(self, max_new_cards):
        current_new_card_len = redis.llen(self.newQueue)
        num_request_cards = max(max_new_cards - current_new_card_len, 0)
        if num_request_cards > 0:
            new_cards = Card.query.filter(Card.deck_id == self.deck.id, Card.learned.is_(False)) \
                .order_by(Card.number_in_deck).limit(num_request_cards).all()
            for card in new_cards:
                redis.rpush(self.newQueue, card.id)

    def get_next_card(self):
        card_id = None
        if redis.llen(self.newQueue) > 0:
            card_id = int(redis.lrange(self.newQueue, 0, 0)[0])
        elif redis.llen(self.revQueue) > 0:
            card_id = int(redis.lrange(self.revQueue, 0, 0)[0])

        if card_id is None:
            return None

        return Card.query.get(card_id)

    def __remove_card(self, card: Card):
        redis.lrem(self.newQueue, 0, card.id)
        redis.lrem(self.revQueue, 0, card.id)

    def __insert_card_to_rev(self, card: Card):
        redis.rpush(self.revQueue, card.id)

    def on_card_fail(self, card: Card):
        self.__remove_card(card)
        self.__insert_card_to_rev(card)

    def on_card_correct(self, card: Card):
        self.__remove_card(card)

    def close_queues(self):
        redis.delete(self.newQueue)
        redis.delete(self.revQueue)

