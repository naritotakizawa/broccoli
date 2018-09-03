"""broccoliフレームワーク内データの、シリアライズ・デシリアライズに関するモジュール。"""
import json
from broccoli import register
from broccoli.layer import BaseLayer, BaseItemLayer, BaseObjectLayer, BaseTileLayer
from broccoli.material import BaseMaterial


class JsonEncoder(json.JSONEncoder):
    """jsonエンコーダー"""

    def layer_to_json(self, o):
        result = {'kind': 'Layer'}
        if isinstance(o, BaseItemLayer):
            result['layer'] = [[[] for _ in range(o.tile_layer.x_length)] for _ in range(o.tile_layer.y_length)]
            for x, y, items in o.all():
                if items:
                    result['layer'][y][x] = [
                        {'class_name': item.__class__.__name__, 'kwargs': self.material_to_json(item), 'kind': 'Item'}
                        for item in items
                    ]
                else:
                    result['layer'][y][x] = []

        elif isinstance(o, BaseTileLayer):
            result.update({
                'x_length': o.x_length,
                'y_length': o.y_length,
                'layer': [[None for _ in range(o.x_length)] for _ in range(o.y_length)],
            })
            for x, y, tile in o.all():
                result['layer'][y][x] = {
                    'class_name': tile.__class__.__name__,
                    'kwargs': self.material_to_json(tile),
                    'kind': 'Tile',
                }

        elif isinstance(o, BaseObjectLayer):
            result['layer'] = [[None for _ in range(o.tile_layer.x_length)] for _ in range(o.tile_layer.y_length)]
            for x, y, obj in o.all():
                if obj is None:
                    result['layer'][y][x] = None
                else:
                    result['layer'][y][x] = {
                        'class_name': obj.__class__.__name__,
                        'kwargs': self.material_to_json(obj),
                        'kind': 'Object',
                    }
        return result

    def material_to_json(self, o):
        result = {
            'name': o.name,
            'direction': o.direction,
            'diff': o.diff,
            'vars': o.vars,
        }
        for attr_name in o.attrs:
            value = getattr(o, attr_name)
            if attr_name in o.func_attrs:
                value = value.name  # 関数のname属性に、registerに登録する名前が入っている
            result[attr_name] = value
        return result

    def default(self, o):
        if isinstance(o, BaseLayer):
            return self.layer_to_json(o)
        elif isinstance(o, BaseMaterial):
            return self.material_to_json(o)

        return super().default(o)


class JsonDecoder(json.JSONDecoder):
    """jsonデコーダー"""

    def layer_from_json(self, o):
        layer = o['layer']
        for y, row in enumerate(layer):
            for x, col in enumerate(row):
                if not col:
                    continue
                if isinstance(col, list):
                    layer[y][x] = self.item_from_json(col)

                else:
                    kind = col['kind']
                    if kind == 'Tile':
                        layer[y][x] = self.tile_from_json(col)
                    elif kind == 'Object':
                        layer[y][x] = self.object_from_json(col)

        return o

    def _load_material(self, col, container):
        class_name = col['class_name']
        kwargs = col['kwargs']
        cls = container[class_name]
        for func_attr in cls.func_attrs:
            if func_attr in kwargs:
                func_name = kwargs[func_attr]
                func = register.functions[func_name]
                kwargs[func_attr] = func
        return cls, kwargs

    def tile_from_json(self, o):
        return self._load_material(o, register.tiles)

    def object_from_json(self, o):
        if o is not None:
            return self._load_material(o, register.objects)
        return o

    def item_from_json(self, o):
        return [self._load_material(item, register.items) for item in o]

    def decode(self, s, **kwargs):
        o = super().decode(s, **kwargs)
        kind = o.get('kind')
        if kind == 'Layer':
            return self.layer_from_json(o)
        elif kind == 'Tile':
            return self.tile_from_json(o)
        elif kind == 'Object':
            return self.object_from_json(o)
        elif kind == 'Item':
            return self.item_from_json(o)
        return o
