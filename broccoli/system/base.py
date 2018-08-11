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

    def create_material(self, material_cls, **kwargs):
        try:
            material = material_cls(**kwargs)
        except TypeError:
            material = material_cls

        material.system = self
        material.canvas = self.canvas
        return material
