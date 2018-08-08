"""何かを一覧表示するためのダイアログを提供するモジュール"""
from broccoli.conf import settings
from broccoli.dialog import ImgDialog


class ListDialog(ImgDialog):
    """一覧表示に使うダイアログ"""
    resize = (settings.GAME_WIDTH, settings.GAME_HEIGHT)

    def __init__(self, parent, canvas):
        super().__init__(parent, canvas)
        self.index = 0

    def get_key_events(self):
        """このダイアログのキーイベントを返す"""
        return [
            ('<{}>'.format(settings.ATTACK_KEY), self.select),
            ('<{}>'.format(settings.SHOW_ITEM_KEY), self.destroy),
            ('<{}>'.format (settings.UP_KEY), self.move),
            ('<{}>'.format (settings.DOWN_KEY), self.move),
        ]

    def draw(self):
        self.canvas.delete (self.tag)
        x, y = self.canvas.get_current_position_nw()
        # 枠の表示
        self.canvas.create_image(
            x,
            y,
            anchor='nw',
            image=self.image,
            tag=self.tag
        )
        # アイテムの表示
        items = self.kwargs['items']
        for index, item in enumerate(items):
            if index == self.index:
                color = 'red'
            else:
                color = 'white'
            self.canvas.create_text (
                x+5,
                y+40+(index*20),  # 上に40px空けます。画面上段は、よく使われているので...
                anchor='nw',
                text=item.name,
                font=self.font,
                fill=color,
                tag='{} text'.format(self.tag),
            )

    def select(self, event):
        """一覧から選択した"""
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
        """リスト内を移動する"""
        items = self.kwargs['items']
        if event.char == settings.UP_KEY and self.index > 0:
            self.index -= 1
        elif event.char == settings.DOWN_KEY and self.index < len(items)-1:
            self.index += 1
        self.draw()
