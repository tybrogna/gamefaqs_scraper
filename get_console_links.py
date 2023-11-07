import re
from bs4 import BeautifulSoup
import requests
import pickle
import os

import pkl_io as io

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}

url_gamefaqs = "https://gamefaqs.gamespot.com"
url_consoles = "/games/systems"
url_list = "/category/999-all"
url_page = "?page="
url_faqs = "/faqs"

# creates a soup object of the url in parameter
def heat_soup(url):
    req = requests.get(url, headers=headers)
    print(str(req.status_code) + " from " + url)
    return BeautifulSoup(req.text, "html.parser")

def get_console_locations_list(soup_consoles):
    links = []
    for html_link in soup_consoles.find_all('a'):
        link = html_link.get('href')
        if link is None: continue
        if len(link) < 1: continue
        add = True
        add &= link[0] == '/'
        for ch in link[1:]:
            add &= ch != '/'
        add &= link not in links
        if add: links.append(link)
    return links

def verify_games_on_page(console_link):
    console_soup = heat_soup(console_link)
    gamelist = console_soup.find_all('td', class_='rtitle')
    if len(gamelist) == 0:
        return False
    else:
        return True

def console_location_to_link(location):
    return url_gamefaqs + location + url_list

def get_game_links(soup_page):
    game_list = soup_page.find_all('td', class_='rtitle')
    for table_row in game_list:
        url_game = list(table_row.children)[0].get('href')
        print(url_game)

def check_completion(save_location):
    if not os.path.exists(save_location) or os.stat(save_location).st_size == 0:
        with open(save_location, 'wb') as pickout:
            completion_tuple = ("completed", False)
            pickle.dump(completion_tuple, pickout, pickle.HIGHEST_PROTOCOL)
        return False

    with open(save_location, 'rb') as pickin:
        pkl_obj = pickle.load(pickin)
        if (pkl_obj[0] == 'completed'):
            return pkl_obj[1]

def run(save_location):
    print("  scanning all consoles on gamefaqs")

    soup_consoles = heat_soup(url_gamefaqs + url_consoles)
    console_page_all_locations = get_console_locations_list(soup_consoles)
    console_page_all_links = map(console_location_to_link, console_page_all_locations)
    console_links = list(filter(verify_games_on_page, console_page_all_links))
    to_save = len(console_link)
    saved = 0
    with open(save_location, 'wb') as pickout:
        for console_link in console_links:
            link_tuple = (console_link, False)
            print("saving link {0}".format(console_link))
            pickle.dump(link_tuple, pickout, pickle.HIGHEST_PROTOCOL)
            saved = saved + 1

    return saved == to_save
