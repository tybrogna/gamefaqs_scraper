import pkl_io as io
import constants
import progress_data_structures as ds


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
        steps.append(ds.File_Step(game.name, game.link, game.name + '/', game.completion))
    return steps


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


def get_guide_text(page_soup):
    guide_text = page_soup.select('#faqtext pre')
    print(guide_text[0].contents[0])


def create_dl_steps(game_name, guide_links):
    for guide in guide_links:

        ds.File_Step(ds.File_Step())
        io.append_to_pkl(constants.DL_STEP_TEMP_LOC)
    io.append_to_pkl(constants.DL_STEP_TEMP_LOC, 'check off dupes')


def test_run():
    console_test = create_console_steps(constants.CONSOLE_LINK_LIST_LOC)[0]
    game_test = create_game_steps(console_test.save_loc)[0]
    game_test_URL = constants.URL_gamefaqs + '/x/' + game_test.link + 'faqs'
    print(game_test_URL)
    soup_test = constants.heat_soup(game_test_URL)
    alias_url_list = get_game_aliases(soup_test)
    test_guide_links = get_all_guide_links(soup_test)
    guide_url_test = constants.URL_gamefaqs + test_guide_links[0]['href']
    guide_url_test_soup = constants.heat_soup(guide_url_test)
    get_guide_text(guide_url_test_soup)


def run():
    console_steps = create_console_steps(constants.CONSOLE_LINK_LIST_LOC)
    for console in console_steps:
        game_steps = create_game_steps(console.save_loc)
        for game in game_steps:
            if game.completion:
                continue
            # get all guides on the page
            game_step_URL = constants.URL_gamefaqs + '/x/' + game.link + 'faqs'
            print(game_step_URL)
            # page_soup = constants.heat_soup(game_step_URL)
            # ----------------------------------------------
            # guide_links = get_all_guide_links(page_soup)
            # create File_Steps for each guide on the page, with a special final for checking off dupes
            # guide_steps = create_dl_steps(game.name, guide_links)
            # for guide in guide_steps:
            #     break
                # guide_link = guide.save_lo
                # guide_soup = heat_soup(guide.)
                # author = 
                # guide_file_loc = '{0} - {1} - {2}'.format(game.name, )

            # download them all (parallel? gotta watch my bandwith ;) ), check complete as you go
            # check game as complete
            # check each alternate version as complete in the respective console file
            # mark initial File_Step as complete
        return
