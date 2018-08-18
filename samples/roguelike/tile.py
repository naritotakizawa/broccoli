from broccoli import register
from broccoli.material import BaseTile
from broccoli.img.loader import MultiDirection, NoDirection, NormalSplite
from broccoli.funcstions import return_true, return_false, only_player, goal


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
    name = 'マップチップ1'
    image = NormalSplite('img/tipset1.png')
