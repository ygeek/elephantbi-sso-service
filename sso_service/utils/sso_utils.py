import os

from flask import redirect
from flask_jwt import _default_jwt_encode_handler as jwt_encoder

from sso_service import create_app
from sso_service.configuration import get_config
from sso_service.logger import config_logger
from sso_service.models import WxUser
from sso_service.utils.wx_api import WxAPI

logger = config_logger(__name__, 'info', 'wx.log')


def login_wx_user(auth_code, redirect_url, env):
    logger.info('[login_wx_user] auth_code: %s, redirect_url: %s, env: %s')

    # Map env:
    # env = {
    #     'dev': 'develop',
    #     'stage': 'stage',
    #     'prod': 'production',
    # }.get(env)

    # Create a flask  app instance
    flask_app = create_app(get_config(os.getenv(env)))
    with flask_app.app_context():
        login_info = get_user_login_info(auth_code)
        wx_user_id = login_info.get('user_info', {}).get('userid')
        if wx_user_id is None:
            return None

        wx_user = WxUser.query.filter(id=wx_user_id).first()
        if wx_user is None:
            return None

        user = wx_user.user
        access_token = jwt_encoder(user).decode('utf-8')
        logger.info('access_token: %s', access_token)

        response = redirect(redirect_url)
        domain = flask_app.config['SERVER_DOMAIN']
        cookie_domain = '.%s' % domain
        response.set_cookie('BI_TOKEN', access_token, domain=cookie_domain)

        return response


def get_user_login_info(auth_code):
    """获取登录用户信息"""
    logger.info('[get_user_login_info] auth_code: %s', auth_code)

    wx_api = WxAPI()

    login_info = wx_api.get_user_login_info(auth_code)

    logger.info('[get_user_login_info] auth_code: %s', auth_code)
    logger.info('[get_user_login_info] login_info: %s', login_info)

    return login_info
