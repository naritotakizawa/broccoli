"""ゲーム中のキャラクターに関するモジュール。

物体やキャラクターといったものが該当します。
Mapクラスにおける、object_layerに格納されるクラス群です。

"""

from broccoli import const
from broccoli.funcstions import roguelike
from broccoli.material.base import BaseMaterial


class BaseObject(BaseMaterial):
    pass


class RogueLikeObject(BaseObject):
    attrs = {
        'see_x': 2,
        'see_y': 2,
        'kind': const.NEUTRAL,
        'hp': -1,
        'max_hp': -1,
        'power': -1,
        'items': [],
        'action': roguelike.object.action,
        'move': roguelike.object.move,
        'attack': roguelike.object.attack,
        'random_walk': roguelike.object.random_walk,
        'is_enemy': roguelike.object.is_enemy,
        'on_damage': roguelike.object.on_damage,
        'die': roguelike.object.die,
        'towards': roguelike.object.towards,
        'get_enemies': roguelike.object.get_enemies,
    }

