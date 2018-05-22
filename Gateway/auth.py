import datetime
import jwt
import werkzeug.exceptions
from functools import wraps
from flask import g, request


class Jwt(object):
    def __init__(self, app):
        self.app = app
        self.secret = app.config['SECRET_KEY']

        @app.before_request
        def get_user_data():
            self.__get_user_data(request)

        @app.after_request
        def update_jwt(response):
            updated = self.__update_token()
            if updated is not None:
                response.set_cookie('jwttoken', updated)
            return response

    def set_token(self, response, user_id, name, mail, role):
        token = self.__encode(user_id, name, mail, role)
        response.set_cookie('jwttoken', token)

    def erase_token(self, response):
        if g.user_data is not None:
            g.user_data = None
        response.set_cookie('jwttoken', '', expires=0)

    def __encode(self, user_id, name, mail, role):
        payload = {'user_id': user_id, 'name': name, 'mail': mail, 'role': role,
                   'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)}
        return jwt.encode(payload, self.secret)

    def __decode(self, payload):
        try:
            return jwt.decode(payload, self.secret)
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def __get_user_data(self, request):
        g.jwt_token = request.cookies.get('jwttoken')
        if g.jwt_token is None:
            g.user_data = None
            return
        g.user_data = self.__decode(g.jwt_token)

    def should_have_role(self, role='user'):
        def should_have_role_inner(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if g.jwt_token is None:
                    raise werkzeug.exceptions.Unauthorized("User doesn't have cookie!")
                if g.user_data is None:
                    raise werkzeug.exceptions.Unauthorized("User's token is invalid!")
                if role not in g.user_data['role']:
                    raise werkzeug.exceptions.Forbidden("User does not have necessary role!")
                return f(*args, **kwargs)
            return decorated_function
        return should_have_role_inner

    def should_have_login(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.jwt_token is None:
                raise werkzeug.exceptions.Unauthorized("User doesn't have cookie!")
            if g.user_data is None:
                raise werkzeug.exceptions.Unauthorized("User's token is invalid!")
            return f(*args, **kwargs)
        return decorated_function

    def __update_token(self):
        if g.user_data is None:
            return
        updated = self.__encode(
            g.user_data['user_id'], g.user_data['name'], g.user_data['mail'], g.user_data['role'])
        return updated
