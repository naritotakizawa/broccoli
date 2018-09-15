"""オブゾェクトレイヤの具象クラスを提供する。"""
import json
import random
from broccoli import serializers
from broccoli.layer import BaseObjectLayer


class PythonObjectLayer(BaseObjectLayer):
    """Pythonコードからオブジェクトレイヤを作成する

    object_layer=PythonObjectLayer(
        [
            [(Sheep, {}), None],
            [None, None],
        ]
    ),
    のようにして作成することができます。

    """
    def __init__(self, data):
        super().__init__()
        self.data = data

    def create_layer(self):
        for y, row in enumerate(self.data):
            for x, col in enumerate(row):
                try:
                    cls, kwargs = col
                except TypeError:
                    pass
                else:
                    self.create_material(material_cls=cls, x=x, y=y, **kwargs)


class EmptyObjectLayer(BaseObjectLayer):
    """何もオブジェクトを作らない。

    layer内を全てNoneで初期化します。
    エディタ等で、真っさらなマップを作成したい場合に有用です。

    """

    def __init__(self):
        super().__init__()

    def create_layer(self):
        pass


class RandomObjectLayer(BaseObjectLayer):
    """オブジェクトをランダム生成する。"""

    def __init__(self, enemies, number_of_enemies):
        super().__init__()
        self.enemies = enemies
        self.number_of_enemies = number_of_enemies

    def create_layer(self):
        for i in range(self.number_of_enemies):
            enemy = random.choice(self.enemies)
            # ランダム生成の場合は、向きや差分もランダム。
            self.create_material(material_cls=enemy, direction=-1, diff=-1)


class JsonObjectLayer(BaseObjectLayer):
    """オブジェクトをJSONから読み込んで作成する。"""

    def __init__(self, file_path):
        super().__init__()
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file, cls=serializers.JsonDecoder)
        self.data = data['layer']

    def create_layer(self):
        for y, row in enumerate(self.data):
            for x, col in enumerate(row):
                if col is not None:
                    obj_cls, kwargs = col
                    self.create_material(material_cls=obj_cls, x=x, y=y, **kwargs)
