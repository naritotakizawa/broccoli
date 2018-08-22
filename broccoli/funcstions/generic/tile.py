from broccoli import register
from broccoli import const


@register.function('generic.tile.only_player', attr='is_public', material='tile')
def only_player(self, obj=None):
    """プレイヤーのみ、通行を許可する。

    obj引数がNoneの場合は、通行不可です。
    obj引数があり、かつプレイヤーならば通行を許可します。

    """
    if obj is not None and obj.kind == const.PLAYER:
        return True

    return False


@register.function('generic.tile.goal', attr='on_self', material='tile')
def goal(self, obj):
    """プレイヤーが乗ったら、次のマップへ移動する。"""
    if obj.kind == const.PLAYER:
        obj.canvas.manager.next_canvas()
