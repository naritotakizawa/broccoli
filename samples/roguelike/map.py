from broccoli.canvas import GameCanvas2D
from broccoli.layer import RandomTileLayer, RandomObjectLayer, RandomItemLayer, JsonItemLayer, JsonObjectLayer, JsonTileLayer
from broccoli.system import RogueWithPlayer, RogueNoPlayer
from broccoli.dialog import LogAndActiveMessageDialog, ActiveMessageDialog, LogMessageDialog, ListDialog
# from broccoli.dialog.img import LogAndActiveMessageDialog, ActiveMessageDialog, LogMessageDialog, ListDialog
from tile import *
from object import *
from item import *


def dungeon1(manager):
    return GameCanvas2D(
        manager=manager,
        name='かんたんなダンジョン1',
        tile_layer=RandomTileLayer(
            x_length=10, y_length=10,
            inner_tile=GrassTile, outer_tile=WallTile,
            split_x=2, split_y=2,
        ),
        object_layer=RandomObjectLayer(
            enemies=[Sheep, Sparrow], number_of_enemies=3
        ),
        item_layer=RandomItemLayer(items=[HealingHerb], number_of_items=3),
        system=RogueWithPlayer(message_class=LogAndActiveMessageDialog, show_item_dialog_class=ListDialog),
    )


def dungeon2(manager):
    return GameCanvas2D(
        manager=manager,
        name='かんたんなダンジョン2',
        tile_layer=RandomTileLayer(
            x_length=10, y_length=10,
            inner_tile=GrassTile, outer_tile=WallTile,
            split_x=2, split_y=2
        ),
        object_layer=RandomObjectLayer(
            enemies=[Sheep, RoboSheep, NechigaeSheep], number_of_enemies=3
        ),
        system=RogueWithPlayer(message_class=ActiveMessageDialog),
    )


def dungeon3(manager):
    return GameCanvas2D(
        manager=manager,
        name='かんたんなダンジョン3',
        tile_layer=RandomTileLayer(
            x_length=10, y_length=10,
            inner_tile=GrassTile, outer_tile=WallTile,
            split_x=2, split_y=2
        ),
        object_layer=RandomObjectLayer(
            enemies=[Sheep, RoboSheep, NechigaeSheep], number_of_enemies=3
        ),
        system=RogueWithPlayer(message_class=ActiveMessageDialog),
    )
