from broccoli import register
from broccoli.material import HealingItem
from broccoli.img.loader import NoDirection


@register.item
class HealingHerb(HealingItem):
    name = '薬草'
    description = '薬草です。'
    default_power = 10
    image = NoDirection('img/item/herb1.png')
