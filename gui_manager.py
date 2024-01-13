import tkinter
import tkinter as tk_base
from tkinter import filedialog
import typing
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import os


class Gui(tk_base.Tk):
    def __init__(self):
        super().__init__()
        self.display_box: ScrolledText = None
        self.save_loc: ttk.Entry = None
        self.save_loc_button: ttk.Button = None
        self.check_progress_button: ttk.Button = None
        self.start_button: ttk.Button = None
        self.interrupt_button: ttk.Button = None
        self.silent = False
        self.test = False

    def setup(self, check_func, start_func, interrupt_func):
        self.title('Gamefaqs Scraper')
        window_width = 600
        window_height = 500
        self.minsize(window_width, window_height)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.__frame_scrollbox()
        ttk.Separator(self, orient='horizontal').pack(fill='x')
        self.__grid_options(check_func, start_func, interrupt_func)

    def add_button(self, name: str, target_func: typing.Callable):
        btn = ttk.Button(self, text=name, command=target_func)
        btn.pack()

    def __grid_options(self, check_func, start_func, interrupt_func):
        frame = ttk.Frame(self)
        frame.rowconfigure(0)
        frame.rowconfigure(1)
        frame.columnconfigure(0)
        frame.columnconfigure(1, weight=3)
        frame.columnconfigure(2)
        frame.columnconfigure(3)
        self.check_progress_button = ttk.Button(frame, text='Check Progress', command=check_func)
        self.check_progress_button.grid(row=0, column=0, padx=10, sticky=tk_base.W)
        self.start_button = ttk.Button(frame, text='Start Scraper', command=start_func)
        self.start_button.grid(row=1, column=0, padx=10, sticky=tk_base.W)
        ttk.Label(frame, text='save location').grid(row=0, column=1, ipadx=1, sticky=tk_base.E)
        self.save_loc = ttk.Entry(frame)
        self.save_loc.insert(0, os.path.join(os.path.abspath('/'), 'gamefaqs_data'))
        self.save_loc.grid(row=0, column=2, padx=10, sticky=tk_base.EW)
        self.save_loc_button = ttk.Button(frame, text='select save location', command=lambda: self.get_save_folder(self.save_loc))
        self.save_loc_button.grid(row=0, column=3, padx=1, sticky=tk_base.EW)
        self.interrupt_button = ttk.Button(frame, text='Stop', command=interrupt_func)
        self.interrupt_button.grid(row=1, column=3, padx=1, sticky=tk_base.E)
        frame.pack(fill=tk_base.BOTH)

    def get_save_folder(self, save_loc_entry: ttk.Entry):
        save_loc_entry.delete(0, 999)
        loc = filedialog.askdirectory()
        if loc:
            save_loc_entry.insert(0, loc)

    def __frame_scrollbox(self):
        frame = ttk.Frame(self)
        frame['padding'] = (10,10,10,10)
        ttk.Label(frame, text='Scraping Info').pack()
        self.display_box = ScrolledText(frame, width=10, height=22)
        self.display_box.pack(fill=tk_base.BOTH, side=tk_base.LEFT, expand=True)
        frame.pack(fill=tk_base.BOTH)

    def display(self, *strs):
        if self.silent:
            return
        for s in strs:
            if self.test:
                print(s)
            self.display_box.insert(tk_base.INSERT, s)
            self.display_box.insert(tk_base.INSERT, '\n')
        self.display_box.see(tk_base.END)

    def enable_buttons(self):
        self.start_button['state'] = 'normal'
        self.check_progress_button['state'] = 'normal'

    def disable_buttons(self):
        self.start_button['state'] = 'disabled'
        self.check_progress_button['state'] = 'disabled'


def create_scrollbox(gui: tk_base.Tk) -> None:
    st = ScrolledText(gui, width=50, height=10)
    st.pack(fill=tk_base.BOTH, side=tk_base.LEFT, expand=True)
