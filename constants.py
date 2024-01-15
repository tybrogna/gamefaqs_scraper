import _thread
import requests
import random
import math
import scraper_io as io
from bs4 import BeautifulSoup
import time
from progress_data_structures import SaveData
from concurrent.futures import ThreadPoolExecutor
import gui_manager

HEADERS = [
    {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
]

CONSOLE_LINK_LIST_LOC = 'console_link_list'
CONSOLE_LINK_FOR_GUIDES = 'console_link_list_2'
CONSOLE_PAGE_LENGTHS = 'console_page_lengths'
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
GUI: gui_manager.Gui = None

def heat_soup(url) -> BeautifulSoup:
    """
    makes a web request of the paramter url, then creates a soup object

    :param url: string url of webpage
    :return: BeautifulSoup html object
    """
    r_num = math.floor(random.random() * len(HEADERS))
    if r_num == len(HEADERS):
        r_num = len(HEADERS) - 1
    random_header = HEADERS[r_num]
    r_num = 13 + math.floor(random.random() * 17)
    time.sleep(r_num)
    req = requests.get(url, headers=random_header)
    if GUI:
        GUI.display(str(req.status_code) + " from " + url)
    print(str(req.status_code) + " from " + url)

    return BeautifulSoup(req.text, "html.parser")


def url_request_blob(url: str) -> requests.Response:
    req = requests.get(url, headers=HEADERS[-1], stream=True)
    GUI.display(str(req.status_code) + " from " + url)
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


def force_save_pack_sync(*save_pack: SaveData):
    queue_interrupt = False
    interrupt_count = 0
    saves_count = 0

    for save in save_pack:
        if type(save.blob) is int:
            save.blob = str(save.blob)
        if type(save.old_blob_for_overwrite) is int:
            save.old_blob_for_overwrite = str(save.old_blob_for_overwrite)

    while saves_count < len(save_pack):
        try:
            time.sleep(.3)
            save = save_pack[saves_count]
            if save.file_type == 'pickle':
                if save.old_blob_for_overwrite is not None:
                    done = io.pkl_overwrite(save.file_loc, save.old_blob_for_overwrite, save.blob)
                elif isinstance(save.blob, list):
                    done = io.pkl_append_all(save.file_loc, save.blob)
                else:
                    done = io.pkl_append(save.file_loc, save.blob)
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


def force_save_pack(*save_pack: SaveData):
    for save in save_pack:
        save.file_loc = io.__save_in_data(save.file_loc)
        if type(save.blob) is int:
            save.blob = str(save.blob)
        if type(save.old_blob_for_overwrite) is int:
            save.old_blob_for_overwrite = str(save.old_blob_for_overwrite)

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


def __saved_future(save: SaveData) -> bool:
    if save.file_type == 'pickle':
        if save.old_blob_for_overwrite is not None:
            done = io.pkl_overwrite(save.file_loc, save.old_blob_for_overwrite, save.blob)
        elif isinstance(save.blob, list):
            done = io.pkl_append_all(save.file_loc, save.blob)
        else:
            done = io.pkl_append(save.file_loc, save.blob)
    elif save.file_type == 'image':
        done = io.save_img(save.file_loc, save.blob)
    elif save.file_type == 'css':
        done = io.save_css(save.file_loc, save.blob)
    else:
        done = io.save_text(save.file_loc, save.blob)
    return done
