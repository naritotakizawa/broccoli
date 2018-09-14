from broccoli.containers import IndexDict
from broccoli.manage import SimpleGameManager

from map import tutorial
from object import Dog


class MyGame(SimpleGameManager):
    canvas_list = IndexDict({
        'チュートリアル': tutorial,
    })
    player = (Dog, {'name': 'あなた'})


if __name__ == '__main__':
    game = MyGame()
    game.start()
