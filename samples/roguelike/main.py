from broccoli.manage import SimpleGameManager
from map import dungeon1, dungeon2, dungeon3
from object import Dog


class MyGame(SimpleGameManager):
    canvas_list = [dungeon1, dungeon2, dungeon3]
    player_cls = Dog


if __name__ == '__main__':
    game = MyGame()
    game.start()
