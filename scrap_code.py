import pickle
import time
import random
from pathlib import Path

import scraper_io as io
import progress_data_structures as ds
import constants
import get_guides
import html_guide_manager

scrap_path = Path('D:\\gamefaqs', 'scrap_code')

def __html_guides():
    io.setup('D:\\gamefaqs')
    get_guides.test_html_guide()


def __print_pkls():
    io.pkl_test_print('D:\\gamefaqs\\progress')
    io.pkl_test_print('D:\\gamefaqs\\wii-u_game_list')
    io.pkl_test_print('D:\\gamefaqs\\wii-u_game_list')


def __friendly_filename():
    print(constants.friendly_file_name('//se34fonl00-=:sle'))
    print(constants.friendly_file_name('//se34fonl00-=:sle', '/sefs\\skseu', '*sefse*:yyjur/:'))


def __adjust_links():
    io.setup('D:\\gamefaqs')
    md = ds.GuideMetadata()
    md.game = '3D Ecco the Dolphin'
    md.author = 'NeonFXx'
    md.title = 'Guide and Walkthrough'
    md.platform = 'GEN'
    md.starred = True
    html_guide_manager.__adjust_link_locations(md)


def __pagination():
    soup = constants.heat_soup('https://gamefaqs.gamespot.com/wii-u/683293-bayonetta-2/faqs/70436')
    # soup = constants.heat_soup('https://gamefaqs.gamespot.com/pc/666045-the-amazing-spider-man/faqs/64576')
    for li in soup.select_one('ul.paginate').select('a'):
        for s in li.strings:
            if "next page" in str.lower(s):
                print(li['href'])
    toc_list = soup.select('#faqwrap .ftoc a')
    for idx, page_title in enumerate(toc_list):
        print(f'{idx} {constants.friendly_file_name(page_title.text)}')
    # all_txt = soup.select_one('.paginate li').text
    # final_pg = all_txt[all_txt.rindex(' '):].strip()
    # print(final_pg)


def __save_bayo2():
    io.setup('D:\\gamefaqs')
    base_url = 'https://gamefaqs.gamespot.com/wii-u/683293-bayonetta-2/faqs/70436'
    soup = constants.heat_soup(base_url)
    md = ds.GuideMetadata()
    md.game = 'Bayonetta 2'
    md.author = 'lunacent'
    md.title = 'Guide and Walkthrough'
    md.platform = 'WIIU'
    md.paginated = True
    md.num_pages = 42
    html_guide_manager.save_guide(soup,
                                  guide_metadata=md,
                                  base_url=base_url)


def __save_rdr2():
    io.setup('D:\\gamefaqs')
    base_url = 'https://gamefaqs.gamespot.com/xboxone/200180-red-dead-redemption-2/faqs/76594'
    soup = constants.heat_soup(base_url)
    md = ds.GuideMetadata()
    md.game = 'Red Dead Redemption 2'
    md.author = 'Suprak_the_stud'
    md.title = 'Guide and Walkthrough'
    md.platform = 'XONE'
    html_guide_manager.save_guide(soup,
                                  guide_metadata=md,
                                  base_url=base_url)


def __save_amazing_spider_man():
    io.setup('D:\\gamefaqs')
    base_url = 'https://gamefaqs.gamespot.com/x/666045-the-amazing-spider-man/faqs/64576'
    soup = constants.heat_soup(base_url)
    md = ds.GuideMetadata()
    md.game = 'The Amazing Spider-Man'
    md.author = 'ExtremePhobia'
    md.title = 'Guide and Walkthrough'
    md.platform = 'X360'
    md.paginated = True
    md.num_pages = 2
    html_guide_manager.save_guide(soup,
                                  guide_metadata=md,
                                  base_url=base_url)


def __save_rando_html_guide():
    io.setup('D:\\gamefaqs')
    base_url = 'https://gamefaqs.gamespot.com/3ds/719937-3d-ecco-the-dolphin/faqs/74701'
    soup = constants.heat_soup(base_url)
    md = ds.GuideMetadata()
    md.game = '3D Ecco the Dolphin'
    md.author = 'NeonFXx'
    md.title = 'Guide and Walkthrough'
    md.platform = 'GEN'
    md.paginated = True
    md.num_pages = 2
    html_guide_manager.save_guide(soup,
                                  guide_metadata=md,
                                  base_url=base_url)



def __multi_ital():
    soup = constants.heat_soup('https://gamefaqs.gamespot.com/3ds/632672-3d-classics-excitebike/faqs')
    guide_squares = soup.select('.gf_guides li')
    if len(guide_squares) <= 0:
        return
    for square in guide_squares:
        ital_eles = square.select('.ital')
        for ele in ital_eles:
            for ital in ele.strings:
                print(ital.strip())


def __get_guide_text():
    soup = constants.heat_soup('https://gamefaqs.gamespot.com/3ds/716473-3d-altered-beast/faqs/60260')
    guide_text_elements = soup.select('#faqtext pre')
    if guide_text_elements is not None:
        guide_text = ''.join([ele.string for ele in guide_text_elements])
        guide_text = guide_text.replace('\r', '')
        # for gt in guide_text:
        #     guide_text_list.append(gt.contents)
        new_save = ds.SaveData(file_loc=scrap_path, blob=guide_text, file_type='text')
        constants.force_save_pack(new_save)


def __save_map():
    soup = constants.heat_soup('https://gamefaqs.gamespot.com/3ds/647587-3d-classics-kid-icarus/map/126-labyrinth-map-1')
    img_src = constants.URL_gamefaqs + soup.select_one('#gf_map')['src']
    if img_src is None:
        return None
    guide_data = ds.SaveData(file_loc=scrap_path,
                             blob=constants.url_request_blob(img_src),
                             file_type='image')
    constants.force_save_pack(guide_data)


def __save_efficiency_test():
    nl = [''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5)) for n in range(100000)]
    locl = ['C:\\'.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8)) for n in range(100000)]
    linl = ['https://www.'.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=35)).join('.com') for n in range(100000)]
    sl = []
    st = time.time()
    for x in range(100000):
        sl.append(ds.FileStep(name=nl[x], link=linl[x], save_loc=locl[x]))
    print("--- %s seconds ---" % (time.time() - st))
    save_data = ds.SaveData(file_type='pickle',
                            file_loc=constants.CONSOLE_LINK_LIST_LOC,
                            blob='hehe',)
    print(save_data)


from atomicwrites import atomic_write as atom
def __save_unicode():
    io.setup('D:\\gamefaqs')
    f_name = io.__save_in_data('unicode_temp')
    pd = '√'.encode()
    # print(pd)
    so = pd.decode()
    # print(so)
    with atom(f_name, mode='w', encoding='utf-8', overwrite=True) as a:
        # a.write(pd)
        a.write('√')
    with open(f_name, encoding='utf-8', mode='r') as b:
        b.seek(0)
        print(b.readline())

DATA_FOLDER = Path('')
def __new_path():
    global DATA_FOLDER
    DF = Path('D:\\gamefaqs', 'another') / 'more'
    tf = Path(DF, 'file.txt')
    if not Path.exists(tf):
        if not Path.exists(tf.parent):
            Path.mkdir(tf.parent, parents=True)
        Path.touch(tf)
    pl = 'bumbbo'
    cv = Path(pl)
    if not cv.is_relative_to(DF):
        cv = DF / cv
    print(str(cv))
    if not cv.suffix == '.pickle':
        cv = cv.with_suffix('.pickle')
    with atom(cv, mode='wb', overwrite=True) as wf:
        wf.write(pickle.dumps('haheyehfeyhhs'))
    print(str(cv))


def __skip_none_efficiency():
    big_lists = []
    small_lists = []
    for a in range(100):
        big_lists.append([val for val in range(100000)])
        small_lists.append([val for val in range(6)])
    for big in big_lists:
        rand_big_replace: list[int] = [random.randrange(0, 100000) for val in range(10000)]
        for val in rand_big_replace:
            big[val] = None
    for small in small_lists:
        rand_small_replace: list[int] = [random.randrange(0,6), random.randrange(0,6)]
        for val in rand_small_replace:
            small[val] = None
    temp = 0
    st = time.time()
    for big in big_lists:
        for val in big:
            if val is None:
                continue
            temp = val / 2
            temp = temp / 4
            temp = temp / 8
    print(f'big lists continue method: {time.time() - st}')
    st = time.time()
    for big in big_lists:
        for val in filter(None, big):
            temp = val / 2
            temp = temp / 4
            temp = temp / 8
    print(f'big lists filter method: {time.time() - st}')
    st = time.time()
    for small in small_lists:
        for val in small:
            if val is None:
                continue
            temp = val / 2
            temp = temp / 4
            temp = temp / 8
    print(f'small lists continue method: {time.time() - st}')
    st = time.time()
    for small in small_lists:
        for val in filter(None, small):
            temp = val / 2
            temp = temp / 4
            temp = temp / 8
    print(f'small lists filter method: {time.time() - st}')
    # records
    # big continue: [1.095, 1.092, 1.137, 1.090, 1.085] avg = 1.100
    # big filter: [1.181, 1.106, 1.164. 1.109, 1.125] avg = 1.137
    # small continue: [0.000, 0.001, 0.000, 0.000, 0.000] avg = 0
    # small filter: [0.000, 0.000, 0.000, 0.000, 0.000] avg = 0


def __undo_last_failure():
    io.setup(Path('D:\\gamefaqs'))
    console_list = io.unpickle(constants.CONSOLE_LINK_FOR_GUIDES)
    for console in console_list:
        if console.completion:
            continue
        print(console)
        break
    tds_steps = io.unpickle('3ds_game_list')
    for fs in tds_steps:
        if fs.completion:
            continue
        print(fs)
        io.pkl_test_print('3d Neo_html_steps')
        break


def test():
    __save_map()
