import os
from zhipuai import ZhipuAI
from config.config import config
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
zhipu_api_key = os.environ['ZHIPU_API_KEY']

client = ZhipuAI(api_key=zhipu_api_key)


def get_completion_zhipu(prompt, temperature=0.1):
    """
    prompt: 对应的提示词
    model: 调用的模型名称
    """
    model = "glm-4"
    # 构造消息
    messages = [
        {"role": "system", "content": config.system_prompt},
        {"role": "user", "content": prompt},
    ]

    # 调用 ChatCompletion 接口
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )

    return response.choices[0].message.content


if __name__ == '__main__':
    prompt = config.user_prompt
    print(get_completion_zhipu(prompt))
