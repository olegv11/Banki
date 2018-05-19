from Users import app, db, inject

db.drop_all()
db.create_all()
inject.map(db=db)
app.run(port=app.config['PORT'])
