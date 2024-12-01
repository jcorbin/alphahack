import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections.abc import Generator
from typing import cast

def scrape_links(url: str):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    for a in soup.find_all('a', class_='letter'):
        link_text = cast(str, a.text)
        link_href = cast(str, a['href'])
        link_url = urljoin(url, link_href)
        yield link_text, link_url

def scrape_words(url: str) -> Generator[str]:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    for word in soup.find_all(class_='word'):
        yield cast(str, word.text)

def main():
    for url in sorted(set(url for _text, url in scrape_links('https://www.scrabblehelper.nl/woordenlijst'))):
        for word in scrape_words(url):
            print(word)

if __name__ == '__main__':
    main()
