"""broccoliフレームワーク内データの、シリアライズ・デシリアライズに関するモジュール。"""
import json
from broccoli import register
from broccoli.layer import BaseLayer, BaseItemLayer, BaseObjectLayer, BaseTileLayer
from broccoli.material import BaseTile, BaseObject, BaseItem


LAYER = 'Layer'
TILE = 'Tile'
OBJECT = 'Object'
ITEM = 'Item'
MATERIALS = (TILE, OBJECT, ITEM)


class JsonEncoder(json.JSONEncoder):
    """jsonエンコーダー"""

    def layer_to_json(self, o):
        result = {'kind': LAYER}
        if isinstance(o, BaseItemLayer):
            result['layer'] = [[[] for _ in range(o.tile_layer.x_length)] for _ in range(o.tile_layer.y_length)]
            for x, y, items in o.all():
                if items:
                    result['layer'][y][x] = [self.material_to_json(item, kind=ITEM) for item in items]
                else:
                    result['layer'][y][x] = []

        elif isinstance(o, BaseTileLayer):
            result.update({
                'x_length': o.x_length,
                'y_length': o.y_length,
                'layer': [[None for _ in range(o.x_length)] for _ in range(o.y_length)],
            })
            for x, y, tile in o.all():
                result['layer'][y][x] = self.material_to_json(tile, kind=TILE)

        elif isinstance(o, BaseObjectLayer):
            result['layer'] = [[None for _ in range(o.tile_layer.x_length)] for _ in range(o.tile_layer.y_length)]
            for x, y, obj in o.all():
                if obj is None:
                    result['layer'][y][x] = None
                else:
                    result['layer'][y][x] = self.material_to_json(obj, kind=OBJECT)
        return result

    def material_to_json(self, o, kind):
        result = {
            'class_name': o.__class__.__name__,
            'kwargs': self.kwargs_to_json(o),
            'kind': kind,
        }
        return result

    def kwargs_to_json(self, o):
        result = o.get_instance_attrs()
        for key, value in result.items():
            if key in o.func_attrs:
                result[key] = value.name  # 関数のname属性に、registerに登録する名前が入っている
            elif isinstance(value, (list, tuple)):
                for i, data in enumerate(value):
                    value[i] = self.default(data)
            elif isinstance(value, dict):
                for attr_name, attr_value in value.items():
                    value[attr_name] = self.default(attr_value)

        return result

    def default(self, o):
        if isinstance(o, (list, tuple)):
            for i, data in enumerate(o):
                o[i] = self.default(data)
            return o

        elif isinstance(o, dict):
            for attr_name, attr_value in o.items():
                o[attr_name] = self.default(attr_value)

        elif isinstance(o, BaseLayer):
            return self.layer_to_json(o)
        elif isinstance(o, BaseTile):
            return self.material_to_json(o, kind=TILE)
        elif isinstance(o, BaseObject):
            return self.material_to_json(o, kind=OBJECT)
        elif isinstance(o, BaseItem):
            return self.material_to_json(o, kind=ITEM)
        return super().default(o)


class JsonDecoder(json.JSONDecoder):
    """jsonデコーダー"""

    def layer_from_json(self, o):
        layer = o['layer']
        for y, row in enumerate(layer):
            for x, col in enumerate(row):
                layer[y][x] = self._decode(col)

        return o

    def _load_material(self, col, container):
        class_name = col['class_name']
        kwargs = col['kwargs']
        cls = container[class_name]
        for key, value in kwargs.items():
            if key in cls.func_attrs:
                kwargs[key] = register.functions[value]
            elif isinstance(value, list):
                for i, data in enumerate(value):
                    value[i] = self._decode(data)
            elif isinstance(value, dict):
                for attr_name, attr_value in value.items():
                    value[attr_name] = self._decode(attr_value)
        return cls, kwargs

    def tile_from_json(self, o):
        return self._load_material(o, register.tiles)

    def object_from_json(self, o):
        return self._load_material(o, register.objects)

    def item_from_json(self, o):
        return self._load_material(o, register.items)

    def _decode(self, o):
        if isinstance(o, list):
            for i, data in enumerate(o):
                o[i] = self._decode(data)

        elif isinstance(o, dict):
            kind = o.get('kind')
            if kind == LAYER:
                return self.layer_from_json(o)
            elif kind == TILE:
                return self.tile_from_json(o)
            elif kind == OBJECT:
                return self.object_from_json(o)
            elif kind == ITEM:
                return self.item_from_json(o)

            for key, value in o.items():
                o[key] = self._decode(value)

        return o

    def decode(self, s, **kwargs):
        o = super().decode(s, **kwargs)
        return self._decode(o)
