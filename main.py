# -*- coding: utf-8 -*-
import gradio as gr         # 用于构建Web界面
from loguru import logger   # 用于日志记录
import appbuilder           # 用于构建应用
import time
import os

from src.config import (
    http_proxy,
    hide_history_when_not_logged_in,
    chat_name_method_index,
    my_api_key,
    multi_api_key,
    server_name,
    server_port,
    share,
    config_file,
    api_host,
    authflag,
    dockerflag,
    show_api_billing,
    latex_delimiters_set,
    user_avatar,
    bot_avatar,
    autobrowser,
    update_doc_config,
)
from src.gradio_patch import reg_patch
from src.models import get_model
from src.overwrites import (
    postprocess,
    postprocess_chat_messages,
    reload_javascript,
    get_html,
)
from src.presets import (
    MODEL_ALIASES,
    MODELS,
    HISTORY_NAME_METHODS,
    small_and_beautiful_theme,
    CONCURRENT_COUNT,
    TITLE,
    HIDE_MY_KEY,
    DEFAULT_MODEL,
    REPLY_LANGUAGES,
    ENABLE_STREAMING_OPTION,
    DESCRIPTION,
    favicon_path,
    API_HOST,
    HISTORY_DIR,
    assets_path,
    # Prompt
    DEFAULT_SYSTEM_PROMPT,
    CHILD_SYSTEM_PROMPT,
    STUDENT_SYSTEM_PROMPT,
    ADULT_SYSTEM_PROMPT,
)
from src.utils import (
    delete_chat_history,
    filter_history,
    get_history_list,
    auto_name_chat_history,
    get_template_dropdown,
    rename_chat_history,
    init_history_list,
    get_first_history_name,
    setup_wizard,
    auth_from_conf,
    get_geoip,
    get_template_names,
    load_template,
    get_history_names,
    reset,
    predict,
    interrupt,
    retry,
    i18n,
    dislike,
    toggle_like_btn_visibility,
    set_key,
    set_single_turn,
    hide_middle_chars,
    set_system_prompt,
    start_outputing,
    set_token_upper_limit,
    set_temperature,
    set_user_identifier,
    set_top_p,
    delete_first_conversation,
    delete_last_conversation,
    set_n_choices,
    set_logit_bias,
    load_chat_history,
    end_outputing,
    set_max_tokens,
    reset_default,
    reset_textbox,
    set_stop_sequence,
    set_presence_penalty,
    set_frequency_penalty,
    upload_chat_history,
    export_markdown,
    billing_info,
    get_template_content,
    like,
    transfer_input,
    handle_file_upload,
    handle_summarize_index,
    update_image_text
)

from src.gen_image import image_generator

reg_patch()

gr.Chatbot._postprocess_chat_messages = postprocess_chat_messages
gr.Chatbot.postprocess = postprocess

# 设置环境变量和默认应用ID
os.environ["APPBUILDER_TOKEN"] = "bce-v3/ALTAK-QwuihwYsMjA5jBiIBVfJP/51f962e086efb6f3a2332414360552bae5f3958d"
APPBUILDER_APPID_DEFAULT = "2ef66c07-b4ac-4fb7-adf9-a76b5c80b2b5"
APPBUILDER_APPID_CHILD = "c2de7a91-e17e-4d31-becf-b5d014156de7"
APPBUILDER_APPID_STUDENT = "93ea3085-0e79-40f0-8e3d-f47381af427a"



# def respond(query, app_selection, chat_history):
#     '''
#     根据用户选择的模式和输入的文本，生成回复
#     '''
#     # 根据用户选择设置应用ID
#     if app_selection == "成人模式":
#         app_id = APPBUILDER_APPID_DEFAULT
#     elif app_selection == "儿童模式":
#         app_id = APPBUILDER_APPID_CHILD
#     elif app_selection == "学生模式":
#         app_id = APPBUILDER_APPID_STUDENT

#     # 初始化应用
#     builder = appbuilder.AppBuilderClient(app_id)

#     # 创建会话ID
#     conversation_id = builder.create_conversation()

#     # 执行对话
#     msg = builder.run(conversation_id, query)
    
#     chat_history.append((query, msg.content.answer))
#     time.sleep(2)
#     return "", chat_history

# # 创建独立的模式切换模块
# def mode_switch_ui():
#     with gr.Tab(label=i18n("切换模式")):
#         gr.Markdown(i18n("# 选择运行模式 ⚙️"), elem_id="mode-selection-info")
#         with gr.Accordion(i18n("模式切换"), open=True):
#             mode_selection = gr.Radio(
#                 choices=["默认模式", "成人模式", "儿童模式", "学生模式"],
#                 label=i18n("运行模式"),
#                 value="默认模式"
#             )
#     return mode_selection

def on_mode_change(mode, current_model):
    match(mode):
        case "默认模式":
            prompt = DEFAULT_SYSTEM_PROMPT
        case "成人模式":
            prompt = ADULT_SYSTEM_PROMPT
        case "儿童模式":
            prompt = CHILD_SYSTEM_PROMPT
        case "学生模式":
            prompt = STUDENT_SYSTEM_PROMPT
    current_model.set_system_prompt(prompt)  # 设置模型的Prompt
    return f"已选模式：{mode}\n ---\n Prompt:\n {prompt}"

''' 构建Web界面 '''
with gr.Blocks(theme=small_and_beautiful_theme) as demo:
    user_name = gr.Textbox("", visible=False)
    # 激活/logout路由
    logout_hidden_btn = gr.LogoutButton(visible=False)
    promptTemplates = gr.State(load_template(get_template_names()[0], mode=2))
    user_question = gr.State("")
    assert type(my_api_key) == str
    user_api_key = gr.State(my_api_key)
    current_model = gr.State()
    # mode_selection = mode_switch_ui()

    topic = gr.State(i18n("未命名对话历史记录"))

    with gr.Row(elem_id="chuanhu-header"):
        gr.HTML(get_html("header_title.html").format(
            app_title=TITLE), elem_id="app-title")
        status_display = gr.Markdown(get_geoip, elem_id="status-display")
    with gr.Row(elem_id="float-display"):
        user_info = gr.Markdown(
            value="getting user info...", elem_id="user-info")

    with gr.Row(equal_height=True, elem_id="chuanhu-body"):

        with gr.Column(elem_id="menu-area"):
            with gr.Column(elem_id="chuanhu-history"):
                with gr.Box():
                    with gr.Row(elem_id="chuanhu-history-header"):
                        with gr.Row(elem_id="chuanhu-history-search-row"):
                            with gr.Column(min_width=150, scale=2):
                                historySearchTextbox = gr.Textbox(show_label=False, container=False, placeholder=i18n(
                                    "搜索（支持正则）..."), lines=1, elem_id="history-search-tb")
                            with gr.Column(min_width=52, scale=1, elem_id="gr-history-header-btns"):
                                uploadFileBtn = gr.UploadButton(
                                    interactive=True, label="", file_types=[".json"], elem_id="gr-history-upload-btn")
                                historyRefreshBtn = gr.Button("", elem_id="gr-history-refresh-btn")

                    with gr.Row(elem_id="chuanhu-history-body"):
                        with gr.Column(scale=6, elem_id="history-select-wrap"):
                            historySelectList = gr.Radio(
                                label=i18n("从列表中加载对话"),
                                choices=get_history_names(),
                                value=get_first_history_name(),
                                # multiselect=False,
                                container=False,
                                elem_id="history-select-dropdown"
                            )
                        with gr.Row(visible=False):
                            with gr.Column(min_width=42, scale=1):
                                historyDeleteBtn = gr.Button(
                                    "🗑️", elem_id="gr-history-delete-btn")
                            with gr.Column(min_width=42, scale=1):
                                historyDownloadBtn = gr.Button(
                                    "⏬", elem_id="gr-history-download-btn")
                            with gr.Column(min_width=42, scale=1):
                                historyMarkdownDownloadBtn = gr.Button(
                                    "⤵️", elem_id="gr-history-mardown-download-btn")
                    with gr.Row(visible=False):
                        with gr.Column(scale=6):
                            saveFileName = gr.Textbox(
                                show_label=True,
                                placeholder=i18n("设置文件名: 默认为.json，可选为.md"),
                                label=i18n("设置保存文件名"),
                                value=i18n("对话历史记录"),
                                elem_classes="no-container"
                                # container=False,
                            )
                        with gr.Column(scale=1):
                            renameHistoryBtn = gr.Button(
                                i18n("💾 保存对话"), elem_id="gr-history-save-btn")
                            exportMarkdownBtn = gr.Button(
                                i18n("📝 导出为 Markdown"), elem_id="gr-markdown-export-btn")

            with gr.Column(elem_id="chuanhu-menu-footer"):
                with gr.Row(elem_id="chuanhu-func-nav"):
                    gr.HTML(get_html("func_nav.html"))
                # gr.HTML(get_html("footer.html").format(versions=versions_html()), elem_id="footer")
                # gr.Markdown(CHUANHU_DESCRIPTION, elem_id="chuanhu-author")

        with gr.Column(elem_id="chuanhu-area", scale=5):
            with gr.Column(elem_id="chatbot-area"):
                with gr.Row(elem_id="chatbot-header"):
                    # 获取模型的别名列表
                    MODEL_ALIASES_LIST = list(MODEL_ALIASES.values())
                    DEFAULT_MODEL_ALIAS = MODEL_ALIASES["gpt-3.5-turbo"]
                    
                    model_select_dropdown = gr.Dropdown(
                        label=i18n("选择模型"), choices=MODEL_ALIASES_LIST, multiselect=False, value=DEFAULT_MODEL_ALIAS,
                        interactive=True,
                        show_label=False, container=False, elem_id="model-select-dropdown"
                    )
                    lora_select_dropdown = gr.Dropdown(
                        label=i18n("选择LoRA模型"), choices=[], multiselect=False, interactive=True,
                        container=False, visible=False,
                    )
                    gr.HTML(get_html("chatbot_header_btn.html").format(
                        json_label=i18n("历史记录（JSON）"),
                        md_label=i18n("导出为 Markdown")
                    ), elem_id="chatbot-header-btn-bar")
                with gr.Row():
                    chatbot = gr.Chatbot(
                        label="ChatGPT",
                        elem_id="chuanhu-chatbot",
                        latex_delimiters=latex_delimiters_set,
                        sanitize_html=False,
                        # height=700,
                        show_label=False,
                        avatar_images=[user_avatar, bot_avatar],
                        show_share_button=False,
                    )
                with gr.Row(elem_id="chatbot-footer"):
                    with gr.Box(elem_id="chatbot-input-box"):
                        with gr.Row(elem_id="chatbot-input-row"):
                            gr.HTML(get_html("chatbot_more.html").format(
                                single_turn_label=i18n("单轮对话"),
                                websearch_label=i18n("在线搜索"),
                                upload_file_label=i18n("上传文件"),
                                uploaded_files_label=i18n("知识库文件"),
                                uploaded_files_tip=i18n("在工具箱中管理知识库文件")
                            ))
                            with gr.Row(elem_id="chatbot-input-tb-row"):
                                with gr.Column(min_width=225, scale=12):
                                    user_input = gr.Textbox(
                                        elem_id="user-input-tb",
                                        show_label=False,
                                        placeholder=i18n("在这里输入"),
                                        elem_classes="no-container",
                                        max_lines=5,
                                        # container=False
                                    )
                                with gr.Column(min_width=42, scale=1, elem_id="chatbot-ctrl-btns"):
                                    submitBtn = gr.Button(
                                        value="", variant="primary", elem_id="submit-btn")
                                    cancelBtn = gr.Button(
                                        value="", variant="secondary", visible=False, elem_id="cancel-btn")
                        # Note: Buttons below are set invisible in UI. But they are used in JS.
                        with gr.Row(elem_id="chatbot-buttons", visible=False):
                            with gr.Column(min_width=120, scale=1):
                                emptyBtn = gr.Button(
                                    i18n("🧹 新的对话"), elem_id="empty-btn"
                                )
                            with gr.Column(min_width=120, scale=1):
                                retryBtn = gr.Button(
                                    i18n("🔄 重新生成"), elem_id="gr-retry-btn")
                            with gr.Column(min_width=120, scale=1):
                                delFirstBtn = gr.Button(i18n("🗑️ 删除最旧对话"))
                            with gr.Column(min_width=120, scale=1):
                                delLastBtn = gr.Button(
                                    i18n("🗑️ 删除最新对话"), elem_id="gr-dellast-btn")
                            with gr.Row(visible=False) as like_dislike_area:
                                with gr.Column(min_width=20, scale=1):
                                    likeBtn = gr.Button(
                                        "👍", elem_id="gr-like-btn")
                                with gr.Column(min_width=20, scale=1):
                                    dislikeBtn = gr.Button(
                                        "👎", elem_id="gr-dislike-btn")

        with gr.Column(elem_id="toolbox-area", scale=1):
            # For CSS setting, there is an extra box. Don't remove it.
            with gr.Box(elem_id="chuanhu-toolbox"):
                with gr.Row():
                    gr.Markdown("## " + i18n("工具箱"))
                    gr.HTML(get_html("close_btn.html").format(
                        obj="toolbox"), elem_classes="close-btn")
                with gr.Tabs(elem_id="chuanhu-toolbox-tabs"):
                    with gr.Tab(label=i18n("主题")):
                        with gr.Accordion(label=i18n("模型"), open=not HIDE_MY_KEY, visible=not HIDE_MY_KEY):
                            keyTxt = gr.Textbox(
                                show_label=True,
                                placeholder=f"Your API-key...",
                                value=hide_middle_chars(user_api_key.value),
                                type="password",
                                visible=not HIDE_MY_KEY,
                                label="API-Key",
                                elem_id="api-key"
                            )
                            if multi_api_key:
                                usageTxt = gr.Markdown(i18n(
                                    "多账号模式已开启，无需输入key，可直接开始对话"), elem_id="usage-display",
                                    elem_classes="insert-block", visible=show_api_billing)
                            else:
                                usageTxt = gr.Markdown(i18n(
                                    "**发送消息** 或 **提交key** 以显示额度"), elem_id="usage-display",
                                    elem_classes="insert-block", visible=show_api_billing)
                        gr.Markdown("---", elem_classes="hr-line", visible=not HIDE_MY_KEY)
                        with gr.Accordion(label="讨论主题展示", open=True):
                            theme = gr.Textbox(
                                show_label=True,
                                placeholder=i18n("输入你想讨论的古诗"),
                                label="古诗词全文",
                                value=None, # INITIAL_SYSTEM_PROMPT,
                                lines=8
                            )
                            retain_system_prompt_checkbox = gr.Checkbox(
                                label=i18n("新建对话保留当前讨论主题"), value=False, visible=True, 
                                elem_classes="switch-checkbox")
                            with gr.Accordion(label=i18n("加载自定义讨论主题"), open=True):
                                with gr.Column():
                                    with gr.Row():
                                        with gr.Column(scale=6):
                                            templateFileSelectDropdown = gr.Dropdown(
                                                label=i18n("选择Prompt模板集合文件"),
                                                choices=get_template_names(),
                                                multiselect=False,
                                                value=get_template_names()[0],  # 默认选择第一个文件
                                                container=False,
                                            )
                                        with gr.Column(scale=1):
                                            templateRefreshBtn = gr.Button(
                                                i18n("🔄 刷新"))
                                    with gr.Row():
                                        with gr.Column():
                                            templateSelectDropdown = gr.Dropdown(
                                                label=i18n("从Prompt模板中加载"),
                                                choices=load_template(
                                                    get_template_names()[
                                                        0], mode=1
                                                ),
                                                multiselect=False,
                                                container=False,
                                            )
                        gr.Markdown("---", elem_classes="hr-line")
                        with gr.Accordion(label=i18n("知识库"), open=True, elem_id="gr-kb-accordion", visible=True):
                            use_websearch_checkbox = gr.Checkbox(label=i18n(
                                "使用在线搜索"), value=False, elem_classes="switch-checkbox", elem_id="gr-websearch-cb",
                                visible=False)
                            index_files = gr.Files(label=i18n(
                                "上传"), type="file",
                                file_types=[".pdf", ".docx", ".pptx", ".epub", ".xlsx", ".txt", "text", "image"],
                                elem_id="upload-index-file")
                            two_column = gr.Checkbox(label=i18n(
                                "双栏pdf"), value=False)
                            summarize_btn = gr.Button(i18n("总结"), visible=False)

                    with gr.Tab(label=i18n("模式")):  # 将标题修改为“模式”
                        # gr.Markdown(i18n("## 选择运行模式⚙️"),
                        #             elem_id="mode-selection-info")
                        with gr.Accordion(i18n("模式切换"), open=True):
                            mode_selection = gr.Radio(choices=["默认模式", "成人模式", "儿童模式", "学生模式"], label=i18n("运行模式"), value="默认模式")
                            submit_button = gr.Button(i18n("确认选择"))
                            result = gr.Textbox(label="模式Prompt", value=DEFAULT_SYSTEM_PROMPT)
                            submit_button.click(on_mode_change, 
                                                inputs=[mode_selection, current_model], 
                                                outputs=result)
                        gr.Markdown("---", elem_classes="hr-line")
                        with gr.Accordion(i18n("生图"), open=True):
                            # gr.Markdown("## 智能图片生成🏞️")
                            # 添加文本输入框用于输入生成图片的文本
                            image_output = gr.Image(label="古诗文意象图", show_label=False)
                            image_text = gr.Textbox(label="诗句", placeholder=i18n("输入'本地'可查看默认图片"))
                            generate_button = gr.Button("生成图片")
                            generate_button.click(image_generator.generate_image, inputs=image_text, outputs=image_output)
                            
                    
                    # with gr.Tab(label=i18n("参数")):
                        # gr.Markdown(i18n("# ⚠️ 务必谨慎更改 ⚠️"),
                        #             elem_id="advanced-warning")
                        # with gr.Accordion(i18n("参数"), open=True):
                        temperature_slider = gr.Slider(
                            minimum=-0,
                            maximum=2.0,
                            value=1.0,
                            step=0.1,
                            interactive=True,
                            label="temperature",
                            visible=False
                        )
                        top_p_slider = gr.Slider(
                            minimum=-0,
                            maximum=1.0,
                            value=1.0,
                            step=0.05,
                            interactive=True,
                            label="top-p",
                            visible=False
                        )
                        n_choices_slider = gr.Slider(
                            minimum=1,
                            maximum=10,
                            value=1,
                            step=1,
                            interactive=True,
                            label="n choices",
                            visible=False
                        )
                        stop_sequence_txt = gr.Textbox(
                            show_label=True,
                            placeholder=i18n("停止符，用英文逗号隔开..."),
                            label="stop",
                            value="",
                            lines=1,
                            visible=False
                        )
                        max_context_length_slider = gr.Slider(
                            minimum=1,
                            maximum=32768,
                            value=2000,
                            step=1,
                            interactive=True,
                            label="max context",
                            visible=False
                        )
                        max_generation_slider = gr.Slider(
                            minimum=1,
                            maximum=32768,
                            value=1000,
                            step=1,
                            interactive=True,
                            label="max generations",
                            visible=False
                        )
                        presence_penalty_slider = gr.Slider(
                            minimum=-2.0,
                            maximum=2.0,
                            value=0.0,
                            step=0.01,
                            interactive=True,
                            label="presence penalty",
                            visible=False
                        )
                        frequency_penalty_slider = gr.Slider(
                            minimum=-2.0,
                            maximum=2.0,
                            value=0.0,
                            step=0.01,
                            interactive=True,
                            label="frequency penalty",
                            visible=False
                        )
                        logit_bias_txt = gr.Textbox(
                            show_label=True,
                            placeholder=f"word:likelihood",
                            label="logit bias",
                            value="",
                            lines=1,
                            visible=False
                        )
                        user_identifier_txt = gr.Textbox(
                            show_label=True,
                            placeholder=i18n("用于定位滥用行为"),
                            label=i18n("用户标识符"),
                            value=user_name.value,
                            lines=1,
                            visible=False
                        )

                    with gr.Tab(label=i18n("关于")):
                        gr.Markdown("#### " + i18n("PoetryChat Github地址"))
                        gr.Markdown(DESCRIPTION)

    with gr.Row(elem_id="popup-wrapper"):
        with gr.Box(elem_id="chuanhu-popup"):
            with gr.Box(elem_id="chuanhu-setting"):
                with gr.Row():
                    gr.Markdown("## " + i18n("设置"))
                    gr.HTML(get_html("close_btn.html").format(
                        obj="box"), elem_classes="close-btn")
                with gr.Tabs(elem_id="chuanhu-setting-tabs"):
                    with gr.Tab(label=i18n("高级")):
                        gr.HTML(get_html("appearance_switcher.html").format(
                            label=i18n("切换亮暗色主题")), elem_classes="insert-block", visible=False)
                        use_streaming_checkbox = gr.Checkbox(
                            label=i18n("实时传输回答"), value=True, visible=ENABLE_STREAMING_OPTION,
                            elem_classes="switch-checkbox"
                        )
                        language_select_dropdown = gr.Dropdown(
                            label=i18n("选择回复语言（针对搜索&索引功能）"),
                            choices=REPLY_LANGUAGES,
                            multiselect=False,
                            value=REPLY_LANGUAGES[0],
                            visible=False,
                        )
                        name_chat_method = gr.Dropdown(
                            label=i18n("对话命名方式"),
                            choices=HISTORY_NAME_METHODS,
                            multiselect=False,
                            interactive=True,
                            value=HISTORY_NAME_METHODS[chat_name_method_index],
                        )
                        single_turn_checkbox = gr.Checkbox(label=i18n(
                            "单轮对话"), value=False, elem_classes="switch-checkbox", elem_id="gr-single-session-cb",
                            visible=False)
                        # checkUpdateBtn = gr.Button(i18n("🔄 检查更新..."), visible=check_update)
                        logout_btn = gr.Button(i18n("退出用户"), variant="primary", visible=authflag)

                    with gr.Tab(i18n("网络")):
                        gr.Markdown(
                            i18n("⚠️ 为保证API-Key安全，请在配置文件`config.json`中修改网络设置"),
                            elem_id="netsetting-warning")
                        default_btn = gr.Button(i18n("🔙 恢复默认网络设置"))
                        # 网络代理
                        proxyTxt = gr.Textbox(
                            show_label=True,
                            placeholder=i18n("未设置代理..."),
                            label=i18n("代理地址"),
                            value=http_proxy,
                            lines=1,
                            interactive=False,
                            # container=False,
                            elem_classes="view-only-textbox no-container",
                        )
                        # changeProxyBtn = gr.Button(i18n("🔄 设置代理地址"))

                        # 优先展示自定义的api_host
                        apihostTxt = gr.Textbox(
                            show_label=True,
                            placeholder="api.openai.com",
                            label="OpenAI API-Host",
                            value=api_host or API_HOST,
                            lines=1,
                            interactive=False,
                            # container=False,
                            elem_classes="view-only-textbox no-container",
                        )

                    with gr.Tab(label=i18n("关于"), elem_id="about-tab"):
                        gr.Markdown("# " + i18n("PoetryChat"))
                        gr.Markdown(DESCRIPTION, elem_id="description")

            with gr.Box(elem_id="web-config", visible=False):
                gr.HTML(get_html('web_config.html').format(
                    enableCheckUpdate_config=False,
                    hideHistoryWhenNotLoggedIn_config=hide_history_when_not_logged_in,
                    forView_i18n=i18n("仅供查看"),
                    deleteConfirm_i18n_pref=i18n("你真的要删除 "),
                    deleteConfirm_i18n_suff=i18n(" 吗？"),
                    usingLatest_i18n=i18n("您使用的就是最新版！"),
                    updatingMsg_i18n=i18n("正在尝试更新..."),
                    updateSuccess_i18n=i18n("更新成功，请重启本程序"),
                    updateFailure_i18n=i18n(
                        "更新失败，请尝试[手动更新](https://github.com/shibing624/chatgpt-webui/"),
                    regenerate_i18n=i18n("重新生成"),
                    deleteRound_i18n=i18n("删除这轮问答"),
                    renameChat_i18n=i18n("重命名该对话"),
                    validFileName_i18n=i18n("请输入有效的文件名，不要包含以下特殊字符："),
                    clearFileHistoryMsg_i18n=i18n("⚠️请先删除知识库中的历史文件，再尝试上传！"),
                    dropUploadMsg_i18n=i18n("释放文件以上传"),
                ))
            with gr.Box(elem_id="fake-gradio-components", visible=False):
                changeSingleSessionBtn = gr.Button(
                    visible=False, elem_classes="invisible-btn", elem_id="change-single-session-btn")
                changeOnlineSearchBtn = gr.Button(
                    visible=False, elem_classes="invisible-btn", elem_id="change-online-search-btn")
                historySelectBtn = gr.Button(
                    visible=False, elem_classes="invisible-btn", elem_id="history-select-btn")  # Not used


    def create_greeting(request: gr.Request):
        if hasattr(request, "username") and request.username:
            logger.info(f"Get User Name: {request.username}")
            user_info, user_name = gr.Markdown.update(
                value=f"User: {request.username}"), request.username
        else:
            user_info, user_name = gr.Markdown.update(
                value=f"", visible=False), ""
        current_model = get_model(
            model_name=MODELS[DEFAULT_MODEL], access_key=my_api_key, user_name=user_name)[0]
        if not hide_history_when_not_logged_in or user_name:
            loaded_stuff = current_model.auto_load()
        else:
            loaded_stuff = [gr.update(), gr.update(), gr.Chatbot.update(label=MODELS[DEFAULT_MODEL]),
                            current_model.single_turn, current_model.temperature, current_model.top_p,
                            current_model.n_choices, current_model.stop_sequence, current_model.token_upper_limit,
                            current_model.max_generation_token, current_model.presence_penalty,
                            current_model.frequency_penalty, current_model.logit_bias, current_model.user_identifier]
        return user_info, user_name, current_model, toggle_like_btn_visibility(
            DEFAULT_MODEL), *loaded_stuff, init_history_list(user_name, prepend=current_model.history_file_path[:-5])

    
    demo.load(create_greeting, inputs=None, outputs=[
        user_info, user_name, current_model, like_dislike_area, saveFileName, theme, chatbot,
        single_turn_checkbox, temperature_slider, top_p_slider, n_choices_slider, stop_sequence_txt,
        max_context_length_slider, max_generation_slider, presence_penalty_slider, frequency_penalty_slider,
        logit_bias_txt, user_identifier_txt, historySelectList], api_name="load")
    chatgpt_predict_args = dict(
        fn=predict,
        inputs=[
            current_model,
            user_question,
            chatbot,
            use_streaming_checkbox,
            use_websearch_checkbox,
            index_files,
            language_select_dropdown,
        ],
        outputs=[chatbot, status_display],
        show_progress=True,
    )

    start_outputing_args = dict(
        fn=start_outputing,
        inputs=[],
        outputs=[submitBtn, cancelBtn],
        show_progress=True,
    )

    end_outputing_args = dict(
        fn=end_outputing, inputs=[], outputs=[submitBtn, cancelBtn]
    )

    reset_textbox_args = dict(
        fn=reset_textbox, inputs=[], outputs=[user_input]
    )

    transfer_input_args = dict(
        fn=transfer_input, inputs=[user_input], outputs=[
            user_question, user_input, submitBtn, cancelBtn], show_progress=True
    )

    get_usage_args = dict(
        fn=billing_info, inputs=[current_model], outputs=[
            usageTxt], show_progress=False
    )

    load_history_from_file_args = dict(
        fn=load_chat_history,
        inputs=[current_model, historySelectList],
        outputs=[saveFileName, theme, chatbot, single_turn_checkbox, temperature_slider, top_p_slider,
                 n_choices_slider, stop_sequence_txt, max_context_length_slider, max_generation_slider,
                 presence_penalty_slider, frequency_penalty_slider, logit_bias_txt, user_identifier_txt],
    )

    refresh_history_args = dict(
        fn=get_history_list, inputs=[user_name], outputs=[historySelectList]
    )

    auto_name_chat_history_args = dict(
        fn=auto_name_chat_history,
        inputs=[current_model, name_chat_method, user_question, chatbot, single_turn_checkbox],
        outputs=[historySelectList],
        show_progress=False,
    )

    # Chatbot
    cancelBtn.click(interrupt, [current_model], [])

    user_input.submit(
        **transfer_input_args).then(
        **chatgpt_predict_args).then(
        **end_outputing_args).then(
        **auto_name_chat_history_args)
    user_input.submit(**get_usage_args)

    submitBtn.click(**transfer_input_args).then(
        **chatgpt_predict_args, api_name="predict").then(
        **end_outputing_args).then(
        **auto_name_chat_history_args)
    submitBtn.click(**get_usage_args)
    index_files.upload(handle_file_upload, [current_model, index_files, chatbot, language_select_dropdown], [
        index_files, chatbot, status_display])
    summarize_btn.click(handle_summarize_index, [
        current_model, index_files, chatbot, language_select_dropdown], [chatbot, status_display])
    emptyBtn.click(
        reset,
        inputs=[current_model, retain_system_prompt_checkbox],
        outputs=[chatbot, status_display, historySelectList, theme, single_turn_checkbox, temperature_slider,
                 top_p_slider, n_choices_slider, stop_sequence_txt, max_context_length_slider, max_generation_slider,
                 presence_penalty_slider, frequency_penalty_slider, logit_bias_txt, user_identifier_txt],
        show_progress=True,
        _js='(a,b)=>{return clearChatbot(a,b);}',
    )

    retryBtn.click(**start_outputing_args).then(
        retry,
        [
            current_model,
            chatbot,
            use_streaming_checkbox,
            use_websearch_checkbox,
            index_files,
            language_select_dropdown,
        ],
        [chatbot, status_display],
        show_progress=True,
    ).then(**end_outputing_args)
    retryBtn.click(**get_usage_args)

    delFirstBtn.click(
        delete_first_conversation,
        [current_model],
        [status_display],
    )

    delLastBtn.click(
        delete_last_conversation,
        [current_model, chatbot],
        [chatbot, status_display],
        show_progress=False
    )

    likeBtn.click(
        like,
        [current_model],
        [status_display],
        show_progress=False
    )

    dislikeBtn.click(
        dislike,
        [current_model],
        [status_display],
        show_progress=False
    )
    two_column.change(update_doc_config, [two_column], None)

    # 生图
    theme.change(update_image_text, [theme], [image_text])


    # LLM Models
    keyTxt.change(set_key, [current_model, keyTxt], [
        user_api_key, status_display], api_name="set_key").then(**get_usage_args)
    keyTxt.submit(**get_usage_args)
    single_turn_checkbox.change(
        set_single_turn, [current_model, single_turn_checkbox], None, show_progress=False)
    model_select_dropdown.change(get_model,
                                 [model_select_dropdown, lora_select_dropdown, user_api_key, temperature_slider,
                                  top_p_slider, theme, user_name, current_model], [
                                     current_model, status_display, chatbot, lora_select_dropdown, user_api_key,
                                     keyTxt], show_progress=True, api_name="get_model")
    model_select_dropdown.change(toggle_like_btn_visibility, [model_select_dropdown], [
        like_dislike_area], show_progress=False)
    lora_select_dropdown.change(get_model,
                                [model_select_dropdown, lora_select_dropdown, user_api_key, temperature_slider,
                                 top_p_slider, theme, user_name, current_model],
                                [current_model, status_display, chatbot], show_progress=True)
    # Template
    templateRefreshBtn.click(get_template_dropdown, None, [
        templateFileSelectDropdown])
    templateFileSelectDropdown.input(
        load_template,
        [templateFileSelectDropdown],
        [promptTemplates, templateSelectDropdown],
        show_progress=True,
    )
    templateSelectDropdown.change(
        get_template_content,
        [promptTemplates, templateSelectDropdown, theme], 
        [theme],  
        show_progress=True,
    )


    # # Template
    # systemPromptTxt.change(set_system_prompt, [
    #     current_model, systemPromptTxt], None)
    # templateRefreshBtn.click(get_template_dropdown, None, [
    #     templateFileSelectDropdown])
    # templateFileSelectDropdown.input(
    #     load_template,
    #     [templateFileSelectDropdown],
    #     [promptTemplates, templateSelectDropdown],
    #     show_progress=True,
    # )
    # templateSelectDropdown.change(
    #     get_template_content,
    #     [promptTemplates, templateSelectDropdown, systemPromptTxt],
    #     [systemPromptTxt],
    #     show_progress=True,
    # )


    # S&L
    renameHistoryBtn.click(
        rename_chat_history,
        [current_model, saveFileName, chatbot],
        [historySelectList],
        show_progress=True,
        _js='(a,b,c,d)=>{return saveChatHistory(a,b,c,d);}'
    )
    exportMarkdownBtn.click(
        export_markdown,
        [current_model, saveFileName, chatbot],
        [],
        show_progress=True,
    )
    historyRefreshBtn.click(**refresh_history_args)
    historyDeleteBtn.click(delete_chat_history, [current_model, historySelectList],
                           [status_display, historySelectList, chatbot],
                           _js='(a,b,c)=>{return showConfirmationDialog(a, b, c);}').then(
        reset,
        inputs=[current_model, retain_system_prompt_checkbox],
        outputs=[chatbot, status_display, historySelectList, theme],
        show_progress=True,
        _js='(a,b)=>{return clearChatbot(a,b);}',
    )
    historySelectList.input(**load_history_from_file_args)
    uploadFileBtn.upload(upload_chat_history, [current_model, uploadFileBtn], [
        saveFileName, theme, chatbot, single_turn_checkbox, temperature_slider, top_p_slider,
        n_choices_slider, stop_sequence_txt, max_context_length_slider, max_generation_slider, presence_penalty_slider,
        frequency_penalty_slider, logit_bias_txt, user_identifier_txt]).then(**refresh_history_args)
    historyDownloadBtn.click(None, [
        user_name, historySelectList], None, _js='(a,b)=>{return downloadHistory(a,b,".json");}')
    historyMarkdownDownloadBtn.click(None, [
        user_name, historySelectList], None, _js='(a,b)=>{return downloadHistory(a,b,".md");}')
    historySearchTextbox.input(
        filter_history,
        [user_name, historySearchTextbox],
        [historySelectList]
    )

    # Advanced
    temperature_slider.input(
        set_temperature, [current_model, temperature_slider], None, show_progress=False)
    top_p_slider.input(set_top_p, [current_model, top_p_slider], None, show_progress=False)
    n_choices_slider.input(
        set_n_choices, [current_model, n_choices_slider], None, show_progress=False)
    stop_sequence_txt.input(
        set_stop_sequence, [current_model, stop_sequence_txt], None, show_progress=False)
    max_context_length_slider.input(
        set_token_upper_limit, [current_model, max_context_length_slider], None, show_progress=False)
    max_generation_slider.input(
        set_max_tokens, [current_model, max_generation_slider], None, show_progress=False)
    presence_penalty_slider.input(
        set_presence_penalty, [current_model, presence_penalty_slider], None, show_progress=False)
    frequency_penalty_slider.input(
        set_frequency_penalty, [current_model, frequency_penalty_slider], None, show_progress=False)
    logit_bias_txt.input(
        set_logit_bias, [current_model, logit_bias_txt], None, show_progress=False)
    user_identifier_txt.input(set_user_identifier, [
        current_model, user_identifier_txt], None, show_progress=False)

    default_btn.click(
        reset_default, [], [apihostTxt, proxyTxt, status_display], show_progress=True
    )

    # Invisible elements
    changeSingleSessionBtn.click(
        fn=lambda value: gr.Checkbox.update(value=value),
        inputs=[single_turn_checkbox],
        outputs=[single_turn_checkbox],
        _js='(a)=>{return bgChangeSingleSession(a);}'
    )
    changeOnlineSearchBtn.click(
        fn=lambda value: gr.Checkbox.update(value=value),
        inputs=[use_websearch_checkbox],
        outputs=[use_websearch_checkbox],
        _js='(a)=>{return bgChangeOnlineSearch(a);}'
    )
    historySelectBtn.click(  # This is an experimental feature... Not actually used.
        fn=load_chat_history,
        inputs=[current_model, historySelectList],
        outputs=[saveFileName, theme, chatbot, single_turn_checkbox, temperature_slider, top_p_slider,
                 n_choices_slider, stop_sequence_txt, max_context_length_slider, max_generation_slider,
                 presence_penalty_slider, frequency_penalty_slider, logit_bias_txt, user_identifier_txt],
        _js='(a,b)=>{return bgSelectHistory(a,b);}'
    )
    logout_btn.click(
        fn=None,
        inputs=[],
        outputs=[],
        _js='self.location="/logout"'
    )

demo.title = TITLE

if __name__ == "__main__":
    reload_javascript()
    setup_wizard()
    demo.queue(concurrency_count=CONCURRENT_COUNT).launch(
        allowed_paths=[HISTORY_DIR, assets_path],
        server_name=server_name,
        server_port=server_port,
        share=share,
        blocked_paths=[config_file],
        auth=auth_from_conf if authflag else None,
        favicon_path=favicon_path,
        inbrowser=autobrowser and not dockerflag,
    )
