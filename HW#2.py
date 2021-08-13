import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import pandas as pd


# =============================================================================
# Вариант №1: hh.ru
# =============================================================================
print(120*'-')
print('Вариант №1. hh.ru')
print(120*'-')

url = 'https://hh.ru'
# clusters=true&ored_clusters=true&enable_snippets=true&st=searchVacancy&text=data+scientist&area=0
params = {'ored_clusters':'true', 'clusters':'true', 'enable_snippets':'true', 'salary':'', 'st':'searchVacancy',
          'text':'data scientist', 'area':'0'}
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}


response = requests.get(url+'/search/vacancy', params=params, headers=headers)

# with open('MyOwnPage.html', 'w', encoding='utf-8') as f:
#     f.write(response.text)

soup = bs(response.text, 'html.parser')

vacancies = list()  #Список словарей вакансий с описаниями

vacancies_list = soup.find_all('div', {'class':'vacancy-serp-item'})

page = 0
print(f'Текущая страница: {page}') 

while len(vacancies_list) < 40:    #Осуществляем переход по страницам с помощью кнопки "далее"
    link = soup.find('a', {'data-qa':'pager-next'})['href'] #Формируем ссылочку
    response = requests.get(url+link, params=params, headers=headers)   #Осуществляем запрос
    soup = bs(response.text, 'html.parser')
    new_list = soup.find_all('div', {'class':'vacancy-serp-item'})
    vacancies_list += new_list  
    page += 1
    print(f'Текущая страница: {page}') 
    
for vac in vacancies_list:
    vacancy = dict()
    
    vac_name = vac.find('a', {'class':'bloko-link'}).string     #Выделяем наименование вакансии
    vacancy['name'] = vac_name
    
    vac_url = vac.find('a', {'class':'bloko-link'})['href']     #Выделяем ссылку на вакансию
    vacancy['url'] = vac_url
    
    vacancy['website'] = url    #Внедряем сслыку на сайт, с которого собирали данные (p.s.: не знаю, зачем это)
    
    vac_city = vac.find('span', {'data-qa':'vacancy-serp__vacancy-address'}).getText().split(',')[0]    #Выделяем город работы
    vacancy['city'] = vac_city
    
    vac_org = vac.find('a', {'data-qa':'vacancy-serp__vacancy-employer'}).getText()     #Выделям работодателя
    vacancy['Employer'] = vac_org
    
    if vac.find('span', {'data-qa':'vacancy-serp__vacancy-compensation'}) is not None:  #Выделяем зарплату
        salary = vac.find('span', {'data-qa':'vacancy-serp__vacancy-compensation'}).string.split()
        
        if len(salary) == 6:
            minm = int(salary[0]+salary[1])
            maxm = int(salary[3]+salary[4])
            currancy = salary[-1][:-1]
            vacancy['salary'] = {'min':minm, 'max':maxm, 'currancy':currancy}
        elif len(salary) == 4:
            if salary[0] == 'от':
                minm = int(salary[1]+salary[2])
                maxm = None
                currancy = salary[-1][:-1]
                vacancy['salary'] = {'min':minm, 'max':maxm, 'currancy':currancy}
            elif salary[0] == 'до':
                maxm = int(salary[1]+salary[2])
                minm = None
                currancy = salary[-1][:-1]
                vacancy['salary'] = {'min':minm, 'max':maxm, 'currancy':currancy}
    else:
        vacancy['salary'] = None
    vacancies.append(vacancy)

pprint(vacancies)

# =============================================================================
# Вариант №2: Горячие напитки 
# =============================================================================

print(120*'-')
print('Вариант №2. Горячие напитки')
print(120*'-')

url = 'https://roscontrol.com'
drinks_url = url + '/category/produkti/goryachie-napitki/'

# url_list = list()   #Список ссылок подкаталогов текущего верхнего каталога


headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}

response = requests.get(drinks_url, headers=headers)

soup = bs(response.text, 'html.parser')

goods_list = list()

urls = soup.find_all('div', {'class':'grid-padding grid-column-3 grid-column-large-6 grid-flex-mobile grid-column-middle-6 grid-column-small-12 grid-left'})

for i in urls:
    # Для каждого типа товаров
    print(urls.index(i))
    next_page = url+i.find('a')['href']     # Точка входа - первая страница подкаталога
    # Проход по страницам для подкаталогов
    while True:
        # Проход по странице
        response = requests.get(next_page, headers=headers)
        soup = bs(response.text, 'html.parser')
        goods = soup.find_all('div', {'class':'wrap-product-catalog__item grid-padding grid-column-4 grid-column-large-6 grid-column-middle-12 grid-column-small-12 grid-left js-product__item'})  #Список объектов из товаров текущей страницы
        next_good = goods[0]    # Обрабатываем текущий товар
        while next_good:
            good = dict()   #Словарь, хранящий информацию о товаре
            # Наименование товара
            good_name = next_good.find('div', {'class':'util-table-cell product__item-title'}).findChildren(recursive=False)[0].getText()
            good['name'] = good_name
            # Параметры
            good_params = dict()
            # Решил по дереву поскакать,изменяется эта часть: [0].getText(), которая и дает название параметра и его чиселко
            if len(next_good.find_all("div", {"class":"rating-block"})) == 0:
                good_params['All'] = None
            else:
                good_params_list = [i.getText().split("\n")[1] for i in next_good.find_all("div", {"class":"rating-block"})[0].findChildren("div", {"class":"left"})]
                if len(good_params_list) == 0:
                    good_params['All'] =  next_good.find_all("div", {"class":"product-rating util-table-cell js-has_vivid_rows"})[0].findChildren(recursive=0)[1].getText()
                else:
                    good_params[good_params_list[0]] = next_good.find_all("div", {"class":"rating-block"})[0].findChildren("div", {"class":"left"})[0].nextSibling.nextSibling.getText()
                    good_params[good_params_list[1]] = next_good.find_all("div", {"class":"rating-block"})[0].findChildren("div", {"class":"left"})[1].nextSibling.nextSibling.getText()
                    good_params[good_params_list[2]] = next_good.find_all("div", {"class":"rating-block"})[0].findChildren("div", {"class":"left"})[2].nextSibling.nextSibling.getText()
            good['params'] = good_params
            # Общая оценка
            if len(next_good.find('div', {'class':'product-rating util-table-cell js-has_vivid_rows'}).findChildren(recursive=False)) == 0:
                good_mark = None
            else:
                good_mark = next_good.find('div', {'class':'product-rating util-table-cell js-has_vivid_rows'}).findChildren(recursive=False)[0].getText()
            good['mark'] = good_mark
            #Внедряем сслыку на сайт, с которого собирали данные (p.s.: не знаю, зачем это)
            good['website'] = next_page
            
            goods_list.append(good)
            next_good = next_good.nextSibling.nextSibling
        # Проверка на окончание товаров подкаталога
        if soup.find('a', {'class':'page-num page-item last AJAX_toggle'}) is None:
            break
        else:
            next_page = url + soup.find('a', {'class':'page-num page-item last AJAX_toggle'})['href']
            print(next_page)
    
pprint(goods_list)













