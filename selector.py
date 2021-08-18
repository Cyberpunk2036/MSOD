import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
# import pandas as pd
import json

def input_vacancies():
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
    
    #Осуществляем переход по страницам с помощью кнопки "далее"
    while True:    
        link = soup.find('a', {'data-qa':'pager-next'}) #Формируем ссылочку
        if link is None:
            break
        link = link['href']
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
    
    return vacancies










