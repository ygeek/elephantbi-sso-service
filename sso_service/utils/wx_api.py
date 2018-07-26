import json
import os
from copy import deepcopy

import requests

from sso_service.logger import config_logger

logger = config_logger(__name__, 'info', 'wx_api.log')


def convert_response_keys(data):
    if type(data) != dict:
        return data

    data_copy = deepcopy(data)
    for old_key in data.keys():
        old_data = data_copy.pop(old_key)
        new_key = old_key.lower()
        new_data = convert_response_keys(old_data)
        data_copy[new_key] = new_data

    return data_copy


class WxAPI:
    # Request headers
    headers = {'content-type': 'application/json'}

    # API: 获取服务商的token
    GET_PROVIDER_TOKEN = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_provider_token'

    # API: 获取登录用户信息
    GET_USER_LOGIN_INFO = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_login_info?access_token={provider_access_token}'

    def __init__(self):
        self.corp_id = os.getenv('WX_CORP_ID')
        self.provider_secret = os.getenv('WX_PROVIDER_SECRET')

    def get_provider_token(self):
        """服务商的token

        以corpid、provider_secret（获取方法为：登录服务商管理后台->标准应用服务
        ->通用开发参数，可以看到）换取provider_access_token，代表的是服务商的身份，
        而与应用无关。请求单点登录、注册定制化等接口需要用到该凭证。

        返回结果：
        {
            "errcode":0 ,
            "errmsg":"ok" ,
            "provider_access_token":"enLSZ5xxxxxxJRL",
            "expires_in":7200
        }
        """
        data = {
            'corpid': self.corp_id,
            'provider_secret': self.provider_secret
        }
        resp = requests.post(WxAPI.GET_PROVIDER_TOKEN, data=json.dumps(data),
                             headers=WxAPI.headers)
        new_resp = convert_response_keys(json.loads(resp.text))

        provider_access_token = new_resp.get('provider_access_token')

        logger.info('provider_access_token: %s', provider_access_token)
        return provider_access_token

    def get_user_login_info(self, auth_code, access_token=None):
        """获取登录用户信息

        第三方可通过如下接口，获取登录用户的信息。建议用户以返回信息中的corpid及userid
        为主键匹配用户。

        返回结果：
        {
            "errcode": 0,
            "errmsg": "ok",
            "usertype": 1,
            "user_info": {
                "userid": "xxxx",
                "name": "xxxx",
                "avatar": "xxxx"
            },
            "corp_info": {
                "corpid": "wx6c698d13f7a409a4",
            },
            "agent": [
                {"agentid": 0, "auth_type": 1},
                {"agentid": 1, "auth_type": 1},
                {"agentid": 2, "auth_type": 1}
            ],
            "auth_info": {
                "department": [
                    {
                        "id": "2",
                        "writable": "true"
                    }
                ]
            }
        }
        """
        if access_token is None:
            access_token = self.get_provider_token()

        url = WxAPI.GET_USER_LOGIN_INFO.format(
            provider_access_token=access_token
        )
        data = {
            'auth_code': auth_code
        }

        resp = requests.post(url, data=json.dumps(data), headers=WxAPI.headers)
        new_resp = convert_response_keys(json.loads(resp.text))

        return new_resp
