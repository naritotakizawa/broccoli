"""エディタエディタ"""
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from broccoli import register
from broccoli.conf import settings
from broccoli.layer import RandomTileLayer, SimpleTileLayer, JsonTileLayer, JsonObjectLayer, ExpandTileLayer, JsonItemLayer
from .list import UserDataFrame
from .canvas import EditorCanvasWithScrollBar

STICKY_ALL = (tk.N, tk.S, tk.E, tk.W)
TILE = 0
OBJECT = 1
ITEM = 2
PUBLIC_FNC = 3
ON_FUNC = 4


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
        ttk.Button(self, text='通行可能タイルを強調(public=True)', command=self.master.show_public).grid(column=0, row=17, sticky=STICKY_ALL, columnspan=2)
        ttk.Button(self, text='通行不可タイルを強調(public=False)', command=self.master.show_private).grid(column=0, row=18, sticky=STICKY_ALL, columnspan=2)
        ttk.Button(self, text='特殊通行タイルを強調(public=function)', command=self.master.show_public_func_tile).grid(column=0, row=19, sticky=STICKY_ALL, columnspan=2)
        ttk.Button(self, text='イベントタイルを強調(on=function)', command=self.master.show_on_func_tile).grid(column=0, row=20, sticky=STICKY_ALL, columnspan=2)
        ttk.Button(self, text='マス目をつける', command=self.master.show_line).grid(column=0, row=21, sticky=STICKY_ALL, columnspan=2)
        ttk.Button(self, text='強調マーカーを削除', command=self.master.delete_show_marker).grid(column=0, row=22,sticky=STICKY_ALL, columnspan=2)


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
            public_callback=self.select_public, on_callback=self.select_on
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
        self.kind = TILE

    def select_obj(self, obj):
        """オブジェクトを選択された際に呼び出される"""
        self.select = obj
        self.kind = OBJECT

    def select_item(self, items):
        """アイテム選択された際に呼び出される"""
        if items is None:
            self.select = None
        else:
            self.select = items[0]
        self.kind = ITEM

    def select_public(self, public_func):
        """タイルのパブリック関数を選択サれたら呼ばれる"""
        self.select = public_func
        self.kind = PUBLIC_FNC

    def select_on(self, on_func):
        """タイルのon関数を詮索されたら呼ばれる"""
        self.select = on_func
        self.kind = ON_FUNC

    def click_canvas(self, obj, tile, items):
        """作成中キャンバス欄をクリックされたら呼ばれる"""
        x, y = tile.x, tile.y
        if self.kind == TILE:
            self.canvas_frame.canvas.delete(tile.id)
            direction = self.select.direction
            diff = self.select.diff
            cls = self.select.__class__
            self.canvas_frame.canvas.tile_layer.create_material(
                material_cls=cls, x=x, y=y,
                direction=direction, diff=diff
            )
        elif self.kind == OBJECT:
            if obj is not None:
                self.canvas_frame.canvas.delete(obj.id)
                self.canvas_frame.canvas.object_layer[obj.y][obj.x] = None
            if self.select is not None:
                direction = self.select.direction
                diff = self.select.diff
                cls = self.select.__class__
                self.canvas_frame.canvas.object_layer.create_material(
                    material_cls=cls, x=x, y=y,
                    direction=direction, diff=diff
                )
        elif self.kind == ITEM:
            if self.select is None:
                for item in self.canvas_frame.canvas.item_layer[tile.y][tile.x]:
                    self.canvas_frame.canvas.delete(item.id)
                self.canvas_frame.canvas.item_layer[tile.y][tile.x] = []
            else:
                direction = self.select.direction
                diff = self.select.diff
                cls = self.select.__class__
                self.canvas_frame.canvas.item_layer.create_material(
                    material_cls=cls, x=x, y=y,
                    direction=direction, diff=diff
                )
        elif self.kind == ON_FUNC:
            tile.on = self.select

        elif self.kind == PUBLIC_FNC:
            tile.public = self.select

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
        for x, y, tile in self.canvas_frame.canvas.tile_layer.all():
            if tile.public is True:
                center_x = x * settings.CELL_WIDTH + settings.CELL_WIDTH/2
                center_y = y * settings.CELL_HEIGHT + settings.CELL_HEIGHT/2
                self.canvas_frame.canvas.create_text(center_x, center_y, text='通れる!', tag='show', anchor='center')

    def show_private(self):
        """通行不可タイルを強調で呼ばれる"""
        for x, y, tile in self.canvas_frame.canvas.tile_layer.all():
            if tile.public is False:
                center_x = x * settings.CELL_WIDTH + settings.CELL_WIDTH/2
                center_y = y * settings.CELL_HEIGHT + settings.CELL_HEIGHT/2
                self.canvas_frame.canvas.create_text(center_x, center_y, text='通れない!', tag='show', anchor='center')

    def show_public_func_tile(self):
        """特殊通行タイルを強調で呼ばれる"""
        for x, y, tile in self.canvas_frame.canvas.tile_layer.all():
            if tile.public is not False and tile.public is not True:
                center_x = x * settings.CELL_WIDTH + settings.CELL_WIDTH/2
                center_y = y * settings.CELL_HEIGHT + settings.CELL_HEIGHT/2
                self.canvas_frame.canvas.create_text(center_x, center_y, text=tile.public.__name__, tag='show', anchor='center')

    def show_on_func_tile(self):
        """イベントタイルを強調で呼ばれる"""
        for x, y, tile in self.canvas_frame.canvas.tile_layer.all():
            if tile.on is not None:
                center_x = x * settings.CELL_WIDTH + settings.CELL_WIDTH/2
                center_y = y * settings.CELL_HEIGHT + settings.CELL_HEIGHT/2
                self.canvas_frame.canvas.create_text(center_x, center_y, text=tile.on.__name__, tag='show', anchor='center')

    def show_line(self):
        """マス目をつけるで呼ばれる"""
        for x, y, tile in self.canvas_frame.canvas.tile_layer.all():
            self.canvas_frame.canvas.create_rectangle(
                x * settings.CELL_WIDTH,
                y * settings.CELL_HEIGHT,
                x * settings.CELL_WIDTH+settings.CELL_WIDTH,
                y*settings.CELL_HEIGHT+settings.CELL_HEIGHT,
                tag='show'
            )

    def delete_show_marker(self):
        """強調タイルを削除で呼ばれる"""
        self.canvas_frame.canvas.delete('show')


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
