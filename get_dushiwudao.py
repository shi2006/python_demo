# *-* coding=utf-8 *-*

import requests, os, re, time
from lxml import etree


def request_url(url, path):
    """下载并保存网页"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    with open(path, "w", encoding="utf-8") as f:
        f.write(response.content.decode("utf-8"))


def get_article(page_path, dir):
    """对 page 页处理
    从里面的获取文章链接及标题
    然后通过 request_url() 下载保存"""

    # 用 XPath 来提取 page 页中的文章链接及标题
    parser = etree.HTMLParser(encoding="utf-8")
    html = etree.parse(page_path, parser=parser)

    # 获取 page 页里面的文章网页链接
    links = html.xpath("//h2/a/@href")

    # 获取 page 页里面的文章标题
    titles = html.xpath("//h2/a/text()")

    # 下载每一篇文章网页并以标题命名保存

    # 获取 dushiwudao 里面的文件名，用来判断已经下载过的文章就不用再下载了
    article_name_lists = os.listdir(dir)

    i = 0
    # 下载并保存
    for link in links:
        # 处理 titles, 嗯，为什么要处理呢？因为原标题里面有英文字符的冒号，Windows里面不能用来命名
        # 所以要换成中文的冒号, 这里用正则表达式来替换
        titles[i] = re.sub(r":", "：", titles[i])

        article_name = titles[i] + ".html"
        # 判断文章是否已经下载，没有才会下载
        if article_name not in article_name_lists:
            request_url(link, dir + article_name)
        i += 1
        time.sleep(1)


def main():
    # 创建dushiwudao目录
    dir = "./dushiwudao/"
    if not os.path.exists(dir):
        os.makedirs(dir)

    # 获取每一 page 网页并下载保存
    # 至2019-09-09日，只有6页

    for i in range(1, 7):
        # 分页 page 的 url
        page_url = "http://www.dushiwudao.com/page/" + str(i)

        # page 的保存路径
        page_path = dir + "page" + str(i) + ".html"

        # 下载并保存 page 页，在爬的时候，暂时没有出现异常，因此暂时没有处理异常的步骤
        request_url(page_url, page_path)
        time.sleep(1)

        # 下载完成 page 页后，对 page 页处理
        # 从里面的获取文章链接及标题
        get_article(page_path, dir)


if __name__ == '__main__':
    main()
