from application import app, db, inject
import models
import views


if __name__ == '__main__':
#    db.drop_all()
    db.create_all()
    inject.map(db=db)
    app.run()
