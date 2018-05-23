from Users import app, db, inject

db.create_all()
inject.map(db=db)
app.run(host="0.0.0.0", port=app.config['PORT'])
