"""ゲームにおける主要メッセージのダイアログを提供するモジュール(tkウィジェットを使ったダイアログ)

○○の攻撃!1のダメージ!といったアクティブメッセージウィンドウや
ログ表示でメッセージを確認するためのダイアログを提供しています。

"""
import tkinter as tk
from broccoli.dialog.base import Dialog
from broccoli.conf import settings


class BaseMessageDialog(Dialog):
    """システムメッセージ表示の基底クラス。"""

    def __init__(self, parent, canvas):
        super().__init__(parent=parent, canvas=canvas)
        self.messages = []


class ActiveMessageDialog(BaseMessageDialog):
    """メッセージを都度表示する。

    攻撃をしたら画面に
    「○○の攻撃!」
    と表示され、ボタンクリックで枠が消えるタイプのウィンドウ。
    シレンSFCなどに近いタイプ。

    LogMessageWindowとは仕組みが違うため、showメソッドは何もしません。
    キーイベントではなく、メッセージの追加(addメソッド呼び出し)がされるとすぐに表示をします。

    """
    width = settings.GAME_WIDTH - 40
    height = settings.GAME_HEIGHT // 3
    x = 20  # 左から20pxの位置
    y = settings.GAME_HEIGHT - height- 20  # 下に20pxの余白をつけて配置

    def show(self, *args, **kwargs):
        pass

    def draw(self):
        """ウィジェットを配置する。"""
        self.widget = tk.Canvas(
            master=self.root, bg=self.bg,
            width=self.width, height=self.height,
            highlightthickness=0,  # 枠線を消す
        )
        self.widget.place(x=self.x, y=self.y)

        # アクティブメッセージ用のキーバインドに変更。標準ならzキーでメッセージ進めです。
        self.change_key_event()

    def draw_text(self, message):
        """テキストを描画する。

        このクラスでの、テキスト表示用の共通処理です。

        """
        self.widget.create_text (
            5, 5,  # テキストは、xもyも5px余白をつけて表示する。
            anchor='nw',
            width=self.width-10,  # テキストを折り返す長さ。メッセージ枠から左右5pxの余白をマイナスする
            text=message,
            font=self.font,
            fill=self.color,
            tag='text',
        )

    def get_key_events(self):
        """このダイアログのキーイベントを返す。"""
        return [
            ('<{}>'.format(settings.ATTACK_KEY), self.next),
        ]

    def add(self, message):
        """メッセージを追加する。"""
        self.messages.append(message)
        if self.widget is None:
            self.draw()
            self.next()

    def next(self, event=None):
        """次のメッセージを表示する。"""
        try:
            self.widget.delete('text')
            message = self.messages.pop()
        except IndexError:
            self.destroy()
        else:
            self.draw_text(message)  # メッセージの表示


class LogMessageDialog(BaseMessageDialog):
    """メッセージをログで確認する。

    ログ表示欄にメッセージを表示するタイプのダイアログです。

    """
    width = settings.GAME_WIDTH
    height = settings.GAME_HEIGHT
    x = 0
    y = 0

    def up(self, event):
        """ログエリアを上にスクロール。"""
        self.widget.yview_scroll(-1, 'units')

    def down(self, event):
        """ログエリアを下にスクロール。"""
        self.widget.yview_scroll(1, 'units')

    def get_key_events(self):
        return [
            ('<{}>'.format(settings.SHOW_MESSAGE_KEY), self.destroy),
            ('<{}>'.format(settings.DOWN_KEY), self.down),
            ('<{}>'.format(settings.UP_KEY), self.up),
        ]

    def add(self, message):
        """メッセージをログに追加する。"""
        self.messages.append(message)

    def draw(self):
        """ウィジェットを配置する。"""

        self.widget = tk.Canvas(
            master=self.root, bg=self.bg,
            width=self.width, height=self.height,
            highlightthickness=0,  # 枠線を消す
        )
        self.widget.place(x=self.x, y=self.y)

        message = '\n'.join([text for text in list(self.messages)[::-1]])
        self.widget.create_text(
            5, 5,  # 5pxの余白
            anchor='nw',
            width=self.width-10,  # テキストを折り返す長さ。メッセージ枠から左右5pxの余白をマイナスする
            text=message,
            font=self.font,
            fill=self.color,
        )

        # ログが長いことも考え、スクロールできるようにしておく。
        # bbox('all')で、キャンバス内の描画物がどこまで及んでいるか取得できる
        # キャンバスからはみ出ている部分も取得されるので、現在のログメッセージ合計が何pxあるかがわかる
        # 取得したキャンバスの高さがウィジェット自体より大きければ、それをスクロール可能領域として設定
        try:
            _, _, _, max_y = self.widget.bbox('all')
        except TypeError:
            max_y = 0
        self.widget.configure(scrollregion=(0, 0, 0, max(self.height, max_y)))


class LogAndActiveMessageDialog(LogMessageDialog):
    """アクティブメッセージと、ログ表示に対応したメッセージダイアログ。

    LogMessageDialogをベースにしています。
    つまり、heightやwidth, get_key_eventsメソッド等はLogMessageDialogのものです。
    ActiveMessageな機能は、active_のように名前をつけています。

    """

    active_width = settings.GAME_WIDTH - 40
    active_height = settings.GAME_HEIGHT // 3
    active_x = 20  # 左から20pxの位置
    active_y = settings.GAME_HEIGHT - active_height- 20  # 下に20pxの余白をつけて配置

    def __init__(self, parent, canvas):
        super().__init__(parent, canvas)
        self.active_messages = []
        self.active_widget = None

    def add(self, message):
        """メッセージを追加する。"""
        self.messages.append(message)
        self.active_messages.append(message)

        if self.active_widget is None:
            self.active_draw()
            self.active_next()

    def active_draw(self):
        """ウィジェットを配置する。"""
        self.active_widget = tk.Canvas(
            master=self.root, bg=self.bg,
            width=self.active_width, height=self.active_height,
            highlightthickness=0,  # 枠線を消す
        )
        self.active_widget.place(x=self.active_x, y=self.active_y)

        # アクティブメッセージ用のキーバインドに変更。標準ならzキーでメッセージ進めです。
        self.change_active_key_event()

    def active_draw_text(self, message):
        self.active_widget.create_text (
            5, 5,
            anchor='nw',
            width=self.active_width-10,  # テキストを折り返す長さ。メッセージ枠から左右5pxの余白をマイナスする
            text=message,
            font=self.font,
            fill=self.color,
            tag='text',
        )

    def active_next(self, event=None):
        """次のメッセージを表示する。"""
        try:
            self.active_widget.delete('text')
            message = self.active_messages.pop()
        except IndexError:
            self.active_destroy()
        else:
            self.active_draw_text(message)  # メッセージの表示

    def get_active_key_events(self):
        return [
            ('<{}>'.format(settings.ATTACK_KEY), self.active_next),
        ]

    def active_destroy(self, event=None):
        """ダイアログの削除。"""
        self.active_widget.destroy()
        self.active_widget = None
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