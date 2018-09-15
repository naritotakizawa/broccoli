from broccoli.containers import IndexDict
from broccoli.manage import manager

from map import tutorial
from object import Dog


if __name__ == '__main__':
    manager.canvas_list.update({
        'チュートリアル': tutorial,
    })
    manager.vars['player'] = (Dog, {'name': 'あなた'})
    manager.start()
