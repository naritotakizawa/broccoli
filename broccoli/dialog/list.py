"""何かを一覧表示するためのダイアログを提供するモジュール。"""
import tkinter as tk
from broccoli.conf import settings
from broccoli.dialog import Dialog


class ListDialog(Dialog):
    """一覧表示に使うダイアログ"""
    width = settings.GAME_WIDTH
    height = settings.GAME_HEIGHT
    x = 0
    y = 0

    def __init__(self, parent, canvas):
        super().__init__(parent, canvas)
        self.index = 0

    def get_key_events(self):
        """このダイアログのキーイベントを返す。"""
        return [
            ('<{}>'.format(settings.ATTACK_KEY), self.select),
            ('<{}>'.format(settings.SHOW_ITEM_KEY), self.destroy),
            ('<{}>'.format (settings.UP_KEY), self.move),
            ('<{}>'.format (settings.DOWN_KEY), self.move),
        ]

    def draw(self):
        """ウィジェットを配置する。"""

        self.widget = tk.Canvas(
            master=self.root, bg=self.bg,
            width=self.width, height=self.height,
            highlightthickness=0,  # 枠線を消す
        )
        self.widget.place(x=self.x, y=self.y)

        # アイテムの表示
        items = self.kwargs['items']
        for index, item in enumerate(items):
            self.widget.create_text(
                5,
                5+(index*20),
                anchor='nw',
                text=item.name,
                font=self.font,
                fill=self.color,
                tag='item{}'.format(str(index)),
            )

        self.widget.itemconfig('item0', fill='red')

        try:
            _, _, _, max_y = self.widget.bbox('all')
        except TypeError:
            max_y = 0
        self.widget.configure(scrollregion=(0, 0, 0, max(self.height, max_y)))

    def select(self, event):
        """一覧から選択した。"""
        self.destroy()
        items = self.kwargs['items']
        callback = self.kwargs['callback']
        try:
            item = items[self.index]
        except IndexError:
            pass
        else:
            callback(item)

    def move(self, event):
        """リスト内を移動する。"""
        items = self.kwargs['items']
        if event.char == settings.UP_KEY and self.index > 0:
            self.widget.yview_scroll(-1, 'units')
            self.widget.itemconfig('item{}'.format(str(self.index)), fill=settings.DEFAULT_TEXT_COLOR)
            self.index -= 1
            self.widget.itemconfig('item{}'.format(str(self.index)), fill='red')
        elif event.char == settings.DOWN_KEY and self.index < len(items)-1:
            self.widget.yview_scroll(1, 'units')
            self.widget.itemconfig('item{}'.format(str(self.index)), fill=settings.DEFAULT_TEXT_COLOR)
            self.index += 1
            self.widget.itemconfig('item{}'.format(str(self.index)), fill='red')
