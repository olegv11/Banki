from Gateway.application import app, j
from flask import request, jsonify, g, redirect, url_for, render_template
import werkzeug.exceptions
import requests
from Gateway.views.common import *
from Gateway.exceptions import BankiException, RemoteBankiException
from datetime import datetime


def get_user_id():
    return g.user_data['user_id']


def get_role():
    return g.user_data['role']


@app.route('/decks')
@j.should_have_login
def get_decks():
    print('Getting decks')
    decks = requests.get(make_decks_url('/decks/{0}', get_user_id()))
    print('Got decks')
    json_decks = decks.json()
    return render_template('decks/index.html', decks=json_decks)


def is_own_deck(owner_id):
    return get_user_id() == owner_id or 'admin' == get_role()


@app.route('/deck/<int:deck_id>', methods=['GET'])
def get_deck(deck_id):
    deck = requests.get(make_decks_url("/deck/{0}", deck_id))
    json_deck = deck.json()
    if deck.status_code != 200:
        handle_request_exception(deck.status_code, deck, 'Could not get deck!')

    if not is_own_deck(json_deck['owner_id']):
        raise werkzeug.exceptions.Forbidden("Not your deck!")

    cards = requests.get(make_decks_url("/deck/{0}/cards", deck_id))
    json_cards = cards.json()
    for c in json_cards:
        c['due_time'] = datetime.utcfromtimestamp(c['due_time'])
        c['is_due'] = datetime.utcnow() > c['due_time']

    if cards.status_code != 200:
        handle_request_exception(deck.status_code, deck, 'Could not get cards!')

    return render_template('decks/deck.html', deck=json_deck, cards=json_cards)


def can_create_more_decks(user_id):
    user = requests.get(make_users_url('/user/{0}', get_user_id()))
    user_json = user.json()
    available_decks = user_json['available_decks']

    decks = requests.get(make_decks_url('/decks/{0}', get_user_id()))
    json_decks = decks.json()

    return available_decks > len(list(json_decks))

@app.route('/create_deck', methods=['GET'])
@j.should_have_login
def create_deck_page():
    if not can_create_more_decks(get_user_id()):
        return redirect(url_for('buy_deck_page', user_id=get_user_id()))
    return render_template('decks/createDeck.html', user_id=get_user_id())

@app.route('/create_deck', methods=['POST'])
@j.should_have_login
def create_deck():
    name = request.values['deck_name']

    if not can_create_more_decks(get_user_id()):
        raise werkzeug.exceptions.Forbidden('Нельзя создать больше колод')

    description = request.values['deck_description']
    created_deck = requests.post(make_decks_url('/deck'),
                  data={'name': name, 'description': description, 'owner_id': get_user_id()})
    deck_json = created_deck.json()
    send_statistics('DECK_CREATED')
    return redirect(url_for('get_deck', deck_id=deck_json['id']))


@app.route('/delete_deck', methods=['POST'])
@j.should_have_login
def delete_deck():
    deck_id = request.values['deck_id']

    deck = requests.get(make_decks_url("/deck/{0}", deck_id))
    if deck.status_code != 200:
        handle_request_exception(deck.status_code, deck, 'Could not get deck!')

    json_deck = deck.json()
    if not is_own_deck(json_deck['owner_id']):
        raise werkzeug.exceptions.Forbidden("Not your deck!")

    resp = requests.delete(make_decks_url("/deck"), data={'deck_id': deck_id})
    if resp.status_code != 200:
        handle_request_exception(resp.status_code, resp, 'Could not delete deck!')
    send_statistics('DECK_DELETED')
    return redirect(url_for('get_decks'))


@app.route('/create_card', methods=['POST'])
@j.should_have_login
def create_card():
    deck_id = request.values['deck_id']
    card_front = request.values['card_front']
    card_back = request.values['card_back']

    resp = requests.post(make_decks_url('/deck/{0}/card', deck_id),
                         data={'front': card_front, 'back': card_back})
    if resp.status_code != 200:
        handle_request_exception(resp.status_code, resp, 'Could not create card!')
    return redirect(url_for('get_deck', deck_id=deck_id))


@app.route('/delete_card', methods=['POST'])
@j.should_have_login
def delete_card():
    card_id = request.values['card_id']
    deck_id = request.values['deck_id']
    resp = requests.delete(make_decks_url('/card'), data={'card_id': card_id})
    if resp.status_code != 200:
        handle_request_exception(resp.status_code, resp, 'Could not delete card')
    return redirect(url_for('get_deck', deck_id=deck_id))


@app.route('/deck/<int:deck_id>/learn', methods=['GET'])
@j.should_have_login
def learn(deck_id):
    resp = requests.get(make_decks_url('/deck/{0}/next', deck_id))
    if resp.status_code != 200:
        handle_request_exception(resp.status_code, resp, 'Could not get next card')
    next_card = resp.json()
    if 'status' in next_card and next_card['status'] == 'no more cards':
        return redirect(url_for('get_deck', deck_id=deck_id))
    return render_template('decks/session.html', card=next_card, deck_id=deck_id)

@app.route('/card/answered', methods=['POST'])
@j.should_have_login
def answered():
    card_id = request.values['card_id']
    answer = request.values['answer']
    deck_id = request.values['deck_id']

    resp = requests.post(make_decks_url('/card/{0}/answer', card_id), data={'answer': answer})
    if resp.status_code != 200:
        handle_request_exception(resp.status_code, resp, 'Could not send answer')

    return redirect(url_for('learn', deck_id=deck_id))
