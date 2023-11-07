import get_console_links
import pkl_io as io

import os
import pickle

exp_link_check = "https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)"

gamefaqs_location = './gamefaqs/'
data_location = './data/'

save_progress_location = data_location + 'progress.pickle'

class Save_Name:
    def __init__(self, name):
        self.name = name

class Scraping_Step_Struct(Save_Name):
    def __init__(self, name, save_loc, completion):
        super().__init__(name)
        self.save_loc = save_loc
        self.completion = completion

    def __str__(self):
        return "{0} \n    {1}, {2}" \
        .format(self.name, self.save_loc, "Finished" if self.completion else "Incomplete")

    def __eq__(self, other):
        if not isinstance(other, MyClass):
            return NotImplemented
        return self.name == other.name and self.save_loc == other.save_loc # and self.completion == other.completion

steps = [
    Scraping_Step_Struct("get_console_links", data_location + "console_link_list.pickle", False),
    Scraping_Step_Struct("get_game_links", data_location + "game_link_list.pickle", False)]

def check_completion(step_name):
    if not os.path.exists(save_progress_location) or os.stat(save_progress_location).st_size == 0:
        print("No progress file found, creating progress file")
        for step in steps:
            io.append_to_pkl(save_progress_location, step)
        return

    return io.pkl_contains_name(save_progress_location, step_name)

def check_progress_pkl():
    if not os.path.exists(save_progress_location) or os.stat(save_progress_location).st_size == 0:
        print("No progress file found, creating progress file")
        open(save_progress_location, "wb").close()
        for step in steps:
            io.append_to_pkl(save_progress_location, step)

def run_step(step_struct):
    print("run " + step_struct.name)
    if step_struct.name == "get_console_links":
        complete = get_console_links.run(step_struct.save_loc)
        if complete:
            print("done :)")
            # update save_progress
    else:
        print("no command")

def run():
    # create folder to hold position saves
    if not os.path.exists(data_location):
        print("Creating data folder")
        os.makedirs('data')

    for step in steps:
        print("checking {0} step".format(step.name))
        step_complete = check_completion(step.name)

        if step_complete:
            print("{0} is already complete".format(step.name))
            continue
        else:
            run_step(step)

def test():
    print("hello world")

    if not os.path.exists(data_location):
        print("Creating data folder")
        os.makedirs('data')

    check_progress_pkl()
    io.test_print_pkl(save_progress_location)

test()
# run()
