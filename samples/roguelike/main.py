from broccoli.manage import SimpleGameManager

from map import Tutorial
from object import Dog


class MyGame(SimpleGameManager):
    canvas_list ={
        'チュートリアル': Tutorial,
    }
    vars = {'player': (Dog, {'name': 'あなた'})}


if __name__ == '__main__':
    game = MyGame()
    game.start()
