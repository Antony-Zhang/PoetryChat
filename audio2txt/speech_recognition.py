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
import pyaudio
import keyboard
import re


class Client():
    def __init__(self):
        logging.basicConfig()

        load_dotenv(find_dotenv('.env'))
        appId = os.getenv("APPID_ASR")
        apiKey = os.getenv("APIKEY_ASR")

        self.app_id = appId
        self.api_key = apiKey
        base_url = "ws://rtasr.xfyun.cn/v1/ws"

        ts = str(int(time.time()))
        tt = (self.app_id + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')

        apiKey = self.api_key.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        self.end_tag = "{\"end\": true}"

        self.ws = create_connection(base_url + "?appid=" + self.app_id + "&ts=" + ts + "&signa=" + quote(signa))
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()
        self.recording = False  # 用于跟踪录制状态
        self.max_duration = 30  # 最大录制时长，以秒为单位

    def send(self):
        CHUNK = 300  # 定义数据流块
        FORMAT = pyaudio.paInt16  # 16bit编码格式
        CHANNELS = 1  # 单声道
        RATE = 16000  # 16000采样频率
        p = pyaudio.PyAudio()
        # 创建音频流
        stream = p.open(format=FORMAT,  # 音频流wav格式
                        channels=CHANNELS,  # 单声道
                        rate=RATE,  # 采样率16000
                        input=True,
                        frames_per_buffer=CHUNK)

        print("- - - - - - - Press and hold the space bar to start recording - - - - - - - ")
        while True:
            if keyboard.is_pressed("space"):  # 检测空格键是否被按下
                if not self.recording:
                    print("- - - - - - - Start Recording - - - - - - - ")
                    self.recording = True
                    start_time = time.time()
            else:
                if self.recording:
                    print("- - - - - - - Stop Recording - - - - - - - ")
                    self.recording = False
                continue

            if self.recording:
                chunk = stream.read(1280)
                self.ws.send(chunk)
                time.sleep(0.04)

                if (time.time() - start_time) >= self.max_duration:
                    print("Maximum recording duration reached. Stopping recording.")
                    self.recording = False

        # self.ws.send(bytes(self.end_tag.encode('utf-8')))
        # print("send end tag success")

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
                    result = ''
                    result_1 = re.findall('"w":"(.*?)"', str(result_dict["data"]))
                    for i in result_1:
                        if i == '。' or i == '.。' or i == ' .。' or i == ' 。':
                            pass
                        else:
                            result += i
                    print(result)
                    # 写入文本文件
                    temp = open('temp.txt', 'w', encoding='utf-8')
                    temp.write(result)
                    temp.close()
                    # print("rtasr result: " + str(result_1))

                if result_dict["action"] == "error":
                    print("rtasr error: " + result)
                    self.ws.close()
                    return
        except websocket.WebSocketConnectionClosedException:
            print("receive result end")

    def close(self):
        self.ws.close()
        print("connection closed")


def runc():
    client = Client()
    client.send()


if __name__ == '__main__':
    logging.basicConfig()
    client = Client()
    client.send()
