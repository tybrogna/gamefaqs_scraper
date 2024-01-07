import tkinter
import tkinter as tk_base
from tkinter import filedialog
import typing
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

img = None

class Gui(tk_base.Tk):
    def __init__(self):
        super().__init__()
        self.frames: dict = {}
        self.widgets: dict = {}
        self.save_loc = tk_base.StringVar()
        self.fimage = tk_base.PhotoImage('C:/Users/tybro/Projects/gamefaqs_scraper/fb.png')
        global img
        img = tk_base.PhotoImage('C:/Users/tybro/Projects/gamefaqs_scraper/fb.png')

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

    def __grid_options(self):
        frame = ttk.Frame(self)
        # frame['borderwidth'] = 6
        # frame['relief'] = 'solid'
        frame.rowconfigure(0)
        frame.rowconfigure(1)
        frame.columnconfigure(0)
        frame.columnconfigure(1, weight=3)
        frame.columnconfigure(2)
        frame.columnconfigure(3)
        # frame.columnconfigure(2, weight=1)
        ttk.Button(frame, text='Check Progress').grid(row=0, column=0, padx=10, sticky=tk_base.W)
        ttk.Button(frame, text='Start Scraper').grid(row=1, column=0, padx=10, sticky=tk_base.W)
        ttk.Label(frame, text='save location').grid(row=0, column=1, ipadx=1, sticky=tk_base.E)
        ttk.Entry(frame, textvariable=self.save_loc).grid(row=0, column=2, padx=10, sticky=tk_base.EW)
        ttk.Button(frame, text='select save location', command=Gui.get_save_folder).grid(row=0, column=3, padx=1, sticky=tk_base.EW)
        frame.pack(fill=tk_base.BOTH)

    @staticmethod
    def get_save_folder():
        loc = filedialog.askdirectory()
        if loc:
            print(f'found {loc}')
        else:
            print('nada')

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
