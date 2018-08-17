from .__version__ import (
    __title__, __description__, __url__, __version__,
    __author__, __author_email__, __license__, __copyright__
)


class Register:

    def __init__(self):
        self.tiles = {}
        self.objects = {}
        self.items = {}
        self.public_funcs = {}
        self.on_funcs = {}
        self.generic_funcs = {}

    def tile(self, tile_cls):
        self.tiles[tile_cls.__name__] = tile_cls
        return tile_cls

    def object(self, obj_cls):
        self.objects[obj_cls.__name__] = obj_cls
        return obj_cls

    def item(self, item_cls):
        self.items[item_cls.__name__] = item_cls
        return item_cls

    def public(self, func):
        self.public_funcs[func.__name__] = func
        return func

    def on(self, func):
        self.on_funcs[func.__name__] = func
        return func

    def generic(self, func):
        self.generic_funcs[func.__name__] = func
        return func


register = Register()
