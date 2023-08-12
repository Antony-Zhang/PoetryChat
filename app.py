"""
部署主文件
"""
import gradio as gr
from gradio_ui.gr_chat import chat_poetry


with gr.Blocks() as demo:
    gr.Markdown("# --面向不同年龄段的交互式古诗学习助手--")

    with gr.Row():
        # 聊天交互
        with gr.Column(scale=7):
            with gr.Tab("成人模式"):
                chat_poetry("成人模式")
            with gr.Tab("青少年模式"):
                chat_poetry("青少年模式")
            with gr.Tab("儿童模式"):
                chat_poetry("儿童模式")

        # 文生图
        with gr.Column(scale=3):
            gr.Markdown("## 文生图")
            image_out = gr.Image(shape=(200, 200))
            txt_img = gr.Textbox(
                show_label=False,
                placeholder="Enter text and press enter",
            ).style(container=False)

            image_button = gr.Button("点击生图")
        image_button.click(None, inputs=txt_img, outputs=image_out)  # 生图函数待填充 todo


if __name__ == '__main__':
    demo.queue()
    demo.launch()
