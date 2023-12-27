import re

import constants
import scraper_io as io
import progress_data_structures as ds
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from bs4 import Tag


def __create_html_guide_step(game_name: str, base_url: str, toc_list) -> list[ds.Link_Step]:
    html_guide_steps = []
    for page_title in toc_list:
        filesystem_name = page_title.text.replace(':', ' -')
        filesystem_name = filesystem_name.replace('/', ', ')
        filesystem_name = filesystem_name.replace('\\', ', ')
        filesystem_name = re.sub('[<>*?"|]', '', filesystem_name)
        html_guide_steps.append(ds.Link_Step(filesystem_name, base_url + '/' + page_title['href'], False))
    io.pkl_append_all(game_name + "TEST_MODE", html_guide_steps)
    return html_guide_steps


def __get_css_name(soup) -> str:
    """
    Returns the string name of the css file marked the core_css on the soup page
    """
    tag = soup.select_one("link#core_css")
    return constants.text_after_last_slash(tag['href'])


def __create_css_save_data(soup: BeautifulSoup) -> ds.Save_Data:
    """
    Creates a savable data pack for the css marked core_css on the current soup page

    :param soup: BeautifulSoup object current guide page
    :return: Save_Data object for the core_css
    """
    tag = soup.select_one("link#core_css")
    css_name = constants.text_after_last_slash(tag['href'])
    linked_url = constants.URL_gamefaqs + constants.URL_css + '/' + css_name
    css_sd = ds.Save_Data(css_name)
    css_sd.blob = constants.url_request_blob(linked_url).text
    css_sd.file_type = 'css'
    return css_sd


def __create_html_save_data(metadata: ds.Guide_Data, page_title: Tag, css_name: str, page_content)\
        -> ds.Save_Data:
    """
    Creates a savable data pack for the full html of the guide

    :param metadata: non-content guide data
    :param page_title: Name of the guide page from the Table of Contents
    :param css_name: core_css found in the header
    :param page_content: BS4 Tag
    """
    html_blob = []
    html_blob.append('<!DOCTYPE html>')
    css_location = io.ABSOLUTE_PATH + io.CSS_LOC + css_name
    html_blob.append(f'<link id="core_css" href="{css_location}" rel="stylesheet" type="text/css">')
    html_blob.append('<div class="container">')
    html_blob.append('<div id="faqwrap" class="ffaq ffaqbody">')
    html_blob.append(page_content)
    html_blob.append('</div')
    html_blob.append('</div>')
    html_save_data = ds.Save_Data('{0} by {1}/{2}.html'.format(metadata.title, metadata.author, page_title))
    html_save_data.blob = html_blob
    html_save_data.file_type = 'html'
    return html_save_data


def __create_image_save_data(metadata: ds.Guide_Data, page_content):
    """
    Creates a list of savable data packs for each image found in the page_content

    :param metadata: non-content guide data
    :param page_content: BS4 Tag object
    """
    save_pack = []
    pic_names = list(map(lambda a: a['src'][a['src'].rindex('/'):], page_content.select("img")))
    pic_links = list(map(lambda a: constants.URL_gamefaqs + a['src'], page_content.select("img")))
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = []
        for img_url, img_name in zip(pic_links, pic_names):
            futures.append(pool.submit(__request_image_data, metadata, img_url, img_name))
        for f in futures:
            try:
                save_pack.append(f.result())
            except Exception:
                print(f'couldnt save images for {metadata.game} for some reason')
    return save_pack


def __request_image_data(metadata, img_url, img_name) -> ds.Save_Data:
    img_save_data = ds.Save_Data('{0} by {1}/img{2}'.format(metadata.title, metadata.author, img_name))
    img_save_data.blob = constants.url_request_blob(img_url)
    img_save_data.file_type = 'image'
    return img_save_data


def __adjust_image_locations(page_content: Tag):
    for img in page_content.select('img'):
        original_location = img['src']
        img_name = constants.text_after_last_slash(original_location)
        img['src'] = 'img/' + img_name


def save_guide(page_soup: BeautifulSoup, guide_metadata: ds.Guide_Data, base_url: str):
    """
    Creates list of savable data packs for all the data found on the guide page (html content, images, css)

    :param page_soup: BS4 object
    :param guide_metadata: non-content guide data
    :param base_url: non-Table of content appended url to the guide
    """
    page_steps: list[ds.Link_Step] = io.unpickle(guide_metadata.game + 'TEST_MODE')
    if not page_steps:
        toc_link_list = page_soup.select('#faqwrap .ftoc a')
        page_steps: list[ds.Link_Step] = __create_html_guide_step(guide_metadata.game, base_url, toc_link_list)
    # io.pkl_test_print(guide_metadata.game + 'TEST_MODE')
    # input("yo stop here")
    for step in page_steps:
        guide_save_pack = []
        input("press enter to continue...")
        if step.completion:
            print(step)
            continue
        page_soup = constants.heat_soup(step.link)
        page_content = page_soup.select_one('#faqwrap')
        css_name = __get_css_name(page_soup)
        if not io.css_exists(css_name):
            guide_save_pack.append(__create_css_save_data(page_soup))
        if constants.DL_IMAGES:
            img_list = __create_image_save_data(guide_metadata, page_content)
            __adjust_image_locations(page_content)
            guide_save_pack.extend(img_list)
        # input("hellos")
        guide_save_pack.append(__create_html_save_data(guide_metadata, step.name, css_name, page_content))
        page_progress_data = ds.Save_Data(guide_metadata.game + 'TEST_MODE', step.save_new_completion(), step, True)
        page_progress_data.file_type = "pickle"
        guide_save_pack.append(page_progress_data)
        # for obj in guide_save_pack:
        #     print(obj)
        # input("afhflsie")
        constants.force_save_pack(*guide_save_pack)
        # io.pkl_test_print(guide_metadata.game + 'TEST_MODE')
        # input("yo stop here again")
