from pathlib import Path
from threading import Event
from PIL import Image
from io import BytesIO

import html_guide_manager
import scraper_io as io
import constants
import progress_data_structures as ds
from bs4 import BeautifulSoup

kill_event = Event()


def kill():
    kill_event.set()
    html_guide_manager.kill_event.set()


def enliven():
    kill_event.clear()
    html_guide_manager.kill_event.clear()


def create_console_steps(consoles_loc: str) -> list[ds.FileStep]:
    """
    the results of get_console_links.py  becomes the steps toward completion of get_guides.py.
    For each console found in the pickled parameter, a game step will be created in the returned list

    :param consoles_loc: path to a pickle file containing the results of get_console_links.py
    :return: list of consoles to scan for games
    """
    steps = []
    console_link_steps = io.unpickle(consoles_loc)
    for console in console_link_steps:
        steps.append(ds.FileStep(name=console.name,
                                 link=console.link,
                                 save_loc="{0}_game_list".format(console.name),
                                 completion=console.completion))
    return steps


def create_game_steps(game_list_loc: str) -> list[ds.FileStep]:
    """
    the results of get_game_links.py  becomes the steps toward completion of get_guides.py.
    For each game found in the pickled parameter, a step will be created in the returned list

    :param game_list_loc: path to a pickle file containing the results of get_game_links.py
    :return: list of games to scan for guides
    """
    steps = []
    game_link_steps = io.unpickle(game_list_loc)
    for game in game_link_steps:
        steps.append(ds.FileStep(name=game.name,
                                 link=game.link,
                                 save_loc=game.name + '/',
                                 completion=game.completion))
    return steps


def true_get_guide_metadata(page_soup):
    guide_metadata_list = []
    guide_squares = page_soup.select('.gf_guides li')
    if len(guide_squares) <= 0:
        return
    for square in guide_squares:
        md = ds.GuideMetadata()
        pg_title = page_soup.select_one('.page-title').string
        md.game = pg_title[:pg_title.rindex(' Guides and FAQs')-2]
        # print(md.game)
        md.title = square.select_one('a.bold').string
        md.platform = square['data-platform']
        # print(md.platform)
        md.link = square.select_one('a.bold')['href']
        if md.link.split('/')[-2] == 'map':
            md.map = True
        # print(md.link)
        for author in square.select('span a'):
            md.author += author.string + ' and '
        md.author = md.author[:-5]
        # print(md.author)
        ital_eles = square.select('.ital')
        for ele in ital_eles:
            for ital in ele.strings:
                if 'incomplete' in str.lower(ital):
                    md.incomplete = True
        for flair in square.select('.flair'):
            if flair.string == 'HTML':
                md.html = True
        guide_metadata_list.append(md)
    return guide_metadata_list


def finish_metadata(page_soup, md):
    if md.map:
        map_date = page_soup.select_one('#map_block h4').text
        md.year = map_date[map_date.rindex('/') + 1:]
    else:
        ver_and_date = page_soup.select_one('div.ffaq p').get_text()
        if 'Version' in ver_and_date:
            md.version = ver_and_date[ver_and_date.index('Version:'):ver_and_date.index(' |')]
        if 'Updated' in ver_and_date:
            md.year = ver_and_date[ver_and_date.rindex('/') + 1:]
    if not page_soup.select_one('i.fa-star') is None:
        md.starred = True
    if md.html:
        for list_item in page_soup.select('ul.paginate'):
            for s in list_item.strings:
                if "page 1 of " in str.lower(s):
                    md.paginated = True
                    md.num_pages = int(s[s.rindex(' ') + 1:])
    #do award here?


def get_all_guide_links(page_soup):
    guide_links = page_soup.select('.gf_guides a.bold')
    if len(guide_links) < 0:
        return
    return guide_links


def get_game_aliases(page_soup):
    alias_url_list = []
    alias_links = page_soup.select('#header_more_menu a')
    for alias in alias_links:
        alias_url_list.append(alias['href'])
    return alias_url_list


def create_alias_save_data(alias_url_list):
    alias_sd_list = []
    for alias in alias_url_list:
        alias_no_slash = alias[1:]
        alias_console = alias_no_slash[:alias_no_slash.index('/')]
        if not io.pkl_exists(f'{alias_console}_game_list'):
            continue
        alias_link = alias_no_slash[alias_no_slash.index('/') + 1:]
        alias_game_id = alias_no_slash[alias_no_slash.index('/') + 1:alias_no_slash.index('-')]
        id_found = io.pkl_contains_name(f'{alias_console}_game_list', alias_game_id)
        if id_found:
            file_loc = f'{alias_console}_game_list'
            old_step = ds.FileStep(name=alias_game_id, link=alias_link, completion=False)
            alias_sd = ds.SaveData(file_loc=file_loc,
                                   blob=old_step.save_new_completion(),
                                   old_blob_for_overwrite=old_step,
                                   file_type='pickle')
            alias_sd_list.append(alias_sd)
    return alias_sd_list


def create_guide_save_data(guide_soup: BeautifulSoup, guide_metadata: ds.GuideMetadata) -> ds.SaveData:
    if guide_metadata.map:
        img_src = constants.URL_gamefaqs + guide_soup.select_one('#gf_map')['src']
        if img_src is None:
            return None
        img_blob = constants.url_request_blob(img_src)
        img_as_bio = BytesIO()
        for chunk in img_blob:
            img_as_bio.write(chunk)
        img_as_bio.seek(0)
        with Image.open(img_as_bio) as pil:
            guide_metadata.map_image_type = str.lower(pil.format)
        guide_data = ds.SaveData(blob=img_as_bio.getbuffer(),
                                 file_type='image')
    else:
        guide_text_elements = guide_soup.select('#faqtext pre')
        if guide_text_elements is None:
            return None
        guide_text = ''.join([ele.string for ele in guide_text_elements])
        guide_text = guide_text.replace('\r', '')
        guide_data = ds.SaveData(blob=guide_text, file_type='text')
    guide_data.file_loc = \
        Path(*constants.friendly_file_name(guide_metadata.game, guide_metadata.save_title()))
    return guide_data


# def get_guide_text(guide_soup: BeautifulSoup) -> ds.SaveData:
#     guide_text_elements = guide_soup.select('#faqtext pre')
#     if guide_text_elements is not None:
#         guide_text = ''.join([ele.string for ele in guide_text_elements])
#         guide_text = guide_text.replace('\r', '')
#         new_save = ds.SaveData(blob=guide_text, file_type='text')
#         return new_save
#     return None
#
#
# def get_map_image(guide_soup: BeautifulSoup) -> ds.SaveData:
#     img_src = guide_soup.select_one('#gf_map')['src']
#     if img_src is not None:
#         new_save = ds.SaveData(blob=constants.url_request_blob(img_src),
#                                file_type='image')
#         return new_save
#     return None


def create_dl_steps(game_id, guide_metadatas) -> list[ds.FileStep]:
    if io.exists(game_id):
        return io.unpickle(game_id)
    guide_dl_steps = []
    for md in guide_metadatas:
        gl_name = md.link[md.link.rindex('/') + 1:]
        guide_dl_steps.append(ds.FileStep(name=gl_name, link=md.link, completion=False))
    io.pkl_append_all(game_id, guide_dl_steps)
    return guide_dl_steps


def test_html_guide():
    # tg = open('./temp_files/tg.htm', 'r')
    # soup = BeautifulSoup(tg, "html.parser")
    # base_url = 'https://gamefaqs.gamespot.com/ps4/200179-red-dead-redemption-2/faqs/76594'
    soup = constants.heat_soup('https://gamefaqs.gamespot.com/wii-u/683293-bayonetta-2/faqs')
    metadata = true_get_guide_metadata(soup)
    base_url = 'https://gamefaqs.gamespot.com/wii-u/683293-bayonetta-2/faqs/70436'
    html_guide_manager.save_guide(soup, metadata[0], base_url)


def run(GUI):
    console_steps = create_console_steps(constants.CONSOLE_LINK_FOR_GUIDES)
    for console in console_steps:
        game_steps = create_game_steps(console.save_loc)
        for game in game_steps:
            if kill_event.is_set():
                print('get guides dying')
                return
            if game.completion:
                continue
            game_url = constants.URL_gamefaqs + '/x/' + game.link + 'faqs'
            game_soup: BeautifulSoup = constants.heat_soup(game_url)
            guide_metadatas = true_get_guide_metadata(game_soup)
            alias_url_list = get_game_aliases(game_soup)
            guide_dl_steps: list[ds.FileStep] = create_dl_steps(game.name, guide_metadatas)
            for guide_step, guide_metadata in zip(guide_dl_steps, guide_metadatas):
                if guide_step.completion:
                    continue
                if kill_event.is_set():
                    print('get guides dying')
                    return
                guide_url = constants.URL_gamefaqs + guide_step.link
                # https://gamefaqs.gamespot.com/x/[game_id]-[game_url_name]/[faqs | map]/[guide_id]
                guide_metadata.id = guide_step.link[guide_step.link.rindex('/')+1:]
                guide_soup = constants.heat_soup(guide_url)
                # is_guide = guide_soup.select_one('div.ffaq') is not None
                # if not is_guide:
                #     guide_progress_data = ds.SaveData(file_loc=game.name,
                #                                       blob=guide_step.save_new_completion(),
                #                                       old_blob_for_overwrite=guide_step,
                #                                       file_type='pickle')
                #     constants.force_save_pack(guide_progress_data)
                #     continue
                finish_metadata(guide_soup, guide_metadata)
                alias_data_list = create_alias_save_data(alias_url_list)
                guide_progress_data = ds.SaveData(file_loc=game.name,
                                                  blob=guide_step.save_new_completion(),
                                                  old_blob_for_overwrite=guide_step,
                                                  file_type='pickle')
                if guide_metadata.html:
                    html_guide_manager.save_guide(guide_metadata, guide_url)
                    constants.force_save_pack(guide_progress_data, *alias_data_list)
                else:
                    guide_data = create_guide_save_data(guide_soup, guide_metadata)
                    constants.force_save_pack(guide_data, guide_progress_data, *alias_data_list)
            # below, this point means all guides have been saved
            # mark game as complete and delete guide progress tracker file
            game_progress_data = ds.SaveData(file_loc=console.save_loc,
                                             blob=game.save_new_completion(),
                                             old_blob_for_overwrite=game,
                                             file_type='pickle')
            delete_game_name_data = ds.SaveData(file_loc=game.name,
                                                file_type='delete')
            constants.force_save_pack(game_progress_data, delete_game_name_data)


def verify_complete():
    console_steps = create_console_steps(constants.CONSOLE_LINK_FOR_GUIDES)
    for console in console_steps:
        game_steps = create_game_steps(console.save_loc)
        for game in game_steps:
            if not game.completion:
                return False
    return True


def check_full_progress() -> list[str]:
    """
    Checks the progress of the steps contained in this module
    :return: list of strings to display to the GUI describing progress
    """
    str_arr = []
    if not io.pkl_exists(constants.CONSOLE_LINK_FOR_GUIDES):
        return ['Console Link Save File, doesn\'t exist, not started']
    console_steps = create_console_steps(constants.CONSOLE_LINK_FOR_GUIDES)
    num_consoles = len(console_steps)
    cur_console_idx, cur_console = constants.get_first_match(lambda idx, ele: io.pkl_exists(ele.save_loc), console_steps)
    if cur_console_idx is None or cur_console is None:
        str_arr.append(f'Don\'t know what console. There are {num_consoles} consoles in this list')
        return str_arr
    str_arr.append(f'Console {cur_console_idx} of {num_consoles} ({cur_console.name})')
    game_steps = io.unpickle(cur_console.save_loc)
    num_games = len(game_steps)
    cur_game_idx, cur_game = constants.get_first_match(lambda idx, ele: not ele.completion, game_steps)
    if cur_game is None or cur_console_idx is None:
        str_arr.append(f'Don\'t know what game. There are {num_games} games in this list')
        return str_arr
    str_arr.append(f'  Game {cur_game_idx} of {num_games} ({cur_game.name})')
    if not io.pkl_exists(cur_game.name):
        str_arr.append(f'Guide 0 of [Unknown]')
        return str_arr
    guide_steps = io.unpickle(cur_game.name)
    num_guides = len(guide_steps)
    cur_guide_idx, cur_guide = constants.get_first_match(lambda idx, ele: not ele.completion, guide_steps)
    str_arr.append(f'    Guide {cur_guide_idx} of {num_guides}')
    return str_arr
