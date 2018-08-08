import json
import random
from broccoli import register
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
            self.create_material(material_cls=item, direction=-1, diff=-1)


class PythonItemLayer(BaseItemLayer):
    """Pythonコードからアイテムレイヤを作成する。

    item=PythonItemLayer(
        item_list=[
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 2, 0, 0],
            [0, 0, 0, 0, 0],
        ],
        context={
            1: (HealingHerb, {}),
            2: (HealingHerb, {'direction': 2}),
        },
    ),
    のようにして作成することができます。

    """
    def __init__(self, item_list, context):
        super().__init__()
        self.item_list = item_list
        self.context = context

    def create_layer(self):
        for y, row in enumerate(self.item_list):
            for x, col in enumerate(row):
                try:
                    item_cls, kwargs = self.context[col]
                except KeyError:
                    pass
                else:
                    self.create_material(material_cls=item_cls, x=x, y=y, **kwargs)


class JsonItemLayer(BaseItemLayer):
    """オブジェクトをJSONから読み込んで作成する。"""

    def __init__(self, file_path):
        super().__init__()
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        self.data = data['layer']

    def create_layer(self):
        for y, row in enumerate(self.data):
            for x, col in enumerate(row):
                if col:
                    for item in col:
                        class_name = item['class_name']
                        kwargs = item['kwargs']
                        cls = register.items[class_name]
                        self.create_material(material_cls=cls, x=x, y=y, **kwargs)
