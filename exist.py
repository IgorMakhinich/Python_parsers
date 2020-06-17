import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import csv

# Enter url and file name here
URL = 'https://exist.ua/akkumuljatornye-batarei/trademark=eurostart/'
FILE_NAME = 'Eurostart'

URL = URL.strip() + '?page={}'
HOST = 'https://exist.ua//'
GOODS = []
FILE = 'exist' + FILE_NAME + '.csv'

async def main():
    browser = await launch()
    page = await browser.newPage()
    # Поиск количества страниц в пагинации
    pages_count = await get_pages_count(browser,page)
    await browser.close()
    # Получение данных со всех страниц
    for page in range(1, pages_count + 1):
        print(f'Обработка страницы {page} из {pages_count}...')
        await parse_item(URL.format(page))
        print(f'Получено {len(GOODS)} товаров')
    # Сохранение данных в файл
    save_file(GOODS, FILE)

async def get_pages_count(browser, page):
    await page.goto(URL.format(1))
    await page.waitForSelector('footer.container-fluid')
    pages_count = await page.querySelectorAllEval('div.pager', '(elements => elements.map(e => e.outerHTML))')
    if len(pages_count) > 1:
        count = BeautifulSoup(pages_count[1], 'html.parser').findAll('li')
        return int(len(count)-1)
    else:
        return 1

async def parse_item(url):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url, timeout=1000000)
    await page.waitForSelector('.catalogue-list', timeout=1000000)
    offers = await page.querySelectorEval('.catalogue-list', '(element) => element.outerHTML')
    soup = BeautifulSoup(offers, 'html.parser')
    items = soup.find_all('div', class_='info-block')
    for item in items:
        try:
            price = int(item.find('div', class_='price').get_text().replace(' грн', ''))
        except:
            price = False
        if price:
            GOODS.append({
                'title': str(item.find('div', class_='title-wrapper').find_next('strong').get_text()),
                'code': str(item.find('div', class_='trademark').get_text()),
                'price': int(item.find('div', class_='price').get_text().replace(' грн', ''))
            })

def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Название', 'Код', 'Цена'])
        for item in items:
            writer.writerow([item['title'], item['code'], item['price']])

df = asyncio.get_event_loop().run_until_complete(main())
