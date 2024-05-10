---
title: PoetryChat
emoji: ⚡
colorFrom: pink
colorTo: indigo
sdk: gradio
sdk_version: 4.25.0
app_file: app.py
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference


## 简介
面向多年龄段的交互式古诗学习助手

---

## Todo
- [x] 更新SparkDesk调用方式，同步支持多种llm
- [ ] 向量数据库的RAG检索召回功能完善
- [ ] 接入Stable Diffusion文生图
- [ ] 重构设计Agent逻辑，意图识别+调用工具
- [ ] SFT open source llm

## 调试说明

**`app.py`** 文件的 `main` 函数为项目的入口

## 结构说明
`pass`

### 开发模块
🌟表示核心模块，🌛表示尚未使用或计划优化的模块

`pass`

### 其他
`pass`

---

## 本地依赖
- Python-3.10.14

### Pip ✅
> 注意新的依赖要同步更新requirement.txt文件
- websocket-client
- langchain-0.1.14
- gradio-4.25.0
- python-dotenv
- appbuilder-sdk-0.7.0

