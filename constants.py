import _thread
import requests
import pkl_io as io
from bs4 import BeautifulSoup
import time
from progress_data_structures import Save_Data

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}

CONSOLE_LINK_LIST_LOC = 'console_link_list'
GAME_LINK_LIST_LOC = 'console_link_list'
CONSOLE_DL_LIST_LOC = 'dl_list'


URL_gamefaqs = "https://gamefaqs.gamespot.com"
URL_consoles = "/games/systems"
URL_list = "/category/999-all"
URL_page = "?page="
URL_faqs = "/faqs"

CONSOLE_EXCLUDE = ['ps2', 'gc', 'xbox', 'game_boy']


def heat_soup(url) -> BeautifulSoup: 
    """
    makes a web request of the paramter url, then creates a soup object

    :param url: string url of webpage
    :return: BeautifulSoup html object
    """
    req = requests.get(url, headers=HEADERS)
    print(str(req.status_code) + " from " + url)
    return BeautifulSoup(req.text, "html.parser")


def force_save_pack(*save_pack: Save_Data):
    done = []
    queue_interrupt = False
    interrupt_count = 0
    saves_count = 0

    for save in save_pack:
        if type(save.blob) is int:
            save.blob = str(save.blob)
        if type(save.old_blob_for_overwrite) is int:
            save.old_blob_for_overwrite = str(save.old_blob_for_overwrite)

    while not all_done:
        try:
            time.sleep(.3)
            save = save_pack[saves_count]
            if save.isPickle:
                if save.old_blob_for_overwrite is not None:
                    done[saves_count] = io.overwrite_in_pkl(save.file_loc, save.old_blob_for_overwrite, save.blob)
                else:
                    done[saves_count] = io.append_all_to_pkl(save.file_loc, save.blob)
            else:
                done[saves_count] = io.save_html(save.file_loc, save.blob)
            saves_count = saves_count + 1
            all_done = True
            for d in done:
                all_done = all_done and d
        except KeyboardInterrupt:
            interrupt_count = interrupt_count + 1
            if interrupt_count == 1:
                print('Stopping, please wait...')
                queue_interrupt = True
                continue
            if interrupt_count <= 3:
                print('SAVING PROGRESS, DON\'T INTERRUPT')
                continue
            else:
                print('Ok fine jeez you got it chief')
                all_done = True
    if queue_interrupt:
        _thread.interrupt_main()


def force_save(*loc_data):
    done = []
    interrupt_count = 0
    saves_count = 0

    for save_pack in loc_data:
        if not type(save_pack) is list:
            print("save failed, wrong types")
            return
        if type(save_pack[1]) is int:
            save_pack[1] = str(save_pack[1])
        if len(save_pack) > 2:
            if type(save_pack[2]) is int:
                save_pack[2] = str(save_pack[2])
        done.append(False)
        saves_count = saves_count + 1
    saves_count = 0
    all_done = False

    while not all_done:
        try:
            time.sleep(.3)
            save_pack = loc_data[saves_count]
            if len(save_pack) > 2:
                done[saves_count] = io.overwrite_in_pkl(save_pack[0], save_pack[1], save_pack[2])
            else:
                done[saves_count] = io.append_all_to_pkl(save_pack[0], save_pack[1])
            saves_count = saves_count + 1
            all_done = True
            for d in done:
                all_done = all_done and d
        except KeyboardInterrupt:
            if interrupt_count <= 2:
                print('SAVING PROGRESS, DON\'T INTERRUPT')
                interrupt_count = interrupt_count + 1
                continue
            else:
                print('Ok fine jeez you got it chief')
                all_done = True
