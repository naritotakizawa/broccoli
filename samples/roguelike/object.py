from broccoli import register, const
from broccoli.material import BaseObject, action, do_nothing
from broccoli.img.loader import MultiDirection, NoDirection, MultiDirectionWithDiff, NormalSplite


@register.object
class Sheep(BaseObject):
    name = '羊'
    image = NormalSplite('img/character/sheep/sheep_1.png')
    rogue_hp = 15
    rogue_power = 5
    kind = const.ENEMY


@register.object
class BlownBear(BaseObject):
    name = 'ヒグマ'
    image = NormalSplite('img/character/bear/black_bear.png')
    rogue_hp = 30
    rogue_power = 10
    kind = const.ENEMY


@register.object
class WhiteBear(BaseObject):
    name = '北極熊'
    image = NormalSplite('img/character/bear/white_bear.png')
    rogue_hp = 60
    rogue_power = 15
    kind = const.ENEMY


@register.object
class Sparrow(BaseObject):
    name = 'スズメ'
    image = NormalSplite('img/character/bird/suzume.png')
    rogue_hp = 7
    rogue_power = 2
    kind = const.ENEMY


@register.object
class NormalBison(BaseObject):
    name = 'バイソン'
    image = NormalSplite('img/character/bison/bison_normal.png')
    rogue_hp = 20
    rogue_power = 10
    kind = const.ENEMY


@register.object
class Camel(BaseObject):
    name = 'らくだ'
    image = NormalSplite('img/BaseObject/camel/camel_1.png')
    rogue_hp = 17
    rogue_power = 7
    kind = const.ENEMY


@register.object
class Dog(BaseObject):
    name = '犬'
    image = NormalSplite('img/character/dog/wanko_1.png')
    rogue_hp = 20
    rogue_power = 10
    kind = const.ENEMY


@register.object
class MapTip1(BaseObject):
    name = 'マップチップ1'
    image = NormalSplite('img/tipset1.png')
    rogue_action = do_nothing
