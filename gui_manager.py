import tkinter
import tkinter as tk_base
from tkinter import filedialog
import typing
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


class Gui(tk_base.Tk):
    def __init__(self):
        super().__init__()
        self.frames: dict = {}
        self.widgets: dict = {}
        self.save_loc = tk_base.StringVar()

    def setup(self):
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
        self.__grid_options()

    def add_button(self, name: str, target_func: typing.Callable):
        btn = ttk.Button(self, text=name, command=target_func)
        btn.pack()

    def add_label(self, text: str):
        ttk.Label(self, text=text).pack()

    def add_entry(self, target_var: tk_base.StringVar):
        ttk.Entry(self, textvariable=target_var).pack()

    def __grid_options(self):
        frame = ttk.Frame(self)
        # frame['borderwidth'] = 6
        # frame['relief'] = 'solid'
        frame.rowconfigure(0)
        frame.rowconfigure(1)
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=2)
        # frame.columnconfigure(2, weight=1)
        ttk.Button(frame, text='Check Progress', command=lambda: filedialog.askopenfilename()).grid(row=0, column=0, padx=10, sticky=tk_base.W)
        ttk.Button(frame, text='Start Scraper').grid(row=1, column=0, padx=10, sticky=tk_base.W)
        ttk.Label(frame, text='save location').grid(row=0, column=1, ipadx=20)
        ttk.Entry(frame, textvariable=self.save_loc).grid(row=0, column=1, padx=10, sticky=tk_base.E)
        frame.pack(fill=tk_base.BOTH)

    def __frame_scrollbox(self):
        frame = ttk.Frame(self)
        frame['padding'] = (10,10,10,10)
        # frame['borderwidth'] = 6
        # frame['relief'] = 'solid'
        ttk.Label(frame, text='Scraping Info').pack()
        st = ScrolledText(frame, width=10, height=22)
        st.insert(tk_base.INSERT, 'hello world')
        st.pack(fill=tk_base.BOTH, side=tk_base.LEFT, expand=True)
        frame.pack(fill=tk_base.BOTH)


def create_scrollbox(gui: tk_base.Tk) -> None:
    st = ScrolledText(gui, width=50, height=10)
    st.pack(fill=tk_base.BOTH, side=tk_base.LEFT, expand=True)
