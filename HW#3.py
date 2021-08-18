# import requests
# from bs4 import BeautifulSoup as bs
from pprint import pprint
# import pandas as pd
import json
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup as bs
from selector import input_vacancies

# =============================================================================
# Задание №1.
# =============================================================================

client = MongoClient('127.0.0.1', 27017)
db = client['Vacancies']

vacancies = db.vacancies

vacancies.drop({})
# Выгружаем данные из файла json
with open('Vacancies.json') as jfile:
    data = json.load(jfile)

# Заносим данные в базу данных
vacancies.insert(data)
    
# Выводим содержимое б.д.
for item in vacancies.find({}, {'_id': 0}):
    print(item)

# =============================================================================
# Задание №2.
# =============================================================================

def finder(number):
    # Список держащий нужные вакансии
    lst = list()
    # Проходим по каждой непустой по зарплате вакансии
    for i in vacancies.find({'salary': {'$ne': None}}):
        # Проверяем условия
        if (i['salary']['min'] is not None and i['salary']['min'] > number) or (i['salary']['max'] is not None and i['salary']['max'] > number):
            lst.append(i)
    return lst

num = int(input('На какую зарплату позаритесь: '))
print(finder(num))

# =============================================================================
# Задание №3. || В selector изменить поиск вакансий только по data science!
# =============================================================================

# Заново парсим страницы с запросом вакансии, чтобы найти новые
update_vacancies = input_vacancies()

# Подгружаем все данные из базы данных в список для простоты обработки
temp = list()
for i in vacancies.find({}, {'_id':0}):
    temp.append(i)
    
# Создаем однозначно идентифицирующие вакансию поля
features = [[i['name'], i['city'], i['Employer']] for i in temp]    # Список всех старых вакансий по ключевым полям

# Создаем и обновляем спискок всех новых вакансий
new_vacancies = list()
for i in update_vacancies:
    check = list() # Список проверки на вхождение в базу данных
    for j in features:
        if j != [i['name'], i['city'], i['Employer']]:  # Проверка совпадения по ключевым полям
            check.append(0)
        else:
            check.append(1)
    if 1 not in check:  # Если вакансия ни разу не попалась в базе прошлого обновления вакансий
        new_vacancies.append(i)     # Мы добавляем ее в списочек

# Обновляем базу данных
for i in new_vacancies:
    vacancies.insert_one(i)

# Перенос обновленной базы в json
lst = list()

for i in vacancies.find({}, {'_id':0}):
    lst.append(i)
    
with open('Vacancies.json', 'w') as jfile:
    json.dump(lst, jfile)































