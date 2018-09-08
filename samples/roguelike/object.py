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
    talk = roguelike.simple_talk
    message = 'ガオー'


@register.object
class WhiteBear(RogueLikeObject):
    name = '北極熊'
    image = NormalSplite('img/character/bear/white_bear.png')
    hp = max_hp = 60
    power = 15
    kind = const.ENEMY
    talk = roguelike.simple_talk
    message = 'グォー!'


@register.object
class Sparrow(RogueLikeObject):
    name = 'スズメ'
    image = NormalSplite('img/character/bird/suzume.png')
    hp = max_hp = 7
    power = 2
    kind = const.ENEMY
    talk = roguelike.simple_talk
    message = 'チュンチュン、スズメです。'


@register.object
class NormalBison(RogueLikeObject):
    name = 'バイソン'
    image = NormalSplite('img/character/bison/bison_normal.png')
    hp = max_hp = 20
    power = 10
    kind = const.ENEMY
    talk = roguelike.simple_talk
    message = 'ガオー'


@register.object
class Camel(RogueLikeObject):
    name = 'らくだ'
    image = NormalSplite('img/character/camel/camel_1.png')
    hp = max_hp = 17
    power = 7
    kind = const.ENEMY
    talk = roguelike.simple_talk
    message = 'ガオー'


@register.object
class Dog(RogueLikeObject):
    name = '犬'
    image = NormalSplite('img/character/dog/wanko_1.png')
    hp = 20
    max_hp = 20
    power = 10
    kind = const.ENEMY
    talk = roguelike.simple_talk
    message = 'ワンワン!'


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
    name = '看板'
    image = NormalSplite('img/tipset4.png')
    action = generic.do_nothing
    on_damage = generic.do_nothing
    die = generic.do_nothing
    talk = roguelike.simple_talk
    message = 'かんばんです。'


@register.function('roguelike.object.tutorial_sheep_on_damage', system='roguelike', attr='on_damage', material='object')
def tutorial_sheep_on_damage(self, tile, obj):
    """チュートリアル羊の攻撃を食らった際の処理。

    攻撃するな、話しかけろと伝える。

    """
    # プレイヤーしか話しかかえてくるオブジェクトはいないので、必然的にobj引数はプレイヤー。
    flag = obj.vars.get('tutorial', 0)

    self.system.simple_damage_line(material=self)
    self.hp -= obj.power

    if self.hp <= 0:
        self.die(tile, obj)
    elif flag == 0:
        self.system.add_message('ボクは親切な羊。ちょっとしたインストラクションを君に授けるよ。\nまず、「z」キーでこのメッセージは進めることができる。')
        self.system.add_message('人や動物、もしかしたら植物には、「t」キーで話かけることができるよ。')
        self.system.add_message('次のインストラクションは、「t」で話しかけてから説明するよ。\nもう攻撃しないでね。')


@register.function('roguelike.object.tutorial_sheep_talk1', system='roguelike', attr='talk', material='object')
def tutorial_sheep_talk(self, obj):
    """チュートリアル羊の会話。"""
    # プレイヤーしか話しかかえてくるオブジェクトはいないので、必然的にobj引数はプレイヤー。
    flag = obj.vars.get('tutorial', 0)

    # インストラクション1
    if flag == 0:
        self.system.add_message('ボクは親切な羊。ちょっとしたインストラクションを君に授けるよ。\nまず、「z」キーでこのメッセージは進めることができる。')
        self.system.add_message('人や動物、もしかしたら植物には、今のように「t」キーで話かけることができるよ。')
        self.system.add_message('「z」キーは攻撃ができるけど、友好的っぽい動物にはしないようにしようね。   ')
        self.system.add_message('ちなみに、ここまでの会話はログに保存されてるよ。\n「l」キーで確認ができて、同じキーを押すと閉じる。')
        obj.vars['tutorial'] = 1

    # インストラクション2
    elif flag == 1:
        self.system.add_message('次は戦闘のインストラクションだよ。\n敵に向かって、「z」キーを押すだけさ。')
        self.system.add_message('悪い羊を召喚するから、そいつを倒してみよう!')
        self.layer.create_material(material_cls=Sheep, x=5, y=3, name='悪い羊', die=tutorial_enemy_die)
        obj.vars['tutorial'] = 2

    # インストラクション3
    elif flag == 2:
        self.system.add_message('話しかけている間は、ターン経過しないよ。\n早く悪い羊を倒すんだ。')

    # インストラクション4
    elif flag == 3:
        self.system.add_message('良い仕事をしたね!\n戦闘のコツは大体掴んだかな?')
        self.system.add_message('疲れたと思うから、アイテムを配置するよ。\nアイテムには、上に乗るだけで全て取得できる。')
        self.system.add_message('拾ったアイテムは、「i」キーで使えるよ。\nアイテムウィンドウを閉じるのも「i」キーさ。')
        self.system.add_message('選択状態のアイテムは赤く表示されるよ。\n複数のアイテムがあれば、上下キーで他のアイテムを選択でき、「z」で使える。')
        self.canvas.item_layer.create_material(material_cls=HealingHerb, x=5, y=3, use=tutorial_use)
        self.canvas.item_layer.create_material(material_cls=HealingHerb, x=5, y=3, use=tutorial_use)
        obj.vars['tutorial'] = 4

    elif flag == 4:
        self.system.add_message('拾ったアイテムは、「i」キーで使えるよ。\nアイテムウィンドウを閉じるのも「i」キーさ。')
        self.system.add_message('選択状態のアイテムは赤く表示されるよ。\n複数のアイテムがあれば、上下キーで他のアイテムを選択でき、「z」で使える。')

    elif flag == 5:
        self.system.add_message('ちゃんと使えたみたいだね!')


@register.function('roguelike.object.tutorial_enemy_die', system='roguelike', attr='die', material='object')
def tutorial_enemy_die(self, tile, obj):
    """チュートリアルの敵を倒した際の処理。

    死んだ後、チュートリアル羊のtalk属性を次のメッセージに書き換える。

    """
    roguelike.die(self, tile, obj)
    player = self.layer.get(name='あなた')
    player.vars['tutorial'] = 3


@register.function('roguelike.object.tutorial_use', system='roguelike', attr='use', material='item')
def tutorial_use(self):
    """チュートリアル薬草を使った際の処理。

    使った後、チュートリアル羊のtalk属性を次のメッセージに。

    """
    roguelike.healing_use(self)
    player = self.system.player
    player.vars['tutorial'] = 5


@register.object
class KindnessSheep(RogueLikeObject):
    """チュートリアル羊。"""
    name = '親切な羊'
    image = NormalSplite('img/character/sheep/sheep_1.png')
    hp = max_hp = 30
    action = generic.do_nothing
    talk = tutorial_sheep_talk
    on_damage = tutorial_sheep_on_damage
