from Statistics import app, db

db.create_all()
app.run(port=app.config['PORT'])