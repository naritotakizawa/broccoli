import json
import random
from broccoli import register
from broccoli.layer import BaseObjectLayer


class PythonObjectLayer(BaseObjectLayer):
    """Pythonコードからオブジェクトレイヤを作成する

    object_layer=PythonObjectLayer(
        map_list=[
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 2, 0, 0],
            [0, 0, 0, 0, 0],
        ],
        context={
            1: (BlownBear, {}),
            2: (WhiteBear, {'direction': 2}),
        },
    ),
    のようにして作成することができます。

    """
    def __init__(self, map_list, context):
        super().__init__()
        self.map_list = map_list
        self.context = context

    def create_layer(self):
        for y, row in enumerate(self.map_list):
            for x, col in enumerate(row):
                try:
                    obj_cls, kwargs = self.context[col]
                except KeyError:
                    pass
                else:
                    self.create_material(material_cls=obj_cls, x=x, y=y, **kwargs)


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
            self.create_material(material_cls=enemy, direction=-1, diff=-1)


class JsonObjectLayer(BaseObjectLayer):
    """オブジェクトをJSONから読み込んで作成する。"""

    def __init__(self, file_path):
        super().__init__()
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        self.data = data['layer']

    def create_layer(self):
        for y, row in enumerate(self.data):
            for x, col in enumerate(row):
                if col is not None:
                    class_name = col['class_name']
                    kwargs = col['kwargs']
                    cls = register.objects[class_name]
                    self.create_material(material_cls=cls, x=x, y=y, **kwargs)
