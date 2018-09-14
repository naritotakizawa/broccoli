"""ダイアログの基底クラスを集めたモジュール。

ゲームで使えるダイアログの基底クラスを提供しています。

アイテムの一覧を表示する処理を例に説明すると、
1. 何らかのキーイベント等によって、ダイアログの表示用メソッドを呼ぶ(多くの場合、showメソッド)
2. 親となるダイアログやシステムクラスのキーイベントを全て解除
3. ゲームキャンバス上に、アイテム一覧のダイアログを表示する
4. 自身のキーイベントを登録する。クリックでアイテム選択して閉じる、など

ダイアログを閉じた場合は、
1. 自身のキーイベントを全て解除する
2. ゲームキャンバス上に表示しているダイアログを削除する
3. 親となるダイアログやシステムクラスのキーイベントを登録

という処理をします。
BaseDialogでは、これらを簡単に行うためのインターフェースを定義しています。
全てのダイアログはBaseDialogのサブクラスで、基本的にはshowメソッドで呼び出し、destroyメソッドで消されます。

また、ダイアログ同士での親子関係も簡単に実装できます。
例えば所持アイテムを表示するダイアログがあり、何かアイテムを捨てるならばYes/Noなダイアログを表示するでしょう。
この場合は、所持アイテムダイアログのイベントを解除し、Yes/Noダイアログのイベントを有効化する必要があるはずです。
このような場合でも、キーイベントの登録・解除や、子ダイアログを生成したら親ダイアログの処理はブロックさせておく、といったことが可能です。

BaseDialogには2つのサブクラスがあり、実際のダイアログはこれら2つのうちどちらかのサブクラスです。

ImgDialogは、tkウィジェットではなく画像とテキストで作成する原始的なダイアログで、
特に背景が透明なダイアログを利用したい場合に便利です。
背景が透過なダイアログが欲しい場合、tkinterではウィジェットの背景を透過できないため
透過画像の上にテキストを表示する、といった処理をする必要があります。
そのため、画面の左上に配置する例ならば、ゲームキャンバスの現在表示している部分の座標を求め、
ゲームキャンバス内の絶対座標に変換し、create_image, create_textを呼び出す必要があります。
そのため凝った処理の実装は手間がかかり、シンプルな種類のダイアログしか利用できません。

Dialogのサブクラスは、背景を透過できない代わりに柔軟で高機能なダイアログです。
また、rootに対して直接placeで配置をしているため、ImgDialogと違いゲームキャンバス内の絶対座標を計算する必要はありません。
通常のtkウィジェットを使えるため、複雑な機能を持たせることもできます。

"""
import os
from broccoli.conf import settings
from PIL import ImageTk, Image


class BaseDialog:
    """全てのダイアログの基底クラス。

    主に
    - キーイベントに関連した処理
    - ダイアログを表示するためのインターフェース
    をこのクラスで定義しています。

    ダイアログに共通することとして、
    - showメソッドで表示
    - destroyメソッドで削除
    がされます。

    """
    text_size = settings.DEFAULT_TEXT_SIZE
    text_font = settings.DEFAULT_TEXT_FONT
    font = (text_font, text_size)
    color = settings.DEFAULT_TEXT_COLOR

    def __init__(self, parent, canvas):
        # parentは、システムクラス、又はダイアログクラスです。
        self.parent = parent

        # canvasは、tk.Canvasのサブクラスが格納されます。
        self.canvas = canvas

        # このダイアログで何かしらの処理をしているが、子ダイアログを生成すると処理を中段しておきたい、ということがあります。
        # そのような場合に使うフラグで、親や子とイベントを切り替えるためのchange_key_event、revert_key_eventメソッドで
        # それぞれTrue、Falseを自動で設定されます。
        # ブロックしたい処理には、このis_block属性を利用したコードを書いてください。
        self.is_block = False

        # showメソッド呼び出しの際の引数が保存されます。
        self.args = ()
        self.kwargs = {}

    def create_key_event(self):
        """このダイアログのキーイベントの設定。"""
        root = self.canvas.winfo_toplevel()
        for key, func in self.get_key_events():
            root.bind(key, func)

    def clear_key_event(self):
        """このダイアログのキーイベントを解除する。"""
        root = self.canvas.winfo_toplevel()
        for key, func in self.get_key_events():
            root.unbind(key)

    def change_key_event(self):
        """親のイベントを取り消し、このダイアログのキーイベントを設定します。

        キーイベントを切り替える際に、親のダイアログorシステムのis_blockをTrueにし、
        親で行っている処理を中段するためのお手伝いもします。
        実際に中段するためには、親側でそのフラグを使ったコードを書いてください。

        """
        self.parent.is_block = True
        self.parent.clear_key_event()
        self.create_key_event()

    def revert_key_event(self):
        """このダイアログのキーイベントを削除し、親のキーイベントを再設定します。

        キーイベントを切り替える際に、親のダイアログorシステムのis_blockをFalseにし、
        親で中段していた処理を再開するための手伝いもします。
        実際に処理を再開するためには、親側でそのフラグを使ったコードを書いてください。

        """
        self.clear_key_event()
        self.parent.create_key_event()
        self.parent.is_block = False

    def show(self, *args, **kwargs):
        """ダイアログの表示。"""
        raise NotImplementedError

    def destroy(self, event=None):
        """ダイアログの削除。"""
        raise NotImplementedError

    def draw(self):
        """実際の描画処理。"""
        raise NotImplementedError

    def get_key_events(self):
        """このダイアログのキーイベントを返す。"""
        raise NotImplementedError


class ImgDialog(BaseDialog):
    """画像ダイアログの基底クラス。

    サブクラス化する場合は、
    - クラス属性のsrc(ダイアログの枠となる画像データ、透過画像が指定できます。)
    - クラス属性のresize(画像をリサイズしたい場合、１つの画像を使いまわしたい場合に便利、必要なければNone)
    - get_key_eventsメソッド(ダイアログのキーイベントを定義)
    - drawメソッド(ダイアログの描画処理)
    - 他のメソッド(キーイベントで呼ばれる独自メソッド等)
    を実装してください。

    """
    src = os.path.join(settings.BROCCOLI_IMG_DIR, 'window/default.png')
    resize = None

    def __init__(self, parent, canvas):
        super().__init__(parent=parent, canvas=canvas)

        # ダイアログの画像
        self.image = None

        # ダイアログを描画する際のcreate_imageやcreate_textのtag引数に、指定すると便利なタグ
        self.tag = type(self).__name__

    def load_image(self):
        src = Image.open(self.src)
        if self.resize:
            src = src.resize(self.resize)
        self.image = ImageTk.PhotoImage(src)

    def show(self, *args, **kwargs):
        # 引数を保存しておく
        self.args = args
        self.kwargs = kwargs

        # まだ画像がロードされていなければ、ロードする
        if self.image is None:
            self.load_image()

        self.draw()
        self.change_key_event()

    def destroy(self, event=None):
        self.canvas.delete(self.tag)
        self.revert_key_event()

    def draw(self):
        """実際の描画処理"""
        raise NotImplementedError

    def get_key_events(self):
        """このダイアログのキーイベントを返す"""
        raise NotImplementedError


class Dialog(BaseDialog):
    """通常のtkウィジェットを使ったダイアログの基底クラス。

    サブクラス化する場合は、
    - get_key_eventsメソッド(ダイアログのキーイベントを定義)
    - drawメソッド(ダイアログの描画処理)
    - 他のメソッド(キーイベントで呼ばれる独自メソッド等)
    を上書きしてください。

    """
    bg = 'lavender'

    def __init__(self, parent, canvas):
        super().__init__(parent=parent, canvas=canvas)
        self.root = canvas.winfo_toplevel()
        self.widget = None

    def show(self, *args, **kwargs):
        # 引数を保存しておく
        self.args = args
        self.kwargs = kwargs

        self.draw()
        self.change_key_event()

    def destroy(self, event=None):
        self.widget.destroy()
        self.widget = None
        self.revert_key_event()

    def draw(self):
        """実際の描画処理"""
        raise NotImplementedError

    def get_key_events(self):
        """このダイアログのキーイベントを返す"""
        raise NotImplementedError
