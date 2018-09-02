"""ゲームの進行を管理するための機能を提供する。

ゲームキャンバスクラスを格納する、ゲーム全体の進行管理を行うクラスを提供しています。

"""
import tkinter as tk
from broccoli.containers import IndexDict
from broccoli.conf import settings


class SimpleGameManager:
    """シンプルなゲームを作るためのマネージャークラス。

    クラス属性canvas_listの中にあるマップを、順番に進んでいくシンプルなゲーム管理クラスです。
    ローグライク等に使いやすいです。

    """

    canvas_list = IndexDict({})
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

    def jump(self, index=None):
        """次のマップを表示する"""
        if index is None:
            canvas_index = self.current_canvas_index + 1
            canvas_name = self.canvas_list.get_key_from_index(canvas_index)
        else:
            if isinstance(index, int):
                canvas_index = index
                canvas_name = self.canvas_list.get_key_from_index(canvas_index)
            else:
                canvas_name = index
                canvas_index = self.canvas_list.get_index_from_key(canvas_name)

        if self.current_canvas is not None:
            self.current_canvas.destroy()

        self.current_canvas_index = canvas_index
        canvas = self.canvas_list[canvas_name]
        self.current_canvas = canvas(manager=self, name=canvas_name)
        self.current_canvas.pack()
        self.current_canvas.start()

    def start(self):
        """ゲームの開始。インスタンス化後、このメソッドを呼んでください。"""
        self.setup_game()
        self.jump(index=0)
        self.root.mainloop()
