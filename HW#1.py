import requests

# =============================================================================
# Первое задание
# =============================================================================

url = 'https://api.github.com/users/'

user = 'Cyberpunk2036'
type_repo = ''

url = url + user + '/repos'

params = {'type':type_repo}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'}


response = requests.get(url, params=params, headers=headers)

j_data = response.json()

repos = list()

for i in j_data:
    repos.append(i['name'])

print(f"У пользователя {j_data[0]['owner']['login']} имеются следующие репозитории: {', '.join(repos)}")

with open('data.json', 'w') as jfile:
    jfile.writelines(str(j_data))

# =============================================================================
# Второе задание. Скрапим stepik-api, ключами будут id пользователя и id сертификата
# =============================================================================

user_id = '24773766'
certificate_id = '353601'

url = 'https://stepic.org:443/api'

url_u = url + '/users/' + user_id
url_c = url + '/certificates/' + certificate_id

resp_u = requests.get(url_u, headers=headers)
resp_c = requests.get(url_c, headers=headers)

j_data_u = resp_u.json()
j_data_c = resp_c.json()


with open('UserData.json', 'w') as udata:
    udata.write(str(j_data_u))
    
with open ('CertificateData.json', 'w') as jdata:
    jdata.write(str(j_data_c))

print(50*'-')
print(f"Пользователь: {j_data_u['users'][0]['full_name']}")
print(f"Владеет сертификатом: {j_data_c['certificates'][0]['course_title']}")
