from Decks import app, db, redis, inject

db.create_all()
inject.map(db=db)
inject.map(redis=redis)
app.run(host="0.0.0.0", port=app.config['PORT'])