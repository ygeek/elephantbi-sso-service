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

    # API: 第三方应用接口
    GET_SUITE_TOKEN = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_suite_token'
    GET_PERMANENT_CODE = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_permanent_code?suite_access_token={suite_access_token}'
    GET_AUTH_INFO = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_auth_info?suite_access_token={suite_access_token}'
    GET_CORP_TOKEN = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_corp_token?suite_access_token={suite_access_token}'
    GET_USER_INFO = 'https://qyapi.weixin.qq.com/cgi-bin/service/getuserinfo3rd?access_token={suite_access_token}&code={code}'
    GET_USER_DETAIL = 'https://qyapi.weixin.qq.com/cgi-bin/service/getuserdetail3rd?access_token={suite_access_token}'
    GET_PRE_AUTH_CODE = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_pre_auth_code?suite_access_token={suite_access_token}'
    SET_SESSION_INFO = 'https://qyapi.weixin.qq.com/cgi-bin/service/set_session_info?suite_access_token={suite_access_token}'

    # API: 获取服务商的token
    GET_PROVIDER_TOKEN = ' https://qyapi.weixin.qq.com/cgi-bin/service/get_provider_token'

    # API: 获取登录用户信息
    GET_USER_LOGIN_INFO = 'https://qyapi.weixin.qq.com/cgi-bin/service/get_login_info?access_token={provider_access_token}'

    # API: 通讯录管理
    GET_CORP_USER_DETAIL = 'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token={access_token}&userid={userid}'
    GET_CORP_USER_LIST = 'https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token={access_token}&department_id={department_id}&fetch_child={fetch_child}'

    # API: 发送消息
    SEND_MESSAGE = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'

    # JS-SDK
    GET_JSAPI_TICKET = 'https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket?access_token={access_token}'

    # API: 上传临时素材
    UPLOAD_MEDIA = 'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type={media_type}'

    def __init__(self, suite_id=None, suite_secret=None, corp_id=None,
                 provider_secret=None):
        self.suite_id = suite_id or os.getenv('WX_SUITE_ID')
        self.suite_secret = suite_secret or os.getenv('WX_SUITE_SECRET')
        self.corp_id = corp_id or os.getenv('WX_CORP_ID')
        self.provider_secret = provider_secret or os.getenv(
            'WX_PROVIDER_SECRET')

    def get_suite_token(self, suite_ticket):
        """获取第三方应用凭证"""
        url = WxAPI.GET_SUITE_TOKEN
        data = {
            "suite_id": self.suite_id,
            "suite_secret": self.suite_secret,
            "suite_ticket": suite_ticket
        }

        resp = requests.post(url, data=json.dumps(data),
                             headers=WxAPI.headers)

        logger.info('status_code: %s', resp.status_code)
        logger.info('text: %s', resp.text)

        resp_data = json.loads(resp.text)
        suite_access_token = resp_data.get('suite_access_token')

        return suite_access_token

    def get_install_qr_code_link(self, pre_auth_code, redirect_uri):
        """构造授权链接

        引导用户进入授权页面完成授权过程，并取得临时授权码。
        """
        link_fmt = 'https://open.work.weixin.qq.com/3rdapp/install?suite_id={suite_id}&pre_auth_code={pre_auth_code}&redirect_uri={redirect_uri}'

        return link_fmt.format(
            suite_id=self.suite_id,
            pre_auth_code=pre_auth_code,
            redirect_uri=redirect_uri
        )

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

        return new_resp

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

    @classmethod
    def get_permanent_code(cls, suite_access_token, auth_code):
        """获取企业永久授权码"""
        url = WxAPI.GET_PERMANENT_CODE.format(
            suite_access_token=suite_access_token)
        data = {
            'auth_code': auth_code
        }

        resp = requests.post(url, data=json.dumps(data), headers=WxAPI.headers)
        new_resp = convert_response_keys(json.loads(resp.text))

        return new_resp

    @classmethod
    def get_auth_info(cls, suite_access_token, permanent_code, auth_corpid):
        """获取企业授权信息"""
        url = WxAPI.GET_AUTH_INFO.format(suite_access_token=suite_access_token)
        data = {
            "auth_corpid": auth_corpid,
            "permanent_code": permanent_code
        }

        resp = requests.post(url, data=json.dumps(data), headers=WxAPI.headers)
        new_resp = convert_response_keys(json.loads(resp.text))

        return new_resp

    @classmethod
    def get_corp_token(cls, suite_access_token, auth_corpid, permanent_code):
        """获取企业access_token"""
        url = WxAPI.GET_CORP_TOKEN.format(suite_access_token=suite_access_token)
        data = {
            "auth_corpid": auth_corpid,
            "permanent_code": permanent_code
        }

        resp = requests.post(url, data=json.dumps(data), headers=WxAPI.headers)
        new_resp = convert_response_keys(json.loads(resp.text))

        return new_resp

    @classmethod
    def get_user_info_3rd(cls, suite_access_token, code):
        """第三方根据code获取企业成员信息"""
        url = WxAPI.GET_USER_INFO.format(
            suite_access_token=suite_access_token,
            code=code
        )

        resp = requests.get(url)
        new_resp = convert_response_keys(json.loads(resp.text))

        return new_resp

    @classmethod
    def get_user_detail(cls, suite_access_token, user_ticket):
        """第三方使用user_ticket获取成员详情"""
        url = WxAPI.GET_USER_DETAIL.format(
            suite_access_token=suite_access_token
        )
        data = {
            'user_ticket': user_ticket
        }

        resp = requests.post(url, data=json.dumps(data))
        new_resp = convert_response_keys(json.loads(resp.text))

        return new_resp

    @classmethod
    def get_corp_user_detail(cls, access_token, userid):
        """读取成员"""
        url = WxAPI.GET_CORP_USER_DETAIL.format(
            access_token=access_token,
            userid=userid
        )

        resp = requests.get(url)
        new_resp = convert_response_keys(json.loads(resp.text))

        return new_resp

    @classmethod
    def get_corp_user_list(cls, access_token, department_id, fetch_child=0):
        """获取部门成员详情"""
        url = WxAPI.GET_CORP_USER_LIST.format(
            access_token=access_token,
            department_id=department_id,
            fetch_child=fetch_child
        )

        resp = requests.get(url)
        new_resp = convert_response_keys(json.loads(resp.text))

        return new_resp

    @classmethod
    def send_message(cls, access_token, post_data):
        """发送应用消息"""
        url = WxAPI.SEND_MESSAGE.format(access_token=access_token)

        resp = requests.post(url, data=json.dumps(post_data))
        new_resp = convert_response_keys(json.loads(resp.text))

        return new_resp

    @classmethod
    def get_jsapi_ticket(cls, access_token):
        """获取jsapi_ticket"""
        url = WxAPI.GET_JSAPI_TICKET.format(access_token=access_token)

        resp = requests.get(url)
        new_resp = convert_response_keys(json.loads(resp.text))

        return new_resp

    @classmethod
    def get_pre_auth_code(cls, suite_access_token):
        """获取预授权码

        该API用于获取预授权码。预授权码用于企业授权时的第三方服务商安全验证。

        返回结果：
        {
            "errcode":0 ,
            "errmsg":"ok" ,
            "pre_auth_code":"Cx_Dk6qiBE0Dmx4EmlT3oRfArPvwSQ-oa3NL_fwHM7VI08r52wazoZX2Rhpz1dEw",
            "expires_in":1200
        }
        """
        url = WxAPI.GET_PRE_AUTH_CODE.format(
            suite_access_token=suite_access_token
        )

        resp = requests.get(url)
        new_resp = convert_response_keys(json.loads(resp.text))

        return new_resp

    @classmethod
    def set_session_info(cls, suite_access_token, pre_auth_code, session_info):
        """设置授权配置

        该接口可对某次授权进行配置。可支持测试模式（应用未发布时）。

        返回结果：
        {
            "errcode": 0,
            "errmsg": "ok"
        }
        """
        url = WxAPI.SET_SESSION_INFO.format(
            suite_access_token=suite_access_token
        )
        post_data = {
            'pre_auth_code': pre_auth_code,
            'session_info': session_info
        }

        resp = requests.post(url, data=json.dumps(post_data),
                             headers=WxAPI.headers)
        new_resp = convert_response_keys(json.loads(resp.text))

        return new_resp
