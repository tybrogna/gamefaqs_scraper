from threading import Event

from bs4 import BeautifulSoup
import requests

import scraper_io as io
import constants
import progress_data_structures as ds

COUNT_LOC = 'get_console_links_count'
test = False
kill_event = Event()


def kill():
    kill_event.set()


def enliven():
    kill_event.clear()


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


def verify_games_on_page(console_link: str):
    """
    If the parameterized URL leads to a page where there are links to games, return True

    :param console_link: string url of the page to open
    :return: true if the page opened has games, false otherwise
    """
    if kill_event.is_set():
        return
    console_soup = constants.heat_soup(console_link)
    game_list = console_soup.find_all('td', class_='rtitle')
    if len(game_list) == 0:
        return False
    else:
        return True


def console_location_to_link(location: str) -> str:
    """
    Wraps parameterized string in the necessary urls to get a gamefaqs console page\n
    https://gamefaqs.gamespot.com  :location:  /category/999-all

    :param location: console name (ps1, gamecube, amiga)
    :return: an url that leads to the full list of games for the console
    """
    return constants.URL_gamefaqs + location + constants.URL_list


def get_locations_from_confirmed_link(confirmed_link):
    start_idx = len(constants.URL_gamefaqs) + 1
    end_idx = confirmed_link.index(constants.URL_list)
    return confirmed_link[start_idx:end_idx]


def run(GUI):
    GUI.display('Scanning all consoles on gamefaqs...')
    soup_consoles = constants.heat_soup(constants.URL_gamefaqs + constants.URL_consoles)
    console_page_all_locations = get_console_locations_list(soup_consoles)
    GUI.display('FOUND:')
    for val in console_page_all_locations:
        GUI.display('    ' + val)
    console_page_all_links = map(console_location_to_link, console_page_all_locations)
    console_links = list(filter(verify_games_on_page, console_page_all_links))
    if kill_event.is_set():
        print('get console links dying')
        return False
    GUI.display('confirmed links created')
    for val in console_links:
        GUI.display('    ' + val)
    io.pkl_append(COUNT_LOC, str(len(console_links)))
    for confirmed_link in console_links:
        name = get_locations_from_confirmed_link(confirmed_link)
        link_step = ds.LinkStep(name, link=confirmed_link, completion=False)
        io.pkl_append(constants.CONSOLE_LINK_LIST_LOC, link_step)
        io.pkl_append(constants.CONSOLE_LINK_FOR_GUIDES, link_step)
        io.pkl_append(constants.CONSOLE_DL_LIST_LOC, link_step)
    GUI.display('Console Links Saved!!')
    if test:
        io.pkl_test_print(constants.CONSOLE_LINK_LIST_LOC)
    return True


def verify_complete() -> bool:
    """
    Style: Ensures the number of consoles found before scraping matches the number of consoles found in
    CONSOLE_LINK_LIST_LOC.pickle
    """
    if not io.pkl_exists(constants.CONSOLE_LINK_LIST_LOC):
        print('no CONSOLE_LINK_LIST_LOC file')
        return False
    if not io.pkl_exists(COUNT_LOC):
        print('no COUNT_LOC file')
        return False
    io.pkl_test_print(COUNT_LOC)
    num_links = len(io.unpickle(constants.CONSOLE_LINK_LIST_LOC))
    expected_number = int(io.unpickle(COUNT_LOC)[0])
    if num_links == expected_number:
        return True
    print(f'Saved consoles don\'t match: found {num_links}, expected {expected_number}')
    return False


def check_full_progress() -> list[str]:
    """

    """
    if not io.pkl_exists(constants.CONSOLE_LINK_LIST_LOC) or not io.pkl_exists(COUNT_LOC):
        return ['Console Link Save File not created yet']
    links = io.unpickle(constants.CONSOLE_LINK_LIST_LOC)
    num_links = len(links)
    expected_number = int(io.unpickle(COUNT_LOC)[0])
    return [f'  On step {num_links} of {expected_number}',
            f'  Last saved console link: {links[num_links - 1]}']
