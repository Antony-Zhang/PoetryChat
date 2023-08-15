"""
获取文件路径
"""
import os
import sys


def get_prompts_path(filename: str) -> str:
    """
    获取json文件的绝对路径以供访问
    """
    curPath = os.path.abspath(os.path.dirname(__file__))
    if sys.platform.startswith('win'):
        rootPath = curPath[:curPath.find("PoetryChat\\") + len("PoetryChat\\")]
        return rootPath + f"chat_poets\\chat_poets\\{filename}"
    else:
        rootPath = curPath[:curPath.find("PoetryChat/") + len("PoetryChat/")]
        return rootPath + f"chat_poets/chat_poets/{filename}"


