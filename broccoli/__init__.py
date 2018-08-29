from .__version__ import (
    __title__, __description__, __url__, __version__,
    __author__, __author_email__, __license__, __copyright__
)


def parse_xy(x=None, y=None, material=None):
    """x, y座標(レイヤの)を返す。

    (x, y)というタプルか、マテリアルを受け取り、(x, y)というタプルを返します。
    どちらの引数も指定がない場合は例外を送出します。

    """
    if material is not None:
        return material.x, material.y

    elif x is not None and y is not None:
        return x, y

    raise Exception('座標(x, y)か、ピントを合わせるマテリアルを指定してください。')


class Register:
    """ユーザー定義のデータを登録するクラス。"""

    def __init__(self):
        self.tiles = {}
        self.objects = {}
        self.items = {}
        self.functions = {}
        self.func_system_category = set()
        self.func_attr_category = set()
        self.func_material_category = set()

    def tile(self, tile_cls):
        """ユーザー定義タイルを登録する。"""
        self.tiles[tile_cls.__name__] = tile_cls
        return tile_cls

    def object(self, obj_cls):
        """ユーザー定義オブジェクトを登録する。"""
        self.objects[obj_cls.__name__] = obj_cls
        return obj_cls

    def item(self, item_cls):
        """ユーザー定義アイテムを登録する。"""
        self.items[item_cls.__name__] = item_cls
        return item_cls

    def function(self, name, system='all', attr='all', material='all'):
        """ユーザー関数を登録する。

        引数について
        name引数は関数の登録名です。一意なものであれば何でも構いませんが、
        その関数がどういうものなのかを示す名前にするのがベストです。
        今のところ、「対象システム.対象マテリアル.関数名」という名前をよくつけています。
        broccoli.functionsパッケージにいくつかのサンプルがあります。

        system, attr, material引数は必須ではなく、関数のメタ情報を登録するためのものです。
        マップの編集エディタでは、ユーザー定義関数を検索する際にこれらの引数を利用しています。
        無理に指定する必要はありませんが、つけておいたほうがマップエディタでの関数検索が捗ります。

        system引数は、その関数が主にどのシステムで使われるかの名前です。
        デフォルト値のallならば、おそらく全てのシステムで使える関数である、ということです。
        roguelikeならば、ローグライク系のシステムで使えそうです。

        attr引数は、どの属性に紐づくかの指定です。
        マテリアルのis_public属性に指定されるであろう関数ならば、is_publicと付けます。
        類似の関数(action1, action2, action3)があった場合に、検索が便利になります。

        material引数は、主にどのマテリアルに設定される関数かを表します。
        上に乗ったら次マップに移動する関数ならば、恐らくタイルにしか使われない関数です。tileと指定します。

        """
        def _function(func):
            # 関数オブジェクトから関数の登録名を参照できるように、関数そのもののname属性に登録名を入れています。
            # その他にも、関数の検索を行いやすくするために、対象システム、属性、マテリアルなども属性として登録しています。
            self.functions[name] = func
            func.name = name
            func.system = system
            func.attr = attr
            func.material = material
            self.func_attr_category.add(attr)
            self.func_system_category.add(system)
            self.func_material_category.add(material)
            return func
        return _function

    def search_functions(self, system=None, attr=None, material=None):
        """関数を検索する。

        引数のsystem、attr、materialの内容でself.functionsから関数を検索します。
        これらの引数はregister.functionデコレータに渡したものと同じものを指定することになります。

        """
        result = self.functions.copy()
        if system is not None:
            result = {func_name: func_obj for func_name, func_obj in result.items() if func_obj.system == system}

        if attr is not None:
            result = {func_name: func_obj for func_name, func_obj in result.items() if func_obj.attr == attr}

        if material is not None:
            result = {func_name: func_obj for func_name, func_obj in result.items() if func_obj.material == material}

        return result


register = Register()
