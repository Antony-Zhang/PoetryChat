"""
生成回答
"""


def gen_response(pattern: str, history: list[list]) -> str:
    """
    根据对话历史，产生回答。
    pattern = "adult" | "teen" | "child"，模式
    注：对话历史的最后一项是需要填充的内容，即history[-1] = [Question, None]；Question为用户刚提出的问题，None即尚未回答
    """
    return "哇哇哇!"
