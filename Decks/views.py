from Decks.application import app, db
from Decks.models import Card, Deck, LearningSession
from flask import request, jsonify
from Decks.CardQueues import CardQueues
from Decks.CardScheduler import AnswerDifficulty, CardScheduler, string_to_difficulty
from datetime import datetime

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
    deck.owner_id = request.values['owner_id']

    session = LearningSession()
    deck.session = session

    db.session.add(session)
    db.session.add(deck)
    db.session.commit()
    return jsonify({'id': deck.id})

@app.route('/deck', methods=['DELETE'])
def delete_deck():
    deck_id = request.values['deck_id']
    deck = Deck.query.get(int(deck_id))

    db.session.delete(deck)
    db.session.commit()
    return jsonify({})

@app.route('/deck/<int:deck_id>', methods=['GET'])
def get_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    deck_dict = deck.to_json()

    queues = CardQueues(deck.session)
    deck_dict['new_len'] = queues.new_cards_left()
    deck_dict['rev_len'] = queues.rev_cards_left()

    return jsonify(deck_dict)


@app.route('/decks/<int:user_id>', methods=['GET'])
def get_decks(user_id):
    decks = Deck.query.filter(Deck.owner_id == user_id).all()
    decks_dict = []

    for deck in decks:
        queues = CardQueues(deck.session)
        d = deck.to_json()
        d['new_len'] = queues.new_cards_left()
        d['rev_len'] = queues.rev_cards_left()
        decks_dict.append(d)

    return jsonify(decks_dict)


@app.route('/deck/<int:deck_id>/cards', methods=['GET'])
def get_deck_cards(deck_id):
    cards = Card.query.filter(Card.deck_id == deck_id).all()
    card_list = list(map(lambda x: x.to_json(), cards))
    return jsonify(card_list)


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

@app.errorhandler(500)
def error500(error):
    return jsonify({'Error:', str(error)}, 500)

@app.route('/card/<int:card_id>/answer', methods=['POST'])
def answer_card(card_id):
    card = Card.query.get_or_404(card_id)
    diff = string_to_difficulty(request.values['answer'])

    sched = CardScheduler()
    sched.answer(card, datetime.utcnow(), diff)

    db.add(card)
    db.commit()

    return jsonify({})
