"""ゲーム中の背景に関するモジュール。

壊れない背景が該当します。例えば空や地面です。
Canvasクラスにおける、tile_layerに格納されるクラス群です。

"""
from broccoli.material.base import BaseMaterial


class BaseTile(BaseMaterial):
    name = 'ベースタイル'
    public = True
    on = None

    def __init__(self, public=None, on=None, direction=0, diff=0, name=None):
        # public引数がNoneなら、クラス属性のpublicをインスタンス属性として設定
        if public is None:
            self.public = type(self).public
        else:
            self.public = public

        # on引数がNoneなら、クラス属性のonをインスタンス属性として設定
        if on is None:
            self.on = type(self).on
        else:
            self.on = on

        super().__init__(direction=direction, diff=diff, name=name)

    def is_public(self, obj=None):
        """そのタイルが通行可能かを調べるメソッド。

        このタイルの上に乗れるかを検査するメソッドです。
        特殊な判断(プレイヤーだけ通す)をする場合は専用の関数を定義し、
        それをpublic属性に設定してください。
        関数の書き方は、broccoli.material.function を参考にしてください。

        """
        if self.public is True:
            return True
        elif self.public is False:
            return False
        else:
            return self.public(obj)

    def on_self(self, obj):
        """キャラクターやオブジェクトが上に乗った際の処理。

        上に乗った際に何らかの処理をするためのメソッドです。
        たとえば、溶岩の上にのったらダメージを受けるのが自然です。

        上に乗った際に特殊な処理をする場合は専用の関数を定義し、
        それをon属性に指定してください。
        関数の書き方は、broccoli.material.function を参考にしてください。

        """
        if self.on is not None:
            self.on(obj)

    def to_dict(self):
        dic = super().to_dict()
        dic['public'] = self.public if (self.public is True or self.public is False) else self.public.__name__
        dic['on'] = None if self.on is None else self.on.__name__
        return dic
