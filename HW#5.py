from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait   
from selenium.webdriver.support import expected_conditions as EC  
from selenium.webdriver.common.by import By

import json

import datetime

now = datetime.datetime.now()

from pymongo import MongoClient

import time

# =============================================================================
# Решение задания с mail.ru
# =============================================================================

with open('МСОД/Less#5/Xmail.txt', 'r') as logpass:
    xlogin = logpass.readline().replace('\n', '')
    xpasswd = logpass.readline()
    
chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(executable_path='МСОД/Less#5/chromedriver.exe', options=chrome_options)

driver.get('https://mail.ru/')

login = driver.find_element_by_name('login')
login.send_keys(xlogin)

login.send_keys(Keys.ENTER)

time.sleep(1)

passwd = driver.find_element_by_name('password')
passwd.send_keys(xpasswd)

time.sleep(1)

passwd.send_keys(Keys.ENTER)

# Смотрим, сколько писем у нас всего
wait = WebDriverWait(driver, 9999999)
button_wait = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@title='Выделить все']")))
button_wait.click()
count = int(driver.find_element_by_xpath("//td[contains(@class, 'layout__sidebar ')]/span[position()=1]//span[@class='button2__txt']").text)

# Пошли по циклу, в котором соберем все ссылки на письма
mails = set()
while len(mails) < count:
    # Собираем все ссылки на письма, которые можем
    for i in driver.find_elements_by_xpath("//a[contains(@class, 'js-letter')]"):
        mails.add(i.get_attribute('href'))
    # Крутим в конец списка писем
    actions = ActionChains(driver)  
    actions.move_to_element(i)   
    actions.perform()   
    time.sleep(1)  
mails = list(mails)

# Список всех новостей
mails_list = list()

# Добавляем новость как словарь в список
for i in mails:
    new = dict()
    driver.get(i) 
    time.sleep(5)
    new['title'] = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.TAG_NAME, 'h2'))).text
    new['time'] = driver.find_element_by_class_name("letter__date").text
    if 'Вчера' in new['time']:
        new['time'] = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y.%m.%d %H:%M")
    new['from'] = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, "//div[@class='letter__author']/span"))).get_attribute('title')
    # new['from'] = driver.find_element_by_xpath("//div[@class='letter__author']/span").get_attribute('title')
    new['text'] = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'js-readmsg-msg')]//div[@class]/*"))).text
    # new['text'] = driver.find_element_by_xpath("//div[contains(@class, 'js-readmsg-msg')]//div[@class]/*").text
    mails_list.append(new)

driver.close()
  
# Заполнение базы данных 
client = MongoClient('127.0.0.1', 27017)
db = client['Mails']
mail_news = db.mail_news

mail_news.drop({})

mail_news.insert_many(mails_list)

# Сохранение данных в json
# with open('Mails.json', 'w') as jfile:
#     json.dump([i for i in mail_news.find({}, {'_id':0})], jfile)


