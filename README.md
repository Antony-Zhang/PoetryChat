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

## 结构说明

### 开发模块
- chat_poets： 与星火交互，得出回答的模块
- gradio_ui： 使用gradio搭建demo的模块
- txt2img： 文生图的模块

### 其他
- LLM： 与星火交互的功能封装
- prompts： Prompts提示词文件夹

---

## 本地依赖
- Python-3.9

### (1) Pip
- websocket-client
- langchain
- gradio

### (2) Conda
- websocket-client-0.58.0
#### conda-forge
- langchain-0.0.239
- gradio-3.23.0

# 配置

