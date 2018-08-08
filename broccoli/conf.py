"""設定を管理するモジュール。

settings.CELL_WIDTH のようにしてゲームの設定にアクセスできます。
global_settings.pyの内容を読んでデフォルトの設定をしつつ、
pythonコマンド実行時のカレントにあるsettings.pyの内容も読み込み、上書きします。
特に上書きしたい内容がなければ、settings.pyは作成する必要はありません。

"""
import importlib
import sys
from broccoli import global_settings
# 「mapeditor」コマンド等を使った際はカレントがsys.pathにないので追加する。
if '.' not in sys.path:
    sys.path.insert(0, '.')


class Settings:
    """グローバルな設定を管理するクラス。"""

    def __init__(self):
        self.set_global_attr()
        self.set_user_attr()
        self.set_width_height()

    def set_global_attr(self):
        """global_settings.pyにあるグローバルな設定を、インスタンスの属性にする。"""
        for setting in dir(global_settings):
            if setting.isupper():
                setting_value = getattr(global_settings, setting)
                setattr(self, setting, setting_value)

    def set_user_attr(self):
        """ユーザー定義の設定を、インスタンスの属性にする。

        ユーザー定義の設定ファイル(デフォルトでsettings.py)は作らないケースも考えられるので
        ModuleNotFoundErrorになった場合、passとしています。

        """
        try:
            user_settings = importlib.import_module('settings')
        except ModuleNotFoundError:
            pass
        else:
            for setting in dir(user_settings):
                if setting.isupper():
                    setting_value = getattr(user_settings, setting)
                    setattr(self, setting, setting_value)

    def set_width_height(self):
        """ゲームエリアの幅と高さを計算して設定する。"""
        # ゲーム画面の幅、高さ
        self.GAME_WIDTH = self.CELL_WIDTH * self.DISPLAY_X_NUM
        self.GAME_HEIGHT = self.CELL_HEIGHT * self.DISPLAY_Y_NUM


settings = Settings()
