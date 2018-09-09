#!/usr/bin/env python3
import csv
from time import sleep
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup as BS
from user_agent import generate_user_agent

# URL = 'http://direct.yandex.ru/search/ads?&text={0}&lr=213&p={1}'
# основной адрес запроса
URL = 'http://direct.yandex.ru/search/ads'


FIELDS = ('firm', 'phone', 'email', 'title', 'text', 'domain')
# firm - название фирмы - берется со страницы с контактной информацией
# phone - контактный номер - берется со страницы с контактами
# email - электронная почта - берется со страницы с контактами
# title - заголовок объявления - берется со страницы выдачи поиска
# text - текст, находящийся в объявлении
# domain - URL организации - берется со страницы выдачи поиска

WORDS = [
    'застройщики москвы и московской области',
    'новостройки с отделкой в подмосковье от застройщика',
    'колодцы в подмосковье'
]


def get_html(url, query=None, num=None):
    headers = {
        'User-agent': generate_user_agent(os=['linux', 'mac', 'win'],
                                          navigator=['chrome', 'firefox'])
    }
    if query is None and num is None:
        params = None
    else:
        params = {
            'text': query, 'lr': '213', 'p': num
        }
    r = requests.get(url, headers=headers, params=params)
    return r.text


def get_amount_pages(query, num=0):
    """получает общее количество страниц с результатами поиска

    Бывает, что последняя страница ничего не содержит, поэтому
    возбуждается исключение при попытке получить текст из ссылки.
    В этом случае в конечный результат передается номер предпоследней
    страницы.
    """
    sleep(3)
    html = get_html(URL, query, num)
    soup = BS(html, 'html.parser')

    # ссылки на другие страницы результата поиска
    a_pages = soup.find('div', class_='pager').find_all(class_='pager__item')
    try:
        if a_pages[-1].text == 'дальше':
            num = int(a_pages[-2].text) - 1
            return get_amount_pages(query, num)
        else:
            return a_pages[-1].text
    except IndexError:
        print('По последней ссылке на странице ничего не найдено.\n'
              'Передана предпоследняя ссылка.')
        return num


def main():
    uniq_phones = []
    with open('firms.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(
            csvfile, FIELDS, dialect='unix', delimiter=';'
        )
        writer.writeheader()

        for query in WORDS:
            pages = int(get_amount_pages(query))
            for page in tqdm(range(pages)):
                html = get_html(URL, query, page)
                soup = BS(html, 'html.parser')
                ads = soup.find_all('li', class_='serp-item')

                for item in ads:
                    try:
                        title = item.h2.text.strip()
                    except AttributeError:
                        title = ''
                    try:
                        domain = 'https://' + item.h2.next_sibling.b.text.strip()
                    except AttributeError:
                        domain = ''
                    try:
                        text = item.find('div', class_='text-container').\
                            text.replace('\n', ' ').strip()
                    except AttributeError:
                        text = ''
                    try:
                        vcard_url = item.select('span.serp-meta__items a')[0]['href']
                        vcard = get_html(vcard_url)
                        soup = BS(vcard, 'html.parser')
                        firm = soup.h1.text
                        phone = soup.select('div.contact-item.call-button-container div.large-text')[0].text
                        email = soup.find('a', class_='email').text
                    except Exception:
                        firm = ''
                        phone = ''
                        email = ''

                    # if phone in uniq_phones:
                    #     pass
                    # else:
                    uniq_phones.append(phone)
                    writer.writerow(
                        {'firm': firm, 'phone': phone, 'email': email,
                            'title': title, 'text': text, 'domain': domain}
                    )


if __name__ == '__main__':
    main()
