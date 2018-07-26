from flask import g
from flask_jwt import JWTError
from werkzeug.security import check_password_hash

from sso_service.models import User


class Auth:

    @classmethod
    def error_handler(cls, e):
        raise JWTError(e, 'Auth failed')

    @classmethod
    def authenticate(cls, username, password):
        company_id = g.get('company').id
        if company_id is None:
            cls.error_handler('Bad request')

        user = User.query.filter_by(
            email=username, company_id=company_id).first()

        if not user:
            cls.error_handler('LOGIN_EMAIL_NOT_EXISTS')
        elif not check_password_hash(user.password, password):
            cls.error_handler('INVALID_CREDENTIALS')
        else:
            return user

    @staticmethod
    def identity(payload):
        user_id = payload['identity']
        user = User.query.filter_by(id=user_id).first()
        return user
