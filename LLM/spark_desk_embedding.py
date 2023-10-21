import os
import json
import requests
from typing import Optional, List, Mapping, Any

from LLM.webInteract.web_param import WsParamEmb


class SparkDeskEmbedding(object):
    """
    讯飞星火的Embedding模型
    """
    url = r'https://knowledge-retrieval.cn-huabei-1.xf-yun.com/v1/aiui/embedding/query'
    APPID: str = os.getenv("APPID_EMBEDDING")
    APIKey: str = os.getenv("APIKEY_EMBEDDING")
    APISecret: str = os.getenv("APISECRET_EMBEDDING")

    def _get_param(self, text) -> Mapping[str, Any]:
        """
        组织请求消息
        :param text: 待向量化的文本
        :return:
        """
        param_dict = {
            'header': {
                'app_id': self.APPID
            },
            'payload': {
                'text': text
            }
        }
        return param_dict

    def embed_query(self, text: str,) -> List[float]:
        """Compute query embeddings using the Spark Desk Model.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        ws_param = WsParamEmb(self.url, self.APPID, self.APIKey, self.APISecret)
        wsUrl = ws_param.create_url()
        param_dict = self._get_param(text)
        response = requests.post(url=wsUrl, json=param_dict)    # 得到响应串
        result = json.loads(response.content.decode('utf-8'))
        # embed = json.loads(result_dict['payload']['text']['vector'])
        return result


if __name__ == '__main__':
    llm_embed = SparkDeskEmbedding()
    embed1 = llm_embed.embed_query("你好吗？")
    print(embed1)
    print(len(embed1))
    print(embed1[:5])
