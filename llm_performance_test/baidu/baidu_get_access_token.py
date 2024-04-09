import os
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
baidu_api_key = os.environ['BAIDU_API_KEY']
baidu_secret_key = os.environ['BAIDU_SECRET_KEY']


# https://ai.baidu.com/ai-doc/REFERENCE/Ck3dwjhhu 鉴权认证机制
def get_access_token():
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={baidu_api_key}&client_secret={baidu_secret_key}"

    payload = ""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json().get("access_token")


if __name__ == '__main__':
    print(get_access_token())
