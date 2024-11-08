import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_links(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    for a in soup.find_all('a', class_='letter'):
        yield a.text, urljoin(url, a['href'])

def scrape_words(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    for word in soup.find_all(class_='word'):
        yield word.text

for url in sorted(set(url for text, url in scrape_links('https://www.scrabblehelper.nl/woordenlijst'))):
    for word in scrape_words(url):
        print(word)
