from bs4 import BeautifulSoup
import requests
import os
import signal
import logging

import pkl_io as io
import web_consts as web
import progress_data_structures as ds


GAMES_PER_PAGE = 100
test = True


class DelayedKeyboardInterrupt:

    def __enter__(self):
        self.signal_received = False
        self.old_handler = signal.signal(signal.SIGINT, self.handler)
                
    def handler(self, sig, frame):
        self.signal_received = (sig, frame)
        logging.debug('SIGINT received. Delaying KeyboardInterrupt.')
    
    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)


def create_file_steps(console_links_file):
    steps = []
    console_link_steps = io.unpickle(console_links_file)
    for console in console_link_steps:
        if test:
            print("get_game_links.py - adding {0} to steps".format(console.name))
        steps.append(ds.File_Step(console.name, console.link, "{0}_game_list".format(console.name), console.completion))
    return steps


def create_console_progress_files(step_folder, console_save_loc):
    if io.create_folder(step_folder):
        print("  Data folder created")

    page_search_save_file = step_folder + "/page_at"
    if not io.exists(page_search_save_file):
        io.append_to_pkl(page_search_save_file, '0')

    # if not os.path.exists(page_search_save_file) or os.stat(page_search_save_file).st_size == 0:
    #     io.append_to_pkl(page_search_save_file, "0")

    first_game_save = step_folder + '/' + console_save_loc + '0'
    if not io.exists(first_game_save):
        print("  No Game Link Progress file found, creating Game Link Progress file")
        io.create_file(first_game_save)
    # if not os.path.exists(first_game_save) or os.stat(first_game_save).st_size == 0:
    #     print("  No Game Link Progress file found, creating Game Link Progress file")
    #     open(first_game_save, 'w').close()


def read_console_progress_file(step_folder, console_save_loc):
    for itr in range(200):
        file_loc = step_folder + '/' + console_save_loc + str(itr)
        if not io.exists(file_loc):
            return step_folder + '/' + console_save_loc + str(itr - 1)


def create_page_url(console_name, pg_at):
    ret_url = web.URL_gamefaqs + console_name + web.URL_list
    if pg_at == 0:
        return ret_url
    else:
        return ret_url + web.URL_page + pg_at


def get_all_game_id_and_name(page_soup):
    guide_links = page_soup.select("tr td.rmain:nth-of-type(-n+2) a")
    # do this next


def run(main_step_save_loc, previous_step_save_loc):
    print("  Getting all game links...")
    steps = create_file_steps(previous_step_save_loc)
    for console_step in steps:
        if console_step.completion:
            print("  {0} is done".format(console_step.name))
        else:
            if test:
                print("get_game_links - perfoming {0} step".format(console_step.name))

            create_console_progress_files(console_step.name, console_step.save_loc)
            save_file_at = read_console_progress_file(console_step.name, console_step.save_loc)
            if test:
                print("get_game_links - found link save file {0}".format(save_file_at))
            pg_at = io.unpickle(console_step.name + "\\page_at")
            pg_url = create_page_url(console_step.name, pg_at)
            if test:
                print("get_game_links - resuming on page {0}, at {1}".format(pg_at,pg_url))                
            # page_soup = web.heat_soup(pg_url)
            # game_links = get_all_game_id_and_name(page_soup)

# https://gamefaqs.gamespot.com/pc/629337-text-a-summer-story/faqs