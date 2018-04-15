from Decks import app, db, redis, inject

db.create_all()
inject.map(db=db)
inject.map(redis=redis)
app.run(port=app.config['PORT'])