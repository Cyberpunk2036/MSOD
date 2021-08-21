import requests
from lxml import html
from pprint import pprint
from pymongo import MongoClient

# =============================================================================
# Решение ДЗ для news.mail.ru || Начало переноса в БД
# =============================================================================

url = 'https://news.mail.ru/'

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}

response = requests.get(url, headers=header)

dom = html.fromstring(response.text)

# Вычленяем все новости в головном блоке
super_news = dom.xpath("//div[@class='js-module']/*")

# Список наших будущих новостей
news_list = list()

# Сначала обходим новости с иконками
for i in super_news[0].xpath("//table[@class='daynews__inner']//tr/*")[:-1]:
    new = dict()
    a = i.xpath(".//a[contains(@class,'topnews__item')]/@href")
    # Если новость относится к первому подклассу(самая большая иконка)
    if len(a) < 1:
        new['link'] = a
        news_list.append(new)
    # Для остальных новостей, которые входят в другой подкласс новостей
    else:
        for j in a:
            # Поочередно добавляем каждую
            new = dict()
            new['link'] = j
            news_list.append(new)

# Проходим новости оформленные в качестве списка и тоже их добавляем
for i in super_news[1].xpath("//ul[contains(@class, 'js-module')]/li[@class='list__item']/*"):
    new = dict()
    a = i.xpath("./@href")[0]
    new['link'] = a
    news_list.append(new)

# Функция для обхода содержимого новостей и извлечения информации со страниц 
def news_parser(i):
    response = requests.get(news_list[i]['link'], headers=header)
    dom = html.fromstring(response.text)
    news_list[i]['name'] = dom.xpath("//h1[@class='hdr__inner']/text()")[0] 
    news_list[i]['source'] = dom.xpath("//a[contains(@class, 'breadcrumbs__link')]/span/text()")[0]
    news_list[i]['ago'] = dom.xpath("//span[contains(@class, 'js-ago')]/@datetime")[0].replace('T', ' ')
    
for i in range(len(news_list)):
    news_parser(i)
        
# Загружаем данные в Mongo
client = MongoClient('127.0.0.1', 27017)
db = client['News']

news_db = db.news_db

news_db.insert_many(news_list)