from bs4 import BeautifulSoup
import requests

import pkl_io as io
import constants
import progress_data_structures as ds

test = True


def heat_soup(url):
    """
    makes a web request of the paramter url, then creates a soup object

    :param url: string url of webpage
    :return: BeautifulSoup html object
    """
    req = requests.get(url, headers=constants.HEADERS)
    print(str(req.status_code) + " from " + url)
    return BeautifulSoup(req.text, "html.parser")


def get_console_locations_list(soup_consoles):
    """
    Returns the location of links outgoing from the console list page
    A location is the url keyword of the console. ex: "3ds", "ps2"

    :param soup_consoles: soup html object representing https://gamefaqs.gamespot.com/games/systems 
    :return: string list of locations
    """
    locations = []
    for html_link in soup_consoles.find_all('a'):
        link = html_link.get('href')
        if link is None:
            continue
        if len(link) < 1:
            continue
        add = True
        add &= link[0] == '/'
        for ch in link[1:]:
            add &= ch != '/'
        add &= link not in locations
        if add:
            locations.append(link)
        if test and len(locations) >= 10:
            break
    return locations


def verify_games_on_page(console_link):
    console_soup = heat_soup(console_link)
    gamelist = console_soup.find_all('td', class_='rtitle')
    if len(gamelist) == 0:
        return False
    else:
        return True


def console_location_to_link(location):
    return constants.URL_gamefaqs + location + constants.URL_list


def get_game_links(soup_page):
    game_list = soup_page.find_all('td', class_='rtitle')
    for table_row in game_list:
        url_game = list(table_row.children)[0].get('href')
        print(url_game)


def get_locations_from_confirmed_link(confirmed_link):
    start_idx = len(constants.URL_gamefaqs) + 1
    end_idx = confirmed_link.index(constants.URL_list)
    return confirmed_link[start_idx:end_idx]


def run():
    print("  Scanning all consoles on gamefaqs...")
    soup_consoles = heat_soup(constants.URL_gamefaqs + constants.URL_consoles)
    console_page_all_locations = get_console_locations_list(soup_consoles)

    if test:
        print("  locations found")
        for val in console_page_all_locations:
            print("    " + val)

    console_page_all_links = map(console_location_to_link, console_page_all_locations)
    console_links = list(filter(verify_games_on_page, console_page_all_links))

    if test:
        print("  confirmed links created")
        for val in console_links:
            print("    " + val)

    link_steps = []
    for confirmed_link in console_links:
        name = get_locations_from_confirmed_link(confirmed_link)
        link_steps.append(ds.Link_Step(name, confirmed_link, False))

    if test:
        for ls in link_steps:
            print(ls)

    io.append_all_to_pkl(constants.CONSOLE_LINK_LIST_LOC, link_steps)
    # fake_list = [("link1", False),("link2", False),("link3", False),("link4", False),("link5", False)]
    # io.append_all_to_pkl(step, fake_list)
    print("  Console Links Saved!!")
    return True
