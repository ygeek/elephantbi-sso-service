from flask import Blueprint, redirect
from flask_restful import Resource, reqparse, Api

from sso_service.logger import config_logger
from sso_service.utils.sso_utils import login_wx_user

logger = config_logger(__name__, 'info', 'sso.log')
sso_bp = Blueprint('sso', __name__)
api = Api(sso_bp)

# parser: WxRedirectHandler.get
wx_redirect_parser = reqparse.RequestParser()
wx_redirect_parser.add_argument(
    'redirect_url',
    type=str,
    required=True,
    location='args'
)

# parser: SSOHandler.get
sso_parser = reqparse.RequestParser()
sso_parser.add_argument(
    'auth_code',
    type=str,
    required=True,
    location='args'
)
sso_parser.add_argument(
    'env',
    type=str,
    required=True,
    location='args'
)


class WxRedirectHandler(Resource):

    def get(self):
        args = wx_redirect_parser.parse_args()
        logger.info('[WxRedirectHandler] GET starts, args: %s', args)

        # Params:
        redirect_url = args['redirect_url']

        response = redirect(redirect_url)

        return response


class SSOHandler(Resource):

    def get(self):
        args = sso_parser.parse_args()
        logger.info('[SSOHandler] GET starts, args: %s', args)

        # Params:
        auth_code = args['auth_code']
        env = args['env']

        access_token, wx_corp_id = login_wx_user(auth_code, env)

        redirect_url = {
            'develop': 'wx.flexceed.com',
            'stage': 'wx.visionpsn.com',
            'production': 'wx.elephantbi.com',
        }.get(env)

        response = {
            'corp_id': wx_corp_id,
            'access_token': access_token,
            'redirect_url': redirect_url
        }

        return response


api.add_resource(WxRedirectHandler, '/wx/redirect')
api.add_resource(SSOHandler, '/wx/sso')
