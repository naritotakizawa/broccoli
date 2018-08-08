"""マテリアルに設定する関数を提供しているモジュール。"""
from broccoli import register
from broccoli import const


@register.public
def only_player(obj=None):
    """プレイヤーのみ、通行を許可する。

    obj引数がNoneの場合は、通行不可です。
    obj引数があり、かつプレイヤーならば通行を許可します。

    """
    if obj is not None and obj.kind == const.PLAYER:
        return True

    return False


@register.on
def goal(obj):
    """プレイヤーが乗ったら、次のマップへ移動する。"""
    if obj.kind == const.PLAYER:
        obj.canvas.manager.next_canvas()
