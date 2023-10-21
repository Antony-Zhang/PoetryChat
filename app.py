"""
部署主文件
"""
import gradio as gr
from chat_poets.chat import ChatPoet
from gradio_ui.gr_chat import chat_poetry
from txt2img.txt2img import gen_img


def change_content():
    """
    更新当前聊天的古诗内容（原文）
    """
    chatpoet = ChatPoet()  # 注意！必须要对实例化后的对象进行操作，否则无法更新
    chatpoet.content = "床前明月光，疑是地上霜。举头望明月，低头思故乡。"
    print(chatpoet.content)
    return chatpoet.content


with gr.Blocks() as demo:
    gr.Markdown("# --面向不同年龄段的交互式古诗学习助手--")
    with gr.Row():
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
            # radio = gr.Radio(choices=ChatPoet.sentence_choices,
            #                  label="请选择用于生图的诗句")
            # txt_img = gr.State("txt_img")
            image_out = gr.Image(shape=(300, 700))
            image_button = gr.Button("点击生图")
            # change_button = gr.Button("change")
            txt_img = gr.Textbox(
                show_label=False,
                placeholder="请输入用于生图的诗句吧～",
                label="生图文本"
            ).style(container=False)

            # radio.change(lambda s: s, inputs=radio, outputs=txt_img)  # 监听函数
            image_button.click(gen_img, inputs=txt_img, outputs=image_out)  # 生图函数
            # change_button.click(change_content, outputs=txt_img)  # 测试按钮

demo.queue()
demo.launch()

if __name__ == '__main__':
    demo.queue()
    demo.launch()
