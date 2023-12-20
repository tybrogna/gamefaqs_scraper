from atomicwrites import atomic_write as atom
import pickle
import os
import sqlite3

import constants

DATA_FOLDER = './temp_files/'
DATABASE_NAME = 'scraper.db'
CSS_LOC = 'web_files/'
override_folder = ''


def setup(override_loc=''):
    global override_folder
    override_folder = override_loc
    if not override_folder == '' and not override_folder.endswith('/'):
        override_folder = override_folder + '/'
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        print('data folder created')
    if not os.path.exists(DATA_FOLDER + CSS_LOC):
        os.makedirs(DATA_FOLDER + CSS_LOC)


def __create_folder(folder_loc):
    if not os.path.exists(folder_loc):
        os.makedirs(folder_loc)
        return True
    return False


def __save_in_data(file_loc):
    if override_folder != '' and not file_loc.startswith(override_folder):
        file_loc = override_folder + file_loc
    elif not file_loc.startswith(DATA_FOLDER):
        file_loc = DATA_FOLDER + file_loc
    __create_folder(constants.text_before_last_slash(file_loc))
    return file_loc


def __becomes_pickle(file_loc):
    if not file_loc.endswith(".pickle"):
        file_loc = file_loc + ".pickle"
    return file_loc


def create_file(file_loc):
    file_loc = __save_in_data(file_loc)
    if not os.path.exists(file_loc) or os.stat(file_loc).st_size == 0:
        open(file_loc, 'w').close()
        return True
    return False


def create_pkl(file_loc):
    file_loc = __becomes_pickle(file_loc)
    return create_file(file_loc)


def exists(file_loc):
    file_loc = __save_in_data(file_loc)
    if not os.path.exists(file_loc):
        return False
    return True


def pkl_exists(file_loc):
    file_loc = __becomes_pickle(file_loc)
    return exists(file_loc)


def pkl_create_file(file_loc):
    file_loc = __becomes_pickle(file_loc)
    return create_file(file_loc)


def __atomize(file_loc, file_data):
    with atom(file_loc, mode='wb', overwrite=True) as write_file:
        for data in file_data:
            bin_data = pickle.dumps(data)
            write_file.write(bin_data)


def pkl_overwrite(file_loc, old_data, new_data):
    """
    replaces old_data with new_data in a pickle at file_loc

    :param file_loc: filepath string location of pickle to read
    :param old_data: data in the file to replace
    :param new_data: data going into the file
    """
    file_loc = __becomes_pickle(file_loc)
    file_loc = __save_in_data(file_loc)
    file_data = []
    read_file = open(file_loc, "rb+")
    while True:
        try:
            next_line = pickle.load(read_file)
            if next_line == old_data:
                file_data.append(new_data)
            else:
                file_data.append(next_line)
        except EOFError:
            break
    read_file.close()

    __atomize(file_loc, file_data)
    return True

    # with atom(file_loc, mode='wb', overwrite=True) as write_file:
    #     for data in file_data:
    #         bin_data = pickle.dumps(data)
    #         write_file.write(bin_data)
    # return True


def pkl_append_all(file_loc, data_array):
    """
    appends all data in the list to the end of a file. i feel like i wrote this wrong, but eh

    :param file_loc: filepath string location of pickle to read
    :param data_array: array of data to be appended
    """
    file_loc = __becomes_pickle(file_loc)
    file_loc = __save_in_data(file_loc)
    create_file(file_loc)
    file_data = []
    read_file = open(file_loc, "rb+")
    while True:
        try:
            file_data.append(pickle.load(read_file))
        except EOFError:
            break
    read_file.close()
    file_data.extend(data_array)
    __atomize(file_loc, file_data)
    return True

    # with atom(file_loc, mode='wb', overwrite=True) as write_file:
    #     for data in file_data:
    #         bin_data = pickle.dumps(data)
    #         write_file.write(bin_data)
    #     for data in data_array:
    #         bin_data = pickle.dumps(data)
    #         write_file.write(bin_data)
    # return True


def pkl_append(file_loc, new_data):
    """
    appends data to the end of a file. i feel like i wrote this wrong, but eh

    :param file_loc: filepath string location of pickle to read
    :param new_data: data going into the file
    """
    file_loc = __becomes_pickle(file_loc)
    file_loc = __save_in_data(file_loc)
    create_file(file_loc)
    file_data = []
    read_file = open(file_loc, "rb+")
    while True:
        try:
            file_data.append(pickle.load(read_file))
        except EOFError:
            break
    read_file.close()
    file_data.append(new_data)
    __atomize(file_loc, file_data)
    return True

    # with atom(file_loc, mode='wb', overwrite=True) as write_file:
    #     for data in file_data:
    #         bin_data = pickle.dumps(data)
    #         write_file.write(bin_data)
    #     bin_data = pickle.dumps(new_data)
    #     write_file.write(bin_data)
    # return True


def pkl_contains_name(file_loc, name):
    """
    finds a name in a file. return

    :param file_loc: filepath string location of pickle to read
    :param name: name to find
    :return: object with the correct name if found, else none
    """
    file_loc = __becomes_pickle(file_loc)
    file_loc = __save_in_data(file_loc)
    with open(file_loc, "rb+") as pickin:
        while True:
            try:
                next_line = pickle.load(pickin)
                if next_line.name == name:
                    return next_line
            except EOFError:
                break


def unpickle(file_loc):
    file_loc = __becomes_pickle(file_loc)
    file_loc = __save_in_data(file_loc)
    if not os.path.exists(file_loc) or os.stat(file_loc).st_size == 0:
        create_file(file_loc)
        return []
    file_data = []
    read_file = open(file_loc, "rb+")
    while True:
        try:
            file_data.append(pickle.load(read_file))
        except EOFError:
            break
    read_file.close()
    return file_data


def delete(file_loc):
    file_loc = __save_in_data(file_loc)
    if not os.path.exists(file_loc):
        return False
    os.remove(file_loc)
    return True


def pkl_delete(file_loc):
    file_loc = __becomes_pickle(file_loc)
    return delete(file_loc)


def save_text(file_loc, write_obj):
    file_loc = __save_in_data(file_loc)
    if not exists(file_loc):
        create_file(file_loc)
    with atom(file_loc, mode='w', overwrite=True) as write_file:
        for bs in write_obj:
            write_file.write(str(bs))
    return True


def save_img(img_loc, img):
    img_loc = __save_in_data(img_loc)
    if not exists(img_loc):
        if not os.path.exists(img_loc) or os.stat(img_loc).st_size == 0:
            open(img_loc, 'wb').close()
    with atom(img_loc, mode='wb', overwrite=True) as write_file:
        for chunk in img:
            write_file.write(chunk)
    return True


def css_exists(css_file_name):
    if not css_file_name.startswith(CSS_LOC):
        css_file_name = CSS_LOC + css_file_name
    return exists(css_file_name)


def save_css(css_loc: str, css):
    if not css_loc.startswith(CSS_LOC):
        css_loc = CSS_LOC + css_loc
    css_loc = __save_in_data(css_loc)
    create_file(css_loc)
    with atom(css_loc, mode='w', encoding='utf-8', overwrite=True) as write_file:
        write_file.write(css)
    return True


def pkl_test_print(file_loc):
    file_loc = __becomes_pickle(file_loc)
    file_loc = __save_in_data(file_loc)
    with open(file_loc, "rb+") as pickin:
        pickin.seek(0)
        while True:
            try:
                line_var = pickle.load(pickin)
                print(line_var)
            except EOFError:
                break


def test_atomic_write():
    file_loc = "test"
    file_loc = __becomes_pickle(file_loc)
    file_loc = __save_in_data(file_loc)
    garbo1 = ["hey", "yeah", "no"]
    garbo2 = {'dum': 1,'uesless': "two"}
    with atom(file_loc, mode='wb', overwrite=True) as write_file:
        bin_dump = pickle.dumps(garbo1)
        write_file.write(bin_dump)
        bin_dump = pickle.dumps(garbo2)
        write_file.write(bin_dump)
    pkl_test_print(file_loc)


def create_tables(cursor):
    """
    first run, creates tables
    """
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS consoles (
            id integer PRIMARY KEY,
            name text NOT NULL,
            handheld boolean,
            family text
        );
    """)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS console_name (
            console_id integer NOT NULL,
            name text,
            region text,
            FOREIGN KEY (console_id) REFERENCES consoles (id)
        );
    """)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS games (
            id integer PRIMARY KEY,
            console_id integer NOT NULL,
            franchise text,
            developer text,
            publisher text,
            release_date text,
            FOREIGN KEY (console_id) REFERENCES consoles (id)
        );
    """)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS game_name (
            game_id integer NOT NULL,
            console_id integer,
            name text,
            region text,
            FOREIGN KEY (game_id, console_id) REFERENCES games (id, console_id)
        );
    """)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS guides (
            id integer PRIMARY KEY,
            game_id integer,
            author text,
            version text,
            FOREIGN KEY (game_id) REFERENCES games (id)
        );
    """)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS guide_content (
            guide_id integer NOT NULL,
            count integer,
            content text,
            FOREIGN KEY (guide_id) REFERENCES guides (id)
        );
    """)


def test_add_a_console(cursor):
    cursor.execute(
        """
        INSERT INTO consoles (name, handheld, family) 
        VALUES ('Nintendo Entertainment System', false, 'Nintendo');
        """)

    cursor.execute("SELECT * FROM consoles;")

    rows = cursor.fetchall()

    for row in rows:
        print(row[1])


def try_sql():
    sql_loc = "test.db"
    sql_loc = __save_in_data(sql_loc)
    database_connection = sqlite3.connect(sql_loc)
    cursor = database_connection.cursor()
    # sql.create_tables(cursor)
    # sql.add_a_console(cursor)
