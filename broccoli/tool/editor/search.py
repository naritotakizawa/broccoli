import tkinter as tk
import tkinter.ttk as ttk
from broccoli import register

STICKY_ALL = (tk.N, tk.S, tk.E, tk.W)


class SearchFrame(ttk.Frame):

    def __init__(self, master=None, select_callback=print, **kwargs):
        super().__init__(master=master, **kwargs)
        self.select_callback = select_callback
        self.system_value = tk.StringVar()
        self.systems = list(register.func_system_category)
        self.systems.insert(0, '')

        self.attr_value = tk.StringVar()
        self.attrs = list(register.func_attr_category)
        self.attrs.insert(0, '')

        self.material_value = tk.StringVar()
        self.materials = list(register.func_material_category)
        self.materials.insert(0, '')

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text='システム:').grid(column=0, row=0, sticky=STICKY_ALL)
        system_combo = ttk.Combobox(self, values=self.systems, textvariable=self.system_value)
        system_combo.grid(column=1, row=0, sticky=STICKY_ALL)
        system_combo.bind('<<ComboboxSelected>>', self.update_list)

        ttk.Label(self, text='属性:').grid(column=0, row=1, sticky=STICKY_ALL)
        attr_combo = ttk.Combobox(self, values=self.attrs, textvariable=self.attr_value)
        attr_combo.grid(column=1, row=1, sticky=STICKY_ALL)
        attr_combo.bind('<<ComboboxSelected>>', self.update_list)

        ttk.Label(self, text='マテリアル:').grid(column=0, row=2, sticky=STICKY_ALL)
        material_combo = ttk.Combobox(self, values=self.materials, textvariable=self.material_value)
        material_combo.grid(column=1, row=2, sticky=STICKY_ALL)
        material_combo.bind('<<ComboboxSelected>>', self.update_list)

        self.func_list = tk.Listbox(self)
        self.func_list.grid(column=0, row=3, sticky=STICKY_ALL, columnspan=2)
        for func_name in register.functions:
            self.func_list.insert('end', func_name)
        self.func_list.bind('<Double-Button-1>', self.selection)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)

    def update_list(self, event):
        self.func_list.delete(0, 'end')
        system = self.system_value.get() or None
        attr = self.attr_value.get() or None
        material = self.material_value.get() or None
        functions = register.search_functions(system=system, attr=attr, material=material)
        for func_name in functions:
            self.func_list.insert('end', func_name)

    def selection(self, event):
        select_index = self.func_list.curselection()
        if select_index:
            func_name = self.func_list.get(select_index)
            func = register.functions[func_name]
            self.select_callback(func)





if __name__ == '__main__':
    root = tk.Tk()
    app = SearchFrame(master=root)
    app.pack(expand=True, fill='both')
    root.mainloop()
