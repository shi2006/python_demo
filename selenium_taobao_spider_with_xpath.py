import time
import re
from selenium import webdriver
import csv
from lxml import etree


def search_product(driver, kw):
    # 查找找网页中的搜索框，然后用send_keys()发送数据
    driver.find_element_by_xpath("//input[@id='q']").send_keys(kw)

    # 点击搜索
    driver.find_element_by_xpath('//*[@id="J_TSearchForm"]/div[1]/button').click()
    # 暂停10秒，用来手机淘宝扫码登录
    time.sleep(10)
    html = etree.HTML(driver.page_source)
    token = html.xpath('//*[@id="mainsrp-pager"]/div/div/div/div[1]/text()')[0]
    token = int(re.compile("(\d+)").search(token).group(1))
    return token  # 总页数


# 登录， 拉动下滑条 采集数据 下一页 再拉动下滑条 再采集数据
def drop_down(driver):
    # 一次拉一部分， 拉的时候要有暂停
    for x in range(1, 11, 2):  # 13579
        time.sleep(0.5)
        # j代表我们的滑动条位置
        j = x / 10
        # 这是js的语法，没学过，只能记忆
        js = "document.documentElement.scrollTop = document.documentElement.scrollHeight * %f" % j
        # 应用js语法
        driver.execute_script(js)


def get_product(html, writer):
    # 获取所有商品信息，先获取到包含所有商品信息的div
    divs = html.xpath("//div[@class='items']/div[@class='item J_MouserOnverReq  ']")
    for div in divs:
        titles = div.xpath(".//div[@class='row row-2 title']//text()")
        title = "".join(titles).strip()
        # 有时候商品是没有成交量的，所以要判断一下
        have_deal = div.xpath(".//div[@class='deal-cnt']//text()")
        if have_deal:
            deal = have_deal[0]
        else:
            deal = ""
        image = "http:" + div.xpath(".//div[@class='pic']/a/img/@data-src")[0]
        goods_url = "http:" + div.xpath(".//div[@class='pic']/a/@data-href")[0]
        price = div.xpath(".//div[@class='price g_price g_price-highlight']/strong//text()")[0]
        shop = div.xpath(".//div[@class='shop']/a/span[2]//text()")[0]
        position = div.xpath(".//div[@class='location']//text()")[0]
        writer.writerow((title, deal, price, shop, position, goods_url, image))
        # print(title, deal, price, shop, position, goods_url, image)


def main():
    kw = input("请输入你要查询的商品:")
    # 驱动的位置
    driver_path = r"E:\chromedriver.exe"
    # 打开selenium
    driver = webdriver.Chrome(executable_path=driver_path)
    # get(url) 打开网站
    driver.get("http://www.taobao.com")

    token = search_product(driver, kw)
    drop_down(driver)

    f = open("./taobao.csv", "a", newline="", encoding="utf-8-sig")
    writer = csv.writer(f)
    writer.writerow(("标题", "成交量", "价格", "店铺", "城市", "商品链接", "图片地址"))
    html = etree.HTML(driver.page_source)
    get_product(html, writer)
    print("======已获取并保存第1页商品信息======")
    num = 1
    while num != token:
        driver.get("https://s.taobao.com/search?q={}&s={}".format(kw, 44 * num))
        # 智能等待，最高等待时间为10S，如果超过10S，抛出异常
        driver.implicitly_wait(10)
        num += 1
        drop_down(driver)
        html = etree.HTML(driver.page_source)
        get_product(html, writer)
        print("======已获取并保存第%s页商品信息======" % num)


if __name__ == '__main__':
    main()
