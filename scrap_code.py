import pickle
import time
import random
from pathlib import Path

import scraper_io as io
import progress_data_structures as ds
import constants
import get_guides
import html_guide_manager


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
    md.game = 'Bayonetta 2'
    md.author = 'lunacent'
    md.title = 'Guide and Walkthrough'
    md.platform = 'WIIU'
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


def test():
    __save_rdr2()
