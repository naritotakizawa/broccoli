"""ダンジョンをランダム生成するためのモジュール。"""
import random


class Rectangle:
    """部屋ごとに作る方法で使うクラス"""

    def __init__(self, x, y, max_x, max_y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_x = max_x
        self.max_y = max_y
        self.map = [['#' for _ in range(width)] for _ in range(height)]
        self.create_room()
        self.create_load()
        self.fill_corner()

    def __str__(self):
        return '\n'.join([''.join(row) for row in self.map])

    def create_room(self):
        room_width = random.randint(1, self.width)
        room_height = random.randint(1, self.height)
        for y in range(room_height):
            for x in range(room_width):
                self.map[y][x] = '.'

    def _create_load(self, direction):
        x = 1
        y = 1
        try:
            while True:
                if x < 0 or y < 0:
                    break
                self.map[y][x] = '.'
                if direction == 'top':
                    y -= 1
                elif direction == 'left':
                    x -= 1
                elif direction == 'right':
                    x += 1
                elif direction == 'bottom':
                    y += 1
        except IndexError:
            pass

    def create_load(self):
        self._create_load('top')
        self._create_load('left')
        self._create_load('right')
        self._create_load('bottom')

    def fill_corner(self):
        if self.x == 0:
            for row in self.map:
                row[0] = '#'

        if self.x == self.max_x:
            for row in self.map:
                row[-1] = '#'

        if self.y == 0:
            self.map[0] = ['#' for _ in range(self.width)]

        if self.y == self.max_y:
            self.map[-1] = ['#' for _ in range(self.width)]


class RandomBackgroundCUI:
    """背景をランダム生成する(CUI)"""

    def __init__(self, x_length, y_length, split_x=2, split_y=2):
        if x_length % split_x != 0 or y_length % split_y != 0:
            raise Exception('split_x, split_yは、x_length, y_lengthを割り切れる数にしてください。')
        self.x_length = x_length
        self.y_length = y_length
        self.split_x = split_x
        self.split_y = split_y
        self.map = None
        self.create()

    def __str__(self):
        result = ''
        for row_rects in self.map:
            maps = map(lambda rect: rect.map, row_rects)
            for map_rows in zip(*maps):
                for row in map_rows:
                    result += ''.join(row)
                result += '\n'
        return result

    def create(self):
        max_x = self.split_x - 1
        max_y = self.split_y - 1
        width = self.x_length // self.split_x
        height = self.y_length // self.split_y
        self.map = [
            [Rectangle(x, y, max_x, max_y, width, height) for x in range(self.split_x)]
            for y in range(self.split_y)
        ]
