import os
import copy

import get_console_links
import get_game_links
import pkl_io as io
import progress_data_structures as ds
import constants

exp_link_check = "https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)"


def dummy_func(arg):
    print('im dum')
    return


def sort_links_by_priority(arg, console_links_save_loc):
    print('oof')


steps = [
    ds.Main_Step("get_console_links", get_console_links.run, constants.CONSOLE_LINK_LIST_LOC, False),
    # ds.Main_Step("sort_console_links"),
    ds.Main_Step("get_game_links", get_game_links.run, constants.GAME_LINK_LIST_LOC, False)]


def create_progress_file():
    if io.create_file("progress"):
        for step in steps:
            io.append_to_pkl("progress", step)
    # if not os.path.exists(save_progress_location) or os.stat(save_progress_location).st_size == 0:
    #     print("No Major Progress file found, creating Major Progress file")
    #     open(save_progress_location, 'w').close()
    #     for step in steps:
    #         io.append_to_pkl(save_progress_location, step)
    #     return


def check_progress(step_name):
    print("checking {0} step".format(step_name))
    return io.pkl_contains_name("progress", step_name).completion


def update_progress(step, completion):
    new_step = copy.deepcopy(step)
    new_step.completion = completion
    io.overwrite_in_pkl("progress", step, new_step)


def run():
    # create folder to hold position saves
    # if not os.path.exists("data_location"):
    #     os.makedirs('data')
    #     print("Data folder created")
    io.setup()

    create_progress_file()

    # previous_step = ds.Main_Step("", dummy_func, "", True)

    for step in steps:
        step_complete = check_progress(step.name)

        if step_complete:
            print("{0} is already complete".format(step.name))
            # previous_step = step
            continue
        else:
            print("running {0}".format(step.name))
            complete = step.run_func()
            if complete:
                update_progress(step, True)
                print("progress updated: {0} => Complete".format(step.name))
            else:
                print("{0} failed".format(step.name))
            # previous_step = step

            # run_step(step)


def test():
    print("hello world")

    # a_list = [1,2,3]
    # b_list = [4,5,a_list]

    # copy_step = copy.deepcopy(steps[0])
    # copy_step.name = "im a clone"
    # print(steps[0])
    # print(copy_step)

    # if not os.path.exists(data_location):
    #     print("Creating data folder")
    #     os.makedirs('data')

    # io.test_print_pkl("progress")
    # io.test_print_pkl(steps[0].save_loc)


# test()
run()
