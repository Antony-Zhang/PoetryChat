"""
生成回答
"""
import os
import json
from LLM.spark_desk import SparkDesk
from langchain.prompts import PromptTemplate, load_prompt
from langchain.chains import LLMChain, SimpleSequentialChain

from chat_poets.poet_search import search_poem
from chat_poets.get_path import get_prompts_path


class ChatPoet:
    llm = SparkDesk()
    # 记录所有Prompts的文件
    prompts = json.loads(get_prompts_path("prompts.json"))

    @classmethod
    def allow_chat(cls, user_message: str) -> bool:
        """
        对话开始时判断用户输入是否合规：提及诗人或古诗 todo 需要进一步优化提示词 以及 返回大模型检测到的信息(古诗，诗人),字符串
        """
        prompt_allow = load_prompt("chat_poets/prompts/allow_chat.json")
        chain_allow = LLMChain(llm=cls.llm, prompt=prompt_allow)
        response = chain_allow.run(user_message)
        print(f"response: {response}")

        while True:
            try:
                allow = int(response)
                return allow == 1
            except ValueError:
                response = chain_allow.run(user_message)

    @classmethod
    def get_question_type(cls, user_message: str) -> str:
        """
        返回问题类型字符串
        :param user_message:
        :return:
        """
        prompt_question_type = load_prompt("chat_poets/prompts/question_type.json")
        chain_question_type = LLMChain(llm=cls.llm, prompt=prompt_question_type)
        response = chain_question_type.run(user_message)
        print(f"response: {response}")

        return response

    @classmethod
    def gen_response(cls, pattern: str, history: list[list]) -> str:
        """
        根据对话历史，产生回答。
        pattern = "adult" | "teen" | "child"，模式
        注：对话历史的最后一项是需要填充的内容，即history[-1] = [Question, ]；Question为用户刚提出的问题，尚未回答
        """
        question_type = cls.get_question_type(history[-1][0])
        if pattern == "adult":
            cls.chat_adult(question_type=question_type, history=history)
        else:
            cls.chat_teen_or_child(pattern=pattern, question_type=question_type, history=history)

        # elif pattern == "teen":
        #     return cls.chat_teen(question_type, history)
        # elif pattern == "child":
        #     return cls.chat_child(question_type, history)

    @classmethod
    def get_str_history(cls, history: list[list]) -> str:
        """
        将history列表转换为字符串，并填充入Prompts，
        """
        result_str = ""
        for sublist in history:
            if len(sublist) >= 2:
                question = sublist[0]
                answer = sublist[1]
                result_str += f"Q: {question} A: {answer}\n"

        str_history = cls.prompts["history"].format(history=result_str)
        return str_history

    @classmethod
    def chat_adult(cls, question_type: str, history: list[list]) -> str:
        """
        成人模式
        :param question_type:
        :param history: 对话记录，最后一项是[Question, ]，即答案待给出
        :return: 给出答案
        """
        if question_type == "origin":
            return cls.get_str_response_origin(history)
        elif question_type == "vernacular":
            return cls.get_str_response_vernacular(history)
        elif question_type == "appreciate":
            return cls.get_str_response_appreciate(history)
        elif question_type == "vocab":
            return cls.get_str_response_vocab(history)
        elif question_type == "author":
            return cls.get_str_response_author(history)
        elif question_type == "background":
            return cls.get_str_response_background(history)

    @classmethod
    def chat_teen_or_child(cls, pattern: str, question_type: str, history: list[list]) -> str:
        """
        青少年模式或儿童模式
        :param pattern: 交互模式 "teen" | "child"
        :param history: 对话记录，最后一项是[Question, ]，即答案待给出
        :param question_type: 问题类型
        :return: 给出答案
        """
        prompt_mode = cls.prompts["pattern"][pattern]

        if question_type == "origin":
            return cls.get_str_response_origin(history)
        elif question_type == "vernacular":
            str_prompt_vernacular_s = prompt_mode + cls.get_str_response_vernacular(history)
            return cls.llm(str_prompt_vernacular_s)
        elif question_type == "appreciate":
            str_prompt_appreciate_s = prompt_mode + cls.get_str_response_appreciate(history)
            return cls.llm(str_prompt_appreciate_s)
        elif question_type == "vocab":
            str_prompt_vocab_s = prompt_mode + cls.get_str_response_vocab(history)
            return cls.llm(str_prompt_vocab_s)
        elif question_type == "author":
            str_prompt_author_s = prompt_mode + cls.get_str_response_author(history)
            return cls.llm(str_prompt_author_s)
        elif question_type == "background":
            str_prompt_background_s = prompt_mode + cls.get_str_response_background(history)
            return cls.llm(str_prompt_background_s)

    @classmethod
    def get_str_response_origin(cls, history: list[list]) -> str:
        """古诗原文"""
        str_prompt = cls.get_str_history(history=history) + cls.prompts["questions_type"]["origin"]
        str_response = cls.llm(str_prompt.format(author="作者", poem="古诗标题"))
        return str_response

    @classmethod
    def get_str_response_vernacular(cls, history: list[list]) -> str:
        """古诗白话文翻译"""
        str_prompt = cls.prompts["questions_type"]["vernacular"] + cls.get_str_response_origin(history=history)
        str_response = cls.llm(cls.get_str_history(history=history) + str_prompt.format(author="诗人", poem="古诗标题"))
        return str_response

    @classmethod
    def get_str_response_appreciate(cls, history: list[list]) -> str:
        """古诗鉴赏"""
        str_prompt = cls.prompts["questions_type"]["appreciate"] + cls.get_str_response_origin(history=history)
        str_response = cls.llm(cls.get_str_history(history=history) + str_prompt.format(author="诗人", poem="古诗标题"))
        return str_response

    @classmethod
    def get_str_response_vocab(cls, history: list[list]) -> str:
        str_prompt = cls.prompts["questions_type"]["vocab"].format(author="作者",
                                                                   poem="古诗标题",
                                                                   word="需要解释的词语",
                                                                   response_origin=cls.get_str_response_origin(
                                                                       history=history))
        str_response = cls.llm(cls.get_str_history(history=history) + str_prompt)
        return str_response

    @classmethod
    def get_str_response_author(cls, history: list[list]) -> str:
        str_prompt = cls.prompts["questions_type"]["author"].format(author="诗人")
        str_response = cls.llm(cls.get_str_history(history=history) + str_prompt)
        return str_response

    @classmethod
    def get_str_response_background(cls, history: list[list]) -> str:
        str_prompt = cls.prompts["questions_type"]["background"].format(author="诗人",
                                                                        poem="古诗",
                                                                        response_origin=cls.get_str_response_origin(
                                                                            history=history))
        str_response = cls.llm(cls.get_str_history(history=history) + str_prompt)
        return str_response


if __name__ == '__main__':
    print(os.path.abspath("../"))
    curPath = os.path.abspath(os.path.dirname(__file__))
    print(curPath)
    rootPath = curPath[:curPath.find("PoetryChat/") + len("PoetryChat/")]
    print(rootPath)
    # ChatPoet.get_question_type("静夜思这首诗的内容是什么？")
