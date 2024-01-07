import copy
import tkinter

import get_console_links
import get_game_links
import get_guides
import gui_manager
import scraper_io as io
import progress_data_structures as ds
import constants

exp_link_check = "https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)"
override_folder_loc = ''

def dummy_func(arg):
    print('im dum')
    return


def remove_console_link():
    for name in constants.CONSOLE_EXCLUDE:
        saved_name = io.pkl_contains_name(constants.CONSOLE_LINK_LIST_LOC, name)
        if saved_name:
            finish_step = saved_name.deepcopy()
            finish_step.completion = True
            io.pkl_overwrite(constants.CONSOLE_LINK_LIST_LOC, saved_name, finish_step)


steps = [
    ds.Main_Step('get_console_links', constants.CONSOLE_LINK_LIST_LOC, False),
    # ds.Main_Step('exclude_console_links', remove_console_link),
    ds.Main_Step('get_game_links', constants.GAME_LINK_LIST_LOC, False),
    ds.Main_Step('get_guides', False)]


def create_progress_file():
    if not io.pkl_exists("progress"):
        for step in steps:
            io.pkl_append("progress", step)


def check_progress(step_name):
    # print("checking {0} step".format(step_name))
    return io.pkl_contains_name("progress", step_name).completion

def check_full_progress():
    print('here')
    return

def update_progress(step, completion):
    new_step = copy.deepcopy(step)
    new_step.completion = completion
    io.pkl_overwrite("progress", step, new_step)


def run_db():
    io.setup('ha')


def run():
    io.setup(override_folder_loc)
    create_progress_file()
    try:
        for step in steps:
            print("checking {0} step".format(step.name))
            step_complete = check_progress(step.name)
            if step_complete:
                print("{0} is already complete".format(step.name))
                continue
            else:
                print("running {0}".format(step.name))
                complete = globals()[step.name].run()
                if complete:
                    update_progress(step, True)
                    print("progress updated: {0} => Complete".format(step.name))
                else:
                    print("{0} failed".format(step.name))
    except KeyboardInterrupt:
        for step in steps:
            step_complete = check_progress(step.name)
            if step_complete:
                continue
            else:
                print(f'stopped while performing the {step.name} step')
                print(f'step progress ->')
                globals()[step.name].print_progress()
                break


def test():
    print("hello world")
    io.setup()
    gui = gui_manager.Gui()
    gui.setup()
    # gui.add_button('Check Progress', check_full_progress)
    # gui.add_button('Start Scraper', run)
    # gui.add_label('save location')
    # baloney = tkinter.StringVar()
    # baloney.set('haha')
    # gui.add_entry(baloney)
    gui.mainloop()
    # globals()['get_console_links'].print_progress()
    # get_guides.good_shit()

    # io.try_sql()

    # a_list = [1,2,3]
    # b_list = [4,5,a_list]

    # copy_step = copy.deepcopy(steps[0])
    # copy_step.name = "im a clone"
    # print(steps[0])
    # print(copy_step)

    # if not os.path.exists(data_location):
    #     print("Creating data folder")
    #     os.makedirs('data')

    # io.test_print_pkl("3ds_game_list")
    # io.test_print_pkl(steps[0].save_loc)

test()
# run()
# run_db()
