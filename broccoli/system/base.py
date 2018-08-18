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

    def create_material(self, material_cls, **kwargs):
        try:
            material = material_cls(**kwargs)
        except TypeError:
            material = material_cls
        material.canvas = self.canvas
        material.system = self
        return material