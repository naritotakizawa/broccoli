from .__version__ import (
    __title__, __description__, __url__, __version__,
    __author__, __author_email__, __license__, __copyright__
)


class Register:

    def __init__(self):
        self.tiles = {}
        self.objects = {}
        self.items = {}
        self.functions = {}
        self.function_system_categories = {}
        self.function_attr_categories = {}

    def tile(self, tile_cls):
        self.tiles[tile_cls.__name__] = tile_cls
        return tile_cls

    def object(self, obj_cls):
        self.objects[obj_cls.__name__] = obj_cls
        return obj_cls

    def item(self, item_cls):
        self.items[item_cls.__name__] = item_cls
        return item_cls

    def function(self, name, system='all', attr='all'):
        def _function(func):
            self.functions[name] = func
            # systemでの登録
            category = self.function_system_categories.setdefault(system, set())
            category.add(
                (name, func)
            )
            # attrでの登録
            category = self.function_attr_categories.setdefault(attr, set())
            category.add(
                (name, func)
            )
            return func
        return _function

    def search_functions(self, system=None, attr=None):
        result = {(name ,func) for name, func in self.functions.items()}
        if system is not None:
            data = self.function_system_categories.get(system)
            if data:
                result = result & data

        if attr is not None:
            data = self.function_attr_categories.get(attr)
            if data:
                result = result & data

        return result


register = Register()
from broccoli import funcstions  # import broccoliとされた時点で、registerに登録すべき関数をロードしにいく
