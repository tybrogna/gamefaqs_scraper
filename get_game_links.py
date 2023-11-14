from bs4 import BeautifulSoup
import requests
import os

import pkl_io as io
import web_consts as web
import progress_data_structures as ds

gamefaqs_location = './gamefaqs/'
data_location = './data/'


steps = []

GAMES_PER_PAGE = 100


def create_file_steps(console_links_file):
    for console in console_links_file:
        steps.append(ds.File_Step(console.name, console.link, "{0}_game_list".format(console.name), console.completion))


def create_console_progress_files(step_folder, console_save_loc):
    if not os.path.exists(step_folder):
        os.makedirs(step_folder)
        print("Data folder created")

    page_search_save_file = step_folder + "page_at"

    if not os.path.exists(page_search_save_file) or os.stat(page_search_save_file).st_size == 0:
        open(page_search_save_file, 'w').close()

    first_game_save = step_folder + "\\" + console_save_loc + "0"

    if not os.path.exists(first_game_save) or os.stat(first_game_save).st_size == 0:
        print("  No Game Link Progress file found, creating Game Link Progress file")
        open(first_game_save, 'w').close()

def read_console_progress_file(step_folder, console_save_loc):
    for itr in range(200):
        file_loc = step_folder.name + '\\' + console_save_loc + str(itr)
        game_links = io.unpickle(file_loc)
        if game_links > 10_000:
            return file_loc + itr


def create_page_url(console_name, pg_at):
    ret_url = web.URL_gamefaqs + console_name + web.URL_list
    if pg_at == 0:
        return ret_url
    else:
        return ret_url + web.URL_page + pg_at


def get_all_game_id_and_name(page_soup):
    page_soup.select("tr td.rmain:nth-of-type(-n+2) a")


def run(main_step_save_loc, previous_step_save_loc):
    print("  Getting all game links...")
    console_link_steps = io.unpickle(previous_step_save_loc)
    create_file_steps(console_link_steps)
    for console_step in steps:
        if console_step.completion:
            print("  {0} is done".format(console_step.name))
        else:
            create_console_progress_files(console_step.save_loc)
            file_at = read_console_progress_file(console_step.name, console_step.save_loc)
            game_links = io.unpickle(file_at)
            pg_at = games_complete + len(game_links) / GAMES_PER_PAGE
            print(pg_at)
            pg_url = create_page_url(console_step.name, pg_at)
            web.heat_soup(pg_url)
            print(pg_url)
