import copy

import html_guide_manager
import scraper_io as io
import constants
import progress_data_structures as ds
from bs4 import BeautifulSoup

type LinkStepList = list[ds.Link_Step]
type Save_Pack = list[ds.Save_Data]


def create_console_steps(consoles_loc):
    steps = []
    console_link_steps = io.unpickle(consoles_loc)
    for console in console_link_steps:
        steps.append(ds.File_Step(console.name, console.link, "{0}_game_list".format(console.name), console.completion))
    return steps


def create_game_steps(game_list_loc):
    steps = []
    game_link_steps = io.unpickle(game_list_loc)
    for game in game_link_steps:
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
    if page_soup.select_one('#faqwrap .ftoc a') is not None:
        guide_metadata.html = True
    return guide_metadata


def get_game_aliases(page_soup):
    alias_url_list = []
    alias_links = page_soup.select('#header_more_menu a')
    for alias in alias_links:
        alias_url_list.append(alias['href'])
    return alias_url_list


def create_alias_save_data(alias_URL_list):
    alias_SD_list = []
    for alias in alias_URL_list:
        alias_no_slash = alias[1:]
        alias_console = alias_no_slash[:alias_no_slash.index('/')]
        alias_link = alias_no_slash[alias_no_slash.index('/') + 1:]
        print(alias_console)
        alias_game_id = alias_no_slash[alias_no_slash.index('/') + 1:alias_no_slash.index('-')]
        id_found = io.pkl_contains_name('{0}_game_list'.format(alias_console), alias_game_id)
        if id_found:
            file_loc = '{0}_game_list'.format(alias_console)
            old_step = ds.Link_Step(alias_game_id, alias_link, False)
            new_step = ds.Link_Step(alias_game_id, alias_link, True)
            alias_SD = ds.Save_Data(file_loc, new_step, old_step, True)
            alias_SD_list.append(alias_SD)
    return alias_SD_list


def get_guide_text(page_soup):
    guide_text = page_soup.select('#faqtext pre')
    guide_text_list = []
    if guide_text is not None:
        for gt in guide_text:
            guide_text_list.append(gt.contents)
    new_save = ds.Save_Data()
    new_save.blob = guide_text_list
    return new_save


# def get_guide_html(page_soup, base_url) -> Save_Pack:
#     guide_save_pack = []
#     toc_link_list = page_soup.select('#faqwrap .ftoc a')
#     page_content = page_soup.select_one('#faqwrap')
#     html_strs = []
#     html_strs.append('<!DOCTYPE html>')
#     css_name = get_css_name(page_soup)
#     if not io.css_exists(css_name):
#         guide_save_pack.append(create_css_save_data(page_soup))
#     html_strs.append('<link id="core_css" href="../../{0}{1}" rel="stylesheet" type="text/css">'
#                      .format(io.CSS_LOC, css_name))
#     html_strs.append('<div class="container">')
#     html_strs.append('<div id="faqwrap" class="ffaq ffaqbody">')
#     html_strs.append(page_content)
#     html_strs.append('</div')
#     html_strs.append('</div>')
#     page_title = toc_link_list[0]
#     new_save = ds.Save_Data(page_title, html_strs)
#     guide_save_pack.append(new_save)
#     for toc_name in toc_link_list[1:]:
#         img_list = []
#         html_strs = []
#         page_url = base_url + '/' + toc_name
#         page_soup = constants.heat_soup(page_url)
#         page_content = page_soup.select_one('#faqwrap')
#         if constants.DL_IMAGES:
#             pic_names = map(lambda a: a['src'], page_content.select("img"))
#             pic_links = map(lambda a: constants.URL_gamefaqs + '/' + a['src'], page_content.select("img"))
#             for img, name in zip(page_content.select("img"), pic_names):
#                 img['src'] = './img' + name
#             # img_list
#         html_strs.append('!<DOCTYPE html>')
#         html_strs.append('<link id="core_css" href="../../{0}{1}" rel="stylesheet" type="text/css">'
#                          .format(io.CSS_LOC, css_name))
#         html_strs.append('<div class="container">')
#         html_strs.append('<div id="faqwrap" class="ffaq ffaqbody">')
#         html_strs.append(page_content)
#         html_strs.append('</div')
#         html_strs.append('</div>')
#         new_save = ds.Save_Data(toc_name, html_strs)
#         guide_save_pack.append(new_save)
#     return guide_save_pack


def create_dl_steps(game_id, guide_links) -> list[ds.Link_Step]:
    if io.exists(game_id):
        return io.unpickle(game_id)
    guide_dl_steps = []
    for guide_link in guide_links:
        href = guide_link['href']
        gl_name = href[href.rindex('/') + 1:]
        guide_dl_steps.append(ds.Link_Step(gl_name, href, False))
    io.pkl_append_all(game_id, guide_dl_steps)
    return guide_dl_steps


# def get_css_name(soup) -> str:
#     tag = soup.select_one("link#core_css")
#     return constants.text_after_last_slash(tag['href'])

# def create_css_save_data(soup) -> ds.Save_Data:
#     tag = soup.select_one("link#core_css")
#     css_name = constants.text_after_last_slash(tag['href'])
#     linked_url = constants.URL_gamefaqs + constants.URL_css + '/' + css_name
#     css_sd = ds.Save_Data(css_name)
#     css_sd.blob = constants.url_request_blob(linked_url).text
#     css_sd.file_type = 'css'
#     return css_sd


def test_link():
    tg = open('./temp_files/tg.htm', 'r')
    soup = BeautifulSoup(tg, "html.parser")
    guide_metadata = get_guide_metadata(soup)
    html_guide_manager.create_save_data(soup, guide_metadata, 'url')
    print('donzo')
    input("press enter to continue...")
    return ''


def good_shit():
    # tg = open('./temp_files/tg.htm', 'r')
    # soup = BeautifulSoup(tg, "html.parser")
    base_url = 'https://gamefaqs.gamespot.com/ps4/200179-red-dead-redemption-2/faqs/76594'
    soup = constants.heat_soup(base_url)
    metadata = get_guide_metadata(soup)
    metadata.game = "Red Ded Redemption 2"
    html_guide_manager.create_save_data(soup, metadata, base_url)


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
            game_url = constants.URL_gamefaqs + '/x/' + game.link + 'faqs'
            game_soup = constants.heat_soup(game_url)
            alias_url_list = get_game_aliases(game_soup)
            guide_links_list = get_all_guide_links(game_soup)
            guide_dl_steps = create_dl_steps(game.name, guide_links_list)
            for guide in guide_dl_steps:
                guide_url = constants.URL_gamefaqs + guide.link
                guide_soup = constants.heat_soup(guide_url)
                is_guide = guide_soup.select_one('div.ffaq') is not None
                if not is_guide:
                    guide_progress_data = ds.Save_Data(game.name, guide.save_new_completion(), guide, True)
                    constants.force_save_pack(guide_progress_data)
                    continue
                guide_metadata = get_guide_metadata(guide_soup)
                guide_metadata.game = game.name
                alias_data_list = create_alias_save_data(alias_url_list)
                guide_progress_data = ds.Save_Data(game.name, guide.save_new_completion(), guide, True)
                if guide_metadata.html:
                    html_guide_manager.create_save_data(guide_soup, guide_metadata, guide_url)
                    constants.force_save_pack(guide_progress_data, *alias_data_list)
                else:
                    guide_data = get_guide_text(guide_soup)
                    guide_data.file_loc = guide_metadata.save_title()
                    guide_progress_data = ds.Save_Data(game.name, guide.save_new_completion(), guide, True)
                    # guide_progress_data = ds.Save_Data(game.name)
                    # guide_progress_data.blob = guide.save_new_completion()
                    # guide_progress_data.old_blob_for_overwrite = guide
                    # guide_progress_data = [game.name, guide, guide.save_new_completion()]
                    constants.force_save_pack(guide_data, guide_progress_data, *alias_data_list)

                    # guide_text = get_guide_text(guide_soup)
                    # guide_SD = [guide_metadata.save_title(), guide_text]
                    # guide_progress_SD = [game.name, guide, guide.save_new_completion()]
                    # constants.force_save(guide_SD, guide_progress_SD, *alias_SD_list)
