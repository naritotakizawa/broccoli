"""ゲームのシステム部分に関するモジュール。

現在は、ローグライクに使えそうなシステムクラスだけを提供しています。
つまり、左右上下に移動ができ、攻撃ができ、自分の番が終わったら敵達が行動する、といったものです。

"""
import tkinter as tk
import tkinter.ttk as ttk
from broccoli.material.object import *
from broccoli.dialog import LogAndActiveMessageDialog, ListDialog
from broccoli.conf import settings
from .base import BaseSystem, set_method


class RogueLikeSystem(BaseSystem):
    """ローグライクに使えそうなシステムクラスの基底。"""
    # HPやターン数の表示に関する設定
    text_size = 18
    text_font = settings.DEFAULT_TEXT_FONT
    font = (text_font, text_size)
    color = settings.DEFAULT_TEXT_COLOR

    def __init__(self, message_class=LogAndActiveMessageDialog, show_item_dialog_class=ListDialog):
        super().__init__()
        # 現在ターンを表す変数
        self.turn = 0

        self.message_class = message_class
        self.show_item_dialog_class = show_item_dialog_class

    def create_object(self, material_cls, **kwargs):
        material = super().create_object(material_cls, **kwargs)
        material.max_hp = material.hp = material_cls.rogue_hp
        material.power = material_cls.rogue_power
        material.items = []

        set_method(material, 'rogue_action', rename_attr='action', default=action, kwargs=kwargs)
        set_method(material, 'rogue_random_walk', rename_attr='random_walk', default=random_walk, kwargs=kwargs)
        set_method(material, 'rogue_move', rename_attr='move', default=move, kwargs=kwargs)
        set_method(material, 'rogue_is_enemy', rename_attr='is_enemy', default=is_enemy, kwargs=kwargs)
        set_method(material, 'rogue_on_damage', rename_attr='on_damage', default=on_damage, kwargs=kwargs)
        set_method(material, 'rogue_on_die', rename_attr='on_die', default=on_die, kwargs=kwargs)
        set_method(material, 'rogue_attack', rename_attr='attack', default=attack, kwargs=kwargs)
        set_method(material, 'rogue_towards', rename_attr='towards', default=towards, kwargs=kwargs)
        set_method(material, 'rogue_get_enemies', rename_attr='get_enemies', default=get_enemies, kwargs=kwargs)
        return material

    def setup(self):
        # メッセージクラスのインスタンス化
        self.message = self.message_class(parent=self, canvas=self.canvas)

    def start(self):
        # 0.1 秒ぐらいごとに、ゲームの状態を監視する
        self.canvas.after(100, self.monitor_game)
        self.create_key_event()

    def get_key_events(self):
        """このシステムのキーイベントを返す。"""
        return [
            ('<{}>'.format(settings.UP_KEY), self.move),
            ('<{}>'.format(settings.LEFT_KEY), self.move),
            ('<{}>'.format(settings.RIGHT_KEY), self.move),
            ('<{}>'.format(settings.DOWN_KEY), self.move),
            ('<{}>'.format(settings.ATTACK_KEY), self.attack),
            ('<{}>'.format (settings.SHOW_ITEM_KEY), self.show_item_dialog),
            ('<{}>'.format (settings.SHOW_MESSAGE_KEY), self.message.show),
        ]

    def move(self, event):
        """移動キーを押した際のメソッド。"""
        pass

    def attack(self, event):
        """攻撃キーを押した際のメソッド。"""
        pass

    def update_game_info(self):
        """ゲームの情報を表示する。

        0.1秒ごとに呼ばれるので、常に表示したいデータをここで表示すると便利です。

        """
        pass

    def monitor_game(self):
        """ゲームの状態を監視。0.1秒ごとにhpなどを表示する。"""
        self.update_game_info()
        self.canvas.after(100, self.monitor_game)

    def act_object(self, obj):
        """オブジェクトの行動を呼び出す。

        このメソッドは、ゲームがロック状態ならば解除されるまで待ち
        解除されてからオブジェクトの行動を呼びます。
        基本的に、特定のオブジェクトを行動させるにはこのメソッドを呼んでください。

        """
        if self.is_block:
            self.canvas.after(100, self.act_object, obj)
        else:
            obj.action()

    def act_objects(self, exclude=()):
        """全てのオブジェクトの行動を呼びだします。

        action呼び出しを無視したいキャラクターがいれば、exclude引数に渡してください。

        """
        # オブジェクト一覧を取得
        objects = [obj for _, _, obj in self.canvas.object_layer.all(include_none=False) if obj not in exclude]
        for obj in objects:
            # 生きていれば行動する。objectsリストはビューオブジェクトのようなものではなく、その時点でのリスト
            # そのため、取得時は生きていても今生きているかはわからない。
            if obj.hp > 0:
                self.act_object(obj)

    def add_message(self, message):
        """メッセージを表示する。

        ローグ系のゲームでは、メッセージをどこかに表示することがよくあります。
        どこに表示するかは、message_classによって変わります。

        """
        self.message.add(message)

    def show_item_dialog(self, event):
        """アイテムリストを表示する。"""
        pass


class RogueWithPlayer(RogueLikeSystem):
    """プレイヤーがいるローグライクシステム。"""

    def setup(self,):
        super().setup()
        # プレイヤーがいないとダメ
        self.player = self.canvas.manager.player
        self.canvas.object_layer.create_material(material_cls=self.player)
        self.canvas.move_camera(self.player)  # 主人公位置に合わせて表示部分を動かす

    def move(self, event):
        """主人公の移動処理。"""
        y, x = self.player.y, self.player.x
        if event.char == settings.DOWN_KEY:
            self.player.direction = const.DOWN
            y += 1
        elif event.char == settings.LEFT_KEY:
            self.player.direction = const.LEFT
            x -= 1
        elif event.char == settings.RIGHT_KEY:
            self.player.direction = const.RIGHT
            x += 1
        elif event.char == settings.UP_KEY:
            self.player.direction = const.UP
            y -= 1

        # 移動可能な座標なら移動し、ターンを進める。移動不可能ならターン経過はなし
        ok, obj, tile = self.player.can_move(x, y)
        if ok:
            self.player.move(tile)
            try:
                self.canvas.move_camera(self.player)
            except Exception:
                # moveは背景のon_selfを呼び出しますが、その際次マップへ移動している可能性があります。
                # 次マップへ移動している場合、canvas.move_cameraが参照しているcanvasオブジェクトは
                # destroy済みで例外が送出され、ここにきます。act_objectsなどの他の処理をする必要はないため、pass
                pass
            else:
                self.act_objects(exclude=[self.player])
                self.turn += 1

    def attack(self, event):
        """主人公の攻撃処理。"""
        y, x = self.player.y, self.player.x
        if self.player.direction == const.DOWN:
            y += 1
        elif self.player.direction == const.LEFT:
            x -= 1
        elif self.player.direction == const.RIGHT:
            x += 1
        elif self.player.direction == const.UP:
            y -= 1

        # マップの範囲外ならやめる。範囲内なら、とりあえず攻撃させる。素振りなどもしたいかも
        obj, tile = self.canvas.check_position(x, y)
        if tile is None:
            return

        self.player.attack(tile, obj)
        self.canvas.move_camera(self.player)
        self.act_objects(exclude=[self.player])
        self.turn += 1

    def create_game_info(self):
        """ターン数やプレイヤーHPなどの表示枠を作成する。"""
        root = self.canvas.winfo_toplevel()
        # 表示部分の枠を作成し、配置
        game_info = tk.Canvas(
            master=root, bg='lavender',
            width=settings.GAME_WIDTH, height=30,
            highlightthickness=0,  # 枠線を消す
        )
        game_info.place(x=0, y=0)

        # 更新に使うStringVarの生成
        self.turn_var = tk.StringVar()
        self.player_hp_var  = tk.StringVar()

        # 表示枠(tk.Canvas)に配置するラベルの生成
        turn_label = ttk.Label(
            game_info, textvariable=self.turn_var,
            font=self.font, foreground=self.color, background='lavender'
        )

        hp_label = ttk.Label(
            game_info, textvariable=self.player_hp_var,
            font=self.font, foreground=self.color, background='lavender'
        )

        # 生成したラベルを、表示枠(tk.Canvas)に配置
        game_info.create_window(
            0, 0,
            anchor='nw',
            window=hp_label,
        )
        game_info.create_window(
            settings.GAME_WIDTH, 0,
            anchor='ne',
            window=turn_label,
        )

        self._game_info = game_info

    def update_game_info(self):
        """プレイヤーのHPやターン数を更新する。"""
        if not hasattr(self, '_game_info'):
            self.create_game_info()
        self.turn_var.set('{}ターン'.format(self.turn))
        self.player_hp_var.set('HP {}/{}'.format(self.player.hp, self.player.max_hp))

    def show_item_dialog(self, event):
        """アイテムリストを表示する。"""
        dialog = self.show_item_dialog_class(parent=self, canvas=self.canvas)
        dialog.show(items=self.player.items, callback=lambda item: item.use())


class RogueNoPlayer(RogueLikeSystem):
    """プレイヤーのいない、観戦用モード。"""

    def setup(self):
        super().setup()

        # 中央にカメラ移動
        self.x = self.canvas.tile_layer.x_length // 2
        self.y = self.canvas.tile_layer.y_length // 2
        self.canvas.move_camera(self.canvas.tile_layer[self.y][self.x])

    def move(self, event):
        """カメラ移動処理。"""
        y, x = self.y, self.x
        if event.char == settings.DOWN_KEY:
            y += 1
        elif event.char == settings.LEFT_KEY:
            x -= 1
        elif event.char == settings.RIGHT_KEY:
            x += 1
        elif event.char == settings.UP_KEY:
            y -= 1

        obj, tile = self.canvas.check_position(x, y)
        if tile is None:
            return

        self.x = x
        self.y = y
        self.canvas.move_camera(self.canvas.tile_layer[self.y][self.x])

    def attack(self, event):
        """攻撃キーで次ターンになります。"""
        self.act_objects()
        self.turn += 1

    def create_game_info(self):
        """ターン数やプレイヤーHPなどの表示枠を作成する。"""
        root = self.canvas.winfo_toplevel()
        # 表示部分の枠を作成し、配置
        game_info = tk.Canvas(
            master=root, bg='lavender',
            width=settings.GAME_WIDTH, height=30,
            highlightthickness=0,  # 枠線を消す
        )
        game_info.place(x=0, y=0)

        # 更新に使うStringVarの生成
        self.turn_var = tk.StringVar()

        # 表示枠(tk.Canvas)に配置するラベルの生成
        turn_label = ttk.Label(
            game_info, textvariable=self.turn_var,
            font=self.font, foreground=self.color, background='lavender'
        )

        # 生成したラベルを、表示枠(tk.Canvas)に配置
        game_info.create_window(
            settings.GAME_WIDTH, 0,
            anchor='ne',
            window=turn_label,
        )

        self._game_info = game_info

    def update_game_info(self):
        """プレイヤーのHPやターン数を更新する。"""
        if not hasattr(self, '_game_info'):
            self.create_game_info()
        self.turn_var.set('{}ターン'.format(self.turn))
