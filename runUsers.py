from Users import app as application, db, inject

db.create_all()
inject.map(db=db)
if __name__ == '__main__':
    application.run(host="0.0.0.0", port=application.config['PORT'])
