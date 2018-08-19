"""よく使うTreeView+αを提供するモジュール

- 背景のリスト表示と、背景の説明やプレビュー
- オブジェクトのリスト表示と、オブジェクトの説明やプレビュー
- ユーザー定義関数のリスト表示と、関数の説明(docstring)
などの、よく使うウィジェットを提供しています。

"""
import tkinter as tk
import tkinter.ttk as ttk
from broccoli import register
from broccoli.conf import settings
from broccoli.layer import ExpandTileLayer, SimpleTileLayer
from .canvas import EditorCanvasWithScrollBar, TestTile

STICKY_ALL = (tk.N, tk.S, tk.E, tk.W)


class BaseList(ttk.Frame):
    """リスト表示ウィジェットの基底クラス

    select_callbackには関数を渡すことができ
    リストで選択されたアイテムが引数として渡されます。
    つまり、

    item_id = self.tree.focus()
    select_callback(self.items[item_id])

    といった処理を行ってくれます。

    """

    def __init__(self, master, select_callback=None, **kwargs):
        super().__init__(master=master, **kwargs)
        self.select_callback = select_callback
        self.items = {}
        self.create_widgets()
        self.create_tree_item()
        self.tree.bind('<Double-1>', self.on_select)

    def create_widgets(self):
        raise NotImplementedError

    def create_tree_item(self):
        raise NotImplementedError

    def update_widget(self, item):
        """リストの項目を選択した際の処理

        説明欄やプレビューなどを更新する必要があれば、実装してください。

        """
        pass


class TileList(BaseList):
    """タイルをリスト表示する

    ユーザー定義タイルをリスト表示しつつ、
    説明などの各種情報、プレビューを表示する

    """

    def create_widgets(self):
        self.tree = ttk.Treeview(self)
        self.tree.heading('#0', text='ユーザー定義タイルの一覧')
        ysb = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)

        self.tree.grid(row=0, column=0, sticky=STICKY_ALL)
        ysb.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 選択したマテリアルの説明を横0, 縦1に配置
        self.description = tk.Text(self)
        self.description.insert('1.0', '何も選択していません')
        self.description.grid(row=1, column=0, sticky=STICKY_ALL)

        # 選択したマテリアルのプレビュー欄を横0,縦2に配置
        self.canvas_frame = EditorCanvasWithScrollBar(self)
        self.canvas_frame.grid(row=2, column=0, sticky=STICKY_ALL)
        self.canvas = self.canvas_frame.canvas

        # 引き伸ばしの設定
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

    def create_tree_item(self):
        for tile_name, tile_cls in register.tiles.items():
            item_id = self.tree.insert('', 'end', text=tile_name, open=False)
            self.items[item_id] = tile_cls

    def update_widget(self, item):
        """マテリアルのプレビューや、説明を描画する"""
        des = ''
        for key, value in item.get_class_attrs().items():
            des += '{}: {}\n'.format(key, value)
        self.description.delete('1.0', 'end')
        self.description.insert('1.0', des)

        if item is not None:
            # タイルを、プレビュー欄に展開する
            tile_layer = ExpandTileLayer(tile=item)
            self.canvas_frame = EditorCanvasWithScrollBar(self, tile_layer=tile_layer, click_callback=self.select)
            self.canvas_frame.grid(row=2, column=0, sticky=STICKY_ALL)
            self.canvas = self.canvas_frame.canvas
            self.canvas.draw_cell_line()

    def on_select(self, event):
        # アイテムを取得し、それをもとにプレビュー欄を展開する
        # その際、そのプレビュー欄クリックでselect_callbackを呼び出す
        item_id = self.tree.focus()
        if item_id:
            try:
                item = self.items[item_id]
            except TypeError:
                pass
            else:
                self.update_widget(item)

    def select(self, tile, obj, items):
        """プレビュー欄のタイルクリックで呼ばれる

        選んだタイルを赤く縁取り、select_callbackにtileを引数に呼び出します。

        """
        self.canvas.delete('select')
        self.canvas.create_rectangle(
            tile.x * settings.CELL_WIDTH,
            tile.y * settings.CELL_HEIGHT,
            tile.x * settings.CELL_WIDTH + settings.CELL_WIDTH,
            tile.y * settings.CELL_HEIGHT + settings.CELL_HEIGHT,
            tag='select',
            outline='red',
            width=10
        )
        self.select_callback(tile)


class ObjectList(BaseList):
    """オブジェクトをリスト表示する

    ユーザー定義オブジェクトをリスト表示しつつ、
    説明などの各種情報、プレビューを表示する

    """

    def create_widgets(self):
        self.tree = ttk.Treeview(self)
        self.tree.heading('#0', text='ユーザー定義オブジェクトの一覧')
        ysb = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)

        self.tree.grid(row=0, column=0, sticky=STICKY_ALL)
        ysb.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 選択したマテリアルの説明を横0, 縦1に配置
        self.description = tk.Text(self)
        self.description.grid(row=1, column=0, sticky=STICKY_ALL)

        # 選択したマテリアルのプレビュー欄を横0,縦2に配置
        self.canvas_frame = EditorCanvasWithScrollBar(self)
        self.canvas_frame.grid(row=2, column=0, sticky=STICKY_ALL)
        self.canvas = self.canvas_frame.canvas

        # 引き伸ばしの設定
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

    def create_tree_item(self):
        register.objects['選択なし'] = None
        for obj_name, obj_cls in register.objects.items():
            item_id = self.tree.insert('', 'end', text=obj_name, open=False)
            self.items[item_id] = obj_cls

    def update_widget(self, item):
        """マテリアルのプレビューや、説明を描画する"""
        if item is None:
            des = '何も選択していません。(オブジェクトクリックで消去できます)'
        else:
            des = ''
            for key, value in item.get_class_attrs().items():
                des += '{}: {}\n'.format(key, value)
        self.description.delete('1.0', 'end')
        self.description.insert('1.0', des)

        if item is not None:
            # オブジェクトを、プレビュー欄に展開するが
            # タイルと違い、オブジェクトを展開するレイヤークラスはないため自力で行う
            i = ExpandTileLayer(tile=item)  # 展開するには長さを調べる必要があるので、ExpandTileBackgroudnを利用
            x = i.x_length
            y = i.y_length
            tile_layer = SimpleTileLayer(x_length=x, y_length=y, outer_tile=TestTile, inner_tile=TestTile)
            self.canvas_frame = EditorCanvasWithScrollBar(self, tile_layer=tile_layer, click_callback=self.select)
            self.canvas_frame.grid(row=2, column=0, sticky=STICKY_ALL)
            self.canvas = self.canvas_frame.canvas
            self.canvas.draw_cell_line()
            for y, row in enumerate(self.canvas.tile_layer):
                for x, col in enumerate(row):
                    self.canvas.object_layer.create_material(material_cls=item, x=x, y=y, direction=y, diff=x)

    def on_select(self, event):
        # アイテムを取得し、それをもとにプレビュー欄を展開する
        # その際、そのプレビュー欄クリックでselect_callbackを呼び出す
        # ただし、「選択なし」を選択したらすぐにselect_callback呼び出し。
        item_id = self.tree.focus()
        if item_id:
            try:
                item = self.items[item_id]
            except TypeError:
                pass
            else:
                self.update_widget(item)
                if item is None and self.select_callback is not None:
                    self.select_callback(item)

    def select(self, tile, obj, items):
        """プレビュー欄のオブジェクトクリックで呼ばれる

        選んだオブジェクトを赤く縁取り、select_callbackにobjectを引数に呼び出します。

        """
        self.canvas.delete('select')
        self.canvas.create_rectangle(
            tile.x * settings.CELL_WIDTH,
            tile.y * settings.CELL_HEIGHT,
            tile.x * settings.CELL_WIDTH + settings.CELL_WIDTH,
            tile.y * settings.CELL_HEIGHT + settings.CELL_HEIGHT,
            tag='select',
            outline='red',
            width=10
        )
        self.select_callback(obj)


class ItemList(BaseList):
    """オブジェクトをリスト表示する

    ユーザー定義オブジェクトをリスト表示しつつ、
    説明などの各種情報、プレビューを表示する

    """

    def create_widgets(self):
        self.tree = ttk.Treeview(self)
        self.tree.heading('#0', text='ユーザー定義アイテムの一覧')
        ysb = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)

        self.tree.grid(row=0, column=0, sticky=STICKY_ALL)
        ysb.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 選択したマテリアルの説明を横0, 縦1に配置
        self.description = tk.Text(self)
        self.description.grid(row=1, column=0, sticky=STICKY_ALL)

        # 選択したマテリアルのプレビュー欄を横0,縦2に配置
        self.canvas_frame = EditorCanvasWithScrollBar(self)
        self.canvas_frame.grid(row=2, column=0, sticky=STICKY_ALL)
        self.canvas = self.canvas_frame.canvas

        # 引き伸ばしの設定
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

    def create_tree_item(self):
        register.items['選択なし'] = None
        for obj_name, obj_cls in register.items.items():
            item_id = self.tree.insert('', 'end', text=obj_name, open=False)
            self.items[item_id] = obj_cls

    def update_widget(self, item):
        """マテリアルのプレビューや、説明を描画する"""
        if item is None:
            des = '何も選択していません。(中央キャンバスクリックでアイテムを消去できます)'
        else:
            des = ''
            for key, value in item.get_class_attrs().items():
                des += '{}: {}\n'.format(key, value)
        self.description.delete('1.0', 'end')
        self.description.insert('1.0', des)

        if item is not None:
            # アイテム、プレビュー欄に展開するが
            # タイルと違い、アイテムを展開するレイヤークラスはないため自力で行う
            i = ExpandTileLayer(tile=item)  # 展開するには長さを調べる必要があるので、ExpandTileBackgroudnを利用
            x = i.x_length
            y = i.y_length
            tile_layer = SimpleTileLayer(x_length=x, y_length=y, outer_tile=TestTile, inner_tile=TestTile)
            self.canvas_frame = EditorCanvasWithScrollBar(self, tile_layer=tile_layer, click_callback=self.select)
            self.canvas_frame.grid(row=2, column=0, sticky=STICKY_ALL)
            self.canvas = self.canvas_frame.canvas
            self.canvas.draw_cell_line()
            for y, row in enumerate(self.canvas.tile_layer):
                for x, col in enumerate(row):
                    self.canvas.item_layer.create_material(material_cls=item, x=x, y=y, direction=y, diff=x)

    def on_select(self, event):
        # アイテムを取得し、それをもとにプレビュー欄を展開する
        # その際、そのプレビュー欄クリックでselect_callbackを呼び出す
        # ただし、「選択なし」を選択したらすぐにselect_callback呼び出し。
        item_id = self.tree.focus()
        if item_id:
            try:
                item = self.items[item_id]
            except TypeError:
                pass
            else:
                self.update_widget(item)
                if item is None and self.select_callback is not None:
                    self.select_callback(item)

    def select(self, tile, obj, items):
        """プレビュー欄のオブジェクトクリックで呼ばれる

        選んだオブジェクトを赤く縁取り、select_callbackにobjectを引数に呼び出します。

        """
        self.canvas.delete('select')
        self.canvas.create_rectangle(
            tile.x * settings.CELL_WIDTH,
            tile.y * settings.CELL_HEIGHT,
            tile.x * settings.CELL_WIDTH + settings.CELL_WIDTH,
            tile.y * settings.CELL_HEIGHT + settings.CELL_HEIGHT,
            tag='select',
            outline='red',
            width=10
        )
        self.select_callback(items)


class PublicList(BaseList):
    """タイルの通行可能, 通行不可, 通行チェック関数のリスト表示"""

    def create_widgets(self):
        self.tree = ttk.Treeview(self)
        self.tree.heading('#0', text='タイルの通行可能・不可能設定の一覧')
        ysb = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)

        self.tree.grid(row=0, column=0, sticky=STICKY_ALL)
        ysb.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 選択したマテリアルの説明を横0, 縦1に配置
        self.description = tk.Text(self)
        self.description.grid(row=1, column=0, sticky=STICKY_ALL)

        # 引き伸ばしの設定
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

    def create_tree_item(self):
        register.public_funcs['通行可能'] = True
        register.public_funcs['通行不可'] = False
        for name, func in register.public_funcs.items():
            item_id = self.tree.insert('', 'end', text=name, open=False)
            self.items[item_id] = func

    def update_widget(self, item):
        if item is True:
            des = '選択したタイルを通行可能にします。'
        elif item is False:
            des = '選択したタイルを通行不可にします。'
        else:
            des = item.__doc__

        self.description.delete('1.0', 'end')
        self.description.insert('1.0', des)

    def on_select(self, event):
        # アイテムを取得し、説明欄を更新
        # そして、select_callbackがあればそれを呼び出す
        item_id = self.tree.focus()
        if item_id:
            try:
                item = self.items[item_id]
            except TypeError:
                pass
            else:
                self.update_widget(item)
                if self.select_callback is not None:
                    self.select_callback(item)


class OnList(BaseList):
    """タイルの上に乗った際の処理のリスト表示"""

    def create_widgets(self):
        self.tree = ttk.Treeview(self)
        self.tree.heading('#0', text='タイルに乗った際のイベント一覧')
        ysb = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)

        self.tree.grid(row=0, column=0, sticky=STICKY_ALL)
        ysb.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 選択したマテリアルの説明を横0, 縦1に配置
        self.description = tk.Text(self)
        self.description.grid(row=1, column=0, sticky=STICKY_ALL)

        # 引き伸ばしの設定
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

    def create_tree_item(self):
        register.on_funcs['イベント削除'] = None
        for name, func in register.on_funcs.items():
            item_id = self.tree.insert('', 'end', text=name, open=False)
            self.items[item_id] = func

    def update_widget(self, item):
        """マテリアルのプレビューや、説明を描画する"""
        if item is None:
            des = '選択したタイルのイベントを消去します。'
        else:
            des = item.__doc__

        self.description.delete('1.0', 'end')
        self.description.insert('1.0', des)

    def on_select(self, event):
        # アイテムを取得し、説明欄を更新
        # そして、select_callbackがあればそれを呼び出す
        item_id = self.tree.focus()
        if item_id:
            try:
                item = self.items[item_id]
            except TypeError:
                pass
            else:
                self.update_widget(item)
                if self.select_callback is not None:
                    self.select_callback(item)


class UserDataFrame(ttk.Frame):
    """ユーザー定義データのリスト表示・プレビューなどを行うFrame"""

    def __init__(self, tile_callback=None, obj_callback=None, public_callback=None, on_callback=None, item_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.tile_callback = tile_callback
        self.obj_callback = obj_callback
        self.item_callback = item_callback
        self.public_callback = public_callback
        self.on_callback = on_callback
        self.create_widgets()

    def create_widgets(self):
        """ウィジェットの生成・配置"""
        self.note = ttk.Notebook(master=self)

        tile_list = TileList(master=self.note, select_callback=self.tile_callback)
        self.note.add(tile_list, text='タイル一覧')

        obj_list = ObjectList(master=self.note, select_callback=self.obj_callback)
        self.note.add(obj_list, text='オブジェクト一覧')

        item_list = ItemList(master=self.note, select_callback=self.item_callback)
        self.note.add(item_list, text='アイテム一覧')

        #public_list = PublicList(master=self.note, select_callback=self.public_callback)
        #self.note.add(public_list, text='通行一覧')

        #on_list = OnList(master=self.note, select_callback=self.on_callback)
        #self.note.add(on_list, text='上に乗った際の処理一覧')

        self.note.pack(fill='both')


def debug(*args):
    print(args)


def main():
    import importlib
    importlib.import_module('main')
    root = tk.Tk()
    app = UserDataFrame(master=root, tile_callback=debug, obj_callback=debug, public_callback=debug, on_callback=debug, item_callback=debug)
    app.pack(fill='both', expand=True)
    root.mainloop()


if __name__ == '__main__':
    main()
