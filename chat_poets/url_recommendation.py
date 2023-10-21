from typing import Optional, List, Any
from bs4 import BeautifulSoup as BS
import requests
import re

url = "https://so.gushiwen.cn"


def search_poems(poem: str, num_poems: int) -> Optional[List[str]]:
    """
    实时Web检索古诗，并返回前num_poems首古诗的URL
    :param poem: 诗句
    :param num_poems: 要返回的古诗数量
    :return: 包含前num_poems首古诗URL的列表
    """
    url_search = url + "/search.aspx?value=" + poem + "&valuej=" + poem[0]
    req_search = requests.get(url=url_search)
    req_search.encoding = "utf-8"
    html = req_search.text
    soup_search = BS(html, features="html.parser")

    # 找到多个古诗链接
    poem_links = soup_search.find_all("div", {"class": "sons"})[:num_poems]
    poem_urls = [url + link.find('a').attrs['href'] for link in poem_links]

    return poem_urls


if __name__ == '__main__':
    search_term = "苏轼"
    num_poems_to_return = 3
    poem_urls = search_poems(search_term, num_poems_to_return)
    print(poem_urls)

    # if poem_urls:
    #     print(f"为您推荐更多和'{search_term}'相关的有趣资料:")
    #     for idx, url in enumerate(poem_urls):
    #         print(f"参考资料 {idx + 1}: {url}")
    # else:
    #     print(f"没有找到任何相关的参考资料嘤嘤嘤 '{search_term}'.")
