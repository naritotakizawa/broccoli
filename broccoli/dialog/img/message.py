"""ゲームにおける主要メッセージのダイアログを提供するモジュール

○○の攻撃!1のダメージ!といったアクティブメッセージウィンドウや
ログ表示でメッセージを確認するためのダイアログを提供しています。

"""
from collections import deque
from PIL import Image, ImageTk
from broccoli.dialog.base import ImgDialog
from broccoli.conf import settings


class BaseMessageDialog(ImgDialog):
    """システムメッセージ表示の基底クラス"""
    resize = None

    def __init__(self, parent, canvas):
        super().__init__(parent=parent, canvas=canvas)
        self.messages = deque()


class ActiveMessageDialog(BaseMessageDialog):
    """メッセージを都度表示する

    攻撃をしたら画面に
    「○○の攻撃!」
    と表示され、ボタンクリックで枠が消えるタイプのウィンドウ。
    シレンSFCなどに近いタイプ。

    LogMessageWindowとは仕組みが違うため、showメソッドは何もしません。
    キーイベントではなく、メッセージの追加(addメソッド呼び出し)がされるとすぐに表示をします。

    """
    width = settings.GAME_WIDTH - 40
    height = settings.GAME_HEIGHT // 3
    resize = (width, height)

    def show(self, *args, **kwargs):
        pass

    def get_key_events(self):
        """このダイアログのキーイベントを返す"""
        return [
            ('<{}>'.format(settings.ATTACK_KEY), self.next),
        ]

    def draw_text(self, x, y, message):
        """テキストを描画する

        このクラスでの、テキスト表示用の共通処理です。

        """
        self.canvas.create_text (
            x + 20 + 5,  # メッセージ枠から更に+5して配置
            y + (settings.GAME_HEIGHT - self.height) - 20 + 5,  # メッセージ枠から更に+5
            anchor='nw',
            width=self.width - 10,  # テキストを折り返す長さ。メッセージ枠から左右5pxの余白をマイナスする
            text=message,
            font=self.font,
            fill=self.color,
            tag='{} text'.format (self.tag),
        )

    def add(self, message):
        """メッセージを追加する"""
        # メッセージを表示するときがきたら、画像を読み込む。初回のみ行う。
        if self.image is None:
            self.load_image()

        # 既に表示中なら、メッセージの追加だけ行う。これは攻撃キーでの読み進め時に取り出される
        if self.canvas.find_withtag(self.tag):
            self.messages.append(message)

        # まだメッセージがないなら、メッセージの表示
        else:
            x, y = self.canvas.get_current_position_nw()
            # システムメッセージ枠の表示
            self.canvas.create_image(
                x+20,  # 横は20pxの余白
                y+(settings.GAME_HEIGHT-self.height)-20,  # 下に20px余白
                anchor='nw',
                image=self.image,
                tag=self.tag
            )

            # メッセージの表示
            self.draw_text (x, y, message)

            # アクティブメッセージ用のキーバインドに変更。標準ならzキーでメッセージ進めです。
            self.change_key_event()

    def next(self, event=None):
        """次のメッセージを表示する"""
        # メッセージを取り出して表示する
        try:
            self.canvas.delete('text')
            message = self.messages.popleft()
        except IndexError:
            self.destroy()
        else:
            x, y = self.canvas.get_current_position_nw()
            self.draw_text(x, y, message)  # メッセージの表示


class LogMessageDialog(BaseMessageDialog):
    """メッセージをログで確認する

    ログ表示欄にメッセージを表示するタイプのダイアログです。

    """
    resize = (settings.GAME_WIDTH, settings.GAME_HEIGHT)

    def get_key_events(self):
        return [
            ('<{}>'.format(settings.SHOW_MESSAGE_KEY), self.destroy),
        ]

    def add(self, message):
        """メッセージをログに追加する"""
        self.messages.append(message)

    def draw(self, event=None):
        """ログを表示する"""
        x, y = self.canvas.get_current_position_nw()

        # ログ枠の表示
        self.canvas.create_image(
            x, y, anchor='nw',
            image=self.image,
            tag=self.tag
        )

        message = '\n'.join([text for text in list(self.messages)[::-1]])
        self.canvas.create_text(
            x+5,  # メッセージ枠から更に+5して配置
            y+40,  # # 上に40px空けます。画面上段は、よく使われているので
            anchor='nw',
            width=settings.GAME_WIDTH-10,  # テキストを折り返す長さ。メッセージ枠から左右5pxの余白をマイナスする
            text=message,
            font=self.font,
            fill=self.color,
            tag='{} text'.format(self.tag),
        )


class LogAndActiveMessageDialog(LogMessageDialog):
    """アクティブメッセージと、ログ表示に対応したメッセージダイアログ

    LogMessageDialogをベースにしています。
    つまり、resize属性やimage属性, get_key_eventsメソッド等はLogMessageDialogのものです。
    ActiveMessageな機能は、active_のように名前をつけています。

    """
    active_width = settings.GAME_WIDTH - 40
    active_height = settings.GAME_HEIGHT // 3
    active_resize = (active_width, active_height)

    def __init__(self, parent, canvas):
        super().__init__(parent, canvas)

        # アクティブダイアログの属性
        self.active_image = None
        self.active_messages = deque()

    def load_image(self):
        """ダイアログの枠となる画像の作成、ロード """
        # ログダイアログ画像の設定
        super().load_image()

        # アクティブダイアログ画像の設定
        active_src = Image.open(self.src)
        if self.active_resize:
            active_src = active_src.resize(self.active_resize)
        self.active_image = ImageTk.PhotoImage(active_src)

    def add(self, message):
        """メッセージを追加する"""
        # ログ用のメッセージ追加
        self.messages.append(message)

        # メッセージを表示するときがきたら、画像を読み込む。初回のみ行う。
        if self.active_image is None:
            self.load_image()

        # 既に表示中なら、メッセージの追加だけ行う。これは攻撃キーでの読み進め時に取り出される
        if self.canvas.find_withtag(self.tag):
            self.active_messages.append(message)

        # まだメッセージがないなら、メッセージの表示
        else:
            x, y = self.canvas.get_current_position_nw()
            # システムメッセージ枠の表示
            self.canvas.create_image(
                x+20,  # 横は20pxの余白
                y+(settings.GAME_HEIGHT-self.active_height)-20,  # 下に20px余白
                anchor='nw',
                image=self.active_image,
                tag=self.tag
            )

            # メッセージの表示
            self.draw_active_text(x, y, message)

            # アクティブメッセージ用のキーバインドに変更。標準ならzキーでメッセージ進めです。
            self.change_active_key_event()

    def draw_active_text(self, x, y, message):
        self.canvas.create_text (
            x + 20 + 5,  # メッセージ枠から更に+5して配置
            y + (settings.GAME_HEIGHT - self.active_height) - 20 + 5,  # メッセージ枠から更に+5
            anchor='nw',
            width=self.active_width - 10,  # テキストを折り返す長さ。メッセージ枠から左右5pxの余白をマイナスする
            text=message,
            font=self.font,
            fill=self.color,
            tag='{} text'.format(self.tag),
        )

    def next(self, event=None):
        """次のメッセージを表示する"""
        # メッセージを取り出して表示する
        try:
            self.canvas.delete('text')
            message = self.active_messages.popleft()
        except IndexError:
            self.active_destroy()
        else:
            x, y = self.canvas.get_current_position_nw()
            self.draw_active_text(x, y, message)  # メッセージの表示

    def get_active_key_events(self):
        return [
            ('<{}>'.format(settings.ATTACK_KEY), self.next),
        ]

    def active_destroy(self, event=None):
        """ダイアログの削除"""
        self.canvas.delete(self.tag)
        self.revert_active_key_event()

    def change_active_key_event(self):
        self.parent.is_block = True
        self.parent.clear_key_event()
        root = self.canvas.winfo_toplevel()
        for key, func in self.get_active_key_events():
            root.bind(key, func)

    def revert_active_key_event(self):
        root = self.canvas.winfo_toplevel()
        for key, func in self.get_active_key_events():
            root.unbind(key)
        self.parent.create_key_event()
        self.parent.is_block = False
