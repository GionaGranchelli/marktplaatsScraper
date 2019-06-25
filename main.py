import csv

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from translate import Translator

from item import Item


def translate(textoToTranslate):
    translator = Translator(from_lang="dutch", to_lang="english")
    translation = translator.translate(textoToTranslate)
    return translation


def writetocsv(items):
    csv_file = open(SCRAPE_CSV, 'w')
    cvs_writer = csv.writer(csv_file)
    cvs_writer.writerow(['Title', 'Price', 'Photo', 'Summary'])
    for item in items:
        cvs_writer.writerow([item.title, item.price, 'No Photo', item.summary])
    csv_file.close()


def convert_csv_to_xsl():
    wb = Workbook()
    ws = wb.active
    with open(SCRAPE_CSV, 'r') as f:
        for row in csv.reader(f):
            ws.append(row)
    wb.save('name.xlsx')


def is_correct_response(response):
    """Check that the response returned 'success'"""
    return response == 'success'


def is_defined_item(element):
    if element is not None:
        return element
    else:
        return "not Available"


if __name__ == "__main__":
    SCRAPE_CSV = 'scrape.csv'
    sortBy = 'price'
    priceFrom = '100%2C00'
    priceTo = '400%2C00'
    query = 'playstation+4+pro'
    postalcode = '1051cn'
    distance = '15000'
    sortMethod = 'increasing'
    botToken = ''
    chatID = ''
    url = 'https://www.marktplaats.nl/z.html?sortBy=' + sortBy
    url += '&priceFrom=' + priceFrom
    url += '&sortOrder=' + sortMethod
    url += '&priceTo=' + priceTo
    url += '&query=' + query
    url += '&categoryId=0'
    url += '&postcode=' + postalcode
    url += '&distance=' + distance
    print(url)
    source = requests.get(url)
    print(source)
    marktplaats = BeautifulSoup(source.text, 'lxml')
    body = marktplaats.find('body')
    search_result = is_defined_item(body.find('div', id='search-results'))
    listOfArticles = []
    try:
        section = is_defined_item(search_result.find('section', class_='table'))
        articles = section.find_all('article')
        for article in articles:
            try:
                listing = is_defined_item(article.find('div', class_='listing'))
                title_ = listing.div.div.h2.a.span.text
                href = listing.div.div.h2.a['href']
                summary_ = is_defined_item(listing.find('span', class_='mp-listing-description')).text
                price = is_defined_item(listing.find('div', class_='column-price')).div.span.span.text
                myObj = Item()
                myObj.title = title_.strip()
                myObj.url = href.strip()
                myObj.price = price.strip()
                myObj.summary = summary_.strip()
                listOfArticles.append(myObj)
            except Exception as e:
                summary_ = "None"
                title_ = "None"
                href = "None"
                price = "None"
                print(e)
    except Exception as e:
        print(e)
    for x in listOfArticles:
        print(x.title)
        print(x.summary)
        print(x.price)
        url = 'https://api.telegram.org/bot' + botToken + '/sendMessage?chat_id=' + chatID + '&text='
        text = 'Title:' + translate(x.title) + '\n'
        # text += '<p>Summary: ' + x.summary + '</p>\n'
        # text += '<a href="' + x.url + '"/>'
        text += x.url
        # text += '<bold>Price: ' + x.price + '</bold>\n' + '&parse_mode=HTML'
        url += text
        print(url)
        requests.get(url)
    writetocsv(listOfArticles)
    convert_csv_to_xsl()
