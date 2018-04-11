from application import app, db
from models import Card, Deck, LearningSession
from flask import request, jsonify
from CardQueues import CardQueues

@app.route('/deck/<int:deck_id>/next')
def get_next_card(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    session = deck.session
    queues = CardQueues(session)
    next_card = queues.get_next_card()
    if next_card is None:
        return jsonify({'status': 'no more cards'})
    return next_card.to_json()


@app.route('/deck', methods=['POST'])
def create_deck():
    deck = Deck()
    deck.name = request.values['name']
    deck.description = request.values['description']

    session = LearningSession()
    deck.session = session

    db.session.add(session)
    db.session.add(deck)
    db.session.commit()
    return jsonify({'id': deck.id})

@app.route('/deck/<int:deck_id>', methods=['GET'])
def get_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    return jsonify(deck.to_json())


@app.route('/deck/<int:deck_id>/card', methods=['POST'])
def create_card(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    card = Card()

    card.front = request.values['front']
    card.back = request.values['back']
    card.number_in_deck = len(deck.cards) + 1
    deck.cards.append(card)

    db.session.add(card)
    db.session.add(deck)
    db.session.commit()

    return jsonify({'id': card.id})


@app.route('/card/<int:card_id>')
def get_card(card_id):
    card = Card.query.get_or_404(card_id)
    return jsonify(card.to_json())