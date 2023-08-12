"""
    交互的参数模块
"""
import _thread as thread
import base64
import datetime
import hashlib
import hmac
from urllib.parse import urlparse
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time


class WsParamGPT(object):
    """
    交互参数类(GPT)
    """
    def __init__(self, url, app_id, api_key, api_secret):
        self.url = url
        self.host = urlparse(self.url).netloc
        self.path = urlparse(self.url).path
        self.APPID = app_id
        self.APIKey = api_key
        self.APISecret = api_secret

    def create_signature_origin(self, date) -> str:
        """拼接字符串,得到初始签名signature_origin"""
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"    # GPT交互使用Get
        return signature_origin

    def create_url(self):
        """
        生成url [host主机 + date时间戳(RFC1123格式) + authorization认证信息]
        """
        # print("create_url启动")
        # (可对参数进行逐步打印确认)
        # 生成参数:时间戳date(RFC1123格式)
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 生成参数:认证信息authorization(base64编码)
        signature_origin = self.create_signature_origin(date)
        # 进行hmac-sha256算法进行加密; 得到签名的摘要signature_sha
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        # 进行base64编码生成签名signature_sha_base64
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        # 将字符串拼接成原始认证
        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", ' \
                               f'signature="{signature_sha_base64}"'

        # 进行base64编码生成最终认证信息authorization
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url_final = self.url + '?' + urlencode(v)
        # print("create_url完成")
        return url_final


class WsParamEmb(WsParamGPT):
    """
    交互参数类（Embedding）
    """
    def __init__(self, url, app_id, api_key, api_secret):
        super(WsParamEmb, self).__init__(url, app_id, api_key, api_secret)

    def create_signature_origin(self, date) -> str:
        """拼接字符串,得到初始签名signature_origin"""
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "POST " + self.path + " HTTP/1.1"   # Embedding交互使用Post
        return signature_origin


def gen_params_gpt(appid, question):
    """
        通过appid和用户的提问, 生成请求参数
        """
    # print("gen_params启动")
    data = {
        "header": {
            "app_id": appid,  # AppID
            "uid": "1234"  # 用于区分不同的用户
        },
        "parameter": {
            "chat": {
                "domain": "general",  # (必)指定访问的领域
                "random_threshold": 0,  # 温度系数temperature
                "max_tokens": 2048,  # 模型回答的tokens的最大长度,范围为[1,4096]
                "auditing": "default"
                # "top_k": 4                # 从k个候选中随机选择⼀个（⾮等概率）,范围为[1,6]
                # "chat_id": "1234"         # 用于关联用户会话,需要保障用户对话的唯一性
            }
        },
        "payload": {
            "message": {
                "text": [
                    {
                        "role": "user",  # 对话角色,范围为[user,assistant]
                        "content": question  # 用户和AI的对话内容,text下所有content累计tokens需要控制在8192内
                    }
                ]
            }
        }
    }
    # print("gen_params完成")
    return data
