"""ローグライクシステムのアイテムに使える関数を提供する。"""
from broccoli import register


@register.function('roguelike.item.healing_use', system='roguelike', attr='use', material='item')
def healing_use(self):
    """使う"""
    self.owner.hp += self.power
    if self.owner.hp >= self.owner.max_hp:
        self.owner.hp = self.owner.max_hp
    self.owner.items.remove(self)  # 通常は使ったら消える
    self.system.add_message('{}は\n{}を使った!'.format(self.owner.name, self.name))
