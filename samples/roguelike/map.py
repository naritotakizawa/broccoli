from broccoli.canvas import GameCanvas2D
from broccoli.layer import JsonObjectLayer, JsonTileLayer
from broccoli.system import RogueWithPlayer
from broccoli.dialog import LogAndActiveMessageDialog, ListDialog
from tile import *
from object import *
from item import *


class Tutorial(GameCanvas2D):
    tile_layer = JsonTileLayer('tutorial_tile.json')
    object_layer = JsonObjectLayer('tutorial_obj.json')
    system = RogueWithPlayer(
        message_class=LogAndActiveMessageDialog,
        show_item_dialog_class=ListDialog,
        x=5, y=5
    )
