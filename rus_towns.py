import requests
from bs4 import BeautifulSoup

r = requests.get('https://ru.wikipedia.org/wiki/Список_городов_России')
soup = BeautifulSoup(r.text, 'lxml')
with open('file.html', 'w', encoding='UTF-8') as file:
    file.write(r.text)
items = soup.find('table', class_='standard sortable').find('tbody').find_all('tr')[2:]
for item in items:
    with open('towns.txt', 'a', encoding='UTF-8') as file:
        file.write(item.find_all('a')[1].text + '\n')
