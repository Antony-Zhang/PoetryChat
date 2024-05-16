# -*- coding: utf-8 -*-
import gradio as gr
import json
import appbuilder
import os
import ast
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
# 配置密钥与应用ID
appbuilder_token = os.environ['APPBUILDER_TOKEN']
appbuilder_appid = os.environ['APPBUILDER_APPID_STUDENT']
demo_version = "0.1"

# 初始化Agent
agent_json = appbuilder.AppBuilderClient(appbuilder_appid)

query = """
南乡子
李珣
烟漠漠，雨凄凄，岸花零落鸣鸪啼。
远客扁舟临野渡，思乡处，潮退水平春色幕。
"""


############# 函数 #####################
class ChatTests:
    question_json = {
        "题干": "下面哪一个选项的诗句最能表达词中“远客”的心境？请作出判断。",
        "选项": [
            "春潮带雨晚来急，野渡无人舟自横。",
            "迷津欲有问，平海夕漫漫。",
            "浊酒一杯家万里，燕然未勒归无计。",
            "仍怜故乡水，万里送行舟。"
        ],
        "答案": "C",
        "解析": "《南乡子》表达的远客心境是，身在遥远异乡，内心孤独凄凉，思归心切，却只能在潮退的日暮春色里，遥寄乡愁。而C中“浊酒一杯家万里，燕然未勒归无计”，也是表达了作者深处边疆之“远”，保家卫国，但功业未建，只有在杯酒中表达内心的孤独凄凉，寄托思乡之愁。",
        "难度": "中等",
        "评论": "这道题考察了诗词赏析，需要考生对诗词有一定的积累和理解。",
        "知识点标签": [
            "诗词",
            "举一反三"
        ]
    }

    question = question_json["题干"]
    choices = question_json["选项"]
    answer = question_json["答案"]
    analysis = question_json["解析"]
    difficulty = question_json["难度"]
    comment = question_json["评论"]
    tags = question_json["知识点标签"]
    log = ""
    ques_header = ["题序", "题干", "选项A", "选项B", "选项C", "选项D", "答案", "解析", "难度", "评论", "知识点标签"]
    tmpdir = ""
    question_num = 0
    question_df = []
    # advice_changed = False
    # 创建会话ID
    conversation_current = agent_json.create_conversation()

    # 添加日志
    def addLog(self, log):
        # 获取当前时间
        now = datetime.now()
        # 格式化当前时间
        formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
        self.log = formatted_now + ": " + log + "\n" + self.log

    # 检查结果
    def checkAnswer(self, choice):
        # return choice 
        if choice[0] == self.answer:
            return "恭喜你答对啦！再接再厉！"
        else:
            return "很抱歉你回答错误啦，再试一次吧！记得记录错题~"

    def format_whale_editor(self):
        formatted_data = f"````{{multiple-choice}}\n:correct: {self.answer}\n\n```{{mc-question}}\n{self.question}\n```\n\n```{{mc-choices}}\n"
        for option in self.choices:
            formatted_data += f"- {option}\n"
        formatted_data += f"```\n\n```{{mc-solution}}\n{self.analysis}\n````\n"

        return formatted_data

    def update_self(self):
        self.question = self.question_json["题干"]
        self.choices = self.question_json["选项"]
        self.answer = self.question_json["答案"]
        self.analysis = self.question_json["解析"]
        self.difficulty = self.question_json["难度"]
        self.comment = self.question_json["评论"]
        self.tags = self.question_json["知识点标签"]

    def org_df_style(self):
        df_style = [self.question_num, self.question, self.choices[0], self.choices[1], self.choices[2],
                    self.choices[3],
                    self.answer, self.analysis, self.difficulty, self.comment, self.tags]
        return df_style

    # 获取Text并输出问题
    def generate_quesiton(self, context, advice):
        conversation_new = agent_json.create_conversation()
        context = "```\n" + context + "```\n" + "请基于以上文本出单选题，正确选项必须唯一，其他选项必须是错误的，不同选项内容必须有差异，选项中不要包含选项字母，答案是正确选项的字母。"
        if advice != "":
            context = context + "\n 另外：" + advice
        msg = agent_json.run(conversation_new, context)
        # 提取 JSON 数据，最后生成的类型是‘dict’，可以放入JSON框(否则会报错)
        markdown_text = msg.content.answer
        # print(markdown_text)

        json_start_index = markdown_text.find("```json") + 8
        json_end_index = markdown_text.find("```", json_start_index) - 1
        json_data = ""

        # print(json_data + "\n json_start_index=" + str(json_start_index))

        if json_start_index != 7:
            json_data = markdown_text[json_start_index:json_end_index].strip()
            self.question_json = json.loads(json_data)
            self.update_self()
            self.addLog("生成题目成功，题干为：" + self.question)
            self.conversation_current = conversation_new
        else:
            self.addLog("ERROR：生成题目失败，详见【返回内容】")
            gr.Warning("ERROR: 生成题目失败，详见【返回内容】，请重试")

        options = ["A." + self.choices[0] + "\n", "B." + self.choices[1] + "\n",
                   "C." + self.choices[2] + "\n", "D." + self.choices[3] + "\n"]
        question_markdown = "## " + self.question
        formatted_whale = self.format_whale_editor()
        radio = gr.Radio(options, label="选择你认为最正确的一项")

        return (self.question_json, question_markdown,
                self.question, self.choices[0], self.choices[1], self.choices[2],
                self.choices[3], self.answer, self.analysis,
                self.difficulty, self.comment, self.tags,
                markdown_text, formatted_whale, radio, self.analysis, self.log)

    def optimize_quesiton(self, context):
        msg = agent_json.run(self.conversation_current,
                             context + "，基于同样的知识文本，给出优化后的单选题json，请一定遵循单选题规范")
        # 提取 JSON 数据，最后生成的类型是‘dict’，可以放入JSON框(否则会报错)
        markdown_text = msg.content.answer
        # print("收到回复")

        json_start_index = markdown_text.find("```json") + 8
        json_end_index = markdown_text.find("```", json_start_index) - 1
        json_data = ""
        # print(json_data + "\n json_start_index=" + str(json_start_index))

        if json_start_index != 7:
            json_data = markdown_text[json_start_index:json_end_index].strip()
            self.question_json = json.loads(json_data)
            # print(json_data)
            self.update_self()
            self.addLog("优化题目成功，题干为：" + self.question)
            # print("生成题目成功")
        else:
            self.addLog("ERROR：生成题目失败，详见【返回内容】")
            gr.Warning("ERROR: 生成题目失败，详见【返回内容】，请重试")
            # print("生成题目失败")

        options = ["A." + self.choices[0] + "\n", "B." + self.choices[1] + "\n",
                   "C." + self.choices[2] + "\n", "D." + self.choices[3] + "\n"]
        question_markdown = "## " + self.question
        formatted_whale = self.format_whale_editor()
        radio = gr.Radio(options, label="选择并check吧")

        return (self.question_json, question_markdown,
                self.question, self.choices[0], self.choices[1], self.choices[2],
                self.choices[3], self.answer, self.analysis,
                self.difficulty, self.comment, self.tags,
                markdown_text, formatted_whale, radio, self.analysis, self.log)

    def manual_update(self,
                      question_gen,
                      choicesA_gen, choicesB_gen, choicesC_gen, choicesD_gen,
                      answer_gen,
                      analysis_gen,
                      difficulty_gen,
                      comment_gen,
                      tags_gen
                      ):
        choices_gen = [choicesA_gen, choicesB_gen, choicesC_gen, choicesD_gen]
        # 创建一个字典，包含所有Text组件的内容
        self.question_json = {
            "题干": question_gen,
            "选项": choices_gen,
            "答案": answer_gen,
            "解析": analysis_gen,
            "难度": difficulty_gen,
            "评论": comment_gen,
            "知识点标签": ast.literal_eval(tags_gen)
        }

        self.update_self()
        formatted_whale = self.format_whale_editor()
        options = ["A." + self.choices[0] + "\n", "B." + self.choices[1] + "\n",
                   "C." + self.choices[2] + "\n", "D." + self.choices[3] + "\n"]
        radio = gr.Radio(options, label="选择你认为最正确的一项")
        self.addLog("手动更新题目成功，题干为：" + self.question)

        return self.question_json, formatted_whale, radio, self.analysis, self.log

    # 题库表格管理
    def save_question(self):
        self.question_num += 1
        self.question_df.append(self.org_df_style())

        self.addLog("保存题目成功，ID为：" + str(self.question_num) + "，题干为：" + self.question)

        return self.question_df, self.log

    def delete_question(self, question_id):
        pass

    def clear_xlsx(self):
        self.question_df = []
        self.question_num = 0
        self.addLog("清空题目成功，清空了 " + str(self.question_num) + " 个题目")

        return self.question_df, self.log

    def save_xlsx(self):
        # print("保存题目")
        df = pd.DataFrame(self.question_df, columns=self.ques_header)
        file_name = f"question_{self.question_num}.xlsx"
        df.to_excel(file_name, index=False)
        file_path = os.path.join(self.tmpdir, file_name)
        self.addLog(f"保存题目成功，文件路径为{file_path}\n")

        return file_path, self.log

    def parse_xlsx(self, file):
        # print(file)
        if file == None:
            self.addLog("未选择文件")
            return self.question_df, self.log

        df = pd.read_excel(file, engine='openpyxl')
        df_list = df.values.tolist()
        # print(df_list)
        num = 0
        for row in df_list:
            self.question_num += 1
            num += 1
            row[0] = self.question_num
            # print(row)
            self.question_df.append(row)

        self.addLog("读取题目集成功，共 " + str(num) + " 个题目")
        return self.question_df, self.log


################# 界面 ###################
# my_theme = gr.Theme.from_hub("gstaff/xkcd")
with gr.Blocks(title='ChatTests ' + demo_version, theme=gr.themes.Soft()) as demo:
    # TODO：增加一个随机刷题功能
    # TODO：增加难度选择功能
    chattests = ChatTests()
    options = ["A." + chattests.choices[0], "B." + chattests.choices[1],
               "C." + chattests.choices[2], "D." + chattests.choices[3]]

    with gr.Row():
        with gr.Column():
            with gr.Tab("AI出题"):
                context_input = gr.Textbox(label="输入文本", lines=10, value=query,
                                           info="输入想出题的知识文本，点击【生成新题目】可通过AI生成题目")

                with gr.Row():
                    advice_input = gr.Textbox(label="出题要求/优化需求", lines=6, interactive=True)
                    with gr.Column():
                        generate_button = gr.Button("生成新题目")
                        # random_button = gr.Button("随机K12题目（待实现）")
                        optimize_button = gr.Button("优化题目(效果不稳定)")  # TODO：优化题目
                        manual_button = gr.Button("更新题目")  # TODO：考虑保留历史回退功能
                        save_button = gr.Button("保存题目(满意记得保存)")

            with gr.Tab("刷卷模式(待实现)"):
                score = gr.Number(label="分数", value=0)

        with gr.Tab("题目效果展示"):
            question_markdown = gr.Markdown("## " + chattests.question)
            choices_radio = gr.Radio(options, label="请作答")
            # choices_html = gr.HTML(chattests.format_multiple_choices_html())
            check_button = gr.Button("提交答案")
            check_result = gr.Textbox(label="答题结果")

            with gr.Accordion("查看解析", open=False):
                analysis = gr.Textbox(label="解析", lines=3, interactive=False, value=chattests.analysis)

        with gr.Tab("json & WhaleEditor 格式"):
            with gr.Accordion("查看Json格式", open=False):
                gen_output = gr.JSON(label="题目json", value=chattests.question_json)

            with gr.Accordion("Whale Editor格式", open=False):
                whale_format = gr.Textbox(label="Whale Editor", lines=6, interactive=False,
                                          value=chattests.format_whale_editor())

        with gr.Tab("修改题目信息"):
            with gr.Accordion("修改题目细节", open=False):
                question_gen = gr.Textbox(label="题干", lines=2, interactive=True, value=chattests.question)
                with gr.Accordion("修改选项", open=True):
                    choicesA_gen = gr.Textbox(label="选项A", interactive=True, value=chattests.choices[0])
                    choicesB_gen = gr.Textbox(label="选项B", interactive=True, value=chattests.choices[1])
                    choicesC_gen = gr.Textbox(label="选项C", interactive=True, value=chattests.choices[2])
                    choicesD_gen = gr.Textbox(label="选项D", interactive=True, value=chattests.choices[3])
                with gr.Row():
                    answer_gen = gr.Textbox(label="答案", interactive=True, value=chattests.answer)
                    difficulty_gen = gr.Textbox(label="难度", interactive=True, value=chattests.difficulty)
                analysis_gen = gr.Textbox(label="解析", lines=2, interactive=True, value=chattests.analysis)
                comment_gen = gr.Textbox(label="评论", lines=2, interactive=True, value=chattests.comment)
                tags_gen = gr.Textbox(label="知识点标签", interactive=True, value=chattests.tags)

    with gr.Row():
        with gr.Tab("题库管理"):
            with gr.Row():
                with gr.Row():
                    upload_file = gr.File(label="上传题目集")
                    save_file = gr.File(label="生成的题目集文件")
                    with gr.Column():
                        save_all_button = gr.Button("保存题目集")
                        clear_button = gr.Button("清空题目集")
            questions = gr.Dataframe(headers=chattests.ques_header, interactive=False)

        # 可通过将该格式文本直接作为知识文本的方式进行输入
        # with gr.Tab("读取Whale_editor格式"):
        #         whale_format_text = gr.Textbox(label="Whale_editor格式文本", interactive=True)
        #         whale_format_button = gr.Button("读取Whale_editor格式")

        with gr.Tab("更多信息"):
            with gr.Accordion("日志", open=True):
                op_log = gr.Textbox(label="日志", lines=5, interactive=False)
                # TODO：待添加日志功能

            with gr.Accordion("返回内容", open=True):
                return_log = gr.Textbox(label="返回内容", lines=5, interactive=False)

    check_button.click(chattests.checkAnswer, inputs=choices_radio, outputs=check_result)
    generate_button.click(chattests.generate_quesiton,
                          inputs=[context_input, advice_input],
                          outputs=[gen_output, question_markdown,
                                   question_gen, choicesA_gen, choicesB_gen, choicesC_gen, choicesD_gen,
                                   answer_gen, analysis_gen, difficulty_gen, comment_gen, tags_gen,
                                   return_log, whale_format, choices_radio, analysis, op_log]
                          )
    manual_button.click(chattests.manual_update,
                        inputs=[question_gen, choicesA_gen, choicesB_gen, choicesC_gen, choicesD_gen,
                                answer_gen, analysis_gen, difficulty_gen, comment_gen, tags_gen],
                        outputs=[gen_output, whale_format, choices_radio, analysis, op_log]
                        )
    optimize_button.click(chattests.optimize_quesiton,
                          inputs=advice_input,
                          outputs=[gen_output, question_markdown,
                                   question_gen, choicesA_gen, choicesB_gen, choicesC_gen, choicesD_gen,
                                   answer_gen, analysis_gen, difficulty_gen, comment_gen, tags_gen,
                                   return_log, whale_format, choices_radio, analysis, op_log]
                          )

    save_button.click(chattests.save_question,
                      outputs=[questions, op_log])

    upload_file.upload(fn=chattests.parse_xlsx, inputs=upload_file, outputs=[questions, op_log])
    save_all_button.click(fn=chattests.save_xlsx, outputs=[save_file, op_log])
    clear_button.click(fn=chattests.clear_xlsx, outputs=[questions, op_log])

if __name__ == "__main__":
    demo.launch()
