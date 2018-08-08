"""ゲーム中のキャラクターに関するモジュール。

物体やキャラクターといったものが該当します。
Mapクラスにおける、object_layerに格納されるクラス群です。

"""
import random
from broccoli import const
from broccoli.material.base import BaseMaterial


class BaseObject(BaseMaterial):
    name = 'ベースオブジェクト'
    description = 'オブジェクトのベースクラスです。この説明が見えていると、何かおかしいぞ!'
    default_hp = -1
    default_power = -1
    see_x = 2
    see_y = 2
    kind = const.NEUTRAL

    def __init__(self, direction=0, diff=0, name=None, kind=None, items=None):
        super().__init__(direction, diff, name)
        self.max_hp = self.hp = type(self).default_hp
        self.power = type(self).default_power
        if kind is None:
            self.kind = type(self).kind
        else:
            self.kind = kind
        if items is None:
            self.items = []
        else:
            self.items = items

    def action(self):
        """オブジェクトの行動処理。

        マップクラスからは、基本的にこのメソッドだけ呼ばれます。
        必要に応じて、内部で移動や攻撃などを呼び出してください。

        """
        pass

    def is_enemy(self, obj):
        """自分にとって敵ならTrue、そうでなければFalse。

        引数:
            obj: 相手

        """
        return False

    def on_damage(self, tile, obj):
        """攻撃を食らった際の処理。

        攻撃を食らった際に呼ばれるメソッドです。
        基本的には、このメソッドでダメージ増減等を行ってください。。

        このメソッドは、攻撃可能なオブジェクト(主にキャラクター)のattackメソッド内で
        呼ばれることを想定しています。

        引数:
            tile: 今、自分が乗っている背景
            obj: 攻撃してくるオブジェクト

        """
        pass

    def on_die(self, tile, obj):
        """HPが0になった際の処理。

        on_damage内で呼ばれることを想定しています。
        キャラクターの削除処理を行っています。

        引数:
            tile: 今、自分が乗っている背景
            obj: 攻撃してくるオブジェクト

        """
        pass

    def damage_motion(self, times=0.1):
        """攻撃を食らった際のアニメーション処理。"""
        pass

    def can_move(self, x, y):
        """座標が、自分にとって移動可能(配置可能)かどうかをチェックする。"""
        obj, tile = self.canvas.check_position(x, y)
        # 背景があり、オブジェクトがなくて、通行可能な背景ならばTrue
        if tile is not None and obj is None and tile.is_public(self):
            return True, obj, tile
        else:
            return False, None, None


class UnBreakableObject(BaseObject):
    """何も行動せず、死なないオブジェクト。"""
    name = '壊れないオブジェクト'
    description = '木や岩など、何も行動ないものに設定してください。'


class BreakableObject(BaseObject):
    """壊れるオブジェクト。"""
    name = '壊れるオブジェクト'
    description = '行動はしないが、壊れるものに設定してください。'
    default_hp = 10
    default_power = 10
    kind = const.ENEMY

    def is_enemy(self, obj):
        """壊れるオブジェクトのデフォルトは、主人公と敵対です。"""
        # 自身がPLAYERなら、ENEMYを敵とみなす
        if self.kind == const.PLAYER:
            if obj.kind == const.ENEMY:
                return True
            else:
                return False

        # 自身がENEMYなら、PLAYERは敵とみなす
        elif self.kind == const.ENEMY:
            if obj.kind == const.PLAYER:
                return True
            else:
                return False

        # NEUTRALなら、みんな友達
        return False

    def on_damage(self, tile, obj):
        """ダメージをうける。"""
        self.canvas.simple_damage_line(self.x, self.y)
        self.hp -= obj.power
        self.system.add_message('{}の攻撃!\n{}は{}のダメージを受けた!'.format(obj.name, self.name, obj.power))
        if self.hp <= 0:
            self.on_die(tile, obj)

    def on_die(self, tile, obj):
        """死んだらキャンバス上から消える"""
        self.system.add_message('{}は倒れた!'.format(self.name))
        self.canvas.delete(self.id)
        self.canvas.object_layer[self.y][self.x] = None


class Character(BreakableObject):
    """通常のキャラクター。

    行動し、攻撃したり移動したりします。

    """

    def move(self, tile):
        """移動処理。

        実際の移動処理を行い、背景のon_selfを呼び出します。
        このメソッドを上書きする際、背景のon_selfをは最後に呼び出すようにしてください。
        on_selfで他のマップへ移動したり、ちがうx,y座標にジャンプさせることがありますが
        このメソッドの先頭で呼び出してしまうと、その後のy,x座標の代入やレイヤの参照で問題が発生します。

        引数:
            tile: 移動先の背景

        """
        # object_layer内の移動元にNone(誰もいない状態)にする
        self.canvas.object_layer[self.y][self.x] = None

        # object_layer内の移動先にキャラクターを設定
        self.canvas.object_layer[tile.y][tile.x] = self

        # y、x座標を更新
        self.y = tile.y
        self.x = tile.x

        # 移動する
        self.canvas.simple_move(self.id, self.x, self.y)

        # アイテムの取得
        items = self.canvas.item_layer[self.y][self.x]
        if items:
            messages = []
            for item in items:
                item.owner = self
                self.items.append(item)
                self.canvas.delete(item.id)
                messages.append('{}は{}を拾った!'.format (self.name, item.name))

            self.canvas.item_layer[self.y][self.x] = []
            self.system.add_message('\n'.join(messages))

        # 必ず最後に
        tile.on_self(self)

    def attack(self, tile, obj):
        """攻撃処理。

        一般的な流れとしては、まず攻撃モーションを呼び出します。
        if obj is not None でオブジェクトが存在するかを確認し
        存在していればオブジェクトのon_damageメソッドを呼び出します。

        引数:
            tile: 攻撃先の背景。オブジェクトはないことがあるので(Noneの場合があるので)、背景を目印に攻撃する
            obj: 攻撃先のオブジェクト。なければNone

        """
        # 攻撃モーション
        self.canvas.move_to_animation(self.id, self.x, self.y, tile.x, tile.y)

        # 移動先にオブジェクトがあれば、そいつのon_damageを呼び出す
        if obj is not None:
            obj.on_damage(tile, self)

        # 基の位置に戻す
        self.canvas.simple_move(self.id, self.x, self.y)

    def action(self):
        """キャラクターの行動。"""
        # 4方向に攻撃できそうなのがいれば、攻撃する
        for direction, x, y in self.get_4_position():
            ok, obj, tile = self.can_attack(x, y)
            if ok:
                self.direction = direction
                self.attack(tile, obj)
                break

        # 4方向に攻撃できそうなのがいない
        else:
            # 周囲の敵対キャラを探す
            enemies = list(self.get_enemies())

            # 敵がいれば、一番近いのを探し、そいつに向かって移動
            if enemies:
                target = self.get_nearest(enemies)
                self.towards(target)  # 敵に向かって歩く

            # 敵がいなければ、ランダムに歩く
            else:
                self.random_walk()

    def towards(self, material):
        """対象に向かって移動する。"""
        # 相手が右側にいる
        if self.x < material.x:
            x = self.x + 1
            y = self.y
            ok, obj, tile = self.can_move(x, y)
            if ok:
                self.direction = const.RIGHT
                self.move(tile)
                return

        # 相手が左側にいる
        if self.x > material.x:
            x = self.x - 1
            y = self.y
            ok, obj, tile = self.can_move(x, y)
            if ok:
                self.direction = const.LEFT
                self.move(tile)
                return

        # 相手が下側にいる
        if self.y < material.y:
            x = self.x
            y = self.y + 1
            ok, obj, tile = self.can_move(x, y)
            if ok:
                self.direction = const.DOWN
                self.move(tile)
                return

        # 相手が上側にいる
        if self.y > material.y:
            x = self.x
            y = self.y - 1
            ok, obj, tile = self.can_move(x, y)
            if ok:
                self.direction = const.UP
                self.move(tile)
                return

    def can_attack(self, x, y):
        """座標に、自分が攻撃できる相手がいるかをチェックする。"""
        obj, tile = self.canvas.check_position(x, y)
        # 背景があり、オブジェクトがあり、敵対しているならばTrue
        if tile is not None and obj is not None and self.is_enemy(obj):
            return True, obj, tile
        else:
            return False, None, None

    def get_enemies(self, see_x=None, see_y=None):
        """自分の周りの敵を返す。

        see_x、see_yは範囲です。指定しなければ、デフォルト値としてクラス属性が使われます。
        クラス属性のデフォルトは、2です。

        """
        see_x = see_x or self.see_x
        see_y = see_y or self.see_y
        for x, y, obj in self.canvas.object_layer.all(include_none=False):
            if abs(self.x-x) <= see_x and abs(self.y-y) <= see_y:
                if obj.is_enemy(self) and obj != self:
                    yield obj

    def get_4_position(self):
        """4方向の座標を取得するショートカットメソッドです。

        [
            (DOWN, self.x, self.y+1),
            (LEFT, self.x-1, self.y),
            (RIGHT, self.x+1, self.y),
            (UP, self.x, self.y - 1),
        ]
        といったリストを返します。
        DOWNなどは向きに直接代入できる定数です。

        デフォルトではシャッフルして返しますので、必ずしも下座標から取得できる訳ではありません。

        """
        positions = [
            (const.DOWN, self.x, self.y+1),
            (const.LEFT, self.x-1, self.y),
            (const.RIGHT, self.x+1, self.y),
            (const.UP, self.x, self.y-1),
        ]
        random.shuffle(positions)
        return positions

    def random_walk(self):
        """ランダムに移動する"""
        for direction, x, y in self.get_4_position():
            ok, obj, tile = self.can_move(x, y)
            if ok:
                self.direction = direction
                self.move(tile)
                break
