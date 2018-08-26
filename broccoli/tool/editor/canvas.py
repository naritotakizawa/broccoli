"""エディタで使うゲームキャンバスクラスを提供するモジュール

broccoli.canvasにあるゲームキャンバスクラスを元に、エディタで使いやすくするためのクラスを提供しています。

broccoli.canvasのゲームキャンバスと違うのは、システムクラスが不要なことと
キャンバス内をクリックした際、そこにある背景やオブジェクトの取得や交換といった機能をサポートしていることです。
また、これらのキャンバスにスクロールバーをつけたttk.Frameクラスのサブクラスも提供しています。

"""
import os
import tkinter as tk
import tkinter.ttk as ttk
from broccoli.conf import settings
from broccoli.img.loader import NoDirection
from broccoli.layer import SimpleTileLayer
from broccoli.canvas import GameCanvas2D
from broccoli.material import BaseTile
from .window import SearchWindow, OneInputWindow

STICKY_ALL = (tk.N, tk.S, tk.E, tk.W)


class TestTile(BaseTile):
    name = 'テストタイル'
    image = NoDirection(os.path.join(settings.BROCCOLI_IMG_DIR, 'test.png'))


def method_command(material, attr_name, label):
    def _method_command():
        def callback(func):
            method = material.create_method(func)
            setattr(material, attr_name, method)
            label['text'] = method.name
            material.canvas.itemconfigure(material.id, image=material.image)
            material._canvas.itemconfigure(material._id, image=material.image)
        SearchWindow(select_callback=callback)
    return _method_command


def str_command(material, attr_name, label):
    def _str_command():
        def callback(value):
            setattr(material, attr_name, value)
            label['text'] = value
            material.canvas.itemconfigure(material.id, image=material.image)
            material._canvas.itemconfigure(material._id, image=material.image)
        OneInputWindow(select_callback=callback, cast=str)
    return _str_command


def int_command(material, attr_name, label):
    def _int_command():
        def callback(value):
            setattr(material, attr_name, value)
            label['text'] = value
            material.canvas.itemconfigure(material.id, image=material.image)
            material._canvas.itemconfigure(material._id, image=material.image)
        OneInputWindow(select_callback=callback, cast=int)
    return _int_command


def delete_command(material, frame):
    def _delete_command():
        material.delete()
        frame.destroy()
    return _delete_command


class MaterialListFrame(tk.Toplevel):

    def __init__(self, tile, obj, items, **kwargs):
        super().__init__(**kwargs)
        self.tile = tile
        self.obj = obj
        self.items = items
        self.create_widgets()

    def create_widgets(self):
        self.note = ttk.Notebook(master=self)
        self.note.pack(expand=True, fill='both')
        self.create_tile_area()
        if self.obj is not None:
            self.create_object_area()
        if self.items:
            self.create_item_area()

    def create_tile_area(self):
        row = 0
        tile_frame = ttk.Frame(self)
        # タイルの画像を表示するcanvas
        tile_canvas = tk.Canvas(tile_frame, width=settings.CELL_WIDTH, height=settings.CELL_HEIGHT)
        tile_canvas.grid(row=row, column=0, columnspan=2, sticky=STICKY_ALL)
        row += 1
        self.tile._id = tile_canvas.create_image(0, 0, image=self.tile.image, anchor='nw')
        self.tile._canvas = tile_canvas

        for attr_name, attr_value in self.tile.get_instance_attrs().items():
            ttk.Label(tile_frame, text=attr_name).grid(row=row, column=0, sticky=STICKY_ALL)
            # 属性がメソッドだった場合
            if attr_name in self.tile.func_attrs:
                label = ttk.Label(tile_frame, text=attr_value.name)
                label.grid(row=row, column=1, sticky=STICKY_ALL, padx=50)
                ttk.Button(tile_frame, text='振る舞いの変更', command=method_command(self.tile, attr_name, label)).grid(row=row, column=2, sticky=STICKY_ALL)

            # 属性がリストの場合(未実装)
            elif isinstance(attr_value, list):
                label = ttk.Label(tile_frame, text=','.join(attr_value))
                label.grid(row=row, column=1, sticky=STICKY_ALL, padx=50)

            # 属性が文字列の場合
            elif isinstance(attr_value, str):
                label = ttk.Label(tile_frame, text=attr_value)
                label.grid(row=row, column=1, sticky=STICKY_ALL, padx=50)
                ttk.Button(tile_frame, text='値の変更', command=str_command(self.tile, attr_name, label)).grid(row=row, column=2, sticky=STICKY_ALL)

            # 属性が数値の場合
            elif isinstance(attr_value, int):
                label = ttk.Label(tile_frame, text=attr_value)
                label.grid(row=row, column=1, sticky=STICKY_ALL, padx=50)
                ttk.Button(tile_frame, text='値の変更', command=int_command(self.tile, attr_name, label)).grid(row=row, column=2, sticky=STICKY_ALL)

            row += 1

        self.note.add(tile_frame, text='タイル')

    def create_object_area(self):
        row = 0
        obj_frame = ttk.Frame(self)
        # オブジェクトの画像を表示するcanvas
        obj_canvas = tk.Canvas(obj_frame, width=settings.CELL_WIDTH, height=settings.CELL_HEIGHT)
        obj_canvas.grid(row=row, column=0, sticky=STICKY_ALL)
        ttk.Button(obj_frame, text='削除', command=delete_command(self.obj, obj_frame)).grid(row=row, column=1, sticky=STICKY_ALL)
        row += 1
        self.obj._id = obj_canvas.create_image(0, 0, image=self.obj.image, anchor='nw')
        self.obj._canvas = obj_canvas

        for attr_name, attr_value in self.obj.get_instance_attrs().items():
            ttk.Label(obj_frame, text=attr_name).grid(row=row, column=0, sticky=STICKY_ALL)
            # 属性がメソッドだった場合
            if attr_name in self.obj.func_attrs:
                label = ttk.Label(obj_frame, text=attr_value.name)
                label.grid(row=row, column=1, sticky=STICKY_ALL, padx=50)
                ttk.Button(obj_frame, text='振る舞いの変更', command=method_command(self.obj, attr_name, label)).grid(row=row, column=2, sticky=STICKY_ALL)

            # 属性がリストの場合(未実装)
            elif isinstance(attr_value, list):
                label = ttk.Label(obj_frame, text=','.join(attr_value))
                label.grid(row=row, column=1, sticky=STICKY_ALL, padx=50)

            # 属性が文字列の場合
            elif isinstance(attr_value, str):
                label = ttk.Label(obj_frame, text=attr_value)
                label.grid(row=row, column=1, sticky=STICKY_ALL, padx=50)
                ttk.Button(obj_frame, text='値の変更', command=str_command(self.obj, attr_name, label)).grid(row=row, column=2, sticky=STICKY_ALL)

            # 属性が数値の場合
            elif isinstance(attr_value, int):
                label = ttk.Label(obj_frame, text=attr_value)
                label.grid(row=row, column=1, sticky=STICKY_ALL, padx=50)
                ttk.Button(obj_frame, text='値の変更', command=int_command(self.obj, attr_name, label)).grid(row=row, column=2, sticky=STICKY_ALL)

            row += 1

        self.note.add(obj_frame, text='オブジェクト')

    def create_item_area(self):
        row = 0
        for i, item in enumerate(self.items, 1):
            item_frame = ttk.Frame(self)
            # アイテムの画像を表示するcanvas
            item_canvas = tk.Canvas(item_frame, width=settings.CELL_WIDTH, height=settings.CELL_HEIGHT)
            item_canvas.grid(row=row, column=0, sticky=STICKY_ALL)
            ttk.Button(item_frame, text='削除', command=delete_command(item, item_frame)).grid(row=row, column=1, sticky=STICKY_ALL)
            row += 1
            item._id = item_canvas.create_image(0, 0, image=item.image, anchor='nw')
            item._canvas = item_canvas

            for attr_name, attr_value in item.get_instance_attrs().items():
                ttk.Label(item_frame, text=attr_name).grid(row=row, column=0, sticky=STICKY_ALL)
                # 属性がメソッドだった場合
                if attr_name in item.func_attrs:
                    label = ttk.Label(item_frame, text=attr_value.name)
                    label.grid(row=row, column=1, sticky=STICKY_ALL, padx=50)
                    ttk.Button(item_frame, text='振る舞いの変更', command=method_command(item, attr_name, label)).grid(row=row, column=2, sticky=STICKY_ALL)

                # 属性がリストの場合(未実装)
                elif isinstance(attr_value, list):
                    label = ttk.Label(item_frame, text=','.join(attr_value))
                    label.grid(row=row, column=1, sticky=STICKY_ALL, padx=50)

                # 属性が文字列の場合
                elif isinstance(attr_value, str):
                    label = ttk.Label(item_frame, text=attr_value)
                    label.grid(row=row, column=1, sticky=STICKY_ALL, padx=50)
                    ttk.Button(item_frame, text='値の変更', command=str_command(item, attr_name, label)).grid(row=row, column=2, sticky=STICKY_ALL)

                # 属性が数値の場合
                elif isinstance(attr_value, int):
                    label = ttk.Label(item_frame, text=attr_value)
                    label.grid(row=row, column=1, sticky=STICKY_ALL, padx=50)
                    ttk.Button(item_frame, text='値の変更', command=int_command(item, attr_name, label)).grid(row=row, column=2, sticky=STICKY_ALL)

                row += 1

            self.note.add(item_frame, text='{}番目のアイテム'.format(i))


class EditorCanvas(GameCanvas2D):
    """broccoli.canvas.GameCanvas2Dを、エディタで扱うために特科したゲームキャンバスクラス

    GameCanvas2Dはtk.Canvasを継承しています。
    そのため、GameCanvas2Dを継承したこのEditorCanvasもtk.Canvasとして扱えます。

    """

    def __init__(self, master=None, tile_layer=None, click_callback=None, return_kind='all', **kwargs):
        # tile_layerがNoneの場合は、仮のタイルを使ったSimpleTileLayerを利用する
        if tile_layer is None:
            tile_layer = SimpleTileLayer(x_length=10, y_length=10, inner_tile=TestTile, outer_tile=TestTile)
        super().__init__(master=master, tile_layer=tile_layer)

        self.click_callback = click_callback
        self.return_kind = return_kind
        self.bind('<3>', self.show_materials)
        if click_callback is not None:
            self.bind('<1>', self.click)

    def click(self, event):
        """クリックされた座標の背景、タイルを返す"""
        canvas_x = self.canvasx(event.x)
        canvas_y = self.canvasy(event.y)
        try:
            x, y = self.get_index_from_xy(canvas_x, canvas_y)
        except TypeError:
            pass
        else:
            tile = self.tile_layer[y][x]
            obj = self.object_layer[y][x]
            items = self.item_layer[y][x]
            if self.return_kind == 'tile':
                self.click_callback(tile)
            elif self.return_kind == 'object':
                self.click_callback(obj)
            elif self.return_kind == 'item':
                self.click_callback(items)
            else:
                self.click_callback(tile, obj, items)

    def show_materials(self, event):
        canvas_x = self.canvasx(event.x)
        canvas_y = self.canvasy(event.y)
        try:
            x, y = self.get_index_from_xy(canvas_x, canvas_y)
        except TypeError:
            pass
        else:
            tile = self.tile_layer[y][x]
            obj = self.object_layer[y][x]
            items = self.item_layer[y][x]
            MaterialListFrame(tile=tile, obj=obj, items=items, master=self)


class EditorCanvasWithScrollBar(ttk.Frame):
    """EditorCanvasに、スクロールバーをつけたttk.Frame"""

    def __init__(self, master=None, tile_layer=None, click_callback=None, return_kind='all', **kwargs):
        super().__init__(master=master, **kwargs)
        self.click_callback = click_callback
        self.return_kind = return_kind
        self.tile_layer = tile_layer
        self.create_widgets()

    def create_widgets(self):
        self.canvas = EditorCanvas(
            self, tile_layer=self.tile_layer, click_callback=self.click_callback,
            return_kind=self.return_kind
        )
        self.canvas.grid(row=0, column=0, sticky=STICKY_ALL)
        scroll_x = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        scroll_x.grid(row=1, column=0, sticky=(tk.E, tk.W))
        scroll_y = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)


def debug(*args):
    print(args)


def main():
    root = tk.Tk()
    root.title('マップ作成ツール')
    app = EditorCanvasWithScrollBar(master=root, click_callback=debug)
    app.canvas.draw_cell_line()
    app.pack(fill='both', expand=True)
    root.mainloop()


if __name__ == '__main__':
    main()
