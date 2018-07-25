from flask import Blueprint
from flask_restful import Resource, reqparse, Api

from sso_service.logger import config_logger
from sso_service.utils.sso_utils import login_wx_user

logger = config_logger(__name__, 'info', 'sso.log')
sso_bp = Blueprint('sso', __name__)
api = Api(sso_bp)

# parser: SSOHandler.get
sso_parser = reqparse.RequestParser()
sso_parser.add_argument(
    'auth_code',
    type=str,
    required=True,
    location='json'
)
sso_parser.add_argument(
    'redirect_url',
    type=str,
    required=True,
    location='json'
)
sso_parser.add_argument(
    'env',
    type=str,
    required=True,
)


class SSOHandler(Resource):

    def get(self):
        args = sso_parser.parse_args()
        logger.info('[SSOHandler] GET starts, args: %s', args)

        # Params:
        auth_code = args['auth_code']
        redirect_url = args['redirect_url']
        env = args['env']

        resp = login_wx_user(auth_code, redirect_url, env)

        return resp


api.add_resource(SSOHandler, '/wx/sso')
