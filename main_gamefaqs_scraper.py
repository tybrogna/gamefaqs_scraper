import copy
import time
from threading import Thread

import get_console_links
import get_game_links
import get_guides
import gui_manager
import scraper_io as io
import progress_data_structures as ds
import constants

exp_link_check = "https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)"
GUI: gui_manager.Gui = None


def remove_console_link():
    for name in constants.CONSOLE_EXCLUDE:
        saved_name = io.pkl_contains_name(constants.CONSOLE_LINK_LIST_LOC, name)
        if saved_name:
            finish_step = saved_name.deepcopy()
            finish_step.completion = True
            io.pkl_overwrite(constants.CONSOLE_LINK_LIST_LOC, saved_name, finish_step)


steps = [
    ds.Main_Step('get_console_links', False),
    ds.Main_Step('get_game_links', False),
    ds.Main_Step('get_guides', False)]


def create_progress_file():
    if not io.pkl_exists("progress"):
        for step in steps:
            io.pkl_append("progress", step)


def check_progress(step_name):
    # print("checking {0} step".format(step_name))
    return io.pkl_contains_name("progress", step_name).completion


def check_full_progress():
    ret_strs = []
    if not GUI.save_loc.get() or GUI.save_loc.get() == '':
        GUI.display('No save location specified in the box')
        return
    save_folder_loc = GUI.save_loc.get()
    if not io.can_find_save_data(save_folder_loc):
        GUI.display(f'No Scraper Save Data found at {save_folder_loc}')
        return

    for idx, step in enumerate(steps):
        res = globals()[step.name].check_full_progress()
        if res:
            ret_strs.append(f'============  STEP {idx} OF {len(steps)}: {step.name}  ============')
            ret_strs.extend(res)
            ret_strs.append('\n')
    GUI.display(*ret_strs)


def update_progress(step, completion):
    new_step = copy.deepcopy(step)
    new_step.completion = completion
    io.pkl_overwrite("progress", step, new_step)


def run_db():
    io.setup('ha')


def run_a_thread():
    GUI.display(f'Starting...')
    override_folder_loc = ''
    if GUI.save_loc.get():
        override_folder_loc = GUI.save_loc.get()
    io.setup(override_folder_loc)
    create_progress_file()
    GUI.display('did the normal stuff')
    # global worker
    # global kill_threads
    # kill_threads = False
    # worker = Thread(target=globals()[steps[0].name].run, args=(GUI,))
    # GUI.display('thread start nao')
    # input('shfse')
    # worker.start()
    # GUI.display('thread running')
    # while worker.is_alive():
    #     time.sleep(.1)
    # GUI.display('thread finished')


def stop_a_thread():
    print('hello')


def kill_step_events():
    for step in steps:
        globals()[step.name].kill()


def revive_step_events():
    for step in steps:
        globals()[step.name].enliven()


def run():
    GUI.disable_buttons()
    GUI.display(f'Starting...')
    override_folder_loc = ''
    if GUI.save_loc.get():
        override_folder_loc = GUI.save_loc.get()
    io.setup(override_folder_loc)
    create_progress_file()
    try:
        for step in steps:
            print(f'checking {step.name} step')
            step_complete = check_progress(step.name)
            if step_complete:
                print(f'{step.name} is already complete')
                continue
            else:
                print(f'running {step.name}')
                step_run_func = globals()[step.name].run
                worker = Thread(target=step_run_func, args=(GUI,))
                worker.start()
                time.sleep(.5)
                while worker.is_alive():
                    GUI.update()
                if globals()[step.name].verify_complete():
                    update_progress(step, True)
                    GUI.display(f'progress updated: {step.name} => Complete')
                else:
                    GUI.display(f'{step.name} failed or ended')
                    break
                GUI.display(f'progress updated: {step.name} => Complete')
        GUI.enable_buttons()
        revive_step_events()
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


def app():
    global GUI
    GUI = gui_manager.Gui()
    GUI.setup(check_full_progress, run, kill_step_events)
    constants.GUI = GUI
    GUI.mainloop()


def test():
    io.setup('D:\\gamefaqs')
    io.pkl_test_print(constants.CONSOLE_LINK_LIST_LOC)
    print(get_console_links.check_full_progress())

# test()
app()
# run_db()
