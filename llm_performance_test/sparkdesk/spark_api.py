import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
import os
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from urllib.parse import urlparse
from wsgiref.handlers import format_date_time
from config.config import config
import websocket
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
sparkchat_appid = os.environ['SPARKCHAT_APPID']
sparkchat_apisecret = os.environ['SPARKCHAT_APISECRET']
sparkchat_apikey = os.environ['SPARKCHAT_APIKEY']


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, gpt_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(gpt_url).netloc
        self.path = urlparse(gpt_url).path
        self.gpt_url = gpt_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.gpt_url + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url


# 收到websocket错误的处理
def on_error(ws, error):
    # print("### error:", error)
    pass


# 收到websocket关闭的处理
def on_close(ws):
    # print("### closed ###")
    pass


# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    data = json.dumps(gen_params(appid=ws.appid, prompt=ws.prompt, domain=ws.domain))
    ws.send(data)


# 全局变量
global_contents = []


# 收到websocket消息的处理
def on_message(ws, message):
    # print(message)
    global global_contents
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        # print(content, end='')
        if status == 2:
            # print("#### 关闭会话")
            ws.close()
        # 将content存储到全局变量中
        global_contents.append(content)


def gen_params(appid, prompt, domain):
    """
    通过appid和用户的提问来生成请参数
    """

    data = {
        "header": {
            "app_id": appid,
            "uid": "1234",
            # "patch_id": []    #接入微调模型，对应服务发布后的resourceid          
        },
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": 0.1,
                "max_tokens": 4096,
                "auditing": "default",
            }
        },
        "payload": {
            "message": {
                "text": [
                    {"role": "system", "content": config.system_prompt},
                    {"role": "user", "content": prompt}
                ]
            }
        }
    }
    return data


# 接口文档 https://www.xfyun.cn/doc/spark/Web.html
def get_completion_spark(prompt, max_tokens=4096, temperature=0.1):
    global global_contents
    # 在每次调用get_completion_spark时清空全局列表
    global_contents = []

    appid = sparkchat_appid
    api_secret = sparkchat_apisecret
    api_key = sparkchat_apikey
    gpt_url = "wss://spark-api.xf-yun.com/v3.5/chat"
    domain = "generalv3.5"
    wsParam = Ws_Param(appid, api_key, api_secret, gpt_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()

    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    ws.prompt = prompt
    ws.domain = domain
    ws.temperature = temperature
    ws.max_tokens = max_tokens
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    # 将全局列表中的所有元素拼接成一个字符串并返回
    return ''.join(global_contents)


if __name__ == "__main__":
    prompt = config.user_prompt
    print(get_completion_spark(prompt))
