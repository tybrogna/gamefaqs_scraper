import copy
import math
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

default_steps = [
    ds.MainStep('get_console_links', False),
    ds.MainStep('get_game_links', False),
    ds.MainStep('get_guides', False)]


def remove_console_link():
    for name in constants.CONSOLE_EXCLUDE:
        saved_name = io.pkl_contains_name(constants.CONSOLE_LINK_LIST_LOC, name)
        if saved_name:
            finish_step = saved_name.deepcopy()
            finish_step.completion = True
            io.pkl_overwrite(constants.CONSOLE_LINK_LIST_LOC, saved_name, finish_step)


def get_progress_steps() -> list[ds.MainStep]:
    if not io.pkl_exists('progress'):
        for step in default_steps:
            io.pkl_append('progress', step)
    return io.unpickle('progress')


def check_progress(step_name):
    # print("checking {0} step".format(step_name))
    return io.pkl_contains_name("progress", step_name).completion


def check_full_progress():
    ret_strs = []
    if not GUI.save_loc.get() or GUI.save_loc.get() == '':
        GUI.display('No save location specified in the box')
        return
    save_folder_loc = GUI.save_loc.get()
    if not io.path_exists(save_folder_loc):
        GUI.display(f'{save_folder_loc} doesn\'t exist')
        return
    io.setup(save_folder_loc)
    if not io.pkl_exists('progress'):
        GUI.display(f'No Scraper Save Data found at {save_folder_loc}')
        return
    steps = get_progress_steps()
    for idx, step in enumerate(steps):
        res = globals()[step.name].check_full_progress()
        if res:
            ret_strs.append(f'============  STEP {idx + 1} OF {len(steps)}: {step.name}  ============')
            ret_strs.extend(res)
            ret_strs.append('\n')
    if io.pkl_exists(constants.TIME_LOC):
        time_dict = io.unpickle(constants.TIME_LOC)
        ret_strs.append()
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
    get_progress_steps()
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
    for step in default_steps:
        globals()[step.name].kill()


def revive_step_events():
    for step in default_steps:
        globals()[step.name].enliven()


def run_cleanup(GUI, start_time=0.):
    GUI.enable_buttons()
    revive_step_events()
    time_taken = time.time() - start_time
    spent_waiting = constants.session_waits
    fmt_session_time = constants.time_to_hms_string(time_taken)
    fmt_wait_time = constants.time_to_hms_string(spent_waiting)
    GUI.display('\n')
    GUI.display(f'Session Time: {fmt_session_time}')
    GUI.display(f'Scraping Detection Waiting Time: {fmt_wait_time}')
    if io.pkl_exists(constants.TIME_LOC):
        timing_dict = io.unpickle(constants.TIME_LOC)[0]
        timing_dict['total_time'] += time_taken
        timing_dict['wait_time'] += spent_waiting
        fmt_total_time = constants.time_to_hms_string(timing_dict['total_time'])
        fmt_total_wait_time = constants.time_to_hms_string(timing_dict['wait_time'])
        GUI.display(f'Total Time: {fmt_total_time}')
        GUI.display(f'Total Scraping Detection Waiting Time: {fmt_total_wait_time}')
        io.pkl_save_new(constants.TIME_LOC, timing_dict)
    else:
        timing_dict = {'total_time': time_taken, 'wait_time': spent_waiting}
        io.pkl_save_new(constants.TIME_LOC, timing_dict)


def run():
    start_time = time.time()
    GUI.disable_buttons()
    GUI.display(f'Starting...')
    override_folder_loc = ''
    if GUI.save_loc.get():
        override_folder_loc = GUI.save_loc.get()
    io.setup(override_folder_loc)
    io.create_folders()
    steps = get_progress_steps()
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
        run_cleanup(GUI, start_time)
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
    # io.pkl_test_print('D:\\gamefaqs\\progress')
    io.pkl_test_print('D:\\gamefaqs\\wii-u_game_list')
    # io.pkl_test_print('D:\\gamefaqs\\wii-u_game_list')
    # soup = constants.heat_soup('https://gamefaqs.gamespot.com/3ds/category/999-all')
    # all_txt = soup.select_one('.paginate li').text
    # final_pg = all_txt[all_txt.rindex(' '):].strip()
    # print(final_pg)
    # nl = [''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5)) for n in range(100000)]
    # locl = ['C:\\'.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8)) for n in range(100000)]
    # linl = ['https://www.'.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=35)).join('.com') for n in range(100000)]
    # sl = []
    # st = time.time()
    # for x in range(100000):
    #     sl.append(ds.FileStep(name=nl[x], link=linl[x], save_loc=locl[x]))
    # print("--- %s seconds ---" % (time.time() - st))
    # save_data = ds.SaveData(file_type='pickle',
    #                         file_loc=constants.CONSOLE_LINK_LIST_LOC,
    #                         blob='hehe',)
    # print(save_data)
    # io.setup('D:\\gamefaqs')
    # options_dict = {'name':'ahah', 'save_loc':'c drive', 'completion':True}
    # print(ds.FileStep(name='something'))
    # print(ds.FileStep(**options_dict))
    # io.pkl_test_print(constants.CONSOLE_LINK_LIST_LOC)
    # print(get_console_links.check_full_progress())

# test()
app()
# run_db()
