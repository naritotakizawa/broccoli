"""ゲームの進行を管理するための機能を提供する。

ゲームキャンバスクラスを格納する、ゲーム全体の進行管理を行うクラスを提供しています。

"""
import json
import tkinter as tk
from tkinter import filedialog
from broccoli import serializers, layer
from broccoli.containers import IndexDict
from broccoli.conf import settings


class BaseManager:
    """マネージャークラスの既定クラス。"""
    pass


class SimpleGameManager(BaseManager):
    """シンプルなゲームを作るためのマネージャークラス。

    クラス属性canvas_listの中にあるマップを、順番に進んでいくシンプルなゲーム管理クラスです。
    ローグライク等に使いやすいです。

    """

    canvas_list = {}
    vars = {}

    # ゲームオーバーメッセージや、マップ名の表示に関する設定
    text_size = 18
    text_font = settings.DEFAULT_TEXT_FONT
    font = (text_font, text_size)
    color = settings.DEFAULT_TEXT_COLOR

    def __init__(self):
        cls = type(self)
        self.root = None
        self.canvas_list = IndexDict(cls.canvas_list)
        self.vars = cls.vars
        self.current_canvas = None
        self.current_canvas_index = 0
        self.current_canvas_name = ''

    def setup_game(self):
        """ゲームのセットアップ"""
        self.root = tk.Tk()
        self.root.title(settings.GAME_TITLE)
        self.root.minsize(settings.GAME_WIDTH, settings.GAME_HEIGHT)
        self.root.maxsize(settings.GAME_WIDTH, settings.GAME_HEIGHT)

    def jump(self, index=None):
        """次のマップを表示する"""
        # indexがNoneなら、次の位置のマップ
        if index is None:
            canvas_index = self.current_canvas_index + 1
            canvas_name = self.canvas_list.get_key_from_index(canvas_index)
        else:
            # indexが数値なら、その位置のマップを取得
            if isinstance(index, int):
                canvas_index = index
                canvas_name = self.canvas_list.get_key_from_index(canvas_index)

            # indexが名前なら、マップ名からマップを取得
            else:
                canvas_name = index
                canvas_index = self.canvas_list.get_index_from_key(canvas_name)

        # 初回じゃない限りは、今遊んでいたマップを破棄
        if self.current_canvas is not None:
            self.current_canvas.destroy()

        self.current_canvas_index = canvas_index
        self.current_canvas_name = canvas_name
        canvas = self.canvas_list[canvas_name]
        self.current_canvas = canvas(master=self.root, manager=self, name=canvas_name)
        self.current_canvas.pack()
        self.current_canvas.start()

    def start(self):
        """ゲームの開始。インスタンス化後、このメソッドを呼んでください。"""
        self.setup_game()
        self.jump(index=0)
        self.root.mainloop()

    def save(self, _event=None):
        """ゲームのセーブ処理。"""
        file_path = filedialog.asksaveasfilename(title='保存するファイル名')
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self, file, cls=serializers.JsonEncoder, indent=4)

    def load(self, _event=None):
        """ゲームのロード処理。"""
        file_path = filedialog.askopenfilename(title='ロードするファイル名')
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file, cls=serializers.JsonDecoder)

            self.vars = data['vars']
            self.current_canvas_name = canvas_name = data['name']
            self.current_canvas_index = self.canvas_list.get_index_from_key(canvas_name)

            canvas = self.canvas_list[canvas_name]
            context = {
                'manager': self,
                'name': canvas_name,
                'tile_layer': layer.PythonTileLayer(data['tile_layer']['layer']),
                'object_layer': layer.PythonObjectLayer(data['object_layer']['layer']),
                'item_layer': layer.PythonItemLayer(data['item_layer']['layer']),
            }

            # 初回じゃない限りは、今遊んでいたマップを破棄
            if self.current_canvas is not None:
                self.current_canvas.destroy()

            self.current_canvas = canvas(**context)
            self.current_canvas.pack()
            self.current_canvas.start()
