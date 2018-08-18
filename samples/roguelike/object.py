from broccoli import register, const
from broccoli.funcstions import do_nothing
from broccoli.material import RogueLikeObject
from broccoli.img.loader import MultiDirection, NoDirection, MultiDirectionWithDiff, NormalSplite


@register.object
class Sheep(RogueLikeObject):
    name = '羊'
    image = NormalSplite('img/character/sheep/sheep_1.png')
    hp = max_hp = 15
    power = 5
    kind = const.ENEMY


@register.object
class BlownBear(RogueLikeObject):
    name = 'ヒグマ'
    image = NormalSplite('img/character/bear/black_bear.png')
    hp = max_hp = 30
    power = 10
    kind = const.ENEMY


@register.object
class WhiteBear(RogueLikeObject):
    name = '北極熊'
    image = NormalSplite('img/character/bear/white_bear.png')
    hp = max_hp = 60
    power = 15
    kind = const.ENEMY


@register.object
class Sparrow(RogueLikeObject):
    name = 'スズメ'
    image = NormalSplite('img/character/bird/suzume.png')
    hp = max_hp = 7
    power = 2
    kind = const.ENEMY


@register.object
class NormalBison(RogueLikeObject):
    name = 'バイソン'
    image = NormalSplite('img/character/bison/bison_normal.png')
    hp = max_hp = 20
    power = 10
    kind = const.ENEMY


@register.object
class Camel(RogueLikeObject):
    name = 'らくだ'
    image = NormalSplite('img/RogueLikeObject/camel/camel_1.png')
    hp = max_hp = 17
    power = 7
    kind = const.ENEMY


@register.object
class Dog(RogueLikeObject):
    name = '犬'
    image = NormalSplite('img/character/dog/wanko_1.png')
    hp = 20
    max_hp = 20
    power = 10
    kind = const.ENEMY


@register.object
class MapTip1(RogueLikeObject):
    name = 'マップチップ1'
    image = NormalSplite('img/tipset1.png')
    action = do_nothing
