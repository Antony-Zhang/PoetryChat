"""
获取文件路径
"""
import os
import sys
import json


def get_file_path(filename: str, pattern: str) -> str:
    """
    获取文件的绝对路径以供访问
    :parameter
        filename: 文件名
        pattern: 模式（需要获取的文件）[prompts | image]
    """
    curPath = os.path.abspath(os.path.dirname(__file__))
    # 此处的项目名称需要根据需要更换，若是部署hf则改成“user”

    # windows调试
    if sys.platform.startswith('win'):
        rootPath = curPath[:curPath.find("PoetryChat") + len("PoetryChat")]
        if pattern == "prompts":
            return rootPath + f"\\chat_poets\\{filename}"
        elif pattern == "image":
            return rootPath + f"\\txt2img\\generated_images\\{filename}"
    # mac调试
    elif sys.platform.startswith('darwin'):
        rootPath = curPath[:curPath.find("PoetryChat") + len("PoetryChat")]
        if pattern == "prompts":
            return rootPath + f"/chat_poets/{filename}"
        elif pattern == "image":
            return rootPath + f"/txt2img/generated_images/{filename}"
    # linux部署
    else:
        rootPath = curPath[:curPath.find("app") + len("app")]
        if pattern == "prompts":
            return rootPath + f"/chat_poets/{filename}"
        elif pattern == "image":
            return rootPath + f"/txt2img/generated_images/{filename}"


# if __name__ == '__main__':
#     # with open("prompts.json") as f:
#     #     print(type(json.load(f)))
#     curPath = os.path.abspath(os.path.dirname(__file__))
#     print("1: " + curPath)
#     print("2: " + curPath[:curPath.find("Z/") + len("PP")])
#     print(get_prompts_path("test.json"))
