import copy


class Save_Name:
    def __init__(self, name):
        self.name = name
        self.completion = False

    def save_new_completion(self, completion_val=True):
        ret_val = copy.deepcopy(self)
        ret_val.completion = completion_val
        return ret_val


class Main_Step(Save_Name):
    def __init__(self, name, run_func, save_loc="", completion=False):
        super().__init__(name)
        self.save_loc = save_loc
        self.run_func = run_func
        self.completion = completion

    def __eq__(self, other):
        if not isinstance(other, Main_Step):
            return NotImplemented
        return self.name == other.name and self.save_loc == other.save_loc  # and self.completion == other.completion

    def __str__(self):
        return "Main Step {0} \n    {1}, {2}, {3}" \
            .format(
                self.name,
                self.run_func,
                self.save_loc if self.save_loc != "" else "No Save Location",
                "Finished" if self.completion else "Incomplete")


class File_Step(Save_Name):
    def __init__(self, name, link, save_loc, completion):
        super().__init__(name)
        self.save_loc = save_loc
        self.link = link
        self.completion = completion

    def __eq__(self, other):
        if not isinstance(other, File_Step):
            return NotImplemented
        return self.name == other.name
            # and self.save_loc == other.save_loc \
            # and self.link == other.link  # and self.completion == other.completion

    def __str__(self):
        return "File Step {0} \n    {1},\n    {2},\n    {3}" \
            .format(self.name, self.save_loc, self.link, "Finished" if self.completion else "Incomplete")


class Link_Step(Save_Name):
    def __init__(self, name, link, completion):
        super().__init__(name)
        self.link = link
        self.completion = completion

    def __eq__(self, other):
        if not isinstance(other, Link_Step):
            return NotImplemented
        return self.name == other.name \
        # and self.link == other.link  # and self.completion == other.completion

    def __str__(self):
        return "Link Step {0} \n    {1}, {2}" \
            .format(self.name, self.link, "Finished" if self.completion else "Incomplete")


class Guide_Data():
    def __init__(self):
        self.title = ''
        self.author = ''
        self.version = ''
        self.year = ''
        self.platform = ''
        self.starred = False
        self.link = ''
        self.html = False

    def save_title(self):
        return '{0}{1} - {2} ({3})' \
            .format('[!] ' if self.starred else '', self.author, self.title, self.platform)

    def __str__(self):
        return '{0} by {1} for {2}, {3}, {4}' \
            .format(self.title, self.author, self.platform, self.version, self.year)

class Save_Data():
    def __init__(self, file_loc = '', blob = None, old_blob = None, isPickle=False):
        self.file_loc = file_loc
        self.isPickle = isPickle
        self.blob = blob
        self.old_blob_for_overwrite = old_blob
        self.__done = False
