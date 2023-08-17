"""
助手交互所需函数
"""
import re
import time
import json
import gradio as gr

from chat_poets.chat import ChatPoet


def chat_poetry(tab: gr.Tab):
    """
    交互UI与逻辑的实现
    """
    pattern = gr.Markdown(f"{tab.id}")
    action = gr.State(value=False)  # 指示有效对话是否开始（开始时用户未提及古诗诗人则未进入）
    with gr.Row():
        # todo 历史记录
        with gr.Column(scale=2):
            gr.Markdown("## 历史记录")
            chat_history = gr.State([[]])  # 存储单次聊天记录的组件
        # 交互界面
        with gr.Column(scale=8):
            gr.Markdown("## 交互界面")
            # 聊天
            bot = gr.Chatbot(value=[(None, "今天想学哪首古诗？或是想了解哪位诗人呢？")], label="古诗学习助手",
                             elem_id=f"{tab.id}_chatbot").style(height=400)
            # 输入框
            with gr.Row():
                textbox = gr.Textbox(
                    show_label=False,
                    placeholder="Enter text and press enter",
                )
            # 按钮（New Chat） —— 清空交互界面、聊天记录与输入框
            button_newchat = gr.Button(value="刷新聊天")  # NewChatButton(components=, value="New Chat")

    """模块功能"""
    # 输入框 提交
    textbox.submit(fn=chat_user, inputs=[textbox, bot, action], outputs=[textbox, bot, chat_history, action]) \
        .then(fn=chat_respond, inputs=[bot, pattern, action], outputs=[bot, chat_history])
    # 按钮 刷新
    components = [bot, textbox, chat_history]  # 待刷新的组件
    clear_values = json.dumps(
        [component.postprocess(None) for component in components]
    )
    button_newchat.click(fn=newchat, inputs=chat_history, outputs=components, _js=f"() => {clear_values}")


def newchat(chat_history: list[list]):
    """
    刷新聊天，将已有的聊天记录存入历史记录
    """
    # 输出调试
    print("#########")
    if len(chat_history) > 1:
        for chat_list in chat_history:
            print(f"##用户：{chat_list[0]} ## Bot：{chat_list[1]}")
    ChatPoet.stop_chat()
    # todo 将已有聊天记录存入历史记录

    # 刷新聊天记录
    return [[(None, "今天想学哪首古诗？或是想了解哪位诗人呢？")], None, []]


def chat_user(user_message: str, history: list[list], action: bool):
    """
    单次对话中，首先调用的函数
    """
    print("调用chat_user")
    if action is True:
        allowed = True
    else:
        ChatPoet.allow_chat(user_message=user_message)
        allowed = False
        if (action is True) or (ChatPoet.res_dict != {}) and (ChatPoet.res_dict["exist"]):
            print(f"action is True: {action is True}")
            print(f"ChatPoet.res_dict: {ChatPoet.res_dict == {}}")
            allowed = True

    history += [[user_message, None]]
    # 输出调试
    return "", history, history, allowed


def chat_respond(history: list[list], pattern: str, action: bool):
    """
    单次对话中，在调用chat_user后调用，实现流式输出
    """
    print("调用chat_respond")
    if action is False:
        bot_message = "您似乎没有提到诗人或古诗，请再试试~"
    else:
        # 调用功能函数，获取助手的回答
        pattern_str = re.sub(r'\n', "", re.sub(r'<[^>]+>', "", pattern))
        bot_message = ChatPoet.gen_response(pattern=pattern_str, history=history)

    history[-1][1] = ""  # 下标-1表示最后一个
    for char in bot_message:
        history[-1][1] += char
        time.sleep(0.05)
        yield history, history
