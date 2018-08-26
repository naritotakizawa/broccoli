"""ゲームの進行を管理するための機能を提供する。

ゲームキャンバスクラスを格納する、ゲーム全体の進行管理を行うクラスを提供しています。

"""
import tkinter as tk
from broccoli import const
from broccoli.conf import settings


class SimpleGameManager:
    """シンプルなゲームを作るためのマネージャークラス。

    クラス属性canvas_listの中にあるマップを、順番に進んでいくシンプルなゲーム管理クラスです。
    ローグライク等に使いやすいです。

    """

    canvas_list = []
    player = None

    # ゲームオーバーメッセージや、マップ名の表示に関する設定
    text_size = 18
    text_font = settings.DEFAULT_TEXT_FONT
    font = (text_font, text_size)
    color = settings.DEFAULT_TEXT_COLOR

    def __init__(self):
        cls = type(self)
        self.root = None
        self.player = cls.player
        self.current_canvas = None
        self.current_canvas_index = 0

    def setup_game(self):
        """ゲームのセットアップ"""
        self.root = tk.Tk()
        self.root.title(settings.GAME_TITLE)
        self.root.minsize(settings.GAME_WIDTH, settings.GAME_HEIGHT)
        self.root.maxsize(settings.GAME_WIDTH, settings.GAME_HEIGHT)

    def next_canvas(self, next_canvas_index=None):
        """次のマップを表示する"""
        if next_canvas_index is None:
            self.current_canvas_index += 1
        else:
            self.current_canvas_index = next_canvas_index

        if self.current_canvas is not None:
            self.current_canvas.destroy()

        canvas = self.canvas_list[self.current_canvas_index](self)
        self.current_canvas = canvas
        self.current_canvas.pack()
        self.current_canvas.start()

    def start(self):
        """ゲームの開始。インスタンス化後、このメソッドを呼んでください。"""
        self.setup_game()
        self.next_canvas(next_canvas_index=0)
        self.root.mainloop()
