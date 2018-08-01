from flask_jwt import _default_jwt_encode_handler as jwt_encoder

from sso_service import create_app
from sso_service.configuration import get_config
from sso_service.logger import config_logger
from sso_service.models import WxUser, WxCorp, User
from sso_service.utils.wx_api import WxAPI

logger = config_logger(__name__, 'info', 'sso.log')


def login_wx_user(auth_code, env):
    logger.info('[login_wx_user] auth_code: %s, env: %s', auth_code, env)

    # Map env:
    # env = {
    #     'dev': 'develop',
    #     'stage': 'stage',
    #     'prod': 'production',
    # }.get(env)

    data = {
        'access_token': None,
        'corp_id': None,
        'err_code': '0',
        'err_msg': 'success',
    }

    # Create a flask  app instance
    flask_app = create_app(get_config(env))
    with flask_app.app_context():
        login_info = get_user_login_info(auth_code)
        wx_user_id = login_info.get('user_info', {}).get('userid')
        wx_corp_id = login_info.get('corp_info', {}).get('corpid')
        if wx_user_id is None:
            logger.error('wx_user_id is None')
            data.update({
                'err_code': '-2',
                'err_msg': 'wx_user_id is null'
            })
            return data

        if wx_corp_id is None:
            logger.error('wx_corp_id is None')
            data.update({
                'err_code': '-3',
                'err_msg': 'wx_corp_id is null'
            })
            return data

        wx_corp = WxCorp.query.filter(WxCorp.id == wx_corp_id).first()
        if wx_corp is None:
            # Will redirect user to app installation link
            logger.error('wx_corp is None')
            data.update({
                'err_code': '-1',
                'err_msg': 'wx_corp is null'
            })
            return data

        user = User.query.join(
            WxUser,
            User.id == WxUser.user_id
        ).filter(
            User.company_id == wx_corp.company_id,
            WxUser.id == wx_user_id
        ).first()

        if user is None:
            logger.error('user is None')
            data.update({
                'err_code': '-4',
                'err_msg': 'user is null'
            })
            return None

        access_token = jwt_encoder(user).decode('utf-8')
        logger.info('access_token: %s', access_token)
        data.update({
            'access_token': access_token,
            'corp_id': wx_corp_id
        })

    return data


def get_user_login_info(auth_code):
    """获取登录用户信息"""
    logger.info('[get_user_login_info] auth_code: %s', auth_code)

    wx_api = WxAPI()

    login_info = wx_api.get_user_login_info(auth_code)

    logger.info('[get_user_login_info] auth_code: %s', auth_code)
    logger.info('[get_user_login_info] login_info: %s', login_info)

    return login_info
