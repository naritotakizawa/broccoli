"""ゲーム中の背景に関するモジュール。

壊れない背景が該当します。例えば空や地面です。
tile_layerに格納されます。

"""
from broccoli.material.base import BaseMaterial
from broccoli.funcstions.generic import return_true, do_nothing


class BaseTile(BaseMaterial):
    # おそらく全てのゲームにおいて、この2つの属性は定義しておいても問題ないでしょう。
    is_public = return_true
    on_self = do_nothing

    attrs = ['is_public', 'on_self']
    func_attrs = ['is_public', 'on_self']
