from broccoli import register
from broccoli.material import BaseTile
from broccoli.img.loader import MultiDirection, NoDirection, NormalSplite
from broccoli.material.function import only_player, goal


@register.tile
class GrassTile(BaseTile):
    name = '草原'
    description = '草のタイル'
    image = MultiDirection([
        'img/tile/grass/grass1.png',
        'img/tile/grass/grass2.png',
        'img/tile/grass/grass3.png',
        'img/tile/grass/grass4.png',
    ])


@register.tile
class WallTile(BaseTile):
    name = '壁'
    description = '壁のタイル'
    image = NoDirection('img/tile/wall/wall1.png')
    public = False  # 通れないタイル


@register.tile
class MapTip1(BaseTile):
    name = 'マップチップ1'
    description = 'マップチップ1'
    image = NormalSplite('img/tipset1.png')

