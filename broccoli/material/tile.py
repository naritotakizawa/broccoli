"""ゲーム中の背景に関するモジュール。

壊れない背景が該当します。例えば空や地面です。
Canvasクラスにおける、tile_layerに格納されるクラス群です。

"""
from broccoli import register
from broccoli import const
from broccoli.material.base import BaseMaterial, do_nothing, return_true


class BaseTile(BaseMaterial):
    name = 'ベースタイル'
    is_public = return_true
    on_self = do_nothing

    def to_dict(self):
        dic = super().to_dict()
        dic['is_public'] = self.is_public.__name__
        dic['on_self'] = self.on_self.__name__
        return dic


@register.public
def only_player(self, obj=None):
    """プレイヤーのみ、通行を許可する。

    obj引数がNoneの場合は、通行不可です。
    obj引数があり、かつプレイヤーならば通行を許可します。

    """
    if obj is not None and obj.kind == const.PLAYER:
        return True

    return False


@register.on
def goal(self, obj):
    """プレイヤーが乗ったら、次のマップへ移動する。"""
    if obj.kind == const.PLAYER:
        obj.canvas.manager.next_canvas()
