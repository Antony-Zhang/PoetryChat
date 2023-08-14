"""
生成回答
"""
from LLM.spark_desk import SparkDesk
from langchain.prompts import PromptTemplate, load_prompt
from langchain.chains import LLMChain, SimpleSequentialChain

from chat_poets.poet_search import search_poem


class ChatPoet:
    llm = SparkDesk()

    @classmethod
    def allow_chat(cls, user_message: str) -> bool:
        """
        对话开始时判断用户输入是否合规：提及诗人或古诗 todo 需要进一步优化提示词
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
    def get_question_type(cls, history: list[list]) -> str:
        """
        返回问题类型字符串
        :param history:
        :return:
        """

        return "我是问题类型"

    @classmethod
    def gen_response(cls, pattern: str, history: list[list]) -> str:
        """
        根据对话历史，产生回答。
        pattern = "adult" | "teen" | "child"，模式
        注：对话历史的最后一项是需要填充的内容，即history[-1] = [Question, ]；Question为用户刚提出的问题，尚未回答
        """
        question_type = cls.get_question_type(history)
        if pattern == "adult":
            return cls.chat_adult(question_type, history)
        elif pattern == "teen":
            return cls.chat_teen(question_type, history)
        elif pattern == "child":
            return cls.chat_child(question_type, history)

    @classmethod
    def chat_adult(cls, question_type: str, history: list[list]) -> str:
        """
        成人模式
        :param question_type:
        :param history: 对话记录，最后一项是[Question, ]，即答案待给出
        :return: 给出答案
        """

        return "成人模式回答"

    @classmethod
    def chat_teen(cls, question_type: str, history: list[list]) -> str:
        """
        青少年模式
        :param history: 对话记录，最后一项是[Question, ]，即答案待给出
        :return: 给出答案
        """

        return "青少年模式回答"

    @classmethod
    def chat_child(cls, question_type: str, history: list[list]) -> str:
        """
        儿童模式
        :param history: 对话记录，最后一项是[Question, ]，即答案待给出
        :return: 给出答案
        """

        return "儿童模式回答"
