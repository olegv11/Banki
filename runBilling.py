from Billing import app as application, db

db.create_all()

if __name__ == '__main__':
    application.run(host="0.0.0.0", port=application.config['PORT'])
