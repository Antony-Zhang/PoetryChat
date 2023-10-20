"""
文生图所需函数
"""
import re
import time
import json
import gradio as gr

from chat_poets.chat import ChatPoet


def txt_select(txt_img: str) -> str:
    """
    生图文本选择的响应函数
    """
    return txt_img
