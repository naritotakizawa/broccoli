from broccoli.manage import SimpleGameManager
from map import first
from object import Dog


class MyGame(SimpleGameManager):
    canvas_list = [first]
    player = Dog


if __name__ == '__main__':
    game = MyGame()
    game.start()
