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
    """broccoliフレームワーク専用JSONエンコーダー。

    json.dump(tile_layer, file, cls=serializers.JsonEncoder)
    のように使ってください。

    通常のJSONEncoderと違い、
    - 関数
    - マテリアル
    - レイヤー
    もJSONエンコードされます。

    レイヤー内にマテリアルがある場合はマテリアルも正しくエンコードされ、
    更にマテリアルが何らかのマテリアルを保持している場合(アイテムなど)も再帰的にエンコードされます。

    関数は、
    "generic.do_nothing"
    のような単純な文字列になります。この文字列は関数の登録名です。

    マテリアルは、
    {
        "class_name": "KindnessSheep",
        "kwargs": {},
        "kind": "Object"
    }
    という表現になります。

    レイヤーは、
    {
        "kind": "Layer",
        "layer": [
            [マテリアル, マテリアル...],
            [マテリアル, マテリアル...],
            [マテリアル, マテリアル...],
        ]
    }
    という表現になります。内部のマテリアル部分は、上で紹介したマテリアルのJSON表現が入ります。

    実際にどういうJSONになるかは、samples/roguelike内のjsonファイルを見てください。

    """

    def layer_to_json(self, o):
        """レイヤーをJSONエンコードする。"""
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
        """マテリアルをJSONエンコードする。"""
        result = {
            'class_name': o.__class__.__name__,
            'kwargs': self.kwargs_to_json(o),
            'kind': kind,
        }
        return result

    def kwargs_to_json(self, o):
        """マテリアルのインスタンス属性をJSONエンコードする。"""
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
        """JSONエンコードする。

        このメソッドが最初に呼び出されます。

        """
        # リストやタプルならば、中身がマテリアル等の場合もあるので
        # 再帰的にJSONエンコードする。
        if isinstance(o, (list, tuple)):
            for i, data in enumerate(o):
                o[i] = self.default(data)
            return o

        # 辞書の場合も、中身がマテリアルの場合があるので再帰的にエンコード。
        elif isinstance(o, dict):
            for attr_name, attr_value in o.items():
                o[attr_name] = self.default(attr_value)

        # レイヤーを渡された場合。レイヤーの専用エンコード処理を呼ぶ。
        elif isinstance(o, BaseLayer):
            return self.layer_to_json(o)

        # 各マテリアルも、専用のエンコード処理を呼ぶ。
        elif isinstance(o, BaseTile):
            return self.material_to_json(o, kind=TILE)
        elif isinstance(o, BaseObject):
            return self.material_to_json(o, kind=OBJECT)
        elif isinstance(o, BaseItem):
            return self.material_to_json(o, kind=ITEM)

        # 通常の数値や文字列は、デフォルトのエンコード処理を呼ぶ。
        return super().default(o)


class JsonDecoder(json.JSONDecoder):
    """broccoliフレームワーク専用JSONデコーダー。

    data = json.load(file, cls=serializers.JsonDecoder)
    のように使ってください。

    JSONEncoderでエンコードされたJSONファイルを、broccoliフレームワークで使える形に出コードします。
    通常のJSONデコードと違うのは、
    - 関数のエンコード表現
    - マテリアルのエンコード表現
    - レイヤーのエンコード表現
    もデコードされることです。

    関数は
    "generic.do_nothing"
    のような文字列となっていますが、これをPythonの関数オブジェクトに変換します。

    マテリアルは
    {
        "class_name": "KindnessSheep",
        "kwargs": {},
        "kind": "Object"
    }
    のような表現ですが、これを
    (クラスオブジェクト, インスタンス属性の辞書)
    に変換します。cls(**kwargs)としてインスタンス化できる形式です。

    レイヤーは、
    {
        "kind": "Layer",
        "layer": [
            [マテリアル, マテリアル...],
            [マテリアル, マテリアル...],
            [マテリアル, マテリアル...],
        ]
    }
    という表現ですが、これを
    [
        [(cls, kwargs), (cls, kwargs)...],
        [(cls, kwargs), (cls, kwargs)...],
        [(cls, kwargs), (cls, kwargs)...],
    ]
    という2次元のリストに変換します。(cls, kwargs)部分は上で紹介したマテリアルのデコード表現です。

    """

    def layer_from_json(self, o):
        """レイヤーをデコードする。"""
        layer = o['layer']
        for y, row in enumerate(layer):
            for x, col in enumerate(row):
                layer[y][x] = self._decode(col)

        return o

    def _load_material(self, col, container):
        """マテリアルをデコードする。"""
        class_name = col['class_name']
        kwargs = col['kwargs']
        cls = container[class_name]

        # インスタンスの属性を見ていく。
        for key, value in kwargs.items():
            # 関数となる属性ならば、関数のロード
            if key in cls.func_attrs:
                kwargs[key] = register.functions[value]

            # 属性がリストや辞書ならば、中の要素を再帰的にデコード。
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
        """マテリアル、レイヤーなどをデコードする。"""
        # リストならば各要素を_decodeし、中のマテリアルなどを再帰的にデコードする。
        if isinstance(o, list):
            for i, data in enumerate(o):
                o[i] = self._decode(data)

        # 辞書の場合、マテリアルなどの場合は専用のメソッドを、そうでなければ再帰的にデコードする。
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

        # ここは数値や文字列などがくる。
        return o

    def decode(self, s, **kwargs):
        """デコードする。最初に呼ばれる。"""
        # まず、デフォルトのdecodeで
        # リストと辞書のPythonオブジェクトに変換してもらう。
        o = super().decode(s, **kwargs)

        # そのPythonオブジェクトの中から、マテリアルやレイヤー、関数部分を更にデコードする。
        return self._decode(o)
