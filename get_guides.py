import os
from threading import Event

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
        print(md.game)
        md.title = square.select_one('a.bold').string
        md.platform = square['data-platform']
        print(md.platform)
        md.link = square.select_one('a.bold')['href']
        print(md.link)
        for author in square.select('span a'):
            md.author += author.string + ' and '
        md.author = md.author[:-5]
        print(md.author)
        if square.select('.ital'):
            md.incomplete = True
        for flair in square.select('.flair'):
            if flair.string == 'HTML':
                md.html = True
        guide_metadata_list.append(md)
    return guide_metadata_list


def finish_metadata(page_soup, md):
    ver_and_date = page_soup.select_one('div.ffaq p').get_text()
    if 'Version' in ver_and_date:
        md.version = ver_and_date[ver_and_date.index('Version:'):ver_and_date.index(' |')]
    md.year = ver_and_date[ver_and_date.rindex('/') + 1:]
    if not page_soup.select_one('i.fa-star') is None:
        md.starred = True
    #do award here?



def get_all_guide_links(page_soup):
    guide_links = page_soup.select('.gf_guides a.bold')
    if len(guide_links) < 0:
        return
    return guide_links


def get_guide_metadata(page_soup):
    guide_metadata = ds.GuideMetadata()
    if page_soup.select_one('#faqwrap .ftoc a') is not None:
        guide_metadata.html = True
    title_platform_author = page_soup.select_one('div.ffaq h2').get_text()
    title_platform = title_platform_author[:title_platform_author.rindex(' by ')]
    guide_metadata.platform = title_platform[title_platform.rindex('(') + 1:title_platform.rindex(')')]
    guide_metadata.title = title_platform[:title_platform.rindex(' (')]
    guide_metadata.author = title_platform_author[title_platform_author.rindex(' by ') + 4:]
    # print(f'title: {guide_metadata.title}')
    if guide_metadata.html:
        guide_metadata.game = page_soup.select_one('.platform-title :first-child').string
        guide_metadata.game = guide_metadata.game[:guide_metadata.game.rindex(' ')]
    else:
        guide_metadata.game = page_soup.select_one('.page-title').string
        # print(f'pagetitlestr: {guide_metadata.game}')
        guide_metadata.game = guide_metadata.game[:guide_metadata.game.rindex(guide_metadata.title)-3]
        # print(f'game: {guide_metadata.game}')
    ver_and_date = page_soup.select_one('div.ffaq p').get_text()
    if 'Version' in ver_and_date:
        guide_metadata.version = ver_and_date[ver_and_date.index('Version:'):ver_and_date.index(' |')]
    guide_metadata.year = ver_and_date[ver_and_date.rindex('/') + 1:]
    if not page_soup.select_one('i.fa-star') is None:
        guide_metadata.starred = True
    return guide_metadata


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


def get_guide_text(page_soup):
    guide_text = page_soup.select('#faqtext pre')
    guide_text_list = []
    if guide_text is not None:
        for gt in guide_text:
            guide_text_list.append(gt.contents)
    new_save = ds.SaveData(blob=guide_text_list, file_type='text')
    return new_save


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
    base_url = 'https://gamefaqs.gamespot.com/ps4/200179-red-dead-redemption-2/faqs/76594'
    soup = constants.heat_soup(base_url)
    metadata = get_guide_metadata(soup)
    html_guide_manager.save_guide(soup, metadata, base_url)


def run(GUI):
    #TODO by the time this gets here, all the steps in CONSOLE_LINK_LIST_LOC are complete
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
            print(alias_url_list)
            # guide_links_list = get_all_guide_links(game_soup)
            guide_dl_steps = create_dl_steps(game.name, guide_metadatas)
            for guide_step, guide_metadata in zip(guide_dl_steps, guide_metadatas):
                if guide_step.completion:
                    continue
                if kill_event.is_set():
                    print('get guides dying')
                    return
                guide_url = constants.URL_gamefaqs + guide_step.link
                guide_soup = constants.heat_soup(guide_url)
                is_guide = guide_soup.select_one('div.ffaq') is not None
                if not is_guide:
                    guide_progress_data = ds.SaveData(file_loc=game.name,
                                                      blob=guide_step.save_new_completion(),
                                                      old_blob_for_overwrite=guide_step,
                                                      file_type='pickle')
                    constants.force_save_pack(guide_progress_data)
                    continue
                finish_metadata(guide_soup, guide_metadata)
                # guide_metadata = get_guide_metadata(guide_soup)
                alias_data_list = create_alias_save_data(alias_url_list)
                guide_progress_data = ds.SaveData(file_loc=game.name,
                                                  blob=guide_step.save_new_completion(),
                                                  old_blob_for_overwrite=guide_step,
                                                  file_type='pickle')
                if guide_metadata.html:
                    html_guide_manager.save_guide(guide_soup, guide_metadata, guide_url)
                    constants.force_save_pack(guide_progress_data, *alias_data_list)
                else:
                    guide_data = get_guide_text(guide_soup)
                    guide_data.file_loc = constants.friendly_file_name(
                        os.path.join(guide_metadata.game, guide_metadata.save_title()))
                    print(guide_data.file_loc)
                    guide_progress_data = ds.SaveData(file_loc=game.name,
                                                      blob=guide_step.save_new_completion(),
                                                      old_blob_for_overwrite=guide_step,
                                                      file_type='pickle')
                    constants.force_save_pack(guide_data, guide_progress_data, *alias_data_list)
            game_progress_data = ds.SaveData(file_loc=console.save_loc,
                                             blob=game.save_new_completion(),
                                             old_blob_for_overwrite=game,
                                             file_type='pickle')
            delete_game_name_data = ds.SaveData(file_loc=game.name,
                                                file_type='delete')
            constants.force_save_pack(game_progress_data, delete_game_name_data)

def verify_complete():
    console_steps = create_console_steps(constants.CONSOLE_LINK_LIST_LOC)
    for console in console_steps:
        game_steps = create_game_steps(console.save_loc)
        for game in game_steps:
            if not game.completion:
                return False
    return True


def check_full_progress() -> list[str]:
    str_arr = []
    if not io.pkl_exists(constants.CONSOLE_LINK_LIST_LOC):
        return ['Console Link Save File, doesn\'t exist, not started']
    console_steps = create_console_steps(constants.CONSOLE_LINK_LIST_LOC)
    num_consoles = len(console_steps)
    for console_idx, console in enumerate(console_steps):
        if not io.pkl_exists(console.save_loc):
            continue
        game_steps = io.unpickle(console.save_loc)
        num_games = len(game_steps)
        str_arr.append(f'Console {console_idx} of {num_consoles} ({console.name})')
        for game_idx, game in enumerate(game_steps):
            if game.completion:
                continue
            str_arr.append(f'Game {game_idx} of {num_games} ({game.name})')
            if not io.pkl_exists(game.name):
                str_arr.append(f'Guide 0 of [Unknown]')
                break
            guide_steps = io.unpickle(game.name)
            num_guides = len(guide_steps)
            for guide_idx, guide in enumerate(guide_steps):
                if guide.completion:
                    continue
                str_arr.append(f'Guide {guide_idx} of {num_guides}')
        break
    return str_arr
