"""ゲーム中のアイテムに関するモジュール。

item_layerに格納されます。

"""
from broccoli.funcstions import roguelike, do_nothing
from broccoli.material.base import BaseMaterial


class BaseItem(BaseMaterial):
    """全てのアイテムの基底クラス。"""

    def __init__(self, owner=None, **kwargs):
        super().__init__(**kwargs)
        self.owner = owner


class RogueLikeItem(BaseItem):
    power = 0
    use = do_nothing

    attrs = ['power', 'use']
    func_attrs = ['use']
