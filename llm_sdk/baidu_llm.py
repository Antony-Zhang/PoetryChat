import json
from typing import Any, List, Optional
from config.config import config
import requests
from langchain.callbacks.manager import CallbackManagerForLLMRun
from llm_sdk.base_llm import Base_LLM


# 获取文心access_token的函数 get_access_token()
def get_access_token(baidu_api_key: str, baidu_secret_key: str):
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={baidu_api_key}&client_secret={baidu_secret_key}"

    payload = ""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json().get("access_token")


class Baidu_LLM(Base_LLM):
    # 百度系列大模型的自定义 LLM
    # URL
    url: str = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token={}"
    # api_key 继承自Base_LLM
    # Secret_Key
    secret_key: str = None
    # access_token
    access_token: str = None

    def init_access_token(self):
        if self.api_key != None and self.secret_key != None:
            # 两个 Key 均非空才可以获取 access_token
            try:
                self.access_token = get_access_token(self.api_key, self.secret_key)
            except Exception as e:
                print(e)
                print("获取 access_token 失败，请检查 Key")
        else:
            print("API_Key 或 Secret_Key 为空，请检查 Key")

    def _call(self, prompt: str, stop: Optional[List[str]] = None,
              run_manager: Optional[CallbackManagerForLLMRun] = None,
              **kwargs: Any):
        # 如果 access_token 为空，初始化 access_token
        if self.access_token is None:
            self.init_access_token()
        # API 调用 url
        url = self.url.format(self.access_token)
        # 配置 POST 参数
        payload = json.dumps({
            "system": config.system_prompt,  # system message
            "messages": [
                {
                    "role": "user",
                    "content": "{}".format(prompt)
                }
            ],
            'temperature': self.temperature
        })
        headers = {
            'Content-Type': 'application/json'
        }
        # 发起请求
        response = requests.request("POST", url, headers=headers, data=payload, timeout=self.request_timeout)
        if response.status_code == 200:
            # 返回的是一个 Json 字符串
            js = json.loads(response.text)
            return js["result"]
        else:
            return "请求失败"

    @property
    def _llm_type(self) -> str:
        return "Baidu"
