import requests, re
from lxml import etree
import csv
import threading
from queue import Queue

gLock = threading.Lock()


class BBSpider(threading.Thread):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
    }

    def __init__(self, page_queue, joke_queue, *args, **kwargs):
        super(BBSpider, self).__init__(*args, **kwargs)
        self.base_domain = "http://www.budejie.com"
        self.page_queue = page_queue
        self.joke_queue = joke_queue

    def run(self):
        while True:
            if self.page_queue.empty():
                break
            page_url = self.page_queue.get()
            self.page_parse(page_url)

    def page_parse(self, url):
        response = requests.get(url, headers=self.headers)
        html = etree.HTML(response.content.decode("UTF-8"))
        divs = html.xpath("//div[@class='j-r-list-c-desc']")
        for div in divs:
            # 提取文章url
            link = div.xpath("./a/@href")[0]
            link = self.base_domain + link

            # 提取内容
            descs = div.xpath("./a/text()")
            # 因为descs是列表，所以要合并为一个字符串
            # 以\n连接，并去掉前后空格
            joke = "\n".join(descs).strip()
            # 放到队列中
            self.joke_queue.put((joke, link))
            # print(joke,link)


class BSWriter(threading.Thread):

    def __init__(self, joke_queue, writer, *args, **kwargs):
        super(BSWriter, self).__init__(*args, **kwargs)
        self.joke_queue = joke_queue
        self.writer = writer

    def run(self):
        while True:
            try:
                joke_info = self.joke_queue.get(timeout=40)
                joke, link = joke_info
                gLock.acquire()
                self.writer.writerow((joke, link))
                gLock.release()
            except:
                break


def main():
    page_queue = Queue(10)
    joke_queue = Queue(500)


    # 写入标题行
    f = open("./budejie.csv", "a", encoding="utf-8", newline="")
    writer = csv.writer(f)
    writer.writerow(("content", "link"))

    base_url = "http://www.budejie.com/text/{}"
    for x in range(1, 11):
        page_url = base_url.format(x)
        page_queue.put(page_url)

    for x in range(3):
        t = BBSpider(page_queue, joke_queue)
        t.start()
    for x in range(5):
        # 没想到writer也能这样子传进去
        t = BSWriter(joke_queue, writer)
        t.start()


if __name__ == '__main__':
    main()
