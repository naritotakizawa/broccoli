"""ローグライクシステムのオブジェクトに使える関数を提供する。"""
from broccoli import register
from broccoli import const


@register.function('roguelike.object.action', system='roguelike', attr='action', material='object')
def action(self):
    # 4方向に攻撃できそうなのがいれば、攻撃する
    for direction, x, y in self.get_4_positions():
        tile = self.canvas.tile_layer[y][x]
        obj = self.canvas.object_layer[y][x]
        if obj is not None and self.is_enemy(obj):
            self.change_direction(direction)
            self.attack(tile, obj)
            break

    # 4方向に攻撃できそうなのがいない
    else:
        # 周囲の敵対キャラを探す
        enemies = list(self.get_enemies())

        # 敵がいれば、一番近いのを探し、そいつに向かって移動
        if enemies:
            target = self.get_nearest(enemies)
            self.towards(target)  # 敵に向かって歩く

        # 敵がいなければ、ランダムに歩く
        else:
            self.random_walk()


@register.function('roguelike.object.random_walk', system='roguelike', attr='random_walk', material='object')
def random_walk(self):
    """ランダムに移動する"""
    for direction, x, y in self.get_4_positions():
        tile = self.canvas.tile_layer[y][x]
        obj = self.canvas.object_layer[y][x]
        if tile.is_public(obj=self) and obj is None:
            self.change_direction(direction)
            self.move(tile)
            break


@register.function('roguelike.object.move', system='roguelike', attr='move', material='object')
def move(self, tile):
    """移動処理。

    実際の移動処理を行い、背景のon_selfを呼び出します。
    このメソッドを上書きする際、背景のon_selfをは最後に呼び出すようにしてください。
    on_selfで他のマップへ移動したり、ちがうx,y座標にジャンプさせることがありますが
    このメソッドの先頭で呼び出してしまうと、その後のy,x座標の代入やレイヤの参照で問題が発生します。

    引数:
        tile: 移動先の背景

    """
    # object_layer内の移動元にNone(誰もいない状態)にする
    self.canvas.object_layer[self.y][self.x] = None

    # object_layer内の移動先にキャラクターを設定
    self.canvas.object_layer[tile.y][tile.x] = self

    # y、x座標を更新
    self.y = tile.y
    self.x = tile.x

    # 移動する
    self.system.simple_move(self.id, material=self)

    # アイテムの取得
    items = self.canvas.item_layer[self.y][self.x]
    if items:
        messages = []
        for item in items:
            item.owner = self
            self.items.append(item)
            item.delete()
            messages.append('{}は{}を拾った!'.format(self.name, item.name))

        self.system.add_message('\n'.join(messages))

    # 必ず最後に
    tile.on_self(self)


@register.function('roguelike.object.is_enemy', system='roguelike', attr='is_enemy', material='object')
def is_enemy(self, obj):
    """壊れるオブジェクトのデフォルトは、主人公と敵対です。"""
    # 自身がPLAYERなら、ENEMYを敵とみなす
    if self.kind == const.PLAYER:
        if obj.kind == const.ENEMY:
            return True
        else:
            return False

    # 自身がENEMYなら、PLAYERは敵とみなす
    elif self.kind == const.ENEMY:
        if obj.kind == const.PLAYER:
            return True
        else:
            return False

    # NEUTRALなら、みんな友達
    return False


@register.function('roguelike.object.on_damage', system='roguelike', attr='on_damage', material='object')
def on_damage(self, tile, obj):
    """ダメージをうける。"""
    self.system.simple_damage_line(material=self)
    self.hp -= obj.power
    self.system.add_message('{}の攻撃!\n{}は{}のダメージを受けた!'.format(obj.name, self.name, obj.power))
    if self.hp <= 0:
        self.die(tile, obj)


@register.function('roguelike.object.die', system='roguelike', attr='die', material='object')
def die(self, tile, obj):
    """死んだらキャンバス上から消える"""
    self.system.add_message('{}は倒れた!'.format(self.name))
    self.delete()


@register.function('roguelike.object.player_die', system='roguelike', attr='die', material='object')
def player_die(self, tile, obj):
    """プレイヤーが死んだらゲームオーバー"""
    die(self, tile, obj)
    self.system.game_over()


@register.function('roguelike.object.attack', system='roguelike', attr='attack', material='object')
def attack(self, tile, obj):
    """攻撃処理。

    一般的な流れとしては、まず攻撃モーションを呼び出します。
    if obj is not None でオブジェクトが存在するかを確認し
    存在していればオブジェクトのon_damageメソッドを呼び出します。

    引数:
        tile: 攻撃先の背景。オブジェクトはないことがあるので(Noneの場合があるので)、背景を目印に攻撃する
        obj: 攻撃先のオブジェクト。なければNone

    """
    # 攻撃モーション
    self.system.move_to_animation(self.id, from_material=self, to_material=tile)

    # 移動先にオブジェクトがあれば、そいつのon_damageを呼び出す
    if obj is not None:
        obj.on_damage(tile, self)

    # 基の位置に戻す
    self.system.simple_move(self.id, material=self)


@register.function('roguelike.object.towards', system='roguelike', attr='towards', material='object')
def towards(self, material):
    """対象に向かって移動する。"""
    # 相手が右側にいる
    if self.x < material.x:
        x = self.x + 1
        y = self.y
        if self.canvas.check_position(x, y):
            tile = self.canvas.tile_layer[y][x]
            obj = self.canvas.object_layer[y][x]
            if tile.is_public(obj=self) and obj is None:
                self.change_direction(const.RIGHT)
                self.move(tile)
                return

    # 相手が左側にいる
    if self.x > material.x:
        x = self.x - 1
        y = self.y
        if self.canvas.check_position(x, y):
            tile = self.canvas.tile_layer[y][x]
            obj = self.canvas.object_layer[y][x]
            if tile.is_public(obj=self) and obj is None:
                self.change_direction(const.LEFT)
                self.move(tile)
                return

    # 相手が下側にいる
    if self.y < material.y:
        x = self.x
        y = self.y + 1
        if self.canvas.check_position(x, y):
            tile = self.canvas.tile_layer[y][x]
            obj = self.canvas.object_layer[y][x]
            if tile.is_public(obj=self) and obj is None:
                self.change_direction(const.DOWN)
                self.move(tile)
                return

    # 相手が上側にいる
    if self.y > material.y:
        x = self.x
        y = self.y - 1
        if self.canvas.check_position(x, y):
            tile = self.canvas.tile_layer[y][x]
            obj = self.canvas.object_layer[y][x]
            if tile.is_public(obj=self) and obj is None:
                self.change_direction(const.UP)
                self.move(tile)
                return


@register.function('roguelike.object.get_enemies', system='roguelike', attr='get_enemies', material='object')
def get_enemies(self, see_x=None, see_y=None):
    """自分の周りの敵を返す。

    see_x、see_yは範囲です。指定しなければ、デフォルト値としてクラス属性が使われます。
    クラス属性のデフォルトは、2です。

    """
    see_x = see_x or self.see_x
    see_y = see_y or self.see_y
    for x, y, obj in self.canvas.object_layer.all(include_none=False):
        if abs(self.x-x) <= see_x and abs(self.y-y) <= see_y:
            if self.is_enemy(obj) and obj != self:
                yield obj


@register.function('roguelike.object.simple_talk', system='roguelike', attr='talk', material='object')
def simple_talk(self, obj):
    """シンプルにしゃべる。

    message属性の内容を、そのまま喋ります。
    obj引数は、話しかけてきた相手です。多くの場合、プレイヤーになります。

    """
    if isinstance(self.message, str):
        self.system.add_message(self.message)
    else:
        for mes in self.message:
            self.system.add_message(mes)
