from broccoli.canvas import GameCanvas2D
from broccoli.layer import RandomTileLayer, RandomObjectLayer, RandomItemLayer, JsonItemLayer, JsonObjectLayer, JsonTileLayer
from broccoli.system import RogueWithPlayer, RogueNoPlayer
from broccoli.dialog import LogAndActiveMessageDialog, ActiveMessageDialog, LogMessageDialog, ListDialog
# from broccoli.dialog.img import LogAndActiveMessageDialog, ActiveMessageDialog, LogMessageDialog, ListDialog
from tile import *
from object import *
from item import *


def first(manager):
    return GameCanvas2D(
        manager=manager,
        name='はじめてのマップ',
        tile_layer=JsonTileLayer('map_1.json'),
        object_layer=JsonObjectLayer('obj_1.json'),
        system=RogueWithPlayer(message_class=LogAndActiveMessageDialog, show_item_dialog_class=ListDialog, x=5, y=5),
    )
