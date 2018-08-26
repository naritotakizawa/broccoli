"""ゲームシステムの基底クラスを提供する。"""


class BaseSystem:

    def __init__(self):
        # Trueのときは、次のキャラクターは行動を待つ、などに使うフラグです。
        self.is_block = False

        # ゲームキャンバス
        self.canvas = None

    def setup(self):
        """システムのセットアップを行う。

        多くの場合、ゲームキャンバスがインスタンス化された段階で呼び出され、
        他レイヤクラスも作成済みになっています。

        システムで使う何らかのダイアログがあれば先にインスタンス化や初期設定を行ったり、
        マップにプレイヤーや味方を配置する必要があれば、ここで行うこともできます

        """
        pass

    def start(self):
        """システムをスタートします。

        多くの場合、ゲームキャンバスのstartメソッド後に呼び出されます。

        ゲームの開始は、ターン制のゲームであればキーボードイベントが有効になった瞬間と考えますので
        ここでゲームのキーボードイベントをbindすることになります。

        リアルタイム制なゲームであれば、ここで各キャラクターの行動を開始することになるでしょう。

        マップにターン数や経過時間という概念があれば、それもここで始めるのが得策です。

        """
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
        """マテリアルの生成と初期設定を行う。

        レイヤークラスのcreate_materialメソッドから呼ばれます。

        このcreate_materialを直接呼び出すケースは少なく、
        各システム毎にマテリアル生成に変化をもたせたい場合や、
        マテリアル生成の際のフックとして利用するのが多いと思われます。

        """
        try:
            material = material_cls(**kwargs)
        except TypeError:
            material = material_cls
        material.canvas = self.canvas
        material.system = self
        return material