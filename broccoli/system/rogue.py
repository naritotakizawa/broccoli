"""ローグライク系ゲームのゲームシステムを提供する。

左右上下に移動ができ、攻撃ができ、自分の番が終わったら敵達が行動する、とゲームシステムが主です。

"""
import tkinter as tk
import tkinter.ttk as ttk
from broccoli import register, parse_xy
from broccoli.conf import settings
from broccoli.dialog import LogAndActiveMessageDialog, ListDialog
from broccoli.material.object import *
from .base import BaseSystem


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

    def setup(self):
        # メッセージクラスのインスタンス化
        self.message = self.message_class(parent=self, canvas=self.canvas)

    def start(self):
        # 0.1 秒ぐらいごとに、ゲームの状態を監視する
        self.canvas.after(100, self.monitor_game)
        self.show_map_name()
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
            ('<{}>'.format(settings.TALK_KEY), self.talk),
            ('<{}>'.format(settings.SAVE_KEY), self.canvas.manager.save),
            ('<{}>'.format(settings.LOAD_KEY), self.canvas.manager.load),
        ]

    def move(self, event):
        """移動キーを押した際のメソッド。"""
        pass

    def attack(self, event):
        """攻撃キーを押した際のメソッド。"""
        pass

    def update_game_info(self):
        """ゲームの情報を更新する。

        デフォルトでは0.1秒ごとに呼ばれます。
        定期的に更新したいデータや表示があれば、上書きしてください。

        """
        pass

    def monitor_game(self):
        """ゲームの状態を監視する。

        update_game_infoを0.1秒毎に呼び出し、ゲーム情報を更新しています。
        秒を変更したかったり、他に呼び出したいメソッドがあれば上書きしてください。

        """
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

    def show_map_name(self):
        """マップ名をかっこよく表示する。"""
        x, y = self.canvas.get_current_position_center()
        text = ''
        for char in self.canvas.name:
            text += char
            self.canvas.delete('start_message')
            self.canvas.create_text(
                x,
                y,
                anchor='center',
                text=text,
                font=self.font,
                fill=self.color,
                tag='start_message',
            )
            self.canvas.after(100)
            self.canvas.update_idletasks()
        self.canvas.after(1000)
        self.canvas.delete('start_message')

    def game_over(self):
        """ゲームオーバー処理。"""
        self.clear_key_event()
        x, y = self.canvas.get_current_position_center()
        self.canvas.create_text(
            x,
            y,
            anchor='center',
            text='Game Over',
            font=self.font,
            fill=self.color,
        )

    def simple_move(self, obj_id, x=None, y=None, material=None):
        """layer[y][x]にキャラクターを移動する、ショートカットメソッドです。"""
        x, y = parse_xy(x, y, material)
        self.canvas.coords(obj_id, x*settings.CELL_WIDTH, y*settings.CELL_HEIGHT)

    def move_to_animation(
            self, obj_id,
            from_x=None, from_y=None, from_material=None,
            to_x=None, to_y=None, to_material=None,
            times=0.1, frame=10):
        """今の場所から、layer[y][x]に向かって移動するアニメーションを行います。

        timesの時間をかけて、frame回描画します。

        """
        # まずレイヤ内の座標に変換する。
        from_x, from_y = parse_xy(from_x, from_y, from_material)
        to_x, to_y = parse_xy(to_x, to_y, to_material)

        current_x = from_x * settings.CELL_WIDTH
        current_y = from_y * settings.CELL_HEIGHT
        target_x = to_x * settings.CELL_WIDTH
        target_y = to_y * settings.CELL_HEIGHT
        diff_x = target_x - current_x
        diff_y = target_y - current_y
        step_x = diff_x / frame
        step_y = diff_y / frame
        for i in range(1, frame+1):
            self.canvas.coords(obj_id, current_x+step_x*i, current_y+step_y*i)
            self.canvas.update_idletasks()
            self.canvas.after(int(times/frame*1000))
            self.canvas.lift(obj_id)

    def simple_damage_line(self, x=None, y=None, material=None, width=2, fill='red', times=0.1):
        """キャラの右上から左下にかけて、線をつける。

        x, yはlayer内の座標です。

        """
        x, y = parse_xy(x, y, material)
        damage_line = self.canvas.create_line(
            x*settings.CELL_WIDTH+settings.CELL_WIDTH,  # セルの幅も加えることを忘れずに
            y*settings.CELL_HEIGHT,
            x*settings.CELL_WIDTH,
            y*settings.CELL_HEIGHT+settings.CELL_HEIGHT,  # セルの高さも加えることを忘れずに
            width=width, fill=fill,
        )
        self.canvas.update_idletasks()  # すぐに描画する
        # デフォルトでは、0.1秒後にダメージ線を消す
        self.canvas.after(int(times*1000))
        self.canvas.delete(damage_line)

    def talk(self, event):
        """話しかける。"""
        pass


class RogueWithPlayer(RogueLikeSystem):
    """プレイヤーがいるローグライクシステム。"""

    def __init__(self, message_class=LogAndActiveMessageDialog, show_item_dialog_class=ListDialog, x=None, y=None):
        super().__init__(message_class=message_class, show_item_dialog_class=show_item_dialog_class)
        # プレイヤーの初期座標
        self.x = x
        self.y = y

    def setup(self,):
        super().setup()
        player_cls, kwargs = self.canvas.manager.vars['player']
        kwargs.update({
            'kind': const.PLAYER,
            'die': register.functions['roguelike.object.player_die'],
        })
        # プレイヤーがいないとダメ
        self.player = self.canvas.object_layer.create_material(
            material_cls=player_cls, x=self.x, y=self.y, **kwargs
        )
        self.canvas.move_camera(material=self.player)  # 主人公位置に合わせて表示部分を動かす

    def move(self, event):
        """主人公の移動処理。"""
        y, x = self.player.y, self.player.x
        if event.char == settings.DOWN_KEY:
            self.player.change_direction(const.DOWN)
            y += 1
        elif event.char == settings.LEFT_KEY:
            self.player.change_direction(const.LEFT)
            x -= 1
        elif event.char == settings.RIGHT_KEY:
            self.player.change_direction(const.RIGHT)
            x += 1
        elif event.char == settings.UP_KEY:
            self.player.change_direction(const.UP)
            y -= 1

        if self.canvas.check_position(x, y):
            tile = self.canvas.tile_layer[y][x]
            obj = self.canvas.object_layer[y][x]
            if obj is None and tile.is_public(obj=self.player):
                self.player.move(tile)
                try:
                    self.canvas.move_camera(material=self.player)
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
        if not self.canvas.check_position(x, y):
            return

        tile = self.canvas.tile_layer[y][x]
        obj = self.canvas.object_layer[y][x]
        self.player.attack(tile, obj)
        self.canvas.move_camera(material=self.player)
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

    def talk(self, event):
        y, x = self.player.y, self.player.x
        if self.player.direction == const.DOWN:
            y += 1
        elif self.player.direction == const.LEFT:
            x -= 1
        elif self.player.direction == const.RIGHT:
            x += 1
        elif self.player.direction == const.UP:
            y -= 1

        # マップの範囲外ならやめる
        if not self.canvas.check_position(x, y):
            return

        obj = self.canvas.object_layer[y][x]
        if obj is not None:
            obj.talk(self.player)


class RogueNoPlayer(RogueLikeSystem):
    """プレイヤーのいない、観戦用モード。"""

    def setup(self):
        super().setup()

        # 中央にカメラ移動
        self.x = self.canvas.tile_layer.x_length // 2
        self.y = self.canvas.tile_layer.y_length // 2
        self.canvas.move_camera(self.x, self.y)

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

        if not self.canvas.check_position(x, y):
            return

        self.x = x
        self.y = y
        self.canvas.move_camera(self.x, self.y)

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
