"""ゲーム中のキャラクターに関するモジュール。

物体やキャラクターといったものが該当します。
Mapクラスにおける、object_layerに格納されるクラス群です。

"""

from broccoli import const
from broccoli.funcstions.roguelike import (
    rogue_action, rogue_attack, rogue_die, rogue_get_enemies,
    rogue_is_enemy, rogue_move, rogue_on_damage, rogue_towards,
    rogue_random_walk
)
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
        'action': rogue_action,
        'move': rogue_move,
        'attack': rogue_attack,
        'random_walk': rogue_random_walk,
        'is_enemy': rogue_is_enemy,
        'on_damage': rogue_on_damage,
        'die': rogue_die,
        'towards': rogue_towards,
        'get_enemies': rogue_get_enemies,
    }
    func_attrs = {'action', 'move', 'attack', 'random_walk', 'is_enemy', 'on_damage', 'die', 'towards', 'get_enemies'}

