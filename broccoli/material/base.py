"""マップ上に表示される背景、オブジェクトに関するモジュール。

大きく分けて、3つのデータがあります。
1つは背景(tile)で、Canvasクラスのtile_layerに格納されるものです。
地面や空など、そういったものが該当します。

もう１つはオブジェクト(object)で、キャラクターや物体が当てはまります。
objects_layerに格納されるもので、壁や木、岩、
あとは普通のキャラクター等が該当します。

最後は、アイテム(item)です。

tileとobjectの中にはどちらにも属せそうなものがありますが、この1背景につき1オブジェクトという仕様(システムクラスにもよります)や
使いたい画像の透過具合(tileの画像内に透過部分があると、表示が上手くされません)などを見ながら使うと良いでしょう。

"""
import random
import types
from broccoli import const


class BaseMaterial:
    """マップ上に表示される背景、物体、キャラクター、アイテムの基底クラス。"""
    attrs = {}

    def __init__(self, direction=0, diff=0, name=None, **kwargs):
        """初期化処理

        全てのマテリアルインスタンスは重要な属性として
        ・マップ上でのy座標、x座標
        ・キャラを識別するためのid
        ・自分が今いるゲームキャンバスオブジェクト
        ・今のゲームキャンバスのシステムオブジェクト
        を持っています。

        x, y座標、canvas, systemはマップの作成時に設定されます。
        idは、canvas.create_imageで返される一意な数値で、各キャラをcanvas上で識別するためのIDです。
        canvasは、ゲームキャンバスクラス(tk.Canvasのサブクラス)のインスタンスで、描画などを担当します。
        systemには、そのマップにおける移動や戦闘など、ゲームのシステム部分を担当するオブジェクトがあります。

        idを使うことでself.canvas.itemconfig(id, image=self.image)といった描画画像の変更や
        self.canvas.delete(id)での削除
        self.canvas.coords(id, x, y)での移動に使えます。
        idは必ず一意なものになります。

        マテリアルを表す名前(name)、今の向き(direction)、向きの差分カウント(diff)などの属性もあります。

        """
        cls = type(self)
        if name is None:
            self.name = cls.name
        else:
            self.name = name

        self.y = None
        self.x = None
        self.canvas = None
        self.system = None
        self.id = None

        # 向きに関する属性
        self._direction = direction  # 現在の向き。移動のほか、攻撃などにも影響する
        self.diff = diff  # 同じ向きを連続で向いた数。差分表示等に使う

        for key, value in cls.attrs.items():
            # kwargs.get(key) or getattr(cls, key, value) のようには書かないでください。
            # const.PLAYERのように、0などのFalseと評価される値を持つことも往々にしてあります。
            if key in kwargs:
                value = kwargs[key]
            elif hasattr(cls, key):
                value = getattr(cls, key)
            if callable(value):
                value = types.MethodType(value, self)

            # クラス属性の空リストや辞書等を使った場合は、他と共有されるのでcopy
            # ミュータブルなオブジェクト全てに言えるので、いずれ汎用的に。
            if isinstance(value, (list, dict)):
                value = value.copy()
            setattr(self, key, value)

    def __str__(self):
        return '{}({}, {}) - {}'.format(self.name, self.x, self.y, self.id)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        # 前と違う向き
        if self._direction != value:
            self.diff = 0
            self._direction = value

        # 前と同じ向き、差分カウンタを増やす
        else:
            self.diff += 1

        # 向きを変えたら、画像もすぐに反映させる。imageはディスクリプタです。
        self.canvas.itemconfig(self.id, image=self.image)

    def get_4_positions(self):
        """4方向の座標を取得するショートカットメソッドです。

        [
            (DOWN, self.x, self.y+1),
            (LEFT, self.x-1, self.y),
            (RIGHT, self.x+1, self.y),
            (UP, self.x, self.y - 1),
        ]
        といったリストを返します。
        DOWNなどは向きに直接代入できる定数です。
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

    def to_dict(self):
        result = {
            'direction': self.direction,
            'diff': self.diff,
            'name': self.name,
        }
        for key, value in self.attrs.items():
            if callable(value):
                value = value.__name__
            result[key] = value
        return result
