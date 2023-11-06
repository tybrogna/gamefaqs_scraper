import get_console_links

import os
import pickle

exp_link_check = "https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)"

gamefaqs_location = './gamefaqs/'
data_location = './data/'

save_progress_location = data_location + 'progress.pickle'

class Scraping_Step_Struct:
    def __init__(self, step_name, save_loc, completion):
        self.step_name = step_name
        self.save_loc = save_loc
        self.completion = completion

steps = [
    Scraping_Step_Struct("get_console_links", data_location + "console_link_list.pickle", False)]

def check_completion(step_location):
    if not os.path.exists(save_progress_location) or os.stat(save_progress_location).st_size == 0:
        print("No progress file found, creating progress file")
        with open(step_location, 'wb') as pickout:
            for step in steps:
                pickle.dump(step, pickout, pickle.HIGHEST_PROTOCOL)
            return False

    with open(save_progress_location, 'rb') as pickin:
        step = pickle.load(pickin)
        if (step.save_loc == step_location):
            return step.completion

def run_step(step_struct):
    if step_struct.step_name == "get_console_links":
        print("run get_console_links")
        # complete = get_console_links.run(step_struct.save_loc)
        # if complete:
            # update save_progress
    else:
        print("no command")

def run():
    # create folder to hold position saves
    if not os.path.exists(data_location):
        print("Creating data folder")
        os.makedirs('data')

    for step in steps:
        print("checking {0} step".format(step.step_name))
        step_complete = check_completion(step.save_loc)

        if step_complete:
            print("{0} is already complete".format(step.step_name))
            continue
        elif:
            run_step(step)

run()