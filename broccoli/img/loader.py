"""背景、オブジェクト、キャラクター画像の、読み込み機能に関するモジュール。"""
import random
from PIL import Image, ImageTk
from broccoli.conf import settings


class BaseLoader:
    """読み込み機能の基底クラス。"""

    def __init__(self, path):
        self.path = path
        self.image = None

    def load(self):
        self.image = ImageTk.PhotoImage(file=self.path)

    def __get__(self, instance, owner):
        if self.image is None:
            self.load()
        return self.image

    def get_x_length(self):
        return 1

    def get_y_length(self):
        return 1


class NoDirection(BaseLoader):
    """向きのない、1画像だけを読み込む。

    特に向きがない画像を読み込み場合に使います。。
    画像サイズは、settings.pyのCELL_WIDTH、CELL_HEIGHTに合わせて用意してください。

    例.
    image = NoDirection('img/sample/sample.png')

    """
    pass


class MultiDirection(BaseLoader):
    """いくつかの向きを持つ画像を読み込める。

    キャラクターなら、4方向で、歩き差分などがない場合に使えます。
    各画像サイズは、settings.pyのCELL_WIDTH、CELL_HEIGHTに合わせて用意してください。
    リストの0番目が下向き、1番目が左向き、2番目が右向き、3番目が上向きです。
    例.
    image = MultiDirection([
        'img/sample/player0.png',  # 下向き
        'img/sample/player1.png',  # 左向き
        'img/sample/player2.png',  # 右向き
        'img/sample/player3.png',  # 上向き
    ])

    タイルならば、特に4方向に拘らずに使えます。
    例.
    image = MultiDirection([
        'img/sample/green_tile1.png',
        'img/sample/green_tile2.png',
        'img/sample/green_tile3.png',
        'img/sample/green_tile4.png',
        'img/sample/green_tile5.png',
        'img/sample/green_tile6.png',
    ])
    """

    def __init__(self, path):
        super().__init__(path)
        self.images = None

    def load(self):
        self.images = [ImageTk.PhotoImage(file=path) for path in self.path]

    def __get__(self, instance, owner):
        if self.images is None:
            self.load()

        # directionが-1なら、ランダムに設定
        direction = instance.direction
        if direction == -1:
            direction = random.randrange(len(self.path))
        return self.images[direction]

    def get_x_length(self):
        return 1

    def get_y_length(self):
        return len(self.path)


class MultiDirectionWithDiff(MultiDirection):
    """いくつかの向きと差分を持つ画像を読み込める。

    キャラクターならば、4方向で、歩き差分などがある場合に使ってください。
    各画像サイズは、settings.pyのCELL_WIDTH、CELL_HEIGHTに合わせて用意してください。
    リストの0番目が下向き、1番目が左向き、2番目が右向き、3番目が上向きで
    さらに、[0]で差分1、[1]で差分2...となっていきます。
    例.
    image = MultiDirectionWithDiff([
        ['img/character/sheep/00.png', 'img/character/sheep/01.png', 'img/character/sheep/02.png',],  # 下向き各差分
        ['img/character/sheep/10.png', 'img/character/sheep/11.png', 'img/character/sheep/12.png', ],  # 左向き各差分
        ['img/character/sheep/20.png', 'img/character/sheep/21.png', 'img/character/sheep/22.png', ],  # 右向き各差分
        ['img/character/sheep/30.png', 'img/character/sheep/31.png', 'img/character/sheep/32.png', ],  # 上向き各差分
    ])

    MultiDirectionと同様、タイルなどにも使えます。

    """

    def load(self):
        self.images = [[ImageTk.PhotoImage(file=path) for path in row] for row in self.path]

    def __get__(self, instance, owner):
        if self.images is None:
            self.load()

        # directionが-1なら、ランダムに設定
        direction = instance.direction
        if direction == -1:
            direction = random.randrange(len(self.path))

        row = self.images[direction]

        # diffが-1なら、ランダムに設定
        diff = instance.diff
        if diff == -1:
            diff = random.randrange(len(row))
        else:
            diff = diff % len(row) - 1

        return row[diff]

    def get_x_length(self):
        return len(self.path[0])

    def get_y_length(self):
        return len(self.path)


class NormalSplite(MultiDirection):
    """スプライトで画像読み込みたい場合

    対象画像が186*248で、CELL_WIDTH=62、CELL_HEIGHT=62の例
    image = NormalSplite('img/character/bear/black_bear.png')
    各差分が3つ、4方向分のデータになります。

    """

    def __init__(self, path):
        super().__init__(path)
        self.images = None

    def load(self):
        src = Image.open(self.path)
        width, height = src.size
        yoko = width // settings.CELL_WIDTH
        tate = height // settings.CELL_HEIGHT
        images = [[None for x in range(yoko)] for y in range(tate)]
        for y in range(tate):
            for x in range(yoko):
                box = (
                    x * settings.CELL_WIDTH,
                    y * settings.CELL_HEIGHT,
                    x * settings.CELL_WIDTH + settings.CELL_WIDTH,
                    y * settings.CELL_HEIGHT + settings.CELL_HEIGHT
                )
                image = src.crop(box)
                images[y][x] = ImageTk.PhotoImage(image)
        self.images = images

    def __get__(self, instance, owner):
        if self.images is None:
            self.load()

        # directionが-1なら、ランダムに設定
        direction = instance.direction
        if direction == -1:
            direction = random.randrange(len(self.images))

        row = self.images[direction]

        # diffが-1なら、ランダムに設定
        diff = instance.diff
        if diff == -1:
            diff = random.randrange(len(row))
        else:
            diff = diff % len(row) - 1

        return row[diff]

    def get_x_length(self):
        if self.images is None:
            self.load()
        return len(self.images[0])

    def get_y_length(self):
        if self.images is None:
            self.load()
        return len(self.images)
