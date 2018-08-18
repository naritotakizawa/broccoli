"""ゲーム中の背景に関するモジュール。

壊れない背景が該当します。例えば空や地面です。
Canvasクラスにおける、tile_layerに格納されるクラス群です。

"""
from broccoli.material.base import BaseMaterial
from broccoli.funcstions import generic


class BaseTile(BaseMaterial):
    attrs = {
        'is_public' : generic.return_true,
        'on_self' : generic.do_nothing,
    }
