from Decks import app, db, Card, Deck


@app.route('/deck/<int:deck_id>/next')
def get_next_card(deck_id):
    deck = Deck.query.filter_by(id=deck_id).first_or_404()





#@app.route('/api/person/<int:person_id>')
#def person(person_id):