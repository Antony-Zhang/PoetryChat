"""
    GPT交互的功能模块
"""
import _thread as thread
import json
import websocket

from LLM.webInteract.web_param import gen_params_gpt


class Singleton(object):
    """
    类装饰器,用于实现单例模式
    """

    def __init__(self, cls):
        self._cls = cls
        self._instance = {}

    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]


class WS(websocket.WebSocketApp):
    """
    WebSocketApp子类，添加消息变量
    """

    def __init__(self, appid, url, on_message, on_error, on_close, on_open):
        self.appid = appid
        self.received_message = ""
        super(WS, self).__init__(url=url,
                                 on_message=on_message,
                                 on_error=on_error,
                                 on_close=on_close,
                                 on_open=on_open)


def on_error(ws, error):
    """
    收到websocket错误的处理
    """
    print("### error:", error)


def on_close(ws):
    """
    收到websocket关闭的处理
    """
    print("### closed ###")


def on_open(ws):
    """
    收到websocket连接建立的处理
    """
    # print("### open ###")
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    # print("### run ###")
    data = json.dumps(gen_params_gpt(appid=ws.appid, question=ws.question))
    ws.send(data)


def on_message(ws, message):
    """
    到websocket消息的处理
    :param ws:
    :param message:
    :return:
    """
    # print("### message ###")
    data = json.loads(message)  # 将JSON字符串转化为Python对象
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
        # print("# closed 1 #")
    else:
        choices = data["payload"]["choices"]  # 有效载荷数据
        status = choices["status"]  # 消息的状态
        content = choices["text"][0]["content"]  # 消息的内容
        # 存储返回的消息
        ws.received_message += content

        # print(ws.received_message)
        if status == 2:  # 判断末尾消息
            ws.close()
            # print("# closed 2 #")
            # print(ws.received_message)


