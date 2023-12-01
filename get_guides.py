import copy

import pkl_io as io
import constants
import progress_data_structures as ds
from bs4 import Tag


def create_console_steps(consoles_loc):
    steps = []
    console_link_steps = io.unpickle(consoles_loc)
    for console in console_link_steps:
        # if test:
        #     print("get_game_links.py - adding {0} to steps".format(console.name))
        steps.append(ds.File_Step(console.name, console.link, "{0}_game_list".format(console.name), console.completion))
    return steps


def create_game_steps(game_list_loc):
    steps = []
    game_link_steps = io.unpickle(game_list_loc)
    for game in game_link_steps:
        # print(game)
        steps.append(ds.File_Step(game.name, game.link, game.name + '/', game.completion))
    return steps


def get_all_guide_links(page_soup):
    guide_links = page_soup.select('.gf_guides a.bold')
    if len(guide_links) < 0:
        return
    return guide_links


def get_guide_metadata(page_soup):
    guide_metadata = ds.Guide_Data()
    title_and_author = page_soup.select_one('div.ffaq h2').get_text()
    ver_and_date = page_soup.select_one('div.ffaq p').get_text()
    tnp = title_and_author[:title_and_author.rindex(' by ')]
    guide_metadata.platform = tnp[tnp.rindex('(') + 1:tnp.rindex(')')]
    guide_metadata.title = tnp[:tnp.rindex(' (')]
    guide_metadata.author = title_and_author[title_and_author.rindex(' by ') + 4:]
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


def get_alias_save_data(alias):
    alias_no_slash = alias[1:]
    alias_console = alias_no_slash[:alias_no_slash.index('/')]
    alias_link = alias_no_slash[alias_no_slash.index('/') + 1:]
    print(alias_console)
    alias_game_id = alias_no_slash[alias_no_slash.index('/') + 1:alias_no_slash.index('-')]
    id_found = io.pkl_contains_name('{0}_game_list'.format(alias_console), alias_game_id)
    if id_found:
        old_step = ds.Link_Step(alias_game_id, alias_link, False)
        new_step = ds.Link_Step(alias_game_id, alias_link, True)
        alias_save_data = ['{0}_game_list'.format(alias_console), old_step, new_step]
        return alias_save_data
    return None


def get_guide_text(page_soup):
    guide_text = page_soup.select('#faqtext pre')
    if len(guide_text) > 1:
        guide_text_list = []
        for gt in guide_text:
            guide_text_list.append(guide_text.contents)
        return guide_text_list
    else:
        return guide_text.contents[0]


def create_dl_steps(game_id, guide_links):
    if io.exists(game_id):
        return io.unpickle(game_id)
    guide_dl_steps = []
    for guide_link in guide_links:
        href = guide_link['href']
        gl_name = href[href.rindex('/') + 1:]
        guide_dl_steps.append(ds.Link_Step(gl_name, href, False))
    io.append_all_to_pkl(game_id, guide_dl_steps)
    return guide_dl_steps


def test_run():
    console_test = create_console_steps(constants.CONSOLE_LINK_LIST_LOC)[0]
    print(console_test)
    game_test = create_game_steps(console_test.save_loc)[0]
    print(game_test)
    input("Press Enter to continue...")
    game_test_URL = constants.URL_gamefaqs + '/x/' + game_test.link + 'faqs'
    soup_test = constants.heat_soup(game_test_URL)
    alias_url_list = get_game_aliases(soup_test)
    input("Press Enter to continue...")
    test_guide_links = get_all_guide_links(soup_test)
    game_id = game_test.name
    if '/' in game_id:
        game_id = game_id.replace('/', '')
    guide_dl_steps = create_dl_steps(game_id, test_guide_links)
    for dls in guide_dl_steps:
        print(dls)
    input("Press Enter to continue...")
    guide_url_test = constants.URL_gamefaqs + guide_dl_steps[0].link
    guide_url_test_soup = constants.heat_soup(guide_url_test)
    guide_metadata = get_guide_metadata(guide_url_test_soup)
    guide_text = get_guide_text(guide_url_test_soup)
    guide_save_data = [guide_metadata.save_title(), guide_text]
    print(guide_save_data[0])
    updated_step = copy.deepcopy(guide_dl_steps[0])
    updated_step.completion = True
    guide_progress_data = [game_id, guide_dl_steps[0], updated_step]
    alias_save_data_list = []
    for alias in alias_url_list:
        alias_sd = get_alias_save_data(alias)
        if alias_sd is not None:
            alias_save_data_list.append(alias_sd)
    input("Press Enter to continue...")
    constants.force_save()
    guide_dl_progress_loc = console_test.name + '-' + game_test.name
    #save guide text
    #mark alias as complete
    #mark game as complete


def run():
    console_steps = create_console_steps(constants.CONSOLE_LINK_LIST_LOC)
    for console in console_steps:
        game_steps = create_game_steps(console.save_loc)
        for game in game_steps:
            if game.completion:
                continue
            game_URL = constants.URL_gamefaqs + '/x/' + game.link + 'faqs'
            game_soup = constants.heat_soup(game_URL)
            alias_URL_list = get_game_aliases(game_soup)
            guide_links_list = get_all_guide_links(game_soup)
            guide_dl_steps = create_dl_steps(game.name, guide_links_list)
            for guide in guide_dl_steps:
                guide_url = constants.URL_gamefaqs + guide.link
                guide_soup = constants.heat_soup(guide_url)
                guide_metadata = get_guide_metadata(guide_soup)
                guide_text = get_guide_text(guide_soup)
                guide_SD = [guide_metadata.save_title(), guide_text]
