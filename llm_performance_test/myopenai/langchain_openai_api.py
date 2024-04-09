import os
import openai
from dotenv import load_dotenv, find_dotenv

from langchain_openai import ChatOpenAI  # from langchain.chat_models import ChatOpenAI (deprecated)
from langchain.prompts import ChatPromptTemplate

load_dotenv(find_dotenv())

# 配置通过代理端口访问
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
os.environ["HTTP_PROXY"] = 'http://127.0.0.1:7890'
# 获取环境变量 OPENAI_API_KEY
openai.api_key = os.environ['OPENAI_API_KEY']

# langchain_openai的调用测试，实际使用中和openai_api.py二选一即可
if __name__ == '__main__':

    template_string = """Analysis the poet \
    that is delimited by triple backticks. \
    text: ```{text}```
    """

    chat_template = ChatPromptTemplate.from_template(template_string)

    text = "Today is a nice day."

    # 调用 format_messages 将 template 转化为 message 格式
    message = chat_template.format_messages(text=text)
    print(message)

    get_completion_openai = ChatOpenAI(temperature=0.1)
    response = get_completion_openai(message)
    print(response)
