from threading import Event

from bs4 import BeautifulSoup
from bs4 import Tag
import scraper_io as io
import constants
import progress_data_structures as ds


test = False
kill_event = Event()


def kill():
    kill_event.set()


def enliven():
    kill_event.clear()


def create_file_steps(console_links_file: str) -> list[ds.FileStep]:
    """
    The results of get_console_links.py becomes the steps toward completion for get_game_links.py.
    For each console found in the parameter, a step will be created in the returned list

    :param console_links_file: file path to a pickle file containing results of get_console_links.py
    :return: list of consoles to scan for games
    """
    steps = []
    console_link_steps = io.unpickle(console_links_file)
    for console in console_link_steps:
        if test:
            print("get_game_links.py - adding {0} to steps".format(console.name))
        # steps.append(ds.File_Step(console.name, console.link, "{0}_game_list".format(console.name), console.completion))
        steps.append(ds.FileStep(name=console.name,
                                 link=console.link,
                                 save_loc="{0}_game_list".format(console.name),
                                 completion=console.completion))
    return steps


def create_console_progress_files(step_name: str, console_save_loc: str):
    """
    Generates a pickle file that keeps track of the number of pages the scraper has scanned so far.
    On a console's "all games" page, only 100 games are displayed. If the app is closed or stopped,
    this file will tell it which page of games to start at after reload

    :param step_name: console name (ps2, gamecube, amiga)
    :param console_save_loc: pickle file location
    """
    page_search_save_file = step_name + "_page_at"
    if not io.pkl_exists(page_search_save_file):
        io.pkl_append(page_search_save_file, '0')

    first_game_save = console_save_loc
    if not io.pkl_exists(first_game_save):
        # print("  No Game Link Progress file found, creating Game Link Progress file")
        io.pkl_create_file(first_game_save)


def create_page_url(console_name: str, pg_at: str) -> str:
    """
    Creates an url of a console's all games page, at the specified page
    https://gamefaqs.gamespot.com  /  console_name  ?page=  pg_at

    :param console_name: console name (ps2, gamecube, amiga)
    :param pg_at: page number
    :return: valid url for link checking
    """
    ret_url = constants.URL_gamefaqs + '/' + console_name + constants.URL_list
    if pg_at == 0:
        return ret_url
    else:
        return ret_url + constants.URL_page + pg_at


def page_contains_games(page_soup: BeautifulSoup) -> bool:
    """
    Checks <tbody> on the paramaterized web page for content.

    :param page_soup: BS4 object, web page with <tbody>
    :return: True if <tbody> exists and has content, False otherwise
    """
    return len(page_soup.select_one("tbody").contents) != 0


def get_all_game_id_and_name(page_soup: BeautifulSoup) -> list[Tag]:
    """
    On the page of the parameterized soup, return a list of that have a "guide" link next to the table

    :param page_soup: BS4 object, web page with <tbody> with content in it
    :return: list of BS4 Tags that are links to guides of games
    """
    guide_links = page_soup.select("tr td.rmain:nth-of-type(-n+2) a")
    if len(guide_links) < 0:
        return
    return guide_links


def run(GUI):
    GUI.display('Getting all game links...')
    steps = create_file_steps(constants.CONSOLE_LINK_LIST_LOC)
    for console_step in steps:
        if console_step.completion:
            GUI.display(f'  {console_step.name} is done')
            continue
        GUI.display(f'Starting {console_step.name}')
        create_console_progress_files(console_step.name, console_step.save_loc)
        page_file_loc = console_step.name + '_page_at'
        GUI.display(f'Found Link Save File at {console_step.save_loc}')
        while True:
            if kill_event.is_set():
                return
            page_at = io.unpickle(page_file_loc)[0]
            url_pg = create_page_url(console_step.name, page_at)
            GUI.display(f'Scraping page {page_at} of {url_pg}')
            if test:
                if int(page_at) > 1:
                    finished_step = ds.FileStep(name=console_step.name,
                                                link=console_step.link,
                                                save_loc=console_step.save_loc,
                                                completion=True)
                    io.pkl_overwrite(constants.CONSOLE_LINK_LIST_LOC, console_step, finished_step)
                    io.pkl_test_print(constants.CONSOLE_LINK_LIST_LOC)
            html_soup = constants.heat_soup(url_pg)
            if not page_contains_games(html_soup):
                io.pkl_delete(page_file_loc)
                # finished_step = ds.File_Step(console_step.name, console_step.link, console_step.save_loc, True)
                save_data = ds.SaveData(file_loc=constants.CONSOLE_LINK_LIST_LOC,
                                        blob=console_step.save_new_completion(),
                                        old_blob_for_overwrite=console_step,
                                        file_type='pickle')
                # save_data = ds.SaveData(constants.CONSOLE_LINK_LIST_LOC)
                # save_data.blob = console_step.save_new_completion()
                # save_data.old_blob_for_overwrite = console_step
                # save_data.file_type = 'pickle'
                constants.force_save_pack(save_data)
                # io.pkl_overwrite(constants.CONSOLE_LINK_LIST_LOC, console_step, finished_step)
                break
            guide_links = get_all_game_id_and_name(html_soup)
            guide_link_steps = []
            for link in guide_links:
                guide_remove_console = link['href'][len(console_step.name) + 2:-4]
                guide_name = guide_remove_console[:guide_remove_console.index('-')]
                guide_link_steps.append(ds.LinkStep(name=guide_name, link=guide_remove_console, completion=False))
                if test:
                    print(guide_link_steps[-1])
            save_data = ds.SaveData(file_loc=console_step.save_loc,
                                    blob=guide_link_steps,
                                    file_type='pickle')
            # save_data = ds.SaveData(console_step.save_loc)
            # save_data.blob = guide_link_steps
            # save_data.file_type = 'pickle'
            save_page = ds.SaveData(file_loc=page_file_loc,
                                    blob=int(page_at) + 1,
                                    old_blob_for_overwrite=page_at,
                                    file_type='pickle')
            # save_page = ds.SaveData(page_file_loc)
            # save_page.blob = int(page_at) + 1
            # save_data.old_blob_for_overwrite = page_at
            # save_data.file_type = 'pickle'
            GUI.display(f'  Saving {len(guide_link_steps)} game links...')
            constants.force_save_pack(save_data, save_page)


def verify_complete() -> bool:
    """
    Style: Checks if all the steps in CONSOLE_LINK_LIST_LOC.pickle are marked as complete
    """
    steps = create_file_steps(constants.CONSOLE_LINK_LIST_LOC)
    for step in steps:
        if not step.completion:
            print(f'{step.name} never finished')
            return False
    return True


def print_progress():
    if not io.pkl_exists(constants.CONSOLE_LINK_LIST_LOC):
        print('no CONSOLE_LINK_LIST_LOC file')
        return False
    steps = io.unpickle(constants.CONSOLE_LINK_LIST_LOC)
    num_steps = len(steps)
    cur_step = 0
    for idx, step in enumerate(steps):
        if not step.completion:
            cur_step = idx
            break
    print(f'  On step {cur_step} ({steps[cur_step].name}) of {num_steps}')


def check_full_progress() -> list[str]:
    if not io.exists(constants.CONSOLE_LINK_LIST_LOC):
        return ['CONSOLE_LINK_LIST_LOC doesn\'t exist']
    steps = io.unpickle(constants.CONSOLE_LINK_LIST_LOC)
    num_steps = len(steps)
    cur_step = 0
    for idx, step in enumerate(steps):
        if not step.completion:
            cur_step = idx
            break
    return [f'On step {cur_step} ({steps[cur_step].name}) of {num_steps}']
