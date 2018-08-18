from broccoli import register
from broccoli.material import RogueLikeItem
from broccoli.img.loader import NoDirection


@register.item
class HealingHerb(RogueLikeItem):
    name = '薬草'
    power = 10
    image = NoDirection('img/item/herb1.png')
