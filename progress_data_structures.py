import copy
import types

import constants
import scraper_io as io


class SaveName:
    def __init__(self, name):
        self.name = name
        self.completion = False

    def save_new_completion(self, completion_val=True):
        ret_val = copy.deepcopy(self)
        ret_val.completion = completion_val
        return ret_val


class MainStep(SaveName):
    def __init__(self, name, completion=False):
        super().__init__(name)
        # self.save_loc: str = save_loc
        self.completion: bool = completion

    def __eq__(self, other) -> bool:
        if not isinstance(other, MainStep):
            return NotImplemented
        return self.name == other.name #and self.save_loc == other.save_loc  # and self.completion == other.completion

    def __str__(self) -> str:
        return "Main Step {0} \n    {1}" \
            .format(
                self.name,
                # self.save_loc if self.save_loc != "" else "No Save Location",
                "Finished" if self.completion else "Incomplete")


class FileStep(SaveName):
    """
    :param name: str. unique identifier, unchecked.
    :param save_loc: str. file location associated with this step
    :param link: str. URL associated with this step
    :param completion: bool. step progress flag
    """
    def __init__(self, name, save_loc='', link='', completion=False):
        super().__init__(name)
        self.save_loc: str = save_loc
        self.link: str = link
        self.completion: bool = completion

    def __eq__(self, other):
        if not isinstance(other, FileStep):
            return NotImplemented
        return self.name == other.name

    def __str__(self):
        return f"File Step {self.name} \n    {self.save_loc},\n    {self.link},\n    {"Finished" if self.completion else "Incomplete"}"


class LinkStep(SaveName):
    """
    :param name: str. unique identifier, unchecked.
    :param link: str. URL associated with this step
    :param completion: bool. step progress flag
    """
    def __init__(self, name, link='', completion=False):
        super().__init__(name)
        self.link: str = link
        self.completion: bool = completion

    def __eq__(self, other):
        if not isinstance(other, LinkStep):
            return NotImplemented
        return self.name == other.name \
        # and self.link == other.link  # and self.completion == other.completion

    def __str__(self):
        return f'Link Step {self.name} \n    {self.link}, {"Finished" if self.completion else "Incomplete"}'


class NamedNumber:
    def __init__(self, name, data=0):
        self.name = name
        self.data = data

    def __eq__(self, other):
        if not isinstance(other, LinkStep):
            return NotImplemented
        return self.name == other.name


class GuideMetadata:
    def __init__(self):
        self.game = ''
        self.title = ''
        self.author = ''
        self.version = ''
        self.year = ''
        self.platform = ''
        self.starred = False
        self.link = ''
        self.html = False

    def save_title(self):
        star_ornament = '[!] ' if self.starred else ''
        return f'{star_ornament}{self.author} - {self.title} ({self.platform})'

    def __str__(self):
        return f'{self.title} by {self.author} for {self.platform}, {self.version}, {self.year}'


class PageMetadata:
    def __init__(self, game, file_save_path='', image_save_path=''):
        self.game = game
        self.file_save_path = ''
        self.image_save_path = ''


class SaveData:
    def __init__(self, file_loc='', blob=None, old_blob_for_overwrite=None, file_type='text'):
        self.file_loc: str = file_loc
        self.file_type: str = file_type
        self.blob = blob
        self.old_blob_for_overwrite = old_blob_for_overwrite
        self.__done = False

    def __str__(self):
        return f'{self.file_type} save pack \n  {self.file_loc}'
