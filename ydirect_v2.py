import requests
from bs4 import BeautifulSoup as BS
from user_agent import generate_user_agent
import csv
from time import sleep

# URL = 'http://direct.yandex.ru/search?&lr=213&text={0}&p={1}'
URL = 'http://direct.yandex.ru/search/ads'
FIELDS = ('firm', 'phone', 'email', 'title', 'text', 'domain')
WORDS = [
    'застройщики москвы и московской области',
    'новостройки с отделкой в подмосковье от застройщика'
]


def get_html(url, query, num):
    headers = {
        'User-agent': generate_user_agent(os=['linux', 'mac', 'win'],
                                          navigator=['chrome', 'firefox'])
    }
    params = {
        'lr': '213', 'text': query, 'p': num
    }
    r = requests.get(url, headers=headers, params=params)
    return r.text


def get_amount_pages(query, num):
    """получает общее количество страниц с результатами поиска"""
    sleep(3)
    html = get_html(URL, query, num)
    soup = BS(html, 'html.parser')

    # ссылки на другие страницы результата поиска
    a_pages = soup.find('div', class_='pager').find_all(class_='pager__item')
    if a_pages[-1].text == 'дальше':
        num = int(a_pages[-2].text) - 1
        return get_amount_pages(query, num)
    else:
        return a_pages[-1].text


def main():
    # html = get_html(URL, WORDS[1], 7)
    # with open('saved.html', 'w') as f:
        # f.write(html)
    n = get_amount_pages(WORDS[1], 0)
    print('количество страниц ', n)


if __name__ == '__main__':
    main()
