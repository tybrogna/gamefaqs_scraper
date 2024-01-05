import _thread
import requests
import scraper_io as io
from bs4 import BeautifulSoup
import time
from progress_data_structures import Save_Data
from concurrent.futures import ThreadPoolExecutor

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}

CONSOLE_LINK_LIST_LOC = 'console_link_list'
GAME_LINK_LIST_LOC = 'console_link_list'
CONSOLE_DL_LIST_LOC = 'dl_list'
DL_IMAGES = True


URL_gamefaqs = "https://gamefaqs.gamespot.com"
URL_consoles = "/games/systems"
URL_list = "/category/999-all"
URL_page = "?page="
URL_faqs = "/faqs"
URL_css = '/a/css'

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


def url_request_blob(url: str) -> requests.Response:
    req = requests.get(url, headers=HEADERS, stream=True)
    print(str(req.status_code) + " from " + url)
    return req


def text_before_last_slash(text: str) -> str:
    if '/' in text:
        return text[:text.rindex('/')]
    elif '\\' in text:
        return text[:text.rindex('\\')]
    return ''


def text_after_last_slash(text: str) -> str:
    if '/' in text:
        return text[text.rindex('/') + 1:]
    elif '\\' in text:
        return text[text.rindex('\\') + 1:]
    return ''


def force_save_pack_sync(*save_pack: Save_Data):
    # done = []
    queue_interrupt = False
    interrupt_count = 0
    saves_count = 0

    for save in save_pack:
        if type(save.blob) is int:
            save.blob = str(save.blob)
        if type(save.old_blob_for_overwrite) is int:
            save.old_blob_for_overwrite = str(save.old_blob_for_overwrite)
        # done.append(False)

    print(save_pack)

    # TODO futurize this?
    while saves_count < len(save_pack):
        try:
            time.sleep(.3)
            save = save_pack[saves_count]
            if save.file_type == 'pickle':
                if save.old_blob_for_overwrite is not None:
                    done = io.pkl_overwrite(save.file_loc, save.old_blob_for_overwrite, save.blob)
                else:
                    done = io.pkl_append_all(save.file_loc, save.blob)
            elif save.file_type == 'image':
                done = io.save_img(save.file_loc, save.blob)
            elif save.file_type == 'css':
                done = io.save_css(save.file_loc, save.blob)
            else:
                done = io.save_text(save.file_loc, save.blob)
            if done:
                saves_count = saves_count + 1
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
                saves_count = len(save_pack)
    if queue_interrupt:
        raise KeyboardInterrupt


def force_save_pack(*save_pack: Save_Data):
    for save in save_pack:
        save.file_loc = io.__save_in_data(save.file_loc)
        if type(save.blob) is int:
            save.blob = str(save.blob)
        if type(save.old_blob_for_overwrite) is int:
            save.old_blob_for_overwrite = str(save.old_blob_for_overwrite)
    print(save_pack)

    with ThreadPoolExecutor(max_workers=8) as pool:
        finished_futures = []
        for save in save_pack:
            finished_futures.append(pool.submit(__saved_future, save))
        for future in finished_futures:
            try:
                future.result()
            except Exception:
                print(f'couldn\'t save something')
                _thread.interrupt_main()


def __saved_future(save: Save_Data) -> bool:
    if save.file_type == 'pickle':
        if save.old_blob_for_overwrite is not None:
            done = io.pkl_overwrite(save.file_loc, save.old_blob_for_overwrite, save.blob)
        else:
            done = io.pkl_append_all(save.file_loc, save.blob)
    elif save.file_type == 'image':
        done = io.save_img(save.file_loc, save.blob)
    elif save.file_type == 'css':
        done = io.save_css(save.file_loc, save.blob)
    else:
        done = io.save_text(save.file_loc, save.blob)
    return done

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
                done[saves_count] = io.pkl_overwrite(save_pack[0], save_pack[1], save_pack[2])
            else:
                done[saves_count] = io.pkl_append_all(save_pack[0], save_pack[1])
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
