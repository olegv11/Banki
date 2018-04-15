from Users import app, db, inject

db.create_all()
inject.map(db=db)
app.run(port=app.config['PORT'])
