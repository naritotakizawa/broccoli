"""ゲーム中のアイテムに関するモジュール。

Mapクラスにおける、item_layerに格納されるクラス群です。

"""
from broccoli.funcstions.roguelike import rogue_use
from broccoli.material.base import BaseMaterial


class BaseItem(BaseMaterial):
    """全てのアイテムの基底クラス。"""

    def __init__(self, direction=0, diff=0, name=None, owner=None, **kwargs):
        super().__init__(direction=direction, diff=diff, name=name, **kwargs)
        self.owner = owner


class RogueLikeItem(BaseItem):
    attrs = {
        'power': 0,
        'use': rogue_use,
    }
    func_attrs = {'use'}
