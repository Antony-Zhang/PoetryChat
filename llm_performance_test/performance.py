from baidu.baidu_api import get_completion_baidu
from myopenai.openai_api import get_completion_openai
from sparkdesk.spark_api import get_completion_spark
from zhipu.zhipu_api import get_completion_zhipu
from config.config import config


if __name__ == '__main__':
    prompt = config.user_prompt
    system = config.system_prompt
    print("temperature: 0.1")
    print("system:", system)
    print("prompt:", prompt)
    print("\n")

    # ernie_4_8k_response = get_completion_baidu(prompt)  # 欠费, 如果api正常可以取消注释
    gpt_35_turbo = get_completion_openai(prompt)
    spark_v35 = get_completion_spark(prompt)
    glm_4 = get_completion_zhipu(prompt)

    # print("Baidu ERNIE-4.0-8K: ", ernie_4_8k_response + "\n")
    print("OpenAI GPT-3.5-turbo: ", gpt_35_turbo + "\n")
    print("SparkDesk V3.5: ", spark_v35 + "\n")
    print("ZhipuAI glm-4: ", glm_4 + "\n")
