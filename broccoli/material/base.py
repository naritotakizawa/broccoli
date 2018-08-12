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
import inspect


class BaseMaterial:
    """マップ上に表示される背景、物体、キャラクター、アイテムの基底クラス。"""
    name = 'ベースマテリアル'
    image = None

    def __init__(self, direction=0, diff=0, name=None):
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
        if name is None:
            self.name = type(self).name
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

    def get_nearest(self, materials):
        """materialsの中から、自分に最も近いものを返す。"""

        def _nearest(material):
            return abs(self.x-material.x) + abs(self.y-material.y)

        sorted_materials = sorted(materials, key=_nearest)
        return sorted_materials[0]

    def to_dict(self):
        return {
            'direction': self.direction,
            'diff': self.diff,
        }

    @classmethod
    def get_class_attrs(cls):
        """重要なクラス属性を辞書として返します。

        エディタ等で、そのクラスを説明するに足る情報を辞書として返します。
        nameや、タイルならばonやpublic、システムクラスが「power」などの属性を求めていれば、それも返します。

        具体的には以下のような処理を行います。
        - 「_」で始まらず
        - directionとimage属性は除き
        - クラスの持つメソッド・関数を除く(onやpublicといった、関数にもなりえる属性は返す)

        """
        result = {}
        allow_func_names = ('on', 'public')
        for key, value in inspect.getmembers(cls):
            if not key.startswith('_') and key != 'direction' and key != 'image':
                if key in allow_func_names or  not inspect.isroutine(value):
                    result[key] = value
        return result
