import os
from openai import OpenAI
from config.config import config
from dotenv import load_dotenv, find_dotenv

# 读取本地/项目的环境变量。

# find_dotenv()寻找并定位.env文件的路径
# load_dotenv()读取该.env文件，并将其中的环境变量加载到当前的运行环境中
# 如果你设置的是全局的环境变量，这行代码则没有任何作用。
load_dotenv(find_dotenv())

# 如果你需要通过代理端口访问，你需要如下配置
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
os.environ["HTTP_PROXY"] = 'http://127.0.0.1:7890'

# 获取环境变量 OPENAI_API_KEY 并实例化 OpenAI
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])


# 一个封装 OpenAI 接口的函数，参数为 Prompt，返回对应结果
def get_completion_openai(prompt, model="gpt-3.5-turbo", temperature=0.1):
    """
    prompt: 对应的提示词
    model: 调用的模型，默认为 gpt-3.5-turbo，也可以选择 gpt-4
    """

    # 构造消息
    messages = [
        {"role": "system", "content": config.system_prompt},
        {"role": "user", "content": prompt}
    ]

    # 调用 ChatCompletion 接口
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,  # 模型输出的温度系数，控制输出的随机程度
    )

    return response.choices[0].message.content


if __name__ == '__main__':
    prompt = config.user_prompt
    print(get_completion_openai(prompt))
