# -*- encoding:utf-8 -*-
import os
from dotenv import load_dotenv, find_dotenv
import hashlib
import hmac
import base64
from socket import *
import json, time, threading
from websocket import create_connection
import websocket
from urllib.parse import quote
import logging

# reload(sys)
# sys.setdefaultencoding("utf8")
class Client():
    def __init__(self):
        base_url = "ws://rtasr.xfyun.cn/v1/ws"
        ts = str(int(time.time()))
        tt = (app_id + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')

        apiKey = api_key.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        self.end_tag = "{\"end\": true}"

        self.ws = create_connection(base_url + "?appid=" + app_id + "&ts=" + ts + "&signa=" + quote(signa))
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()

    def send(self, file_path):
        file_object = open(file_path, 'rb')
        try:
            index = 1
            while True:
                chunk = file_object.read(1280)
                if not chunk:
                    break
                self.ws.send(chunk)

                index += 1
                time.sleep(0.04)
        finally:
            file_object.close()

        self.ws.send(bytes(self.end_tag.encode('utf-8')))
        print("send end tag success")

    def recv(self):
        try:
            while self.ws.connected:
                result = str(self.ws.recv())
                if len(result) == 0:
                    print("receive result end")
                    break
                result_dict = json.loads(result)
                # 解析结果
                if result_dict["action"] == "started":
                    print("handshake success, result: " + result)

                if result_dict["action"] == "result":
                    result_1 = result_dict
                    # result_2 = json.loads(result_1["cn"])
                    # result_3 = json.loads(result_2["st"])
                    # result_4 = json.loads(result_3["rt"])
                    print("rtasr result: " + result_1["data"])

                if result_dict["action"] == "error":
                    print("rtasr error: " + result)
                    self.ws.close()
                    return
        except websocket.WebSocketConnectionClosedException:
            print("receive result end")

    def close(self):
        self.ws.close()
        print("connection closed")


if __name__ == '__main__':
    logging.basicConfig()
    load_dotenv(find_dotenv('.env'))
    appId = os.getenv("APPID_ASR")
    apiKey = os.getenv("APIKEY_ASR")

    app_id = appId
    api_key = apiKey
    file_path = r"./test_1.pcm"

    client = Client()
    client.send(file_path)
