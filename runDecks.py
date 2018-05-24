from Decks import app as application, db, redis, inject

db.create_all()
inject.map(db=db)
inject.map(redis=redis)

if __name__ == '__main__':
    application.run(host="0.0.0.0", port=application.config['PORT'])
