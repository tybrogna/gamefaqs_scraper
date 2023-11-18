from bs4 import BeautifulSoup
import requests
import os
import time

import pkl_io as io
import constants
import progress_data_structures as ds


GAMES_PER_PAGE = 100
test = True


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
    if not io.exists(page_search_save_file):
        io.append_to_pkl(page_search_save_file, '0')

    first_game_save = console_save_loc
    if not io.exists(first_game_save):
        print("  No Game Link Progress file found, creating Game Link Progress file")
        io.create_file(first_game_save)


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


def force_save(console_step_save_loc, guide_links, page_file_loc, page_at):
    if test:
        print('saving {0} links to {1}'.format(len(guide_links), console_step_save_loc))
    done = False
    links_saved = False
    interrupt_count = 0
    next_page = int(page_at) + 1
    while not done:
        try:
            if not links_saved:
                links_saved = io.append_all_to_pkl(console_step_save_loc, guide_links)
            io.overwrite_in_pkl(page_file_loc, page_at, str(next_page))
            done = True
        except KeyboardInterrupt:
            print('SAVING PROGRESS, DON\'T INTERRUPT')
            interrupt_count = interrupt_count + 1
            if interrupt_count <= 3:
                continue
            else:
                print('Ok fine jeez you got it chief')
                done = True
    if test:
        print('...saved!')


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
            html_soup = constants.heat_soup(url_pg)
            if not page_contains_games(html_soup):
                io.delete_pkl(page_file_loc)
                finished_step = ds.File_Step(console_step.name, console_step.link, console_step.save_loc, True)
                # this needs to be forced
                io.overwrite_in_pkl(constants.CONSOLE_LINK_LIST_LOC, console_step, finished_step)
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
            force_save(console_step.save_loc, guide_link_steps, page_file_loc, page_at)
            input("Press Enter to continue...")
