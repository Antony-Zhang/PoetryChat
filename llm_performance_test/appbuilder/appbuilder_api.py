import os
import appbuilder
from config.config import config
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
# 配置密钥与应用ID
appbuilder_token = os.environ['APPBUILDER_TOKEN']
appbuilder_appid = os.environ['APPBUILDER_APPID']

# 初始化应用
builder = appbuilder.AppBuilderClient(appbuilder_appid)

# 创建会话ID
conversation_id = builder.create_conversation()

# 提问内容
# query = input("输入你想问AI的话：")
query = config.user_prompt

# 执行对话
msg = builder.run(conversation_id, query)
print("AI回答内容：", msg.content.answer)

# 输入你想问AI的话：你是谁
# AI回答内容： 你好，我是一位精通古诗词文化的老师，很高兴与你交流。如果你对古诗词有任何问题或者想要了解的内容，都可以随时告诉我，我会尽力为你解答和分享相关知识。

# 请给出一段以下由三重反引号包裹的古诗文的赏析。古诗文: ```{枯藤老树昏鸦，小桥流水人家，古道西风瘦马，夕阳西下，断肠人在天涯。}```
# AI回答内容： 您好，为了更好地为您提供古诗文的赏析，我想先了解一下您的身份和年龄，以便用最适合您的方式进行解释。请问您是一位古诗词爱好者，还是正在学习古诗词的初中生或高中生呢？或者，您是一位对古诗词感兴趣的小朋友呢？
