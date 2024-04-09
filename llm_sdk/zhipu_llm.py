from typing import Any, List, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from zhipuai import ZhipuAI
from config.config import config
from llm_sdk.base_llm import Base_LLM


class ZhipuLLM(Base_LLM):
    # 智谱清言GLM大模型的自定义 LLM
    # api_key 继承自Base_LLM
    model: str = "glm-4"

    def _call(self, prompt: str, stop: Optional[List[str]] = None,
              run_manager: Optional[CallbackManagerForLLMRun] = None,
              **kwargs: Any):
        client = ZhipuAI(api_key=self.api_key)  # 请填写您自己的APIKey

        # 构造消息
        messages = [
            {"role": "system", "content": config.system_prompt},  # system message
            {"role": "user", "content": prompt},
        ]

        # 调用 ChatCompletion 接口
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )

        try:
            return response.choices[0].message.content
        except Exception as e:
            print(e)
            print("请求失败")
            return "请求失败"

    @property
    def _llm_type(self) -> str:
        return "Zhipu"
