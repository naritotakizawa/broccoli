"""タイルレイヤの具象クラスを提供する。"""
import json
from broccoli import serializers
from broccoli.layer import BaseTileLayer
from .randomlib import RandomBackgroundCUI


class PythonTileLayer(BaseTileLayer):
    """Pythonコードから背景を作成する。

    tile_layer=PythonTileLayer(
        map_list=[
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1]
        ],
        context={
            1: (WallTile, {}),
            0: (GreenTile, {'direction': 2}),
        }
    ),
    のようにして作成することができます。

    """
    def __init__(self, map_list, context):
        super().__init__(x_length=len(map_list[0]), y_length=len(map_list))
        self.map_list = map_list
        self.context = context

    def create_layer(self):
        for y, row in enumerate(self.map_list):
            for x, col in enumerate(row):
                tile_cls, kwargs = self.context[col]
                self.create_material(material_cls=tile_cls, x=x, y=y, **kwargs)


class SimpleTileLayer(BaseTileLayer):
    """4隅の壁だけがある、見通しの良いマップを作る。

    エディタ等で、真っさらなマップを作成したい場合に有用です。

    """

    def __init__(self, x_length, y_length, inner_tile, outer_tile):
        super().__init__(x_length, y_length)
        self.inner_tile = inner_tile
        self.outer_tile = outer_tile

    def create_layer(self):
        for y, row in enumerate(self):
            for x, col in enumerate(row):
                # 端っこなら、そこはPrivateTile(壁など)で詰める
                if y == 0 or x == 0 or y == self.y_length - 1 or x == self.x_length - 1:
                    self.create_material(material_cls=self.outer_tile, x=x, y=y)
                else:
                    self.create_material(material_cls=self.inner_tile, x=x, y=y)


class RandomTileLayer(BaseTileLayer):
    """背景をランダム生成する。"""
    create_cls = RandomBackgroundCUI

    def __init__(self, x_length, y_length, inner_tile, outer_tile, split_x=2, split_y=2):
        super().__init__(x_length, y_length)
        self.inner_tile = inner_tile
        self.outer_tile = outer_tile
        self.split_x = split_x
        self.split_y = split_y

    def create_layer(self):
        creator = self.create_cls(self.x_length, self.y_length, self.split_x, self.split_y)
        creator.create()
        for y, row in enumerate(str(creator).split()):
            for x, col in enumerate(row):
                if col == '#':
                    self.create_material(material_cls=self.outer_tile, x=x, y=y)
                else:
                    self.create_material(material_cls=self.inner_tile, x=x, y=y)


class JsonTileLayer(BaseTileLayer):
    """背景をJSONから読み込んで作成する。"""

    def __init__(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file, cls=serializers.JsonDecoder)
        super().__init__(data['x_length'], data['y_length'])
        self.data = data['layer']

    def create_layer(self):
        for y, row in enumerate(self.data):
            for x, col in enumerate(row):

                tile_cls, kwargs = col
                self.create_material(material_cls=tile_cls, x=x, y=y, **kwargs)


class ExpandTileLayer(BaseTileLayer):
    """タイルの全方向・全差分を展開して背景にする。"""

    def __init__(self, tile):
        self.tile = tile
        super().__init__(
            x_length=tile.__dict__['image'].get_x_length(),
            y_length=tile.__dict__['image'].get_y_length(),
        )

    def create_layer(self):
        for y, row in enumerate(self):
            for x, col in enumerate(row):
                self.create_material(material_cls=self.tile, x=x, y=y, direction=y, diff=x)