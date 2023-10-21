"""
部署主文件
"""
import gradio as gr
from gradio_ui.gr_chat import chat_poetry
from txt2img.txt2img import gen_img

with gr.Blocks() as demo:
    gr.Markdown("# --面向不同年龄段的交互式古诗学习助手--")

    with gr.Row():
        # 聊天交互
        with gr.Column(scale=7):
            with gr.Tab(label="成人模式", id="adult") as AdultTab:
                chat_poetry(AdultTab)
            with gr.Tab(label="青少年模式", id="teen") as TeenTab:
                chat_poetry(TeenTab)
            with gr.Tab(label="儿童模式", id="child") as ChildTab:
                chat_poetry(ChildTab)

        # 文生图
        with gr.Column(scale=3):
            gr.Markdown("## 诗句生图")
            # txt_img = gr.Textbox(
            #     show_label=False,
            #     placeholder="Enter text and press enter",
            # ).style(container=False)
            radio = gr.Radio(choices=["枯藤老树昏鸦", "小桥流水人家", "夕阳西下，断肠人在天涯"],
                             label="请选择用于生图的诗句")
            txt_img = gr.State("txt_img")
            image_button = gr.Button("点击生图")
            image_out = gr.Image(shape=(300, 700))

        radio.change(lambda s: s, inputs=radio, outputs=txt_img)  # 监听函数
        image_button.click(gen_img, inputs=txt_img, outputs=image_out)  # 生图函数


demo.queue()
demo.launch()

if __name__ == '__main__':
    demo.queue()
    demo.launch()
