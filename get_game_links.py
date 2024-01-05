from bs4 import BeautifulSoup
import requests
import os
import time

import scraper_io as io
import constants
import progress_data_structures as ds


test = False


def create_file_steps(console_links_file):
    steps = []
    console_link_steps = io.unpickle(console_links_file)
    for console in console_link_steps:
        if test:
            print("get_game_links.py - adding {0} to steps".format(console.name))
        steps.append(ds.File_Step(console.name, console.link, "{0}_game_list".format(console.name), console.completion))
    return steps


def create_console_progress_files(step_name, console_save_loc):
    page_search_save_file = step_name + "_page_at"
    if not io.pkl_exists(page_search_save_file):
        io.pkl_append(page_search_save_file, '0')

    first_game_save = console_save_loc
    if not io.pkl_exists(first_game_save):
        print("  No Game Link Progress file found, creating Game Link Progress file")
        io.pkl_create_file(first_game_save)


def create_page_url(console_name, pg_at):
    ret_url = constants.URL_gamefaqs + '/' + console_name + constants.URL_list
    if pg_at == 0:
        return ret_url
    else:
        return ret_url + constants.URL_page + pg_at


def page_contains_games(page_soup):
    return len(page_soup.select_one("tbody").contents) != 0


def get_all_game_id_and_name(page_soup):
    guide_links = page_soup.select("tr td.rmain:nth-of-type(-n+2) a")
    if len(guide_links) < 0:
        return
    return guide_links


def run():
    print("  Getting all game links...")
    steps = create_file_steps(constants.CONSOLE_LINK_LIST_LOC)
    for console_step in steps:
        if console_step.completion:
            print("  {0} is done".format(console_step.name))
            continue

        if test:
            print("get_game_links - perfoming {0} step".format(console_step.name))
        create_console_progress_files(console_step.name, console_step.save_loc)
        page_file_loc = console_step.name + '_page_at'
        if test:
            print("get_game_links - found link save file {0}".format(console_step.save_loc))
        while True:
            page_at = io.unpickle(page_file_loc)[0]
            url_pg = create_page_url(console_step.name, page_at)
            if test:
                print("get_game_links - resuming on page {0}, at {1}".format(page_at, url_pg))
                if int(page_at) > 1:
                    finished_step = ds.File_Step(console_step.name, console_step.link, console_step.save_loc, True)
                    io.pkl_overwrite(constants.CONSOLE_LINK_LIST_LOC, console_step, finished_step)
                    io.pkl_test_print(constants.CONSOLE_LINK_LIST_LOC)

            html_soup = constants.heat_soup(url_pg)
            if not page_contains_games(html_soup):
                io.pkl_delete(page_file_loc)
                finished_step = ds.File_Step(console_step.name, console_step.link, console_step.save_loc, True)
                # this needs to be forced
                io.pkl_overwrite(constants.CONSOLE_LINK_LIST_LOC, console_step, finished_step)
                # nothing found in the table body, break
                break

            guide_links = get_all_game_id_and_name(html_soup)
            guide_link_steps = []
            for link in guide_links:
                guide_remove_console = link['href'][len(console_step.name) + 2:-4]
                guide_name = guide_remove_console[:guide_remove_console.index('-')]
                guide_link_steps.append(ds.Link_Step(guide_name, guide_remove_console, False))
                if test:
                    print(guide_link_steps[-1])
            save_data = [console_step.save_loc, guide_link_steps]
            save_page = [page_file_loc, page_at, int(page_at) + 1]
            print("  Saving {0} game links...".format(len(guide_link_steps)))
            constants.force_save(save_data, save_page)
            print("  Done")
            # force_save(console_step.save_loc, guide_link_steps, page_file_loc, page_at)
            input("Press Enter to continue...")


def print_progress():
    steps = io.unpickle(constants.CONSOLE_LINK_LIST_LOC)
    num_steps = len(steps)
    cur_step = 0
    for idx, step in enumerate(steps):
        if not step.completion:
            cur_step = idx

            break
    print(f'  On step {cur_step} of {num_steps}')
    print(f'  {step}')
