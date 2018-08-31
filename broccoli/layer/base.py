"""ゲームキャンバスにおける、レイヤーを扱うモジュールです。

ゲームキャンバス内のデータは、レイヤーという層に格納されます。
背景は背景レイヤーに、キャラクターや物体はオブジェクトレイヤー、アイテムはアイテムレイヤーという具合です。
それらのレイヤーを作成するためのクラスを提供しています。

"""
import json
import random


class BaseLayer:
    """全てのレイヤの基底クラス。"""

    def __init__(self):
        self.layer = None
        self.canvas = None

    def put_material(self, material, x, y):
        """レイヤに、マテリアルを登録する。"""
        self[y][x] = material
        material.x = x
        material.y = y
        material.layer = self

    def all(self, include_none=True):
        """レイヤ内のものを全て返す。

        include_noneがTrueの場合、オブジェクトレイヤやアイテムレイヤで返されるNoneや空リストも含めて返します。
        Falseの場合はそれらを省き、存在しているマテリアルだけ返します。

        """
        for y, row in enumerate(self):
            for x, col in enumerate(row):
                if include_none or col:
                    yield x, y, col

    def get(self, **kwargs):
        """レイヤ内のマテリアルを検索する。"""
        for _, _, material in self.all():
            for key, value in kwargs.items():
                attr = getattr(material, key, None)
                if attr != value:
                    break
            else:
                return material

    def create_material(self, material_cls, x=None, y=None, **kwargs):
        """マテリアルの生成と初期設定、レイヤへの配置、キャンバスへの描画を行う。

        material_clsはクラスオブジェクトを渡せますが、インスタンスも渡せます。
        インスタンスを渡した場合は、そのマテリアルの__init__が呼ばれません。
        既にほかの場所で作成したマテリアルを流用したい場合は、インスタンスを渡すだけで済みます。

        """
        # マテリアルの生成と初期設定
        material = self.canvas.system.create_material(material_cls, **kwargs)

        # レイヤへの配置
        # x,y座標の指定がなければ座標を探す
        if x is None or y is None:
            x, y = self.get_random_empty_space(material)
        self.put_material(material, x, y)

        # キャンバスへの描画
        self.canvas.create_material(material)
        return material

    def delete_material(self, material):
        """マテリアルを削除する。"""
        raise NotImplementedError

    def get_empty_space(self, material=None):
        """空いているスペースを全てyieldで返す。

        マテリアルの種類によって空いているの定義が異なるため、それぞれでオーバーライドしています。

        """
        raise NotImplementedError

    def get_random_empty_space(self, material=None):
        """空いているスペースをランダムで1つ返す。"""
        empty_spaces = list(self.get_empty_space(material))
        return random.choice(empty_spaces)

    def __getitem__(self, item):
        """self.layerにデリゲート。

        item_layer.layer[y][x]ではなく、
        item_layer[y][x]と書くために実装しています。

        """
        return self.layer[item]


class BaseTileLayer(BaseLayer):
    """背景レイヤの基底クラス。"""

    def __init__(self, x_length, y_length):
        super().__init__()
        self.x_length = x_length
        self.y_length = y_length
        self.first_tile_id = None

    def create(self):
        """レイヤーの作成、描画を行う。"""
        self.layer = [[None for _ in range(self.x_length)] for _ in range(self.y_length)]
        self.create_layer()

    def get_empty_space(self, material=None):
        """空いているスペースを全てyieldで返す。

        is_publicがTrueのタイルであれば空いているとみなします。
        ランダムにゴールタイルなどを設定したい場合には便利です。

        しかし逆に、既に存在する特殊なタイル(ゴールタイル等)の座標を返してしまう恐れもあるため、
        tile_layerのget_empty_space及びget_random_empty_spaceの利用は注意してください。

        material引数は他レイヤのメソッドの引数と合わせる必要があるために定義していますが、使いません。

        """
        for x, y, tile in self.all():
            if tile.is_public():
                yield x, y

    def to_json(self, path):
        """背景レイヤをjsonとして出力する。"""
        data = {
            'x_length': self.x_length,
            'y_length': self.y_length,
            'layer': [[None for _ in range(self.x_length)] for _ in range(self.y_length)],
        }
        for x, y, tile in self.all():
            data['layer'][y][x] = {
                'class_name': tile.__class__.__name__,
                'kwargs': tile.to_dict(),
            }
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file)

    def create_material(self, material_cls, x=None, y=None, **kwargs):
        material = super().create_material(material_cls, x=x, y=y, **kwargs)
        self.canvas.lower(material.id)  # 背景は一番下に配置する

        # 一番はじめのタイルはIDを保存しておきます。
        # オブジェクトはどんどん上に描画され、タイルはどんどん下に描画され、アイテムは最初のタイルの上に描画されます。
        # 結果として、オブジェクト アイテム タイル という順番での重なりで描画されます。
        if self.first_tile_id is None:
            self.first_tile_id = material.id
        return material

    def delete_material(self, material):
        """タイルを削除する。

        タイルは存在しているのが当然なため、レイヤ内にNoneを入れる等はできません。

        このメソッドは、新しいタイルを設定する際に古いタイルを消したい、というケースに使ってください。
        このメソッドはキャンバス上から消す(表示だけ消す)ことしか行いません。
        その後にcreate_materialで、新しいタイルを設定してください。

        """
        self.canvas.delete(material.id)


class BaseObjectLayer(BaseLayer):
    """オブジェクトレイヤの基底クラス。"""

    def __init__(self):
        super().__init__()
        self.tile_layer = None

    def create(self):
        """レイヤーの作成、描画を行う。"""
        self.layer = [[None for _ in range(self.tile_layer.x_length)] for _ in range(self.tile_layer.y_length)]
        self.create_layer()

    def get_empty_space(self, material=None):
        """空いているスペースを全てyieldで返す。

        そのオブジェクトを受け入れるタイルであり、
        まだオブジェクトがない座標ならばOK。

        """
        for x, y, tile in self.tile_layer.all():
            if tile.is_public(obj=material) and self[y][x] is None:
                yield x, y

    def to_json(self, path):
        """オブジェクトレイヤーをJSON出力する"""
        data = {
            'layer': [[None for _ in range(self.tile_layer.x_length)] for _ in range(self.tile_layer.y_length)],
        }
        for x, y, obj in self.all():
            if obj is None:
                data['layer'][y][x] = None
            else:
                data['layer'][y][x] = {
                    'class_name': obj.__class__.__name__,
                    'kwargs': obj.to_dict(),
                }

        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file)

    def clear(self):
        """layer内を全てNoneにし、表示中のオブジェクトを削除します。"""
        for x, y, obj in self.all(include_none=False):
            self.delete_material(obj)

    def create_material(self, material_cls, x=None, y=None, **kwargs):
        material = super().create_material(material_cls, x=x, y=y, **kwargs)
        self.canvas.lift(material.id)  # オブジェクトは一番上に配置する
        return material

    def delete_material(self, material):
        """マテリアルを削除する"""
        self[material.y][material.x] = None
        self.canvas.delete(material.id)


class BaseItemLayer(BaseLayer):
    """アイテムレイヤの基底クラス。"""

    def __init__(self):
        super().__init__()
        self.tile_layer = None

    def put_material(self, material, x, y):
        """アイテムを配置する。

        アイテムは1座標に複数格納できます。つまり、リストで管理しています。
        そのため、アイテムの配置はappendメソッドを使います。

        """
        self[y][x].append(material)
        material.x = x
        material.y = y
        material.layer = self

    def create(self):
        """レイヤーの作成、描画を行う。"""
        self.layer = [[[] for _ in range(self.tile_layer.x_length)] for _ in range(self.tile_layer.y_length)]
        self.create_layer()

    def get_empty_space(self, material=None):
        """空いているスペースを全てyieldで返す。

        そのアイテムにとって、配置可能な座標を返します。
        tileのis_public(引数なし)がTrueであれば配置可能と考えます。

        """
        for x, y, tile in self.tile_layer.all():
            if tile.is_public():
                yield x, y

    def to_json(self, path):
        """アイテムレイヤーをJSON出力する。"""
        data = {
            'layer': [[[] for _ in range(self.tile_layer.x_length)] for _ in range(self.tile_layer.y_length)],
        }
        for x, y, items in self.all():
            if items:
                data['layer'][y][x] = [
                    {'class_name': item.__class__.__name__, 'kwargs': item.to_dict()} for item in items
                ]

            else:
                data['layer'][y][x] = []

        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file)

    def clear(self):
        """layer内を全てNoneにし、表示中のオブジェクトを削除します。"""
        for x, y, items in self.all(include_none=False):
            for item in items:
                self.delete_material(item)

    def create_material(self, material_cls, x=None, y=None, **kwargs):
        material = super().create_material(material_cls, x=x, y=y, **kwargs)
        self.canvas.lift(material.id, self.tile_layer.first_tile_id)  # 一番上にある背景の上
        return material

    def delete_material(self, material):
        """マテリアルを削除する"""
        self[material.y][material.x].remove(material)
        self.canvas.delete(material.id)

    def get(self, **kwargs):
        """レイヤ内のアイテムを検索する。"""
        for _, _, items in self.all():
            for item in items:
                for key, value in kwargs.items():
                    attr = getattr(item, key, None)
                    if attr != value:
                        break
                else:
                    return item
