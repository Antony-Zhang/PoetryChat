"""
生成回答
"""
import os
import json
import re
from LLM.spark_desk import SparkDesk
from langchain.prompts import PromptTemplate, load_prompt
from langchain.chains import LLMChain, SimpleSequentialChain

from chat_poets.poet_web_search import search_poem
from get_path import get_file_path


class ChatPoet:
    llm = SparkDesk()
    # 记录所有Prompts的文件
    with open(get_file_path("prompts.json", "prompts")) as f:
        prompts = json.load(f)
    # {"author", "content", "title"}
    res_dict = dict()

    sentence_choices = ["枯藤老树昏鸦", "小桥流水人家", "古道西风瘦马"]

    content = " "  # 当前的古诗内容

    @property
    def content(self):
        return ChatPoet.content

    @content.setter
    def content(self, new_content):
        if new_content != ChatPoet.content:
            print("解析到的诗句已更改！")
            ChatPoet.content = new_content
            ChatPoet.sentence_choices =  [item for item in re.split(r'[。？！；]', new_content) if re.search(r'[\u4e00-\u9fa5]', item)]
            # re.split(r'[。？！；]', new_content)

            print(ChatPoet.sentence_choices)

    # def change_content(self, new_content):
    #     self.content = new_content

    @classmethod
    def allow_chat(cls, user_message: str):
        """
        对话开始时判断用户输入是否合规：提及诗人,诗名或诗句中的至少两个
        :param user_message:用户的问题
        """
        count = 0
        prompt_allow = cls.prompts["allow_chat"].format(user_message=user_message)
        print(f"prompt_allow:{prompt_allow}")
        while True:
            try:
                res_json_str = cls.llm(prompt_allow)
                start_index = res_json_str.find('{')
                end_index = res_json_str.rfind('}') + 1
                json_content = res_json_str[start_index:end_index]
                cls.res_dict = json.loads(json_content)
                break
            except:
                print("allow_chat error: 大模型没有正确输出json格式")
                continue

        while True:
            try:
                # 计数器
                for field in ["author", "title", "content"]:
                    if cls.res_dict.get(field):
                        count += 1

                # 判断用户输入是否合规（提及至少两个字段）
                if count >= 2:
                    # print(f"用户输入合规，开始后续对话")
                    break
                else:
                    # print("用户输入不合规，缺少足够的关键字段。")
                    print("可以告诉小框更多关于这首诗的信息吗~~小框我作为古诗学习助手的目标是针对特定的古诗和你一起探讨，交流和进步！")
                    # 重新提问
                    prompt_allow = cls.prompts["allow_chat"].format(user_message=user_message)
                    print(f"prompt_allow:{prompt_allow}")
                    res_json_str = cls.llm(prompt_allow)
                    start_index = res_json_str.find('{')
                    end_index = res_json_str.rfind('}') + 1
                    json_content = res_json_str[start_index:end_index]
                    cls.res_dict = json.loads(json_content)
                    count = 0
            except ValueError:
                pass


        # while True:
        #     try:
        #         res_json_str = cls.llm(prompt_allow)
        #         print(f"allow_chat: {res_json_str}")
        #         cls.res_dict = json.loads(res_json_str)
        #         break
        #     except:
        #         continue
        # while True:
        #     try:
        #         cls.res_dict["exist"] = int(cls.res_dict["exist"])
        #         if cls.res_dict["author"] is None:
        #             cls.res_dict["author"] = ""
        #         if cls.res_dict["poem"] is None:
        #             cls.res_dict["poem"] = ""
        #         print(f"res_dict:{cls.res_dict}")
        #         return
        #     except ValueError:
        #         prompt_allow = cls.prompts["allow_chat"].format(user_message=user_message)
        #         print(prompt_allow)
        #         res_json_str = cls.llm(prompt_allow)
        #         print(f"allow_chat: {res_json_str}")
        #         cls.res_dict = json.loads(res_json_str)

    @classmethod
    def stop_chat(cls):
        """结束本次对话，清空对话关键内容"""
        cls.res_dict.clear()

    @classmethod
    def get_question_type(cls, user_message: str) -> str:
        """
        返回问题类型字符串
        :param user_message:
        :return:
        """
        prompt_question_type = cls.prompts["get_question_type"].format(user_message=user_message)
        question_type = cls.llm(prompt_question_type)

        return question_type

    @classmethod
    def gen_response(cls, pattern: str, history: list[list]) -> str:
        """
        根据对话历史，产生回答。
        pattern = "adult" | "teen" | "child"，模式
        注：对话历史的最后一项是需要填充的内容，即history[-1] = [Question, ]；Question为用户刚提出的问题，尚未回答
        """
        limit_list = ["诗词原文", "诗词白话文翻译", "诗词鉴赏", "词语解释", "写作背景", "作者简介"]
        time = 0
        while True:
            # 循环纠错，保证输出的问题类型在给定范围内
            question_type = cls.get_question_type(history[-1][0])
            if limit_list.count(question_type) > 0:
                print(f"question_type:{question_type}")
                break
            else:
                print(f"错误的question_type:{question_type}")
                time += 1
                if time > 5:
                    return "请求次数过多，请重试"

        if pattern == "adult":
            print("成人模式")
            response = cls.chat_adult(question_type=question_type, history=history)
        else:
            print("青少年或儿童模式")
            response = cls.chat_teen_or_child(pattern=pattern, question_type=question_type, history=history)
        print(f"response:{response}")
        return response
        # return "wow"

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
        if question_type == "诗词原文":
            return cls.get_str_response_origin(history)
        elif question_type == "诗词白话文翻译":
            return cls.get_str_response_vernacular(history)
        elif question_type == "诗词鉴赏":
            return cls.get_str_response_appreciate(history)
        elif question_type == "词语解释":
            return cls.get_str_response_vocab(history)
        elif question_type == "作者简介":
            return cls.get_str_response_author(history)
        elif question_type == "写作背景":
            return cls.get_str_response_background(history)

    @classmethod
    def chat_teen_or_child(cls, pattern: str, question_type: str, history: list[list]) -> str:
        """
        青少年模式或儿童模式
        :param pattern: 交互模式 "teen" | "child"
        :param history: 对话记录，最后一项是[Question, ]，即答案待给出
        :param question_type:  
        :return: 给出答案
        """
        prompt_mode = cls.prompts["pattern"][pattern]

        if question_type == "诗词原文":
            return cls.get_str_response_origin(history)
        elif question_type == "诗词白话文翻译":
            str_prompt_vernacular_s = prompt_mode + cls.get_str_response_vernacular(history)
            return cls.llm(str_prompt_vernacular_s)
        elif question_type == "诗词鉴赏":
            str_prompt_appreciate_s = prompt_mode + cls.get_str_response_appreciate(history)
            return cls.llm(str_prompt_appreciate_s)
        elif question_type == "词语解释":
            str_prompt_vocab_s = prompt_mode + cls.get_str_response_vocab(history)
            return cls.llm(str_prompt_vocab_s)
        elif question_type == "作者简介":
            str_prompt_author_s = prompt_mode + cls.get_str_response_author(history)
            return cls.llm(str_prompt_author_s)
        elif question_type == "写作背景":
            str_prompt_background_s = prompt_mode + cls.get_str_response_background(history)
            return cls.llm(str_prompt_background_s)

    @classmethod
    def get_str_response_origin(cls, history: list[list]) -> str:
        """古诗原文"""
        print(f"res_dict:{cls.res_dict}")
        print("----古诗原文----")
        str_prompt = cls.get_str_history(history=history) + \
                     cls.prompts["questions_type"]["origin"].format(author=cls.res_dict["author"],
                                                                    poem=cls.res_dict["poem"])
        str_response = cls.llm(str_prompt)
        return str_response

    @classmethod
    def get_str_response_vernacular(cls, history: list[list]) -> str:
        """古诗白话文翻译"""
        print(" ----古诗白话文翻译 ----")
        str_prompt = cls.prompts["questions_type"]["vernacular"].format(author=cls.res_dict["author"],
                                                                        poem=cls.res_dict["poem"]) + \
                     cls.get_str_response_origin(history=history)
        str_response = cls.llm(cls.get_str_history(history=history) + str_prompt)
        return str_response

    @classmethod
    def get_str_response_appreciate(cls, history: list[list]) -> str:
        """古诗鉴赏"""
        print(" ----古诗鉴赏 ----")
        str_prompt = cls.prompts["questions_type"]["appreciate"].format(author=cls.res_dict["author"],
                                                                        poem=cls.res_dict["poem"]) + \
                     cls.get_str_response_origin(history=history)
        print(f"该问题的最终Prompt（除历史记录）：{str_prompt}")

        str_response = cls.llm(cls.get_str_history(history=history) + str_prompt)
        return str_response

    @classmethod
    def get_str_response_vocab(cls, history: list[list]) -> str:
        """词语解释"""
        print(" ----词语解释 ----")
        str_prompt = cls.prompts["questions_type"]["vocab"].format(author=cls.res_dict["author"],
                                                                   poem=cls.res_dict["poem"],
                                                                   word="需要解释的词语",  # todo 这是个啥
                                                                   response_origin=cls.get_str_response_origin(
                                                                       history=history))
        str_response = cls.llm(cls.get_str_history(history=history) + str_prompt)
        return str_response

    @classmethod
    def get_str_response_author(cls, history: list[list]) -> str:
        """作者简介"""
        print(" ----作者简介 ----")
        str_prompt = cls.prompts["questions_type"]["author"].format(author=cls.res_dict["poem"])
        str_response = cls.llm(cls.get_str_history(history=history) + str_prompt)
        return str_response

    @classmethod
    def get_str_response_background(cls, history: list[list]) -> str:
        """写作背景"""
        print(" ----写作背景 ----")
        str_prompt = cls.prompts["questions_type"]["background"].format(author=cls.res_dict["author"],
                                                                        poem=cls.res_dict["poem"],
                                                                        response_origin=cls.get_str_response_origin(
                                                                            history=history))
        str_response = cls.llm(cls.get_str_history(history=history) + str_prompt)
        return str_response

# if __name__ == '__main__':
# ChatPoet.allow_chat("你知道《静夜思》这首诗吗？")
