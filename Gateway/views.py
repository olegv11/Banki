from Gateway.application import app, j
from flask import request, jsonify, g, redirect, url_for
import werkzeug.exceptions
import requests


def make_decks_url(p, *args):
    return app.config['DECKS_URL'] + p.format(*args)

@app.route('/deck/<int:deck_id>')
@j.should_have_login
def get_deck(deck_id):
    deck = requests.get(make_decks_url("/deck/{0}", deck_id))
    print(deck)