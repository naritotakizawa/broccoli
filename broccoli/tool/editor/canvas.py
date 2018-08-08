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
from broccoli.layer import EmptyObjectLayer, SimpleTileLayer, EmptyItemLayer
from broccoli.canvas import GameCanvas2D
from broccoli.material import BaseTile

STICKY_ALL = (tk.N, tk.S, tk.E, tk.W)


class TestTile(BaseTile):
    name = 'テストタイル'
    description = '初回にだけ表示されるテスト用のタイルです。必ず他のタイルで上書きしてください。'
    image = NoDirection(os.path.join(settings.BROCCOLI_IMG_DIR, 'test.png'))
    public = False


class EditorCanvas(GameCanvas2D):
    """broccoli.canvas.GameCanvas2Dを、エディタで扱うために特科したゲームキャンバスクラス

    GameCanvas2Dはtk.Canvasを継承しています。
    そのため、GameCanvas2Dを継承したこのEditorCanvasもtk.Canvasとして扱えます。

    """

    def __init__(self, master=None, tile_layer=None, click_callback=None, **kwargs):
        self.click_callback = click_callback

        # tile_layerがNoneの場合は、仮のタイルを使ったSimppleBackgroundを利用する
        if tile_layer is None:
            tile_layer = SimpleTileLayer(x_length=10, y_length=10, inner_tile=TestTile, outer_tile=TestTile)
        self.tile_layer = tile_layer
        self.object_layer = EmptyObjectLayer()
        self.item_layer = EmptyItemLayer()
        self.system = None  # ゲームシステムは不要

        # マップ全体の高さと幅
        max_height = self.tile_layer.y_length * settings.CELL_HEIGHT
        max_width = self.tile_layer.x_length * settings.CELL_WIDTH

        # Canvas内をスクロール可能にし、スクロールの最大値を設定
        scroll_region = (0, 0, max_width, max_height)
        tk.Canvas.__init__(
            self, master=master,
            scrollregion=scroll_region,
            width=settings.GAME_WIDTH, height=settings.GAME_HEIGHT,
            **kwargs
        )
        self.tile_layer.create(self)
        self.object_layer.create(self, self.tile_layer)
        self.item_layer.create(self, self.tile_layer)
        if click_callback is not None:
            self.bind('<1>', self.click)

    def draw_cell_line(self):
        """各セルに線を引き、1つ1つのセルをわかりやすくします。"""
        for x, y, tile in self.tile_layer.all():
            self.create_rectangle(
                x*settings.CELL_WIDTH,
                y*settings.CELL_HEIGHT,
                x*settings.CELL_WIDTH+settings.CELL_WIDTH,
                y*settings.CELL_HEIGHT+settings.CELL_HEIGHT,
                tag='line'
            )

    def click(self, event):
        """クリックされた座標の背景、タイルを返す"""
        canvas_x = self.canvasx(event.x)
        canvas_y = self.canvasy(event.y)
        try:
            x, y = self.get_index_from_xy(canvas_x, canvas_y)
        except TypeError:
            pass
        else:
            try:
                tile = self.tile_layer[y][x]
            except IndexError:
                tile = None
            try:
                obj = self.object_layer[y][x]
            except IndexError:
                obj = None
            try:
                items = self.item_layer[y][x]
            except IndexError:
                items = None

            self.click_callback(tile=tile, obj=obj, items=items)


class EditorCanvasWithScrollBar(ttk.Frame):
    """EditorCanvasに、スクロールバーをつけたttk.Frame"""

    def __init__(self, master=None, tile_layer=None, click_callback=None, **kwargs):
        super().__init__(master=master, **kwargs)
        self.click_callback = click_callback
        self.tile_layer = tile_layer
        self.create_widgets()

    def create_widgets(self):
        self.canvas = EditorCanvas(master=self, tile_layer=self.tile_layer, click_callback=self.click_callback)
        self.canvas.grid(row=0, column=0, sticky=STICKY_ALL)
        scroll_x = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        scroll_x.grid(row=1, column=0, sticky=(tk.E, tk.W))
        scroll_y = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)


def debug(**kwargs):
    print(*kwargs.values())


def main():
    root = tk.Tk()
    root.title('マップ作成ツール')
    app = EditorCanvasWithScrollBar(master=root, click_callback=debug)
    app.canvas.draw_cell_line()
    app.pack(fill='both', expand=True)
    root.mainloop()


if __name__ == '__main__':
    main()
