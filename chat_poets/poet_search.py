from typing import Optional, Any
from bs4 import BeautifulSoup as BS
import requests
import re  # 正则表达式

url = "https://so.gushiwen.cn"


def search_poem(poem: str) -> Optional[dict[Any, Any]]:
    """
    实时Web检索古诗(选取检索出来的第一首)
    :param poem: 诗句
    :return: 古诗信息的字典["title", "author", "contents", "trans"]
    """
    # 进入搜索界面
    url_search = url + "/search.aspx?value=" + poem + "&valuej=" + poem[0]
    req_search = requests.get(url=url_search)
    req_search.encoding = "utf-8"
    html = req_search.text  # 返回的html内容
    soup_search = BS(html, features="html.parser")  # 返回解析对象

    # 定位第一首古诗，并跳转至详情页
    new_url = soup_search.find("div", {"class": "sons"}).find('a').attrs['href']  # 获取古诗跳转链接
    url_poetry = url + new_url
    req_poetry = requests.get(url=url_poetry)
    req_poetry.encoding = "utf-8"
    soup_poetry = BS(req_poetry.text, features="html.parser")

    # 提取数据
    title = soup_poetry.find('h1').text.strip()
    if len(title) == 0:
        print("未找到古诗")
        return None

    author = soup_poetry.find("p", class_="source").text.strip()  # 作者
    contents = soup_poetry.find("div", class_="contson").text.strip()  # 原文

    try:
        exp_html_href = soup_poetry.find("div", id=re.compile(r'fanyi+\d'))\
            .find('a', style=re.compile(r'^text-decoration:none')).get("href")
        # 针对“点击展开”组件
        if exp_html_href:  # 存在则获取对应资源href,拼接成url
            exp_html_href_id = re.match(r"javascript:.*?,'(.*?)'.*?", str(exp_html_href)).group(1)
            exp_html_href_url = 'https://so.gushiwen.cn/nocdn/ajaxfanyi.aspx?id=' + exp_html_href_id
            exp_html = requests.get(url=exp_html_href_url)
            exp_html.encoding = "utf-8"
            exp_poetry = BS(exp_html.text, features="html.parser")
            # 提取元素数据
            trans_notes = exp_poetry.find("div", class_="contyishang").find_all('p')
            trans = trans_notes[0].text.strip().lstrip("译文")
            notes = trans_notes[1].text.strip().lstrip("注释").rstrip("▲")
        else:
            trans_notes = soup_poetry.find("div", id=re.compile(r'fanyi+\d')).find_all('p')
            trans = trans_notes[0].text.strip().lstrip("译文")
            notes = trans_notes[1].text.strip().lstrip("注释")
    except:
        trans = ""
        notes = ""

    # 结果转化为dict
    keys = ["title", "author", "contents", "trans", "notes"]
    values = [title, author, contents, trans, notes]
    poetry_dict = dict(zip(keys, values))

    return poetry_dict


if __name__ == '__main__':
    poetry_dict = search_poem("我曾凌风登此楼，但见苍茫汉阳树。")
    # 打印
    for key, value in poetry_dict.items():
        print(key + ": " + value)
