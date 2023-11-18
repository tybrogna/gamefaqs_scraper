from atomicwrites import atomic_write as atom
import pickle
import os

DATA_FOLDER = './data/'
override_folder = ''


def __save_in_data(file_loc):
    if override_folder != '' and not file_loc.startswith(override_folder):
        file_loc = override_folder + file_loc
    elif not file_loc.startswith(DATA_FOLDER):
        file_loc = DATA_FOLDER + file_loc
    return file_loc


def __becomes_pickle(file_loc):
    if not file_loc.endswith(".pickle"):
        file_loc = file_loc + ".pickle"
    return file_loc


def setup():
    global override_folder
    if not override_folder == '' and not override_folder.endswith('/'):
        override_folder = override_folder + '/'
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        print('data folder created')


def exists(file_loc):
    file_loc = __becomes_pickle(file_loc)
    file_loc = __save_in_data(file_loc)
    if not os.path.exists(file_loc):
        return False
    return True


def create_file(file_loc):
    file_loc = __becomes_pickle(file_loc)
    file_loc = __save_in_data(file_loc)
    if not os.path.exists(file_loc) or os.stat(file_loc).st_size == 0:
        open(file_loc, 'w').close()
        return True
    return False


def create_folder(folder_loc):
    folder_loc = __save_in_data(folder_loc)
    if not os.path.exists(folder_loc):
        os.makedirs(folder_loc)
        return True
    return False


def overwrite_in_pkl(file_loc, old_data, new_data):
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

    with atom(file_loc, mode='wb', overwrite=True) as write_file:
        for data in file_data:
            bin_data = pickle.dumps(data)
            write_file.write(bin_data)

    # write_file = open(file_loc, 'wb+')
    # for data in file_data:
    #     pickle.dump(data, write_file)
    # write_file.close()


def append_all_to_pkl(file_loc, data_array):
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

    with atom(file_loc, mode='wb', overwrite=True) as write_file:
        for data in file_data:
            bin_data = pickle.dumps(data)
            write_file.write(bin_data)
        for data in data_array:
            bin_data = pickle.dumps(data)
            write_file.write(bin_data)

    # write_file = open(file_loc, "wb+")
    # for data in file_data:
    #     pickle.dump(data, write_file)
    # for data in data_array:
    #     pickle.dump(data, write_file)
    # write_file.close()
    return True


def append_to_pkl(file_loc, new_data):
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

    with atom(file_loc, mode='wb', overwrite=True) as write_file:
        for data in file_data:
            bin_data = pickle.dumps(data)
            write_file.write(bin_data)
        bin_data = pickle.dumps(new_data)
        write_file.write(bin_data)
    return True
    # write_file = open(file_loc, "wb+")
    # for data in file_data:
    #     pickle.dump(data, write_file)
    # pickle.dump(new_data, write_file)
    # write_file.close()


def pkl_contains_name(file_loc, name):
    """
    finds a name in a file. return

    :param file_loc: filepath string location of pickle to read
    :param name: name to find
    :return: object with the corrent name if found, else none
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


def delete_pkl(file_loc):
    file_loc = __becomes_pickle(file_loc)
    file_loc = __save_in_data(file_loc)
    if not os.path.exists(file_loc):
        return False
    os.remove(file_loc)
    return True


def test_print_pkl(file_loc):
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
    garbo1 = ["hey","yeah","no"]
    garbo2 = {'dum':1,'uesless':"two"}
    with atom(file_loc, mode='wb', overwrite=True) as write_file:
        bin_dump = pickle.dumps(garbo1)
        write_file.write(bin_dump)
        bin_dump = pickle.dumps(garbo2)
        write_file.write(bin_dump)

    test_print_pkl(file_loc)
    # write_file.close()
