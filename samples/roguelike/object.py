from broccoli import register
from broccoli.material import Character, UnBreakableObject
from broccoli.img.loader import MultiDirection, NoDirection, MultiDirectionWithDiff, NormalSplite


@register.object
class Sheep(Character):
    name = '羊'
    description = '羊'
    image = NormalSplite('img/character/sheep/sheep_1.png')
    default_hp = 15
    default_power = 5


@register.object
class BlownBear(Character):
    name = 'ヒグマ'
    description = 'ヒグマ'
    image = NormalSplite('img/character/bear/black_bear.png')
    default_hp = 30
    default_power = 10


@register.object
class WhiteBear(Character):
    name = '北極熊'
    description = '北極熊'
    image = NormalSplite('img/character/bear/white_bear.png')
    default_hp = 60
    default_power = 15


@register.object
class Sparrow(Character):
    name = 'スズメ'
    description = 'スズメ'
    image = NormalSplite('img/character/bird/suzume.png')
    default_hp = 7
    default_power = 2


@register.object
class NormalBison(Character):
    name = 'バイソン'
    description = 'バイソン'
    image = NormalSplite('img/character/bison/bison_normal.png')
    default_hp = 20
    default_power = 10


@register.object
class Camel(Character):
    name = 'らくだ'
    description = 'らくだ'
    image = NormalSplite('img/character/camel/camel_1.png')
    default_hp = 17
    default_power = 7


@register.object
class Dog(Character):
    name = '犬'
    description = '犬'
    image = NormalSplite('img/character/dog/wanko_1.png')
    default_hp = 20
    default_power = 10


@register.object
class MapTip1(UnBreakableObject):
    name = 'マップチップ1'
    description = 'マップチップ1'
    image = NormalSplite('img/tipset1.png')
