import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}

CONSOLE_LINK_LIST_LOC = 'console_link_list'
GAME_LINK_LIST_LOC = 'console_link_list'

URL_gamefaqs = "https://gamefaqs.gamespot.com"
URL_consoles = "/games/systems"
URL_list = "/category/999-all"
URL_page = "?page="
URL_faqs = "/faqs"


def heat_soup(url):
    """
    makes a web request of the paramter url, then creates a soup object

    :param url: string url of webpage
    :return: BeautifulSoup html object
    """
    req = requests.get(url, headers=HEADERS)
    print(str(req.status_code) + " from " + url)
    return BeautifulSoup(req.text, "html.parser")
