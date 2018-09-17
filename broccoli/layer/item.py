"""アイテムレイヤの具象クラスを提供する。"""
import json
import random
from broccoli import serializers
from .base import BaseItemLayer


class EmptyItemLayer(BaseItemLayer):
    """何もアイテムを作らない。"""

    def __init__(self):
        super().__init__()

    def create_layer(self):
        pass


class RandomItemLayer(BaseItemLayer):
    """アイテムをランダムに配置する。"""

    def __init__(self, items, number_of_items):
        super().__init__()
        self.items = items
        self.number_of_items = number_of_items

    def create_layer(self):
        for i in range(self.number_of_items):
            item = random.choice(self.items)
            # ランダム配置の場合、向きや差分もランダムです。
            self.create_material(material_cls=item, direction=-1, diff=-1)


class PythonItemLayer(BaseItemLayer):
    """Pythonコードからアイテムレイヤを作成する。

    item_layer=PythonItemLayer(
        [
            [[], []],
            [[], [(Herb, {}), (Herb, {})]],
        ]
    ),
    のようにして作成することができます。
    リストがネストしてわかりにくいですが、2*2マップで右下にHerbが2つ落ちている例です。

    """
    def __init__(self, data):
        super().__init__()
        self.data = data

    def create_layer(self):
        for y, row in enumerate(self.data):
            for x, cols in enumerate(row):
                for col in cols:
                    cls, kwargs = col
                    self.create_material(material_cls=cls, x=x, y=y, **kwargs)


class JsonItemLayer(BaseItemLayer):
    """オブジェクトをJSONから読み込んで作成する。"""

    def __init__(self, file_path):
        super().__init__()
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file, cls=serializers.JsonDecoder)
        self.data = data['layer']

    def create_layer(self):
        for y, row in enumerate(self.data):
            for x, col in enumerate(row):
                for item in col:
                    item_cls, kwargs = item
                    self.create_material(material_cls=item_cls, x=x, y=y, **kwargs)
