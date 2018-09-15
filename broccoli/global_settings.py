import os

GAME_TITLE = 'マイゲーム'

# 1つの背景、キャラクター、オブジェクトの幅(px)
CELL_WIDTH = 64

# 1つの背景、キャラクター、オブジェクトの高さ(px)
CELL_HEIGHT = 64

# ゲーム画面にはいくつセルを配置するか
DISPLAY_X_NUM = 5
DISPLAY_Y_NUM = 5

# 各ボタンの設定
UP_KEY = 'w'  # 上に移動
LEFT_KEY = 'a'  # 左に移動
RIGHT_KEY = 'd'  # 右に移動
DOWN_KEY = 's'  # 下に移動
ATTACK_KEY = 'z'  # 攻撃や決定
SHOW_ITEM_KEY = 'i'  # アイテムの表示
SHOW_MESSAGE_KEY = 'l'  # ログ表示キー
TALK_KEY = 't'  # 喋る
SAVE_KEY = 'F1'  # セーブ
LOAD_KEY = 'F2'  # ロード

# ゲーム中のテキストのデフォルトフォント
DEFAULT_TEXT_FONT = 'ＭＳ ゴシック'

# ゲーム中のテキストのデフォルトサイズ
DEFAULT_TEXT_SIZE = 14

# ゲーム中のテキストの色
DEFAULT_TEXT_COLOR = 'black'

# ブロッコリフレームワークで利用・提供している画像のディレクトリパス
BROCCOLI_IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')

# 利用するマネージャークラス
MANAGER_CLASS = 'broccoli.manage.SimpleGameManager'
