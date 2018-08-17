import inspect
import types
from broccoli.material import BaseTile, BaseObject, BaseItem, return_true, do_nothing


def set_method(material, attr, default=None, kwargs=None, rename_attr=None):
    """マテリアルに、メソッドを追加する

    以下のような処理を、簡単に書くための関数です。

    if hasattr(material_cls, 'rogue_action'):
        material.action = types.MethodType(material_cls.rogue_action, material)
    else:
        material.action = types.MethodType(rogue_standard_action, material)

    クラス属性としてcls_attrが定義されていれば、インスタンスのメソッドとしてそれを設定します。
    なかった場合に、defaultとして渡された属性をインスタンスのメソッドとして設定します。

    """
    cls = type(material)
    if kwargs is None:
        dic = {}

    if attr in kwargs:
        method = kwargs[attr]

    elif hasattr(cls, attr):
        method = getattr(cls, attr)

    else:
        method = default

    if method is None:
        raise Exception('メソッドが指定できませんでした。')

    setattr(
        material,
        attr,
        types.MethodType(method, material)
    )
    if rename_attr is not None:
        setattr(
            material,
            rename_attr,
            types.MethodType(method, material)
        )


class BaseSystem:

    def __init__(self):
        # Trueのときは、次のキャラクターは行動を待つ、などに使うフラグです。
        self.is_block = False
        # ゲームキャンバス
        self.canvas = None

    def setup(self):
        pass

    def start(self):
        pass

    def get_key_events(self):
        """このシステムのキーイベントを返す。"""
        return []

    def create_key_event(self):
        """キーイベントの設定。"""
        root = self.canvas.winfo_toplevel()
        for key, func in self.get_key_events():
            root.bind(key, func)

    def clear_key_event(self):
        """キーイベントを一時解除する。"""
        root = self.canvas.winfo_toplevel()
        for key, func in self.get_key_events():
            root.unbind(key)

    def create_tile(self, material_cls, **kwargs):
        try:
            material = material_cls(**kwargs)
        except TypeError:
            material = material_cls

        material.system = self
        material.canvas = self.canvas

        # タイルのis_publicとon_selfは、恐らくどんなシステムでも概ね使えることでしょう...
        set_method(material, 'is_public', default=return_true, kwargs=kwargs)
        set_method(material, 'on_self', default=do_nothing, kwargs=kwargs)
        return material

    def create_object(self, material_cls, **kwargs):
        try:
            material = material_cls(**kwargs)
        except TypeError:
            material = material_cls

        material.system = self
        material.canvas = self.canvas
        return material

    def create_item(self, material_cls, **kwargs):
        try:
            material = material_cls(**kwargs)
        except TypeError:
            material = material_cls

        material.system = self
        material.canvas = self.canvas
        return material

    def create_material(self, material_cls, **kwargs):
        """マテリアルを生成する。

        現在のシステムに合った形で、マテリアルの生成と初期設定を行う。

        """
        if inspect.isclass(material_cls):
            if issubclass(material_cls, BaseTile):
                return self.create_tile(material_cls, **kwargs)
            elif issubclass(material_cls, BaseObject):
                return self.create_object(material_cls, **kwargs)
            elif issubclass(material_cls, BaseItem):
                return self.create_item(material_cls, **kwargs)
        else:
            if isinstance(material_cls, BaseTile):
                return self.create_tile(material_cls, **kwargs)
            elif isinstance(material_cls, BaseObject):
                return self.create_object(material_cls, **kwargs)
            elif isinstance(material_cls, BaseItem):
                return self.create_item(material_cls, **kwargs)

        raise Exception('知らないのが来た')

