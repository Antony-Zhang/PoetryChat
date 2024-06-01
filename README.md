---
title: PoetryChat
emoji: ⚡
colorFrom: pink
colorTo: indigo
sdk: gradio
sdk_version: 3.23.0
app_file: app.py
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference


## 简介
面向多年龄段的交互式古诗学习助手，基于讯飞星火大模型（SparkDesk）API开发

---

- [ ] Prompt进一步开发“词语解释”
- [ ] 向量数据进一步处理，削减信息长度
- [ ] 尝试使用HuggingFace的模型API部署，而不是本地模型
- [ ] 文生图

## 调试说明

在**app.py**文件下，运行main函数，待终端输出本地网址后双击打开，在弹出的窗口进行交互调试。
> 注意修改 LLM/spark_desk.py中的环境变量获取方式

## 结构说明

### 开发模块
🌟表示核心模块，🌛表示尚未使用或计划优化的模块
- chat_poets
  - prompts.json：🌟所有的Prompts提示词
  - get_path.py：🌟根据系统环境，获取json文件的绝对路径以供访问
  - poet_search：实时检索古诗信息（古诗文网）
- gradio_ui
  - gr_chat：🌟使用gradio搭建demo的模块
- gushiwen_vector_database：🌟向量知识库【已跑通验证，需要进一步处理】
  - gushiwen.json 古诗文数据
  - search_vectors.py：计算向量并获得相似文本
  - local_vectors：向量化的数据文件
  - embedding_model：下载的模型【未附上】
- txt2img：🌟文生图的模块

### 其他
- LLM： 与星火交互的功能封装
- requirement.txt：依赖包列表
- .gitattributes：hf配置
- .env：环境变量文件，存储星火api访问信息⚠️注意不要上传具体值
- 古诗文外挂json数据库与已经训练好的pt权重
  - [提取地址](https://pan.baidu.com/s/1n6x1gtNeS01bZh4_PYt4vg), 提取密码：h14p
  - 应放置位置：
    - PoetryChat/gushiwen_vector_database/gushiwen.json
    - PoetryChat/gushiwen_vector_database/local_vectors/data_and_vectors.pt


---

## 本地依赖
- Python-3.9

### Pip ✅
> 注意新的依赖要同步更新requirement.txt文件
- websocket-client
- langchain
- gradio-3.23.0
- bs4
- python-dotenv

## 贡献指南
如果您想为本项目做出贡献，请遵循以下步骤：

1. Fork 本仓库并克隆到您的本地环境。
2. 安装 pre-commit 钩子来确保代码风格和质量：
   ```
   pip install pre-commit==2.17.0
   pre-commit install
   ```
3. 创建一个新的分支并进行您的更改。
4. 在提交 Pull Request 之前，请确保运行了 pre-commit 检查并通过了所有测试。
5. 提交 Pull Request，并提供清晰的描述和修改理由。

感谢您的贡献！
