from broccoli import register
from broccoli import const


@register.function(name='generic.tile.only_player', system='all', attr='is_public')
def only_player(self, obj=None):
    """プレイヤーのみ、通行を許可する。

    obj引数がNoneの場合は、通行不可です。
    obj引数があり、かつプレイヤーならば通行を許可します。

    """
    if obj is not None and obj.kind == const.PLAYER:
        return True

    return False


@register.function(name='generic.tile.goal', system='all', attr='on_self')
def goal(self, obj):
    """プレイヤーが乗ったら、次のマップへ移動する。"""
    if obj.kind == const.PLAYER:
        obj.canvas.manager.next_canvas()
