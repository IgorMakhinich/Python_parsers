import requests
from bs4 import BeautifulSoup
import csv

URL = 'https://avtozvuk.ua/motornye-masla/c355/5000=50001'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0', 'accept': '*/*'}
HOST = 'https://avtozvuk.ua/'
FILE_NAME = 'goods'
FILE = 'avtozvuk_' + FILE_NAME + '.csv'

def get_html(url, page=1):
    url = url + '/page' + str(page)
    r = requests.get(url, headers=HEADERS)
    return r

def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find('div', class_='pagination__el_next').find_previous('div').get_text()
    if pagination:
        return int(pagination)
    else:
        return 1

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='product-view__inner')
    goods = []
    for item in items:
        goods.append({
            'title': item.find('a', class_='product-view-title__link').get_text(strip=True),
            'link': HOST + item.find('a', class_='product-view-title__link').get('href'),
            'price': item.find('div', class_='product-view-prices__base-price-number').get_text(),
            'status': item.find('p', class_='product-view-description__status').get_text()
        })
        print(goods)
    return (goods)

def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Название', 'Ссылка', 'Цена', 'Статус'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['price'], item['status']])

def parse(URL, FILE_NAME):
    URL = input('Введите URL: ')
    URL = URL.strip()
    FILE_NAME = input('Что ,загружаем: ')
    FILE_NAME = FILE_NAME.strip()
    FILE = 'avtozvuk_' + FILE_NAME + '.csv'
    html = get_html(URL)
    if html.status_code == 200:
        goods = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Парсинг страницы {page} из {pages_count}...')
            html = get_html(URL,page)
            goods.extend(get_content(html.text))
        save_file(goods, FILE)
        print(f'Получено {len(goods)} товаров')
    else:
        print('Error')

parse(URL, FILE_NAME)