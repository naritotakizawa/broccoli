"""ゲームキャンバスに関する基底クラスを提供するモジュール。

このモジュールで提供しているクラスを、フレームワーク内では「ゲームキャンバス」と呼ぶことにします。

モジュール内のクラスはtk.Canvasのサブクラスで、ゲーム内における1つのマップ、又はゲームを表現します。
インスタンス化することで、そのマップ又はゲームが表示されるようになり、
startメソッドを呼び出すことで、そのマップ又はゲームが動作し楽しむことができます。

ゲームキャンバスクラスはいくつかの層...タイルレイヤーやオブジェクトレイヤー、アイテムレイヤーといったものを持っており、
更にゲームシステムを担当するオブジェクトも持っています。
これにより、マップ毎に異なるゲームシステムの採用や、同じマップをいくつかのゲームシステムで動作させる、といったことができます。

tk.Canvasのサブクラスなため、実際の画面への描画や、キャンバス情報の取得、アニメーションといった処理も担当します。

"""
import tkinter as tk
from tkinter import filedialog
from broccoli.conf import settings
from broccoli.layer import EmptyObjectLayer, EmptyItemLayer
from broccoli.system import BaseSystem


class GameCanvas2D(tk.Canvas):
    """2Dゲームキャンバスの基底クラス。

    - 背景(tile)を管理するtile_layer
    - 物体(object)を管理するobject_layer
    - アイテム(item)を管理するitem_layer
    の3層で構成されています。

    """

    def __init__(self, tile_layer, master=None, name='名前のないマップ', manager=None, system=None, object_layer=None, item_layer=None):
        self.manager = manager
        self.name = name

        # 背景層
        self.tile_layer = tile_layer
        self.tile_layer.canvas = self

        # 物体層。object_layerがNoneなら、object_layerが何もない(layer内が全てNone)なEmptyObjectLayerを利用する。
        if object_layer is None:
            object_layer = EmptyObjectLayer()
        self.object_layer = object_layer
        self.object_layer.canvas = self
        self.object_layer.tile_layer = self.tile_layer

        # アイテム層。item_layerがNoneなら、item_layerが何もない(layer内が全てNone)ならEmptyItemLayerを利用する
        if item_layer is None:
            item_layer = EmptyItemLayer()
        self.item_layer = item_layer
        self.item_layer.canvas = self
        self.item_layer.tile_layer = self.tile_layer

        # ゲームシステムを保持する。
        if system is None:
            system = BaseSystem()
        self.system = system
        self.system.canvas = self

        # マップ全体の高さと幅
        max_height = self.tile_layer.y_length * settings.CELL_HEIGHT
        max_width = self.tile_layer.x_length * settings.CELL_WIDTH

        # Canvas内をスクロール可能にし、スクロールの最大値を設定
        scroll_region = (0, 0, max_width, max_height)
        super().__init__(master=master, scrollregion=scroll_region, width=settings.GAME_WIDTH, height=settings.GAME_HEIGHT)

        # マップとシステムの初期設定
        self.tile_layer.create()
        self.object_layer.create()
        self.item_layer.create()
        self.system.setup()

    def start(self):
        """このマップを楽しく遊ぶことができます。"""
        # ゲームのシステムクラスを動作させる。
        self.system.start()

    def move_camera(self, target):
        """ターゲットにピントを合わせる。

        実際は、キャンバス内をスクロールしているだけです。
        super().__init__(scrollregion=(0, 0, 1000, 1000)...としている場合、
        内部的には仮想的なサイズとして1000pxをCanvasは持っており、スクロールできるようになります。
        yview_movetoには、割合を渡す必要があり、0.0から1.0までの範囲です。

        1.0ならば1000px部分までスクロール、0.5ならば500px部分までスクロール、のように動作します。

        """

        # 単純にtarget.y / self.tile_layer.y_lengthのようにすると、キャラクターが一番上や左に配置されるようにスクロールされる
        # 5セル分の表示ならば、更に上を2つ空けるほうが見栄えがよくなります。
        # DISPLAY_Y_NUM//2 とすると、5セルなら上に2つ空けて、7セルなら上に3つ空けて、といった具合になります。
        fractal_x = (target.x-settings.DISPLAY_X_NUM//2) / self.tile_layer.x_length
        fractal_y = (target.y-settings.DISPLAY_Y_NUM//2) / self.tile_layer.y_length
        self.xview_moveto(fractal_x)
        self.yview_moveto(fractal_y)

    def get_current_position_nw(self):
        """今現在表示しているエリアの、左上の座標を返す(px)。

        画面の左上に何かを配置したいが、rootに直接placeできない場合に利用してください。
        具体的には、ImgDialogのように背景が透明な枠を配置したい場合に便利です。

        """
        x, y = self.canvasx(0) + 1, self.canvasy(0) + 1
        return x, y

    def get_current_position_center(self):
        """今現在表示しているエリアの、中央の座標を返す。

        画面の中央に何かを配置したいが、rootに直接placeできない場合に利用してください。
        具体的には、ImgDialogのように背景が透明な枠を配置したい場合に便利です。

        """
        x, y = self.canvasx(0) + 1, self.canvasy(0) + 1
        center_x = x + settings.GAME_WIDTH / 2
        center_y = y + settings.GAME_HEIGHT / 2
        return center_x, center_y

    def check_position(self, x, y):
        """座標が正常かチェックする。

        x, yはレイヤ内の座標です。

        - x, yがマイナスの値の場合
        - マップの範囲外の場合
        にはFalseを返します。

        """
        if x < 0 or y < 0 or x >= self.tile_layer.x_length or y >= self.tile_layer.y_length:
            return False

        return True

    def to_json(self, event=None):
        """現在のマップデータを、jsonで出力する。"""
        file_path = filedialog.asksaveasfilename(title='背景の保存先')
        if file_path:
            self.tile_layer.to_json(file_path)

        file_path = filedialog.asksaveasfilename(title='オブジェクトの保存先')
        if file_path:
            self.object_layer.to_json(file_path)

        file_path = filedialog.asksaveasfilename(title='アイテムの保存先')
        if file_path:
            self.item_layer.to_json(file_path)

    def get_index_from_xy(self, click_x, click_y):
        """絶対座標を元にレイヤ内でのxyを返す。

        例えば、クリックされた座標にあるマテリアルを取得したい場合に有効です。

        # クリック座標(event.x, event.y)を、キャンバス内の絶対座標に変換
        canvas_x = self.canvasx(event.x)
        canvas_y = self.canvasy(event.y)

        x, y = self.get_index_from_xy(canvas_x, canvas_y)
        tile = self.tile_layer[y][x]

        """
        click_x /= settings.CELL_WIDTH
        click_y /= settings.CELL_HEIGHT
        for x, y, tile in self.tile_layer.all():
            if x <= click_x <= x + 1:
                if y <= click_y <= y + 1:
                    return x, y

    def simple_move(self, obj_id, x, y):
        """layer[y][x]にキャラクターを移動する、ショートカットメソッドです。

        x, yはlayer内での座標です。

        """
        self.coords(obj_id, x*settings.CELL_WIDTH, y*settings.CELL_HEIGHT)

    def move_to_animation(self, obj_id, from_x, from_y, to_x, to_y, times=0.1, frame=10):
        """今の場所から、layer[y][x]に向かって移動するアニメーションを行います。

        x, yはlayer内の座標です。
        timesの時間をかけて、frame回描画します。

        """
        current_x = from_x * settings.CELL_WIDTH
        current_y = from_y * settings.CELL_HEIGHT
        target_x = to_x * settings.CELL_WIDTH
        target_y = to_y * settings.CELL_HEIGHT
        diff_x = target_x - current_x
        diff_y = target_y - current_y
        step_x = diff_x / frame
        step_y = diff_y / frame
        for i in range(1, frame+1):
            self.coords(obj_id, current_x+step_x*i, current_y+step_y*i)
            self.update_idletasks()
            self.after(int(times/frame*1000))
            self.lift(obj_id)

    def simple_damage_line(self, x, y, width=2, fill='red', times=0.1):
        """キャラの右上から左下にかけて、線をつける。

        x, yはlayer内の座標です。

        """
        damage_line = self.create_line(
            x*settings.CELL_WIDTH+settings.CELL_WIDTH,  # セルの幅も加えることを忘れずに
            y*settings.CELL_HEIGHT,
            x*settings.CELL_WIDTH,
            y*settings.CELL_HEIGHT+settings.CELL_HEIGHT,  # セルの高さも加えることを忘れずに
            width=width, fill=fill,
        )
        self.update_idletasks()  # すぐに描画する
        # デフォルトでは、0.1秒後にダメージ線を消す
        self.after(int(times*1000))
        self.delete(damage_line)

    def create_material(self, material):
        """マテリアルの描画を行う。

        レイヤークラスのcreate_materialメソッドから呼ばれます。

        このcreate_materialを直接呼び出すケースは少なく、
        描画処理の際のフックとして利用するのが多いと思われます。

        """
        material_id = self.create_image(
            material.x*settings.CELL_WIDTH,
            material.y*settings.CELL_HEIGHT,
            image=material.image, anchor='nw'
        )
        material.id = material_id
