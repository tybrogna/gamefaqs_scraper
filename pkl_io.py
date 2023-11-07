import pickle
import os

def overwrite_in_pkl(file_loc, old_data, new_data):
    """
    replaces old_data with new_data in a pickle at file_loc

    :param file_loc: filepath string location of pickle to read
    :param old_data: data in the file to replace
    :param new_data: data going into the file
    """
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

    write_file = open(file_loc, 'wb+')
    for data in file_data:
        pickle.dump(data, file)
    write_file.close()

def append_to_pkl(file_loc, new_data):
    """
    appends data to the end of a file. i feel like i wrote this wrong, but eh

    :param file_loc: filepath string location of pickle to read
    :param new_data: data going into the file
    """
    file_data = []
    read_file = open(file_loc, "rb+")
    while True:
        try:
            file_data.append(pickle.load(read_file))
        except EOFError:
            break
    read_file.close()

    write_file = open(file_loc, "wb+")
    for data in file_data:
        pickle.dump(data, write_file)
    pickle.dump(new_data, write_file)
    write_file.close()

def pkl_contains_name(file_loc, name):
    """
    finds a name in a file. return

    :param file_loc: filepath string location of pickle to read
    :param name: name to find
    :return: object with the corrent name if found, else none
    """
    with open(file_loc, "rb+") as pickin:
        while True:
            try:
                next_line = pickle.load(pickin)
                if next_line.name == name:
                    return next_line
            except EOFError:
                break

def test_print_pkl(file_loc):
    with open(file_loc, "rb+") as pickin:
        pickin.seek(0)
        while True:
            try:
                line_var = pickle.load(pickin)
                print(line_var)
            except EOFError:
                break