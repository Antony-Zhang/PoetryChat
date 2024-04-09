import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
import os
import queue
import ssl
from datetime import datetime
from time import mktime
from config.config import config
from urllib.parse import urlencode
from urllib.parse import urlparse
from wsgiref.handlers import format_date_time

import requests
import websocket  # 使用websocket_client
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from zhipuai import ZhipuAI


def get_completion(prompt: str, model: str, temperature=0.1, api_key=None, secret_key=None, access_token=None,
                   appid=None, api_secret=None, max_tokens=2048):
    # 调用LLM获取回复，支持baidu,openai,spark,zhipu
    # arguments:
    # prompt: 输入提示
    # model：模型名
    # temperature: 温度系数
    # api_key：api_key
    # secret_key, access_token：调用文心系列模型需要
    # appid, api_secret: 调用星火系列模型需要
    # max_tokens : 返回最长序列
    # return: 模型返回，字符串

    if model in ["gpt-3.5-turbo", "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-0613", "gpt-4", "gpt-4-32k"]:
        return get_completion_openai(prompt, model, temperature, api_key, max_tokens)
    elif model in ["ERNIE-4.0-8K", "ERNIE-3.5-8K", "ERNIE-3.5-8K-0205"]:  # 3.5的模型调用未完成，参考下面的todo
        return get_completion_baidu(prompt, model, temperature, api_key, secret_key)
    elif model in ["Spark-3.5", "Spark-3.0"]:
        return get_completion_spark(prompt, model, temperature, api_key, appid, api_secret, max_tokens)
    elif model in ["glm-4", "glm-3-turbo"]:
        return get_completion_zhipu(prompt, model, temperature, api_key, max_tokens)
    else:
        return "incorrect model name!"


def get_completion_openai(prompt: str, model: str, temperature: float, api_key: str, max_tokens: int):
    if api_key is None:
        api_key = parse_llm_api_key("openai")

    client = OpenAI(api_key=api_key)
    # 具体调用
    messages = [
        {"role": "system", "content": config.system_prompt},
        {"role": "user", "content": prompt}
    ]

    # 调用 ChatCompletion 接口
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content


def get_access_token(api_key, secret_key):
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """
    # 指定网址
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
    # 设置 POST 访问
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    # 通过 POST 访问获取账户对应的 access_token
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")


def get_completion_baidu(prompt: str, model: str, temperature: float, api_key: str, secret_key: str):
    if api_key is None or secret_key is None:
        api_key, secret_key = parse_llm_api_key("baidu")
    # 获取access_token
    access_token = get_access_token(api_key, secret_key)
    # 调用接口
    # todo url 参考文档不同模型对应不同的配置调用
    url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token={access_token}"
    # 配置 POST 参数
    payload = json.dumps({
        "system": config.system_prompt,
        "messages": [
            {
                "role": "user",
                "content": "{}".format(prompt)
            }
        ],
        "temperature": temperature
    })
    headers = {
        'Content-Type': 'application/json'
    }
    # 发起请求
    response = requests.request("POST", url, headers=headers, data=payload)
    # 返回的是一个 Json 字符串
    js = json.loads(response.text)
    return js["result"]


def get_completion_spark(prompt: str, model: str, temperature: float, api_key: str, appid: str, api_secret: str,
                         max_tokens: int):
    if api_key is None or appid is None and api_secret is None:
        api_key, appid, api_secret = parse_llm_api_key("spark")

    # 配置 v3.5 和 v3 的不同请求参数
    if model == "Spark-v3.5":
        domain = "generalv3.5"  # v3.5版本
        spark_url = "ws://spark-api.xf-yun.com/v3.5/chat"  # v3.5环境的地址
    else:
        domain = "generalv3"  # v3.0版本
        spark_url = "ws://spark-api.xf-yun.com/v3.1/chat"  # v2.0环境的地址

    question = [
        {"role": "system", "content": config.system_prompt},
        {"role": "user", "content": prompt}
    ]
    response = spark_main(appid, api_key, api_secret, spark_url, domain, question, temperature, max_tokens)
    return response


def get_completion_zhipu(prompt: str, model: str, temperature: float, api_key: str, max_tokens: int):
    if api_key is None:
        api_key = parse_llm_api_key("zhipu")
    client = ZhipuAI(api_key=api_key)
    model = "glm-4"
    # 构造消息
    messages = [
        {"role": "system", "content": config.system_prompt},
        {"role": "user", "content": prompt},
    ]

    # 调用 ChatCompletion 接口
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )

    return response.choices[0].message.content


# 星火 API 调用使用
answer = ""


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(spark_url).netloc
        self.path = urlparse(spark_url).path
        self.spark_url = spark_url
        # 自定义
        self.temperature = 0
        self.max_tokens = 2048

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
        url = self.spark_url + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url


# 收到websocket错误的处理
def on_error(ws, error):
    pass


# 收到websocket关闭的处理
def on_close(ws, one, two):
    pass


# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    data = json.dumps(gen_params(appid=ws.appid, domain=ws.domain, question=ws.question, temperature=ws.temperature,
                                 max_tokens=ws.max_tokens))
    ws.send(data)


# 收到websocket消息的处理
def on_message(ws, message):
    # print(message)
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        print(content, end="")
        global answer
        answer += content
        # print(1)
        if status == 2:
            ws.close()


def gen_params(appid, domain, question, temperature, max_tokens):
    """
    通过appid和用户的提问来生成请参数
    """
    data = {
        "header": {
            "app_id": appid,
            "uid": "1234"
        },
        "parameter": {
            "chat": {
                "domain": domain,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text": question
            }
        }
    }
    return data


def spark_main(appid, api_key, api_secret, spark_url, domain, question, temperature, max_tokens):
    output_queue = queue.Queue()

    def on_message(ws, message):
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
            # 将输出值放入队列
            output_queue.put(content)
            if status == 2:
                ws.close()

    wsParam = Ws_Param(appid, api_key, api_secret, spark_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    ws.question = question
    ws.domain = domain
    ws.temperature = temperature
    ws.max_tokens = max_tokens
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    return ''.join([output_queue.get() for _ in range(output_queue.qsize())])


def parse_llm_api_key(model: str):
    # 从环境变量中获取API Key，注意自己的.env文件
    load_dotenv(find_dotenv())
    if model == "openai":
        return os.environ["OPENAI_API_KEY"]
    elif model == "baidu":
        return os.environ["BAIDU_SECRET_KEY"], os.environ["BAIDU_ACCESS_TOKEN"]
    elif model == "spark":
        return os.environ["SPARKCHAT_APIKEY"], os.environ["SPARKCHAT_APPID"], os.environ["SPARKCHAT_APISECRET"]
    elif model == "zhipu":
        return os.environ["ZHIPU_API_KEY"]
    else:
        raise ValueError(f"model{model} not supported!!!")
