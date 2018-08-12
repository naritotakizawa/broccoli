"""ゲーム中のアイテムに関するモジュール。

Mapクラスにおける、item_layerに格納されるクラス群です。

"""
from broccoli.material.base import BaseMaterial


class BaseItem(BaseMaterial):
    """全てのアイテムの基底クラス。"""
    name = 'ベースアイテム'
    default_power = 0

    def __init__(self, direction=0, diff=0, name=None, owner=None):
        super().__init__(direction=direction, diff=diff, name=name)
        self.power = type (self).default_power
        self.owner = owner


class HealingItem(BaseItem):
    """回復アイテムの基底クラス。"""
    name = '回復アイテム'
    default_power = 1

    def use(self):
        """使う"""
        self.owner.hp += self.power
        if self.owner.hp >= self.owner.max_hp:
            self.owner.hp = self.owner.max_hp
        self.owner.items.remove(self)  # 通常は使ったら消える
        self.system.add_message('{}は\n{}を使った!'.format(self.owner.name, self.name))
