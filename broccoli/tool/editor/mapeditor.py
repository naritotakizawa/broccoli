"""エディタエディタ"""
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from broccoli import register
from broccoli.conf import settings
from broccoli.layer import RandomTileLayer, SimpleTileLayer, JsonTileLayer, JsonObjectLayer, ExpandTileLayer, JsonItemLayer
from broccoli.material import BaseObject, BaseItem, BaseTile
from .list import UserDataFrame
from .canvas import EditorCanvasWithScrollBar
from .search import SearchFrame

STICKY_ALL = (tk.N, tk.S, tk.E, tk.W)


class CustomHighLight(tk.Toplevel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.select = None
        self.material_var = tk.StringVar()
        self.attr_var = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        search = SearchFrame(self,select_callback=self.select_function)
        search.grid(row=0, column=0, sticky=STICKY_ALL, columnspan=2)

        ttk.Label(self, text='マテリアル').grid(column=0, row=1, sticky=STICKY_ALL)
        ttk.Combobox(self, textvariable=self.material_var, values=['タイル', 'オブジェクト', 'アイテム']).grid(column=1, row=1, sticky=STICKY_ALL)

        ttk.Label(self, text='属性').grid(column=0, row=2, sticky=STICKY_ALL)
        ttk.Combobox(self, textvariable=self.attr_var, values=list(register.func_attr_category)).grid(column=1, row=2, sticky=STICKY_ALL)

        ttk.Button(self, text='ハイライト', command=self.highlight).grid(column=0, row=3, sticky=STICKY_ALL, columnspan=2)

    def select_function(self, func):
        self.select = func

    def highlight(self):
        func = self.select
        attr = self.attr_var.get()
        canvas = self.master.canvas_frame.canvas
        canvas.delete('redline')
        kind = self.material_var.get()
        if kind == 'タイル':
            for x, y, material in canvas.tile_layer.all(include_none=False):
                material_attr = getattr(material, attr, None)
                if material_attr and material_attr.name == func.name:
                    canvas.create_red_line(material)

        elif kind == 'オブジェクト':
            for x, y, material in canvas.object_layer.all(include_none=False):
                material_attr = getattr(material, attr, None)
                if material_attr and material_attr.name == func.name:
                    canvas.create_red_line(material)

        elif kind == 'アイテム':
            for x, y, materials in canvas.item_layer.all(include_none=False):
                for material in materials:
                    material_attr = getattr(material, attr, None)
                    if material_attr and material_attr.name == func.name:
                        canvas.create_red_line(material)


class MapEditorConfig(ttk.Frame):
    """マップエディタの設定画面

    MapEditorクラスから使われることを想定しています。
    単体では動作しません。

    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master=master, **kwargs)
        self.create_var()
        self.create_widgets()

    def create_var(self):
        self.x_length_var = tk.StringVar()
        self.x_length_var.set('10')
        self.y_length_var = tk.StringVar()
        self.y_length_var.set('10')
        self.x_room_var = tk.StringVar()
        self.x_room_var.set('2')
        self.y_room_var = tk.StringVar()
        self.y_room_var.set('2')
        self.inner_tile_var = tk.StringVar()
        self.outer_tile_var = tk.StringVar()
        self.all_tile_var = tk.StringVar()
        self.expand_tile_var = tk.StringVar()

    def create_widgets(self):
        # ランダム生成に関する部分
        ttk.Label(self, text='マップ最大幅(セルの数)').grid(column=0, row=0, sticky=STICKY_ALL)
        ttk.Entry(self, textvariable=self.x_length_var).grid(column=1, row=0, sticky=STICKY_ALL)
        ttk.Label(self, text='マップ最大高さ(セルの数)').grid(column=0, row=1, sticky=STICKY_ALL)
        ttk.Entry(self, textvariable=self.y_length_var).grid(column=1, row=1, sticky=STICKY_ALL)
        ttk.Label(self, text='横の部屋の数').grid(column=0, row=2, sticky=STICKY_ALL)
        ttk.Entry(self, textvariable=self.x_room_var).grid(column=1, row=2, sticky=STICKY_ALL)
        ttk.Label(self, text='縦の部屋の数').grid(column=0, row=3, sticky=STICKY_ALL)
        ttk.Entry(self, textvariable=self.y_room_var).grid(column=1, row=3, sticky=STICKY_ALL)
        ttk.Label(self, text='内側のタイル').grid(column=0, row=4, sticky=STICKY_ALL)
        ttk.Combobox(self, textvariable=self.inner_tile_var, values=list(register.tiles.keys())).grid(column=1, row=4, sticky=STICKY_ALL)
        ttk.Label(self, text='外側のタイル').grid(column=0, row=5, sticky=STICKY_ALL)
        ttk.Combobox(self, textvariable=self.outer_tile_var, values=list(register.tiles.keys())).grid(column=1, row=5, sticky=STICKY_ALL)
        ttk.Button(self, text='ランダムマップ作成', command=self.master.create_random).grid(column=0, row=6, sticky=STICKY_ALL, columnspan=2)
        ttk.Button(self, text='真っさらなマップ作成', command=self.master.create_new).grid(column=0, row=7, sticky=STICKY_ALL, columnspan=2)

        ttk.Frame(self, height=30, relief=tk.SUNKEN).grid(column=0, row=8, sticky=STICKY_ALL, columnspan=2)

        # jsonに関する部分
        ttk.Button(self, text='背景をJSONから読み込み', command=self.master.bg_from_json).grid(column=0, row=9, sticky=STICKY_ALL)
        ttk.Button(self, text='オブジェクトをJSONから読み込み', command=self.master.object_from_json).grid(column=0, row=10, sticky=STICKY_ALL)
        ttk.Button (self, text='アイテムをJSONから読み込み', command=self.master.item_from_json).grid (column=0, row=11, sticky=STICKY_ALL)
        ttk.Button(self, text='JSONとして保存', command=self.master.save_json).grid(column=0, row=12, sticky=STICKY_ALL, columnspan=2)

        ttk.Frame(self, height=30, relief=tk.SUNKEN).grid(column=0, row=13, sticky=STICKY_ALL, columnspan=2)

        # タイルの全向き・差分をマップに展開する
        ttk.Label(self, text='全展開の元となるタイル').grid(column=0, row=14, sticky=STICKY_ALL)
        ttk.Combobox(self, textvariable=self.expand_tile_var, values=list(register.tiles.keys())).grid(column=1, row=14, sticky=STICKY_ALL)
        ttk.Button(self, text='全展開(一枚絵のマップとかに便利です)', command=self.master.expand_tile).grid(column=0, row=15, sticky=STICKY_ALL, columnspan=2)

        ttk.Frame(self, height=30, relief=tk.SUNKEN).grid(column=0, row=16, sticky=STICKY_ALL, columnspan=2)

        # 各種タイルの強調
        ttk.Button(self, text='通行可能タイルを表示(is_public=return_true)', command=self.master.show_public).grid(column=0, row=17, sticky=STICKY_ALL)
        ttk.Button(self, text='通行不可タイルを表示(is_public=return_false)', command=self.master.show_private).grid(column=1, row=17, sticky=STICKY_ALL)
        ttk.Button(self, text='カスタムハイライト', command=self.master.show_custom).grid(column=0, row=18, columnspan=2, sticky=STICKY_ALL)

        ttk.Frame(self, height=30, relief=tk.SUNKEN).grid(column=0, row=19, sticky=STICKY_ALL, columnspan=2)

        ttk.Button(self, text='マス目をつける', command=self.master.show_mass).grid(column=0, row=20, sticky=STICKY_ALL)
        ttk.Button(self, text='マス目を消す', command=self.master.delete_mass).grid(column=1, row=20, sticky=STICKY_ALL)
        ttk.Button(self, text='赤線を削除', command=self.master.delete_show_marker).grid(column=0, row=21,sticky=STICKY_ALL, columnspan=2)


class MapEditor(ttk.Frame):
    """マップエディタのメインフレーム

    マップエディタを利用する場合、このクラスをインスタンス化してください。

    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master=master, **kwargs)
        self.select = None
        self.kind = None
        self.create_widgets()

    def create_widgets(self):
        self.list = UserDataFrame(
            master=self,
            tile_callback=self.select_tile, obj_callback=self.select_obj,
            item_callback=self.select_item,
        )
        self.canvas_frame = EditorCanvasWithScrollBar(master=self, click_callback=self.click_canvas)
        self.config = MapEditorConfig(master=self)

        # 左から順に詰める。引き伸ばすのは中央の部分(canvas_frame)だけ。
        self.list.grid(row=0, column=0, sticky=STICKY_ALL)
        self.canvas_frame.grid(row=0, column=1, sticky=STICKY_ALL)
        self.config.grid(row=0, column=2, sticky=STICKY_ALL)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    def _create_canvas(self, tile_layer):
        self.canvas_frame = EditorCanvasWithScrollBar(master=self, click_callback=self.click_canvas, tile_layer=tile_layer)
        self.canvas_frame.grid(row=0, column=1, sticky=STICKY_ALL)

    def select_tile(self, tile):
        """タイルを選択された際に呼び出される"""
        self.select = tile

    def select_obj(self, obj):
        """オブジェクトを選択された際に呼び出される"""
        self.select = obj

    def select_item(self, item):
        """アイテム選択された際に呼び出される"""
        self.select = item

    def click_canvas(self, tile, obj, items):
        """作成中キャンバス欄をクリックされたら呼ばれる"""
        x, y = tile.x, tile.y
        if isinstance(self.select, BaseTile):
            self.canvas_frame.canvas.delete(tile.id)
            self.canvas_frame.canvas.tile_layer.create_material(
                material_cls=self.select.copy(), x=x, y=y,
            )
        elif isinstance(self.select, BaseObject):
            if obj is not None:
                obj.layer.delete_material(self)
            self.canvas_frame.canvas.object_layer.create_material(
                material_cls=self.select.copy(), x=x, y=y,
            )
        elif isinstance(self.select, BaseItem):
            self.canvas_frame.canvas.item_layer.create_material(
                material_cls=self.select.copy(), x=x, y=y,
            )

        else:
            raise Exception('選択中のタイル、オブジェクト、関数がありません。')

    def create_random(self):
        """ランダムマップ生成ボタンで呼ばれる"""
        inner_tile_name = self.config.inner_tile_var.get()
        inner_tile = register.tiles[inner_tile_name]
        outer_tile_name = self.config.outer_tile_var.get()
        outer_tile = register.tiles[outer_tile_name]
        tile_layer = RandomTileLayer(
            x_length=int(self.config.x_length_var.get()), y_length=int(self.config.y_length_var.get()),
            split_x=int(self.config.x_room_var.get()), split_y=int(self.config.y_room_var.get()),
            inner_tile=inner_tile, outer_tile=outer_tile,
        )
        self._create_canvas(tile_layer)

    def create_new(self):
        """真っさらなマップ生成ボタンで呼ばれる"""
        inner_tile_name = self.config.inner_tile_var.get()
        inner_tile = register.tiles[inner_tile_name]
        outer_tile_name = self.config.outer_tile_var.get()
        outer_tile = register.tiles[outer_tile_name]
        tile_layer = SimpleTileLayer(
            x_length=int(self.config.x_length_var.get()), y_length=int(self.config.y_length_var.get()),
            inner_tile=inner_tile, outer_tile=outer_tile,
        )
        self._create_canvas(tile_layer)

    def bg_from_json(self):
        """背景をjsonから読み込みボタンで呼ばれる"""
        file_path = filedialog.askopenfilename(title='背景jsonの選択')
        if file_path:
            tile_layer = JsonTileLayer(file_path)
            self._create_canvas(tile_layer)

    def object_from_json(self):
        """オブジェクトをjsonから読み込みボタで呼ばれる"""
        file_path = filedialog.askopenfilename(title='オブジェクトjsonの選択')
        if file_path:
            object_layer = JsonObjectLayer(file_path)
            object_layer.canvas = self.canvas_frame.canvas
            object_layer.tile_layer = self.canvas_frame.tile_layer
            self.canvas_frame.canvas.object_layer.clear()
            self.canvas_frame.canvas.object_layer = object_layer
            self.canvas_frame.canvas.object_layer.create()

    def item_from_json(self):
        """アイテムをjsonから読み込みボタで呼ばれる"""
        file_path = filedialog.askopenfilename(title='アイテムjsonの選択')
        if file_path:
            item_layer = JsonItemLayer(file_path)
            item_layer.canvas = self.canvas_frame.canvas
            item_layer.tile_layer = self.canvas_frame.tile_layer
            self.canvas_frame.canvas.item_layer.clear()
            self.canvas_frame.canvas.item_layer = item_layer
            self.canvas_frame.canvas.item_layer.create()

    def save_json(self):
        """jsonとして保存ボタンで呼ばれる"""
        self.canvas_frame.canvas.to_json()

    def expand_tile(self):
        """全展開ボタンで呼ばれる"""
        tile_name = self.config.expand_tile_var.get()
        tile = register.tiles[tile_name]
        tile_layer = ExpandTileLayer(tile=tile)
        self._create_canvas(tile_layer)

    def show_public(self):
        """通行可能タイルを強調ボタンで呼ばれる"""
        self.canvas_frame.canvas.delete('redline')
        for x, y, tile in self.canvas_frame.canvas.tile_layer.all(include_none=False):
            if tile.is_public.name == 'generic.return_true':
                self.canvas_frame.canvas.create_red_line(tile)

    def show_private(self):
        """通行不可タイルを強調で呼ばれる"""
        self.canvas_frame.canvas.delete('redline')
        for x, y, tile in self.canvas_frame.canvas.tile_layer.all(include_none=False):
            if tile.is_public.name == 'generic.return_false':
                self.canvas_frame.canvas.create_red_line(tile)

    def show_mass(self):
        """マス目をつけるで呼ばれる"""
        self.canvas_frame.canvas.draw_cell_line()

    def show_custom(self):
        """カスタムハイライト表示で呼ばれる"""
        CustomHighLight(master=self)

    def delete_mass(self):
        """マス目を消すで呼ばれる"""
        self.canvas_frame.canvas.delete('line')

    def delete_show_marker(self):
        """強調タイルを削除で呼ばれる"""
        self.canvas_frame.canvas.delete('redline')


def main():
    import importlib
    importlib.import_module('main')
    root = tk.Tk()
    root.title('マップ作成ツール')
    app = MapEditor(master=root)
    app.pack(fill='both', expand=True)
    root.mainloop()


if __name__ == '__main__':
    main()
