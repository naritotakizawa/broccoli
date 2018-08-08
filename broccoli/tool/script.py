"""ちょっとしたスクリプトを提供しているモジュール"""
from pathlib import Path
from PIL import Image


def split(file_name, yoko, tate):
    """画像をn*m等に分割します。

    yoko引数は横に何等分するか、tate引数は縦に何等分するかを表しています。
    300px*300pxの画像があり、yoko=5, tate=10 とした場合は
    60px、縦30pxとなり、全部で50個の画像が作られます。

    """
    image = Image.open(file_name)
    width, height = image.size
    split_width = width / yoko
    split_height = height / tate
    for row_index in range(tate):
        for col_index in range(yoko):
            start_y = row_index * split_height
            start_x = col_index * split_width
            box = (start_x, start_y, start_x+split_width, start_y+split_height)
            img = image.crop(box)
            img.save('{}{}.png'.format(row_index, col_index))


def resize(width, height, extensions=('.png', '.jpg')):
    """カレントの画像を全てリサイズする

    カレントディレクトリにある、デフォルトではpng,jpgの画像ファイルを
    widthとheightの値でリサイズします。

    """
    for file in Path().iterdir():
        if file.suffix in extensions:
            img = Image.open(file)
            img = img.resize((width, height))
            img.save(file)
