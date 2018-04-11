from application import app, db, redis, inject
import models
import views


if __name__ == '__main__':
#    db.drop_all()
    db.create_all()
    inject.map(db=db)
    inject.map(redis=redis)
    app.run()
