import re
import os
from threading import Event

import constants
import scraper_io as io
import progress_data_structures as ds
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from bs4 import Tag


kill_event = Event()


def __create_html_guide_step(pkl_name: str, base_url: str, toc_list) -> list[ds.FileStep]:
    html_guide_steps = []
    for idx, page_title in enumerate(toc_list):
        filesystem_name = constants.friendly_file_name(f'{idx} {page_title.text}')
        html_guide_steps.append(ds.FileStep(name=filesystem_name,
                                            completion=False))
        # html_guide_steps.append(ds.FileStep(name=filesystem_name,
        #                                     link=base_url + '/' + page_title['href'],
        #                                     completion=False))
    html_guide_steps[0].link = base_url
    io.pkl_append_all(pkl_name, html_guide_steps)
    return html_guide_steps


def __get_pagination_link(page_soup: BeautifulSoup) -> str:
    for li in page_soup.select_one('ul.paginate').select('a'):
        for s in li.strings:
            if "Next Page" in s:
                return li['href']


def __get_css_name(soup) -> str:
    """
    Returns the string name of the css file marked the core_css on the soup page
    """
    tag = soup.select_one("link#core_css")
    return constants.text_after_last_slash(tag['href'])


def __create_css_save_data(soup: BeautifulSoup) -> ds.SaveData:
    """
    Creates a savable data pack for the css marked core_css on the current soup page

    :param soup: BeautifulSoup object current guide page
    :return: Save_Data object for the core_css
    """
    tag = soup.select_one("link#core_css")
    css_name = constants.text_after_last_slash(tag['href'])
    linked_url = constants.URL_gamefaqs + constants.URL_css + '/' + css_name
    css_name = os.path.join(io.CSS_LOC, css_name)
    css_sd = ds.SaveData(css_name)
    css_sd.blob = constants.url_request_blob(linked_url).text
    css_sd.file_type = 'css'
    return css_sd


def __get_page_metadata(guide_metadata: ds.GuideMetadata, page_name) -> ds.PageMetadata:
    page_metadata = ds.PageMetadata(guide_metadata.game)
    page_metadata.file_save_path = os.path.join(
        f'{guide_metadata.save_title()}',
        f'{page_name}.html')
    page_metadata.image_save_path = os.path.join(
        f'{guide_metadata.save_title()}',
        'img')
    return page_metadata


def __create_html_save_data(page_metadata: ds.PageMetadata, css_name: str, page_content)\
        -> ds.SaveData:
    """
    Creates a savable data pack for the full html of the guide

    :param metadata: non-content guide data
    :param page_title: Name of the guide page from the Table of Contents
    :param css_name: core_css found in the header
    :param page_content: BS4 Tag
    """
    html_blob = []
    html_blob.append('<!DOCTYPE html>')
    css_location = os.path.join(io.DATA_FOLDER, io.CSS_LOC, css_name)
    html_blob.append(f'<link id="core_css" href="{css_location}" rel="stylesheet" type="text/css">')
    html_blob.append('<div class="container">')
    html_blob.append('<div id="faqwrap" class="ffaq ffaqbody">')
    html_blob.append(page_content)
    html_blob.append('</div')
    html_blob.append('</div>')
    html_save_data = ds.SaveData(file_loc=page_metadata.file_save_path,
                                 blob=html_blob,
                                 file_type='html')
    return html_save_data


def __create_image_save_data(metadata: ds.PageMetadata, page_content):
    """
    Creates a list of savable data packs for each image found in the page_content

    :param metadata: non-content guide data
    :param page_content: BS4 Tag object
    """
    save_pack = []
    pic_names = list(map(lambda a: a['src'][a['src'].rindex('/')+1:], page_content.select("img")))
    pic_links = list(map(lambda a: constants.URL_gamefaqs + a['src'], page_content.select("img")))
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = []
        for img_url, img_name in zip(pic_links, pic_names):
            img_save_loc = os.path.join(metadata.image_save_path, img_name)
            futures.append(pool.submit(__request_image_data, img_url, img_save_loc))
        for f in futures:
            try:
                save_pack.append(f.result())
            except Exception:
                print(f'couldnt save images for {metadata.game} for some reason')
    return save_pack


def __request_image_data(img_url, img_save_loc) -> ds.SaveData:
    img_save_data = ds.SaveData(file_loc=img_save_loc,
                                blob=constants.url_request_blob(img_url),
                                file_type='image')
    return img_save_data


def __adjust_image_locations(page_content: Tag):
    for img in page_content.select('img'):
        original_location = img['src']
        img_name = constants.text_after_last_slash(original_location)
        img['src'] = 'img/' + img_name


def save_guide(page_soup: BeautifulSoup, guide_metadata: ds.GuideMetadata, base_url: str):
    """
    Creates list of savable data packs for all the data found on the guide page (html content, images, css)

    :param page_soup: BS4 object
    :param guide_metadata: non-content guide data
    :param base_url: non-Table of content appended url to the guide
    """
    #TODO check if this works for both RDR2 and Bayo2
    if kill_event.is_set():
        print('html guides dying')
        return
    page_step_pkl_name = guide_metadata.game[0:3] + guide_metadata.author[0:3] + '_html_steps'
    page_steps: list[ds.FileStep] = io.unpickle(page_step_pkl_name)
    if not page_steps:
        toc_link_list = page_soup.select('#faqwrap .ftoc a')
        page_steps: list[ds.FileStep] = __create_html_guide_step(page_step_pkl_name, base_url, toc_link_list)
    # io.pkl_test_print(guide_metadata.game + 'TEST_MODE')
    for st_at, step in enumerate(page_steps):
        if kill_event.is_set():
            print('html guides dying')
            return
        if step.completion:
            continue
        guide_save_pack = []
        page_soup = constants.heat_soup(step.link)
        if st_at < len(page_steps):
            next_step = page_steps[st_at + 1]
            next_step.link = base_url + __get_pagination_link(page_soup)
        page_metadata = __get_page_metadata(guide_metadata, step.name)
        page_content = page_soup.select_one('#faqwrap')
        css_name = __get_css_name(page_soup)
        if not io.css_exists(css_name):
            guide_save_pack.append(__create_css_save_data(page_soup))
        if constants.DL_IMAGES:
            img_list = __create_image_save_data(page_metadata, page_content)
            if kill_event.is_set():
                print('html guides dying')
                return
            __adjust_image_locations(page_content)
            guide_save_pack.extend(img_list)
        guide_save_pack.append(__create_html_save_data(page_metadata, css_name, page_content))
        page_progress_data = ds.SaveData(file_loc=page_step_pkl_name,
                                         blob=step.save_new_completion(),
                                         old_blob_for_overwrite=step,
                                         file_type='pickle')
        guide_save_pack.append(page_progress_data)
        constants.force_save_pack(*guide_save_pack)
    io.pkl_delete(page_step_pkl_name)
