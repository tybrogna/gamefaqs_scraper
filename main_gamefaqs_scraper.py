import get_console_links
import pkl_io as io

import os
import pickle
import copy

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

    def __eq__(self, other):
        if not isinstance(other, Scraping_Step_Struct):
            return NotImplemented
        return self.name == other.name and self.save_loc == other.save_loc # and self.completion == other.completion

    def __str__(self):
        return "{0} \n    {1}, {2}" \
        .format(self.name, self.save_loc, "Finished" if self.completion else "Incomplete")

steps = [
    Scraping_Step_Struct("get_console_links", data_location + "console_link_list.pickle", False),
    Scraping_Step_Struct("get_game_links", data_location + "game_link_list.pickle", False)]

def create_progress_file():
    if not os.path.exists(save_progress_location) or os.stat(save_progress_location).st_size == 0:
        print("No progress file found, creating progress file")
        open(save_progress_location, 'w').close()
        for step in steps:
            io.append_to_pkl(save_progress_location, step)
        return

def check_progress(step_name):
    print("checking {0} step".format(step_name))
    return io.pkl_contains_name(save_progress_location, step_name).completion

def update_progress(step, completion):
    new_step = copy.deepcopy(step)
    new_step.completion = completion
    io.overwrite_in_pkl(save_progress_location, step, new_step)

def run_step(step):
    print("running {0}".format(step.name))
    if step.name == "get_console_links":
        complete = get_console_links.run(step.save_loc)
        if complete:
            update_progress(step, True)
            print("progress updated: {0} => Complete".format(step.name))
        else:
            print("failed")
    else:
        print("no command")

def run():
    # create folder to hold position saves
    if not os.path.exists(data_location):
        os.makedirs('data')
        print("Data folder created")

    create_progress_file()

    for step in steps:
        step_complete = check_progress(step.name)

        if step_complete:
            print("{0} is already complete".format(step.name))
            continue
        else:
            run_step(step)

def test():
    print("hello world")

    # copy_step = copy.deepcopy(steps[0])
    # copy_step.name = "im a clone"
    # print(steps[0])
    # print(copy_step)

    # if not os.path.exists(data_location):
    #     print("Creating data folder")
    #     os.makedirs('data')

    io.test_print_pkl(save_progress_location)
    io.test_print_pkl(steps[0].save_loc)

# test()
run()
