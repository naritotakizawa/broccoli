from broccoli import register
from broccoli.material import BaseTile
from broccoli.img.loader import MultiDirection, NoDirection, NormalSplite
from broccoli.funcstions.generic import return_true, return_false
from broccoli.funcstions.generic.tile import goal, only_player


@register.tile
class GrassTile(BaseTile):
    name = '草原'
    image = MultiDirection([
        'img/tile/grass/grass1.png',
        'img/tile/grass/grass2.png',
        'img/tile/grass/grass3.png',
        'img/tile/grass/grass4.png',
    ])


@register.tile
class WallTile(BaseTile):
    name = '壁'
    image = NoDirection('img/tile/wall/wall1.png')
    is_public = return_false


@register.tile
class MapTip1(BaseTile):
    name = '森・草原マップチップ'
    image = NormalSplite('img/tipset1.png')
