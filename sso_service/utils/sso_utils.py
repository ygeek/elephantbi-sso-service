from flask import redirect
from flask_jwt import _default_jwt_encode_handler as jwt_encoder

from sso_service import create_app
from sso_service.configuration import get_config
from sso_service.logger import config_logger
from sso_service.models import WxUser, WxCorp, User
from sso_service.utils.wx_api import WxAPI

logger = config_logger(__name__, 'info', 'wx.log')


def login_wx_user(auth_code, redirect_url, env):
    logger.info('[login_wx_user] auth_code: %s, redirect_url: %s, env: %s',
                auth_code, redirect_url, env)

    # Map env:
    # env = {
    #     'dev': 'develop',
    #     'stage': 'stage',
    #     'prod': 'production',
    # }.get(env)

    # Create a flask  app instance
    flask_app = create_app(get_config(env))
    with flask_app.app_context():
        login_info = get_user_login_info(auth_code)
        wx_user_id = login_info.get('user_info', {}).get('userid')
        wx_corp_id = login_info.get('corp_info', {}).get('corpid')
        if wx_user_id is None:
            logger.error('wx_user_id is None')
            return None

        if wx_corp_id is None:
            logger.error('wx_corp_id is None')
            return None

        wx_corp = WxCorp.query.filter(WxCorp.id == wx_corp_id).first()
        if wx_corp is None:
            logger.error('wx_corp is None')
            return None

        user = User.query.join(
            WxUser,
            User.id == WxUser.user_id
        ).filter(
            User.company_id == wx_corp.company_id,
            WxUser.id == wx_user_id
        ).first()

        if user is None:
            logger.error('user is None')
            return None

        access_token = jwt_encoder(user).decode('utf-8')
        logger.info('access_token: %s', access_token)

        domain = flask_app.config['SERVER_DOMAIN']
        logger.info('domain: %s', domain)
        cookie_domain = '.%s' % domain

    response = redirect(redirect_url)
    response.set_cookie('BI_TOKEN', access_token, domain=cookie_domain)
    response.set_cookie('BI_CORP_ID', wx_corp_id, domain=cookie_domain)

    return response


def get_user_login_info(auth_code):
    """获取登录用户信息"""
    logger.info('[get_user_login_info] auth_code: %s', auth_code)

    wx_api = WxAPI()

    login_info = wx_api.get_user_login_info(auth_code)

    logger.info('[get_user_login_info] auth_code: %s', auth_code)
    logger.info('[get_user_login_info] login_info: %s', login_info)

    return login_info
