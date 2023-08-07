"""
    项目主文件
"""
from LLM.spark_desk import SparkDesk
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import load_prompt

import json
import codecs


if __name__ == "__main__":
    # 创建大模型
    llm = SparkDesk()

    poem_input = input("请输入诗句：")

    # chain1
    prompt1 = load_prompt("prompts/example1.json")
    chain1 = LLMChain(llm=llm,prompt=prompt1)
    # chain2
    prompt2 = load_prompt("prompts/example2.json")
    chain2 = LLMChain(llm=llm, prompt=prompt2)
    # 简单连接chain
    overall_chain = SimpleSequentialChain(chains=[chain1, chain2], verbose=True)

    result = overall_chain.run(poem_input)
