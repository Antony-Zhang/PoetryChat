import os
import sys
import json

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))  # 当前脚本所在目录的绝对路径
CONFIG_FILE_PATH = os.path.join(ROOT_PATH, 'config.json')  # 配置文件的绝对路径


class Config:
    def __init__(self, config_file):
        with open(config_file, 'r', encoding="utf-8") as f:
            config = json.load(f)
        self.system_prompt = config['system_prompt']
        self.user_prompt = config['user_prompt']
        self.poet = config['poet']


# 创建一个Config实例
config = Config(CONFIG_FILE_PATH)

if __name__ == '__main__':
    print(config.system_prompt)
    print(config.user_prompt)
    print(config.poet)
