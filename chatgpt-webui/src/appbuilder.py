import os
import appbuilder
from src.base_model import BaseLLMModel
from config.config import config
from dotenv import load_dotenv, find_dotenv


class AppBuilderClient(BaseLLMModel):
    def __init__(self, model_name, system_prompt=config.system_prompt, user_name="", **kwargs):
        super().__init__(
            model_name=model_name,
            system_prompt=system_prompt,
            user=user_name,
            **kwargs
        )
        # 从环境变量中加载AppBuilder的token和appid
        load_dotenv(find_dotenv())
        self.appbuilder_token = os.environ.get('APPBUILDER_TOKEN')
        self.appbuilder_appid = os.environ.get('APPBUILDER_APPID_DEFAULT')
        self.builder = appbuilder.AppBuilderClient(self.appbuilder_appid)
        self.conversation_id = self.builder.create_conversation()

    def get_answer_stream_iter(self):

        return self.get_answer_at_once()

    def get_answer_at_once(self):

        user_input = self.history[-1]["content"]
        # 执行对话
        msg = self.builder.run(self.conversation_id, user_input)
        # 返回回答内容和token计数
        # 假设msg.content.answer是回答内容
        return msg.content.answer, len(msg.content.answer)

    def count_token(self, user_input):
        # 计算用户输入的token数量
        # 这里需要根据AppBuilder的token计算规则来实现
        return len(user_input)


