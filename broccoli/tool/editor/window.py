import tkinter as tk
import tkinter.ttk as ttk
from .search import SearchFrame


class SearchWindow(tk.Toplevel):

    def __init__(self, master=None, select_callback=print, **kwargs):
        super().__init__(master=master, **kwargs)
        self._select_callback = select_callback
        self.create_widgets()

    def create_widgets(self):
        SearchFrame(master=self, select_callback=self.select_callback).pack(fill='both', expand=True)

    def select_callback(self, func):
        self.destroy()
        self._select_callback(func)


class OneInputWindow(tk.Toplevel):

    def __init__(self, master=None, select_callback=print, cast=None, **kwargs):
        super().__init__(master=master, **kwargs)
        self._select_callback = select_callback
        self.cast = cast
        self.create_widgets()

    def create_widgets(self):
        self.entry = entry = ttk.Entry(self)
        entry.pack(fill='both', expand=True)
        entry.bind('<Return>', self.select_callback)

    def select_callback(self, event):
        value = self.entry.get()
        if self.cast:
            value = self.cast(value)
        self.destroy()
        self._select_callback(value)
