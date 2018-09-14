"""ゲーム中のキャラクターやオブジェクトに関するモジュール。

object_layerに格納されます。

"""

from broccoli import const
from broccoli.funcstions import roguelike, generic
from broccoli.material.base import BaseMaterial


class BaseObject(BaseMaterial):
    pass


class RogueLikeObject(BaseObject):
    see_x = 2
    see_y = 2
    kind = const.NEUTRAL
    hp = -1
    max_hp = -1
    power = -1
    items = []
    action = roguelike.object.action
    move = roguelike.object.move
    attack = roguelike.object.attack
    random_walk = roguelike.object.random_walk
    is_enemy = roguelike.object.is_enemy
    on_damage = roguelike.object.on_damage
    die = roguelike.object.die
    towards = roguelike.object.towards
    get_enemies = roguelike.object.get_enemies
    talk = generic.do_nothing
    message = ''

    attrs = [
        'see_x', 'see_y', 'kind', 'hp', 'max_hp', 'power', 'items',
        'action', 'move', 'attack', 'random_walk', 'is_enemy', 'on_damage', 'die', 'towards', 'get_enemies', 'talk', 'message',
    ]
    func_attrs = ['action', 'move', 'attack', 'random_walk', 'is_enemy', 'on_damage', 'die', 'towards', 'get_enemies', 'talk']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # items内のアイテムを、実際にインスタンス化する。
        self.items = [cls(owner=self, system=self.system, **item_kwargs) for cls, item_kwargs in self.items]
