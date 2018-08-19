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
    image = NoDirection(os.path.join(settings.BROCCOLI_IMG_DIR, 'test.png'))
    public = False


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
