import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
#from test.config import *
import pymongo
MONGO_URL='localhost'
MONGO_DB='taobao'
MONGO_TABLE='product'

SERVICE_ARGS=['--disk-cache=[true]','--load-images=[false]']

client=pymongo.MongoClient(MONGO_URL)
db=client[MONGO_DB]

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
browser = webdriver.Chrome(chrome_options=options,executable_path="C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")
wait=WebDriverWait(browser,10)

def search():
      try:
            browser.get('https://www.taobao.com')
            input=wait.until(
                  EC.presence_of_element_located((By.CSS_SELECTOR,"#q")))
            input.send_keys('女童棉衣')
            submit=wait.until(
                  EC.element_to_be_clickable((By.CSS_SELECTOR,"#J_TSearchForm > div.search-button > button")))
            submit.click()
            total=wait.until(
                  EC.presence_of_element_located((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > div.total")))
            get_products()
            return total.text
      except TimeoutException:
            return search()

#定义自动翻页功能函数
def next_page(page_number):
      try:
            input=wait.until(
                  EC.presence_of_element_located((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > div.form > input")))
            submit=wait.until(
                  EC.element_to_be_clickable((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit")))
            input.clear()
            input.send_keys(page_number)
            submit.click()
            wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > ul > li.item.active > span'),str(page_number)))
            get_products()
      except TimeoutException:
            next_page(page_number)


#定义解析商品及店铺信息的函数           
def get_products():
      wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#mainsrp-itemlist .items .item")))
      html=browser.page_source
      print(html)
      doc=pq(html)
      items=doc("#mainsrp-itemlist .items .item").items()
      for item in items:
            product={
                  'image':item.find('.pic .img').attr('src'),
                  'price':item.find('.price').text(),
                  'deal':item.find('.deal-cnt').text()[:-3],
                  'title':item.find('.title').text(),
                  'shop':item.find('.shop').text(),
                  'location':item.find('.location').text()
            }
            print(product)
            save_to_mongo(product)


def save_to_mongo(result):
      try:
            if db[MONGO_TABLE].insert(result):
                  print('保存至mondb成功',result)
      except Exception:
            print('保存至mondb失败',result)

                  
def main():
      total=search()
      total=int(re.compile('(\d+)').search(total).group(1))
      for i in range(2,total+1):
            next_page(i)
      browser.close()

if __name__=='__main__':
      main()
            
            
      
