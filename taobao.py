from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pyquery import PyQuery as pq
from pymongo import MongoClient
import time

KEYWORD = 'ipad'
MAX_PAGE = 100
client = MongoClient()
collection = client['goods'][KEYWORD]

browser = webdriver.Chrome()
wait = WebDriverWait(browser,10)

# 翻页
def index_page(page):
    print('正在爬第{}页'.format(page))
    try:
        url = 'https://s.taobao.com/search?q=' + KEYWORD
        browser.get(url)
        #等待进行登录
        time.sleep(10)
        if page > 1:
            #页码输入框存在
            input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.J_Input')))
            #页码确定按钮可以点击
            button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.J_Submit')))
            input.clear()
            input.send_keys(page)
            button.click()
            #当前高亮页码等于当前页码，表示翻页成功
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager li.item.active > span'),str(page)))
            #判断商品列表加载完毕
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'.m-itemlist .items .item'))
        )
        get_products()
        #判断超时重新爬取
    except TimeoutException:
        index_page(page)

def get_products():
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {}
        product['image'] = item.find('.pic .img').attr('data-src')
        product['price'] = item.find('.price').text()
        product['deal'] = item.find('.deal-cnt').text()
        product['title'] = item.find('.title').text()
        product['shop'] = item.find('.shop').text()
        product['location'] = item.find('.location').text()
        print(product)
        save_to_mongo(product)

def save_to_mongo(product):
    try:
        if collection.insert(product):
            print('保存到MongoDB成功')
    except Exception:
        print('保存失败')

def main():
    for i in range(1,MAX_PAGE+1):
        index_page(i)

if __name__ == '__main__':
    main()
