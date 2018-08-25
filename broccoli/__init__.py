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
        self.func_system_category = set()
        self.func_attr_category = set()
        self.func_material_category = set()

    def tile(self, tile_cls):
        self.tiles[tile_cls.__name__] = tile_cls
        return tile_cls

    def object(self, obj_cls):
        self.objects[obj_cls.__name__] = obj_cls
        return obj_cls

    def item(self, item_cls):
        self.items[item_cls.__name__] = item_cls
        return item_cls

    def function(self, name, system='all', attr='all', material='all'):
        def _function(func):
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
        result = self.functions.copy()
        if system is not None:
            result = {func_name: func_obj for func_name, func_obj in result.items() if func_obj.system == system}

        if attr is not None:
            result = {func_name: func_obj for func_name, func_obj in result.items() if func_obj.attr == attr}

        if material is not None:
            result = {func_name: func_obj for func_name, func_obj in result.items() if func_obj.material == material}

        return result


register = Register()
from broccoli import funcstions  # load material functions
