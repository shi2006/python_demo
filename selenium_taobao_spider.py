import time
import re
from selenium import webdriver
import csv

PAGES = 0


def search_product(driver, kw):
    # 查找找网页中的搜索框，然后用send_keys()发送数据
    driver.find_element_by_xpath("//input[@id='q']").send_keys(kw)

    # 点击搜索
    driver.find_element_by_xpath('//*[@id="J_TSearchForm"]/div[1]/button').click()
    # 暂停10秒，用来手机淘宝扫码登录
    time.sleep(10)
    token = driver.find_element_by_xpath('//*[@id="mainsrp-pager"]/div/div/div/div[1]').text
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


def get_product(driver, writer):
    # 获取所有商品信息，先获取到包含所有商品信息的div
    divs = driver.find_elements_by_xpath("//div[@class='items']/div[@class='item J_MouserOnverReq  ']")
    for div in divs:
        # text是获取到字符
        title = div.find_element_by_xpath(".//div[@class='row row-2 title']").text
        deal = div.find_element_by_xpath(".//div[@class='deal-cnt']").text
        # get_attribute 是获取到属性的值
        image = "http:" + div.find_element_by_xpath(".//div[@class='pic']/a/img").get_attribute("data-src")
        price = div.find_element_by_xpath(".//div[@class='price g_price g_price-highlight']/strong").text
        shop = div.find_element_by_xpath(".//div[@class='shop']/a/span[2]").text
        position = div.find_element_by_xpath(".//div[@class='location']").text
        writer.writerow((title, deal, price, shop, position, image))
    global PAGES
    PAGES += 1
    print("======已获取并保存第%s页商品信息======" % PAGES)


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
    writer.writerow(("标题", "成交量", "价格", "店铺", "城市", "图片地址"))

    get_product(driver, writer)
    num = 1
    while num != token:
        driver.get("https://s.taobao.com/search?q={}&s={}".format(kw, 44 * num))
        # 智能等待，最高等待时间为10S，如果超过10S，抛出异常
        driver.implicitly_wait(10)
        num += 1
        drop_down(driver)
        get_product(driver, writer)


if __name__ == '__main__':
    main()
