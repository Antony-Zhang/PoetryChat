import gradio as gr


def chatbot():
    with gr.Row():
        # 历史记录
        with gr.Column(scale=0.2):
            gr.Markdown("## 历史记录")
        # 交互界面
        with gr.Column(scale=0.8):
            gr.Markdown("## 交互界面")
            bot = gr.Chatbot(value=[], label="古诗学习助手", elem_id="chatbot").style(height=400)
            # 输入框
            txt = gr.Textbox(
                show_label=False,
                placeholder="Enter text and press enter",
            ).style(container=False)


def txt2img():
    gr.Markdown("## 文生图")
    chatbot_img = gr.Chatbot(value=[], label="古诗学习助手", elem_id="chatbot").style(height=400)
    txt_img = gr.Textbox(
        show_label=False,
        placeholder="Enter text and press enter",
    ).style(container=False)


if __name__ == '__main__':
    with gr.Blocks() as demo:
        gr.Markdown("# --面向不同年龄段的交互式古诗学习助手--")
        with gr.Row():
            # 聊天交互
            with gr.Column(scale=0.7):
                with gr.Tab("成人模式"):
                    chatbot()
                with gr.Tab("青少年模式"):
                    chatbot()
                with gr.Tab("儿童模式"):
                    chatbot()
            # 文生图
            with gr.Column(scale=0.3):
                txt2img()

    demo.launch()
