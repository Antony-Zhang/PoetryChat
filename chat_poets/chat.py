"""
生成回答
"""
from LLM.spark_desk import SparkDesk
from langchain.prompts import PromptTemplate, load_prompt
from langchain.chains import LLMChain, SimpleSequentialChain


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
    def gen_response(cls, pattern: str, history: list[list]) -> str:
        """
        根据对话历史，产生回答。
        pattern = "adult" | "teen" | "child"，模式
        注：对话历史的最后一项是需要填充的内容，即history[-1] = [Question, None]；Question为用户刚提出的问题，None即尚未回答
        """
        return "哇哇哇!"
