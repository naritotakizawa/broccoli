from broccoli import register, const
from broccoli.funcstions import generic, roguelike
from broccoli.material import RogueLikeObject
from broccoli.img.loader import MultiDirection, NoDirection, MultiDirectionWithDiff, NormalSplite
from item import HealingHerb


@register.object
class Sheep(RogueLikeObject):
    name = '羊'
    image = NormalSplite('img/character/sheep/sheep_1.png')
    hp = max_hp = 15
    power = 5
    kind = const.ENEMY
    talk = roguelike.simple_talk
    message = 'メェー!'


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
    talk = roguelike.simple_talk
    message = 'チュンチュン、羊です。'


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
    image = NormalSplite('img/character/camel/camel_1.png')
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
    name = '森・草原・木・洞窟'
    image = NormalSplite('img/tipset1.png')
    action = generic.do_nothing
    on_damage = generic.do_nothing
    die = generic.do_nothing


@register.object
class MapTip2(RogueLikeObject):
    name = '壺・樽'
    image = NormalSplite('img/tipset2.png')
    action = generic.do_nothing
    on_damage = generic.do_nothing
    die = generic.do_nothing


@register.object
class MapTip3(RogueLikeObject):
    name = 'フェンス'
    image = NormalSplite('img/tipset3.png')
    action = generic.do_nothing
    on_damage = generic.do_nothing
    die = generic.do_nothing


@register.object
class MapTip4(RogueLikeObject):
    name = '看板(名前とメッセージ属性を変えるとお話できるよ)'
    image = NormalSplite('img/tipset4.png')
    action = generic.do_nothing
    on_damage = generic.do_nothing
    die = generic.do_nothing
    talk = roguelike.simple_talk
    message = 'かんばんです。'


@register.function('roguelike.object.on_damage_kind_sheep', system='roguelike', attr='on_damage', material='object')
def on_damage_sheep(self, tile, obj):
    self.system.simple_damage_line(material=self)
    self.hp -= obj.power

    if self.hp <= 0:
        self.die(tile, obj)
    else:
        self.hp -= obj.power
        self.system.add_message('ボクは親切な羊。ちょっとしたインストラクションを君に授けるよ。\nまず、「z」キーでこのメッセージは進めることができる。')
        self.system.add_message('人や動物、もしかしたら植物には、「t」キーで話かけることができるよ。')
        self.system.add_message('次のインストラクションは、「t」で話しかけてから説明するよ。\nもう攻撃しないでね。')


@register.function('roguelike.object.talk_kind_sheep', system='roguelike', attr='talk', material='object')
def talk_kind_sheep1(self, obj):
    self.system.add_message('ボクは親切な羊。ちょっとしたインストラクションを君に授けるよ。\nまず、「z」キーでこのメッセージは進めることができる。')
    self.system.add_message('人や動物、もしかしたら植物には、今のように「t」キーで話かけることができるよ。')
    self.system.add_message('「z」キーは攻撃ができるけど、友好的っぽい動物にはしないようにしようね。   ')
    self.system.add_message('ちなみに、ここまでの会話はログに保存されてるよ。「l」キーで確認ができて、同じキーを押すと閉じる。')
    self.talk = self.create_method(talk_kind_sheep2)


def talk_kind_sheep2(self, obj):
    self.system.add_message('次は戦闘のインストラクションだよ。敵に向かって、「z」キーを押すだけさ。')
    self.system.add_message('悪い羊を召喚するから、そいつを倒してみよう!')
    self.layer.create_material(material_cls=Sheep, x=2, y=3, name='悪い羊', die=die_sheep)


def talk_kind_sheep3(self, obj):
    self.system.add_message('良い仕事をしたね!戦闘のコツは大体掴んだかな?')
    self.system.add_message('疲れたと思うから、アイテムを配置するよ。アイテムには、上に乗るだけで取得できる。')
    self.system.add_message('拾ったアイテムは、「i」キーで使えるよ。アイテムウィンドウを閉じるのも「i」キーさ。')
    self.canvas.item_layer.create_material(material_cls=HealingHerb, x=2, y=3, use=tutorial_use)


def talk_kind_sheep4(self, obj):
    self.system.add_message('無事回復できたようだね!これで基本は終わりだよ!')
    self.system.add_message('マップの上に移動すると、ダンジョンに移動できるようにしたよ。')
    self.system.add_message('グッドラック!')


def die_sheep(self, tile, obj):
    roguelike.die(self, tile, obj)
    tutorial_sheep = self.layer.get(name='親切な羊')
    tutorial_sheep.talk = tutorial_sheep.create_method(talk_kind_sheep3)


def tutorial_use(self):
    roguelike.healing_use(self)
    tutorial_sheep = self.canvas.object_layer.get(name='親切な羊')
    tutorial_sheep.talk = tutorial_sheep.create_method(talk_kind_sheep4)


@register.object
class KindnessSheep(RogueLikeObject):
    name = '親切な羊'
    image = NormalSplite('img/character/sheep/sheep_1.png')
    hp = max_hp = 15
    action = generic.do_nothing
    talk = talk_kind_sheep1
    on_damage = on_damage_sheep
