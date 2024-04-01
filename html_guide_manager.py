import re
from pathlib import Path
from threading import Event

import constants
import scraper_io as io
import progress_data_structures as ds
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from bs4 import Tag


kill_event = Event()


def __create_html_guide_steps(pkl_name: str, base_url: str, page_soup: BeautifulSoup, guide_metadata: ds.GuideMetadata):
    html_guide_steps = []
    if guide_metadata.paginated:
        for a in range(guide_metadata.num_pages):
            html_guide_steps.append(ds.FileStep(name=f'{a}',
                                                link=f'{base_url}?page={a}',
                                                completion=False))
    else:
        toc_list = page_soup.select('#faqwrap .ftoc a')
        for idx, page_title in enumerate(toc_list):
            filesystem_name = constants.friendly_file_name(f'{idx} {page_title.text}')
            html_guide_steps.append(ds.FileStep(name=filesystem_name,
                                                link=f'{base_url}/{page_title['href']}',
                                                completion=False))
    io.pkl_append_all(pkl_name, html_guide_steps)
    return html_guide_steps


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
    css_name = Path(io.CSS_LOC, css_name)
    css_sd = ds.SaveData(css_name)
    css_sd.blob = constants.url_request_blob(linked_url).text
    css_sd.file_type = 'css'
    return css_sd


def __get_page_metadata(guide_metadata: ds.GuideMetadata, page_name) -> ds.PageMetadata:
    page_metadata = ds.PageMetadata(guide_metadata.game)
    page_metadata.file_save_path = Path(
        *constants.friendly_file_name(
            guide_metadata.game, guide_metadata.save_title(), f'{page_name}.html'))
    page_metadata.image_save_path = Path(
        *constants.friendly_file_name(
            guide_metadata.game, guide_metadata.save_title(), 'img'))
    return page_metadata


def __create_html_save_data(page_metadata: ds.PageMetadata, css_name: str, page_content) -> ds.SaveData:
    """
    Creates a savable data pack for the full html of the guide

    :param metadata: non-content guide data
    :param page_title: Name of the guide page from the Table of Contents
    :param css_name: core_css found in the header
    :param page_content: BS4 Tag
    """
    html_blob = []
    # html_blob.append('<!DOCTYPE html>')
    css_location = Path(io.DATA_FOLDER, io.CSS_LOC, css_name).as_uri()
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

    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = []
        for img_url, img_name in zip(pic_links, pic_names):
            img_save_loc = Path(metadata.image_save_path, img_name)
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


def __adjust_link_locations(guide_metadata: ds.GuideMetadata):
    """
    this function took so long im an idiot
    """
    html_loc = Path(io.DATA_FOLDER,
                    *constants.friendly_file_name(guide_metadata.game, guide_metadata.save_title()))
    href_names = []
    for file in Path.iterdir(html_loc):
        if Path(html_loc, file).is_dir():
            continue
        href_names.append(file.name)
    for file in Path.iterdir(html_loc):
        if Path(html_loc, file).is_dir():
            continue
        print(file)
        loc_soup = constants.local_soup(file)
        toc = loc_soup.select('.ftoc li a')
        for name in href_names:
            idx_change: int = int(name[:name.index(' ')])
            toc[idx_change]['href'] = name
        constants.force_save_pack(ds.SaveData(file_loc=file,
                                              blob=loc_soup,
                                              file_type='html'))


def __adjust_image_locations(page_content: Tag):
    for img in page_content.select('img'):
        original_location = img['src']
        img_name = constants.text_after_last_slash(original_location)
        img['src'] = 'img/' + img_name


def save_guide(guide_metadata: ds.GuideMetadata, base_url: str):
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
    # page_step_pkl_name = guide_metadata.game[0:3] + guide_metadata.author[0:3] + '_html_steps'
    page_step_pkl_name = guide_metadata.id + '_html_steps'
    page_steps: list[ds.FileStep] = io.unpickle(page_step_pkl_name)
    if not page_steps:
        page_soup = constants.heat_soup(base_url)
        page_steps: list[ds.FileStep] = __create_html_guide_steps(pkl_name=page_step_pkl_name,
                                                                  base_url=base_url,
                                                                  page_soup=page_soup,
                                                                  guide_metadata=guide_metadata)
    for st_at, step in enumerate(page_steps):
        if kill_event.is_set():
            print('html guides dying')
            return
        if step.completion:
            continue
        guide_save_pack = []
        page_soup = constants.heat_soup(step.link)
        if guide_metadata.paginated:
            toc_link_list = page_soup.select('#faqwrap .ftoc a')
            step.name = f'{st_at} Walkthrough'
            if len(toc_link_list) == guide_metadata.num_pages:
                step.name = f'{st_at} {toc_link_list[st_at].string}'
                step.name = constants.friendly_file_name(step.name)
            else:
                for a in range(1,5):
                    biggest_header = page_soup.select_one(f'#faqwrap .section h{a}')
                    if biggest_header:
                        step.name = f'{st_at} {biggest_header.string}'
                        step.name = constants.friendly_file_name(step.name)
                        break
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
    __adjust_link_locations(guide_metadata)
    io.pkl_delete(page_step_pkl_name)
