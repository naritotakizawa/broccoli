"""マップ上に表示される背景、オブジェクトに関するモジュール。

大きく分けて、3つのデータがあります。
1つは背景(tile)で、Canvasクラスのtile_layerに格納されるものです。
地面や空など、そういったものが該当します。

もう１つはオブジェクト(object)で、キャラクターや物体が当てはまります。
objects_layerに格納されるもので、壁や木、岩、
あとは普通のキャラクター等が該当します。

最後は、アイテム(item)です。

"""
import inspect
import random
import types
from broccoli import const


class BaseMaterial:
    """マップ上に表示される背景、物体、キャラクター、アイテムの基底クラス。"""
    name = None
    vars = {}  # フラグ等の値を格納する辞書として使えます。jsonでの読み込み・保存に対応している辞書です。

    attrs = []  # このマテリアルが持つ、固有の属性を書きます。
    func_attrs = []  # マテリアルの固有属性のうち、関数となるものを書きます。

    def __init__(self, x, y, canvas, system, layer, direction=0, diff=0, name=None, vars=None, **kwargs):
        """初期化処理

        全てのマテリアルインスタンスは重要な属性として
        - マテリアルの名前
        - マテリアルの変数辞書(vars)
        - マテリアルの向き
        - マテリアルの差分
        - レイヤ内の位置にあたるx, y座標
        - 所属するゲームキャンバスクラス
        - 所属するゲームシステムクラス
        - 所属するレイヤクラス(背景ならtile_layer等)
        - マテリアルを識別するためのid
        を持っています。

        更に、マテリアルの種類や具象クラスによっては固有の属性を持ちます。

        基本的に、レイヤクラスのcreate_materialを使ってマテリアルを生成することになります。

        x, y, canvas, layer, system, id属性はインスタンス化時には設定されませんが、
        インスタンス化後、順番に設定されていきます。
        そのため、インスタンス化時の引数に渡しても意味はありません。

        """
        cls = type(self)

        self.x = x
        self.y = y
        self.canvas = canvas
        self.system = system
        self.layer = layer
        self.id = None

        if name is None:
            self.name = cls.name
        else:
            self.name = name

        if vars is None:
            self.vars = cls.vars
        else:
            self.vars = vars

        # 向きに関する属性
        self.direction = direction  # 現在の向き。移動のほか、攻撃などにも影響する
        self.diff = diff  # 同じ向きを連続で向いた数。差分表示等に使う

        # マテリアルインスタンスの属性を設定
        for attr_name in cls.attrs:
            # kwargsにあればそれを、そうでなければクラス属性を設定
            if attr_name in kwargs:
                value = kwargs[attr_name]
            else:
                value = getattr(cls, attr_name)

            # 関数ならば、メソッドとして登録。
            if attr_name in self.func_attrs:
                value = self.create_method(value)

            # クラス属性でリストや辞書等を使った場合は、他と共有されるのでcopy
            # ミュータブルなオブジェクト全てに言えるので、いずれ汎用的に。
            if isinstance(value, (list, dict)):
                value = value.copy()

            setattr(self, attr_name, value)

    def __str__(self):
        return '{}({}, {}) - {}'.format(self.name, self.x, self.y, self.id)

    def change_direction(self, value):
        """向きを変え、その画像を反映させる。

        同じ向きを向いた場合は差分を増やし、そして画像を反映させます。
        キャラクターを歩行させたい、歩行させる際のグラフィック更新に便利です。

        """
        # 前と違う向き
        if self.direction != value:
            self.diff = 0
            self.direction = value

        # 前と同じ向き、差分カウンタを増やす
        else:
            self.diff += 1

        # 向きを変えたら、画像もすぐに反映させる。imageはディスクリプタです。
        self.canvas.itemconfig(self.id, image=self.image)

    def get_4_positions(self):
        """4方向の座標を取得するショートカットメソッドです。

        [
            (DOWN, self.x, self.y+1),にも
            (LEFT, self.x-1, self.y),
            (RIGHT, self.x+1, self.y),
            (UP, self.x, self.y - 1),
        ]
        といったリストを返します。
        DOWNなどは向きに直接代入(direction=DOWN)できる定数で、change_directionメソッドにもそのまま渡せます。
        また、その方向がマップの範囲外になる場合は無視されます。
        空のリストが返ったら、4方向が全てマップの範囲外ということです。

        デフォルトではシャッフルして返しますので、必ずしも下座標から取得できる訳ではありません。

        """
        positions = [
            (const.DOWN, self.x, self.y + 1),
            (const.LEFT, self.x - 1, self.y),
            (const.RIGHT, self.x + 1, self.y),
            (const.UP, self.x, self.y - 1),
        ]
        result_positions =[]
        for direction, x, y in positions:
            # マップの範囲外は無視する
            if self.canvas.check_position(x, y):
                result_positions.append(
                    (direction, x, y)
                )
        random.shuffle(result_positions)
        return result_positions

    def get_nearest(self, materials):
        """materialsの中から、自分に最も近いものを返す。"""

        def _nearest(material):
            return abs(self.x-material.x) + abs(self.y-material.y)

        sorted_materials = sorted(materials, key=_nearest)
        return sorted_materials[0]

    @classmethod
    def get_class_attrs(cls):
        """クラスの属性を辞書として返します。

        マテリアルの主要なクラス属性を辞書として返します。
        まだインスタンス化していない状態で、そのマテリアルクラスの属性を確認したい場合に有効です。
        エディタでのマテリアル説明欄に使っています。

        """
        result = {
            'name': cls.name,
            'vars': cls.vars,
        }
        for attr_name in cls.attrs:
            value = getattr(cls, attr_name)
            result[attr_name] = value
        return result

    def get_instance_attrs(self):
        """マテリアルインスタンスの属性を返します。

        関数オブジェクトもそのまま設定されます。
        これはインスタンス化の引数にそのまま使える辞書で、マテリアルのコピーに使えます。

        cls = type(material)
        kwargs = material.get_instance_attrs()
        create_material(material_cls=cls, **kwargs)

        とすると、そのマテリアルのコピーを作成できます。

        """
        result = {
            'name': self.name,
            'direction': self.direction,
            'diff': self.diff,
            'vars': self.vars,
        }
        for attr_name in self.attrs:
            value = getattr(self, attr_name)
            result[attr_name] = value
        return result

    def copy(self):
        """マテリアルのコピーを返します。

        cls = type(material)
        kwargs = material.get_instance_attrs()
        create_material(material_cls=cls, **kwargs)

        を

        create_material(material_cls=material.copy())

        と書くことができます。

        """
        cls = type(self)
        kwargs = self.get_instance_attrs()
        return cls(**kwargs)

    def create_method(self, func):
        """マテリアルのメソッドとして関数を登録します。"""

        # 既にメソッドだった場合はそのままにする
        # 既にメソッドになっているケースとしては、copyでの複製インスタンス化時
        if not inspect.ismethod(func):
            func = types.MethodType(func, self)
        return func

    def delete(self):
        """マテリアルを削除する。

        material.layer.delete_material(material)
        を、簡単に書くためのショートカットです。

        """
        self.layer.delete_material(self)
