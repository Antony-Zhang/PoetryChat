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

    # 将history从列表转换为字符串
    @classmethod
    def history2str(cls, history: list[list]) -> str:
        result_str = ""
        for sublist in history:
            if len(sublist) >= 2:
                question = sublist[0]
                answer = sublist[1]
                result_str += f"Q: {question} A: {answer}\n"
        return result_str

    def getStrHistory(self) -> str:
        str_history = "{}是你和用户之前的对话记录，Q：代表了用户的输入，A：代表了你的回复，根据历史对话记录和下面的要求继续回答用户。".format(self.history2str())
        return str_history

    def getStrResponseOrigin(self) -> str:
        str_prompt_origin = "现在你需要扮演一位精通古诗和诗词文化的老师，根据我提供的信息——诗人[{}]及其《{}》，你需要输出作品的全文。\
                请你给出诗人[{}]的《{}》这首诗的全文，注意：只输出全文，不要对文章进行解释或赏析等任何别的多余操作，并仔细检查全文，确保文字无误、句法通顺和历史准确性，输出格式符合一般诗词的展示格式即可。"
        str_response_origin = self.llm.chat(self.getStrHistory() + str_prompt_origin)
        return str_response_origin

    def getStrResponseVernacular(self) -> str:
        str_prompt_vernacular_s = "你需要扮演一位精通古诗和诗词文化的老师,根据我提供的信息——[{}]及其《{}》的全文，把每一句诗词翻译成现代文，一句诗的定义为以句号作为结尾。\
        要求输出的白话文能让普通人理解,白话文的语句表达要求严谨、通顺、准确。输出按照下面的格式进行,'第1句':；'第2句':；'第3句':；'第4句':；...'第n句':；以此类推写出每句诗词的现代文翻译\
        请再次注意句子的定义是以句号作为结尾。\
        请对以下作品进行翻译并输出，[{}]的《{}》全文为："
        str_prompt_vernacular = str_prompt_vernacular_s + self.getStrResponseOrigin()
        str_response_vernacular = self.llm.chat(self.getStrHistory() + str_prompt_vernacular)
        return str_response_vernacular

    def getStrResponseAppreciate(self) -> str:
        str_prompt_appreciate_s = "你需要扮演一位精通古诗和诗词文化的老师,根据我提供的信息——[{}]及其《{}》的全文进行鉴赏。\
               具体要求如下：你需要对全文中的每一句诗词进行鉴赏，然后再对诗词的整体做一个鉴赏，一句诗的定义为以句号作为结尾。 \
               要求输出的鉴赏语段能让普通人理解,鉴赏内容尽可能的丰富、生动、有趣、能体现鉴赏者思想的深度,同时鉴赏语句需要严谨、通顺、准确，鉴赏的时候需要考虑诗词的意境，诗人创作的时代因素环境因素和诗人的情感等等。\
               输出按照下面的格式进行,'第1句':；'第2句':；'第3句':；'第4句':；...'第n句':；以此类推写出每句诗词的赏析，请再次注意句子的定义是以句号作为结尾。\
               请对下面作品进行鉴赏，[{}]的《{}》全文为："
        str_prompt_appreciate = str_prompt_appreciate_s + self.getStrResponseOrigin()
        str_response_appreciate = self.llm.chat(self.getStrHistory() + str_prompt_appreciate)
        return str_response_appreciate

    def getStrResponseVocab(self) -> str:
        str_prompt_vocab_s = "你需要扮演一位精通古诗和诗词文化的老师,你将对某一词汇或某些词汇进行解释说明，注意：词汇必须在[{}]的《{}》全文里出现，因为脱离语境的词汇解释是没有意义的。\
               你对词汇的解释要求尽可能的丰富、生动、有趣,解释必须准确、严谨、通顺，对词汇的解释需要结合诗词上下文和语境进行分析。\
               若用户的提问词汇没有在诗词全文中出现，则你需要输出：'您好，您所提问的词汇不在该诗词中哦，可以尝试再次检查并请重新向我提问。'\
               [{}]的《{}》全文为："
        str_prompt_vocab_e = "请对该诗词中的'{}'一词进行解释说明"
        str_prompt_vocab = str_prompt_vocab_s + self.getStrResponseOrigin() + str_prompt_vocab_e
        str_response_vocab = self.llm.chat(self.getStrHistory() + str_prompt_vocab)
        return str_response_vocab

    def getStrResponseAuthor(self) -> str:
        str_prompt_author = "你需要扮演一位精通古诗和诗词文化的老师，请以生动、详尽的方式，介绍[{}]的基本人物简介和主要生平事迹。确保输出一定符合历史准确性和中国文化常识，不确定或有争议的内容可以不输出。"
        str_response_author = self.llm.chat(self.getStrHistory() + str_prompt_author)
        return str_response_author

    def getStrResponseBackground(self) -> str:
        str_prompt_background_s = "你需要扮演一位精通古诗和诗词文化的老师,根据我提供的信息——[{}]及其《{}》的全文，对[{}]的写作背景进行介绍。\
                介绍要求尽可能的丰富、生动、有趣,背景介绍包括时代，朝代，诗人当时的年龄，近期的处境，发生的大事件，大变故等所有可能对诗人创作诗词有影响的因素。\
                背景介绍必须确保准确严谨，符合历史准确性和中国文化常识。注意：你只需要给出诗词写作时的背景介绍，不需要对原文进行多余的解释。\
                [{}]的《{}》全文为："
        str_prompt_background_e = "请对《{}》的写作背景进行介绍"
        str_prompt_background = str_prompt_background_s + self.getStrResponseOrigin() + str_prompt_background_e
        str_response_background = self.llm.chat(self.getStrHistory() + str_prompt_background)
        return str_response_background

    @classmethod
    def chat_adult(cls, question_type: str, history: list[list]) -> str:
        """
        成人模式
        :param question_type:
        :param history: 对话记录，最后一项是[Question, ]，即答案待给出
        :return: 给出答案
        """

        str_response_origin = cls.getStrResponseOrigin(self=cls)
        str_response_vernacular = cls.getStrResponseVernacular(self=cls)
        str_response_appreciate = cls.getStrResponseAppreciate(self=cls)
        str_response_vocab = cls.getStrResponseVocab(self=cls)
        str_response_author = cls.getStrResponseAuthor(self=cls)
        str_response_background = cls.getStrResponseBackground(self=cls)

        if question_type == "origin":
            return str_response_origin
        elif question_type == "vernacular":
            return str_response_vernacular
        elif question_type == "appreciate":
            return str_response_appreciate
        elif question_type == "vocab":
            return str_response_vocab
        elif question_type == "author":
            return str_response_author
        elif question_type == "background":
            return str_response_background

    @classmethod
    def chat_teen(cls, question_type: str, history: list[list]) -> str:
        """
        青少年模式
        :param history: 对话记录，最后一项是[Question, ]，即答案待给出
        :return: 给出答案
        """

        str_response_origin = cls.getStrResponseOrigin(self=cls)
        str_response_vernacular = cls.getStrResponseVernacular(self=cls)
        str_response_appreciate = cls.getStrResponseAppreciate(self=cls)
        str_response_vocab = cls.getStrResponseVocab(self=cls)
        str_response_author = cls.getStrResponseAuthor(self=cls)
        str_response_background = cls.getStrResponseBackground(self=cls)
        str_prompt_teenager = "你面对的对象是中学阶段需要参加各种语文考试，诗词竞赛和日常古诗默写练习的初中生和高中生。请将下面的语句重新组织，使得学生能够轻松的理解，激发学生对这首诗词的思考与理解。 \
                   可以多使用尝试联想，举例的方法解释诗词，贴合学生中学阶段的思考和思维方式，输出的内容务必注重诗词相关知识的严谨性，合理性以及历史与文化常识方面的准确性。 \
                   输出内容要尽量符合历年中高考古诗题目的评分标准，按照规范的中高考古诗文赏析的解题思路引导学生，向学生解释说明诗词的内容，帮助学生理顺答题思路，在古诗文相关题目中拿到更高的分数。 \
                   语句如下："
        if question_type == "origin":
            return str_response_origin
        elif question_type == "vernacular":
            str_prompt_vernacular_teenager_s = str_prompt_teenager + str_response_vernacular
            str_response_vernacular_teenager = cls.llm.chat(str_prompt_vernacular_teenager_s)
            return str_response_vernacular_teenager
        elif question_type == "appreciate":
            str_prompt_appreciate_teenager_s = str_prompt_teenager + str_response_appreciate
            str_response_appreciate_teenager = cls.llm.chat(str_prompt_appreciate_teenager_s)
            return str_response_appreciate_teenager
        elif question_type == "vocab":
            str_prompt_vocab_teenager_s = str_prompt_teenager + str_response_vocab
            str_response_vocab_teenager = cls.llm.chat(str_prompt_vocab_teenager_s)
            return str_response_vocab_teenager
        elif question_type == "author":
            str_prompt_author_teenager_s = str_prompt_teenager + str_response_author
            str_response_author_teenager = cls.llm.chat(str_prompt_author_teenager_s)
            return str_response_author_teenager
        elif question_type == "background":
            str_prompt_background_teenager_s = str_prompt_teenager + str_response_background
            str_response_background_teenager = cls.llm.chat(str_prompt_background_teenager_s)
            return str_response_background_teenager

    @classmethod
    def chat_child(cls, question_type: str, history: list[list]) -> str:
        """
        儿童模式
        :param history: 对话记录，最后一项是[Question, ]，即答案待给出
        :return: 给出答案
        """

        str_response_origin = cls.getStrResponseOrigin(self=cls)
        str_response_vernacular = cls.getStrResponseVernacular(self=cls)
        str_response_appreciate = cls.getStrResponseAppreciate(self=cls)
        str_response_vocab = cls.getStrResponseVocab(self=cls)
        str_response_author = cls.getStrResponseAuthor(self=cls)
        str_response_background = cls.getStrResponseBackground(self=cls)
        str_response_origin = cls.getStrResponseOrigin(self=cls)
        str_prompt_child = "你面对的对象是一个8岁左右的小朋友，请将下面的语句重新组织，要求让8岁的小朋友也能够轻松的理解关于诗词和文化的含义\
                你可以多使用尝试比喻，举例，贴合孩子的思考和思维方式，让输出的内容活泼生动可爱，多加入语气词、鼓励词等等，尽可能激发小朋友对诗词和中国文化的兴趣，语句如下："
        if question_type == "origin":
            return str_response_origin
        elif question_type == "vernacular":
            str_prompt_vernacular_child_s = str_prompt_child + str_response_vernacular
            str_response_vernacular_child = cls.llm.chat(str_prompt_vernacular_child_s)
            return str_response_vernacular_child
        elif question_type == "appreciate":
            str_prompt_appreciate_child_s = str_prompt_child + str_response_appreciate
            str_response_appreciate_child = cls.llm.chat(str_prompt_appreciate_child_s)
            return str_response_appreciate_child
        elif question_type == "vocab":
            str_prompt_vocab_child_s = str_prompt_child + str_response_vocab
            str_response_vocab_child = cls.llm.chat(str_prompt_vocab_child_s)
            return str_response_vocab_child
        elif question_type == "author":
            str_prompt_author_child_s = str_prompt_child + str_response_author
            str_response_author_child = cls.llm.chat(str_prompt_author_child_s)
            return str_response_author_child
        elif question_type == "background":
            str_prompt_background_child_s = str_prompt_child + str_response_background
            str_response_background_child = cls.llm.chat(str_prompt_background_child_s)
            return str_response_background_child
