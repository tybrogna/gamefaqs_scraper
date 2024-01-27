from threading import Event

from bs4 import BeautifulSoup
import requests

import scraper_io as io
import constants
import progress_data_structures as ds

COUNT_LOC = 'get_console_links_count'
test = True
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


def get_name_from_link(confirmed_link):
    start_idx = len(constants.URL_gamefaqs) + 1
    end_idx = confirmed_link.index(constants.URL_list)
    return confirmed_link[start_idx:end_idx]

def get_num_pages(soup):
    all_txt = soup.select_one('.paginate li').text
    final_pg = all_txt[all_txt.rindex(' '):].strip()


def run(GUI):
    GUI.display('Scanning all consoles on gamefaqs...')
    soup_consoles = constants.heat_soup(constants.URL_gamefaqs + constants.URL_consoles)
    potential_console_names = get_console_locations_list(soup_consoles)
    GUI.display(f'FOUND: {len(potential_console_names)} potential consoles')
    potential_console_links = [console_location_to_link(val) for val in potential_console_names]
    if io.pkl_exists(COUNT_LOC):
        count_save_data = io.unpickle_dict(COUNT_LOC)
    else:
        count_save_data = {'all_potential_consoles': len(potential_console_links),
                           'consoles_checked': 0}
        io.pkl_append(COUNT_LOC, count_save_data)
    # for console_link in potential_console_links:
    print(count_save_data)
    count_start = count_save_data['consoles_checked']
    count_total = count_save_data['all_potential_consoles']
    print(count_start)
    print(count_total)
    for console_at in range(count_start, count_total):
        console_link = potential_console_links[console_at]
        if kill_event.is_set():
            return
        console_soup = constants.heat_soup(console_link)
        game_list = console_soup.find_all('td', class_='rtitle')
        if len(game_list) == 0:
            count_save_data['consoles_checked'] = count_save_data['consoles_checked'] + 1
            io.pkl_save_new(COUNT_LOC, count_save_data)
            continue
        # link is confirmed from here on
        name = get_name_from_link(console_link)
        # console_link_save_data = ds.SaveData(file_loc=constants.CONSOLE_LINK_LIST_LOC,
        #                                      blob=ds.LinkStep(name, link=console_link, completion=False),
        #                                      file_type='pickle')
        console_link_save_data = ds.SaveData(file_loc=constants.CONSOLE_LINK_LIST_LOC,
                                             blob=ds.FileStep(name, link=console_link, completion=False),
                                             file_type='pickle')
        paginate_text = console_soup.select_one('.paginate li').text
        final_pg = paginate_text[paginate_text.rindex(' '):].strip()
        page_length_save_data = ds.SaveData(file_loc=constants.CONSOLE_PAGE_LENGTHS,
                                            blob=ds.NamedNumber(name, data=final_pg),
                                            file_type='pickle')
        constants.force_save_pack(console_link_save_data, page_length_save_data)
        count_save_data['consoles_checked'] = count_save_data['consoles_checked'] + 1
        io.pkl_save_new(COUNT_LOC, count_save_data)
    io.pkl_delete(COUNT_LOC)



def verify_complete() -> bool:
    if not io.pkl_exists(constants.CONSOLE_LINK_LIST_LOC):
        print('no CONSOLE_LINK_LIST_LOC file')
        return False
    if io.pkl_exists(COUNT_LOC):
        print('COUNT_LOC exists, still counting')
        return False
    return True


def check_full_progress() -> list[str]:
    """

    """
    if io.pkl_exists(constants.CONSOLE_LINK_LIST_LOC) and not io.pkl_exists(COUNT_LOC):
        links = io.unpickle(constants.CONSOLE_LINK_LIST_LOC)
        return [f'  COMPLETE  ',
                f'All Steps Complete, {len(links)} consoles saved']
    if not io.pkl_exists(COUNT_LOC):
        return ['Page at save file not created yet']
    count_save_data = io.unpickle_dict(COUNT_LOC)
    print(count_save_data)
    count_checked = count_save_data['consoles_checked']
    count_total = count_save_data['all_potential_consoles']
    saved_links = io.unpickle(constants.CONSOLE_LINK_LIST_LOC)
    last_link = None
    if len(saved_links) > 0:
        last_link = saved_links[-1].name
    return [f'  On step {count_checked} of {count_total}',
            f'  Last saved console link: {last_link}']
