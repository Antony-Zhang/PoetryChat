"""
文生图所需函数
"""
import os
import re

from PIL import Image
from io import BytesIO

import requests
import hmac
import hashlib
import base64
import json
import time
from urllib.parse import urlparse, urlencode

from dotenv import load_dotenv, find_dotenv

from get_path import get_file_path


# Authentication
def assemble_auth_url(method, addr, apiKey, apiSecret):
    if apiKey == "" and apiSecret == "":
        return addr

    url_parts = urlparse(addr)
    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    sign_string = f'host: {url_parts.netloc}\ndate: {date}\n{method} {url_parts.path} HTTP/1.1'
    sha = hmac_with_sha_to_base64("hmac-sha256", sign_string, apiSecret)
    auth_url = f'api_key="{apiKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{sha}"'
    authorization = base64.b64encode(auth_url.encode()).decode()
    query_params = urlencode({"host": url_parts.netloc, "date": date, "authorization": authorization})
    auth_addr = f"{addr}?{query_params}"
    return auth_addr


def hmac_with_sha_to_base64(algorithm, data, key):
    hmac_obj = hmac.new(key.encode(), data.encode(), hashlib.sha256)
    return base64.b64encode(hmac_obj.digest()).decode()


# HTTP Request
def http_tool(method, auth_addr, data, timeout):
    headers = {"content-type": "application/json;charset=UTF-8"}
    response = requests.post(auth_addr, data=data, headers=headers, timeout=timeout / 1000)
    return response.content, response.status_code


def gen_img(txt):
    """
    生图功能函数，输入诗句文本返回图片
    """
    # Constants
    addr = "https://spark-api.cn-huabei-1.xf-yun.com/v2.1/tti"
    load_dotenv(find_dotenv('.env'))
    appId = os.getenv("APPID_IMAGE")
    apiKey = os.getenv("APIKEY_IMAGE")
    apiSecret = os.getenv("APISECRET_IMAGE")
    # print("APISECRET_IMAGE:", apiSecret)

    # Data
    # txt = "无边落木萧萧下，不尽长江滚滚流。"

    # 将txt_img中的html标签和换行符\n去掉
    txt = txt.replace("\n", "")
    txt = re.sub(r"<[^>]*>", "", txt)

    content = "给我画一张关于诗句" + txt + "的画，要求光影色彩和谐，能体现诗词的意境美"
    reqMsg = [{"Content": content, "Role": "user"}]
    picture_name = txt + time.strftime('_%Y_%m_%d_%H_%M_%S_GMT', time.gmtime()) + ".jpg"
    # 生成完整的图片文件路径
    image_file_path = get_file_path(picture_name, "image")  # os.path.join("generated_images", picture_name)
    # print(image_file_path)

    req = {
        "header": {
            "app_id": appId,
            "uid": "tti_demo"
        },
        "parameter": {
            "chat": {
                "domain": "general"
            }
        },
        "payload": {
            "message": {
                "text": reqMsg
            }
        }
    }

    reqData = json.dumps(req)

    # Main
    auth_addr = assemble_auth_url("POST", addr, apiKey, apiSecret)
    # print(auth_addr)

    response_data, status_code = http_tool("POST", auth_addr, reqData.encode(), 7000)

    if status_code != 200:
        print(f"Request failed with status code {status_code}")
    else:
        # print(response_data.decode())

        result = json.loads(response_data)
        choices = result.get("payload", {}).get("choices", {}).get("text", [])
        if len(choices) > 0:
            base64_image = choices[0]["content"]
            image = base64.b64decode(base64_image)

            with open(image_file_path, "wb") as image_file:
                image_file.write(image)
                image_file.close()

    return image_file_path


if __name__ == '__main__':
    image_file_path = gen_img("欲把西湖比西子")

    # 打开图片文件
    with open(image_file_path, "rb") as image_file:
        image_data = image_file.read()

    image = Image.open(BytesIO(image_data))
    image.show()
    input("Press Enter to close the image...")

