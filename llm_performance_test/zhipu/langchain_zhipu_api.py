import os
from config.config import config
from dotenv import load_dotenv, find_dotenv
from langchain_zhipu import ChatZhipuAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv(find_dotenv())
zhipu_api_key = os.environ['ZHIPU_API_KEY']

llm = ChatZhipuAI(temperature=0.1, api_key=zhipu_api_key, model_name="glm-4")

# langchain_zhipu的调用测试，实际使用中和zhipu_api.py二选一即可
if __name__ == '__main__':

    prompt = ChatPromptTemplate.from_messages([
        ("system", config.system_prompt),
        ("user", "{input}")
    ])

    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    print(chain.invoke({"input": config.user_prompt}))
