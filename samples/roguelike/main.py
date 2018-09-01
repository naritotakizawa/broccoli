from broccoli.manage import SimpleGameManager
from map import tutorial
from object import Dog


class MyGame(SimpleGameManager):
    canvas_list = [tutorial]
    player = Dog


if __name__ == '__main__':
    game = MyGame()
    game.start()
