from bs4 import BeautifulSoup
import requests
import os

import pkl_io as io
import web_consts as web
import progress_data_structures as ds

gamefaqs_location = './gamefaqs/'
data_location = './data/'

save_progress_location = data_location + 'game_links_progress.pickle'


steps = []

GAMES_PER_PAGE = 100


def create_file_steps(console_links_file):
    for console in console_links_file:
        steps.append(ds.File_Step(console.name, console.link, "{0}_game_list.pickle".format(console.name), console.completion))


def create_progress_file():
    if not os.path.exists(save_progress_location) or os.stat(save_progress_location).st_size == 0:
        print("  No Game Link Progress file found, creating Game Link Progress file")
        open(save_progress_location, 'w').close()

        for step in steps:
            io.append_to_pkl(save_progress_location, step)
        return


def run(main_step_save_loc, previous_step_save_loc):
    print("  Getting all game links...")
    console_link_steps = io.unpickle(previous_step_save_loc)
    create_file_steps(console_link_steps)
    for step in steps:
        if step.completion:
            print("  {0} is done".format(step.name))
        else:
            game_links = io.unpickle(step.save_loc)
            pg_at = len(game_links) / GAMES_PER_PAGE
            print(step)
