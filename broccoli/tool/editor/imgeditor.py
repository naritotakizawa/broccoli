import sys
if sys.platform.startswith('win') or sys.platform.startswith('cygwin'):
    from PIL import ImageGrab
elif sys.platform.startswith('darwin'):
    from PIL import ImageGrab
elif sys.platform.startswith('linux'):
    import pyscreenshot as ImageGrab
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from broccoli.conf import settings
from PIL import Image, ImageTk


sticky_all = (tk.N, tk.S, tk.E, tk.W)


class DragToplevel(tk.Toplevel):
    def __init__(self, master, image, x, y):
        tk.Toplevel.__init__(self, master)
        self.overrideredirect(True)
        self.geometry('+%i+%i' % (x, y))

        self.image = image

        self.label = tk.Label(self, image=image, bg='red')
        self.label.pack()

    def move(self, x, y):
        self.geometry('+%i+%i' % (x, y))


class ImgFrame(ttk.Frame):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_var()
        self.create_widgets()
        self.create_events()

    def create_events(self):
        root = self.winfo_toplevel()
        self.preview_canvas.bind('<ButtonPress-1>', self.click_image)
        root.bind('<ButtonRelease-1>', self.release)

    def create_var(self):
        self.resize_width = tk.StringVar()
        self.resize_height = tk.StringVar()
        self.image_width = tk.StringVar()
        self.image_height = tk.StringVar()
        self.splite_width = tk.StringVar()
        self.splite_height = tk.StringVar()
        self.splite_list = [[None for _ in range(5)] for _ in range(5)]
        self.dragged = None
        self.drag_id = None
        self.images = None
        self._images = []

    def create_widgets(self):
        config_frame = ttk.Frame(master=self)
        preview_frame = ttk.Frame(master=self)
        splite_frame = ttk.Frame(master=self)

        config_frame.grid(column=0, row=0, sticky=sticky_all)
        preview_frame.grid(column=1, row=0, sticky=sticky_all)
        splite_frame.grid(column=2, row=0, sticky=sticky_all)

        info_area = ttk.LabelFrame(master=config_frame, text='情報')
        ttk.Label(info_area, text='1マスの幅').grid(column=0, row=0, sticky=sticky_all)
        ttk.Label(info_area, text=settings.CELL_WIDTH).grid(column=1, row=0, sticky=sticky_all)
        ttk.Label(info_area, text='1マスの高さ').grid(column=0, row=1, sticky=sticky_all)
        ttk.Label(info_area, text=settings.CELL_HEIGHT).grid(column=1, row=1, sticky=sticky_all)
        ttk.Label(info_area, text='画像全体の幅').grid(column=0, row=2, sticky=sticky_all)
        ttk.Label(info_area, textvariable=self.image_width).grid(column=1, row=2, sticky=sticky_all)
        ttk.Label(info_area, text='画像全体の高さ').grid(column=0, row=3, sticky=sticky_all)
        ttk.Label(info_area, textvariable=self.image_height).grid(column=1, row=3, sticky=sticky_all)
        ttk.Button(info_area, text='現在の画像を保存(すぐ右の画像)', command=self.save).grid(column=0, row=4, columnspan=2, sticky=sticky_all)
        info_area.pack(fill='both')

        read_area = ttk.LabelFrame(master=config_frame, text='画像の読み込み')
        ttk.Button(read_area, text='読み込み', command=self.read).pack(fill='both')
        read_area.pack(fill='both')

        resize_area = ttk.LabelFrame(master=config_frame, text='リサイズ')
        ttk.Label(resize_area, text='幅').grid(column=0, row=0, sticky=sticky_all)
        ttk.Entry(resize_area, textvariable=self.resize_width).grid(column=1, row=0, sticky=sticky_all)
        ttk.Label(resize_area, text='高さ').grid(column=0, row=1, sticky=sticky_all)
        ttk.Entry(resize_area, textvariable=self.resize_height).grid(column=1, row=1, sticky=sticky_all)
        ttk.Button(resize_area, text='リサイズ実行', command=self.resize).grid(column=0, row=2, columnspan=2, sticky=sticky_all)
        resize_area.pack(fill='both')

        splite_area = ttk.LabelFrame(master=config_frame, text='スプライト画面の設定')
        ttk.Label(splite_area, text='幅(マスの数)').grid(column=0, row=0, sticky=sticky_all)
        ttk.Entry(splite_area, textvariable=self.splite_width).grid(column=1, row=0, sticky=sticky_all)
        ttk.Label(splite_area, text='高さ(マスの数)').grid(column=0, row=1, sticky=sticky_all)
        ttk.Entry(splite_area, textvariable=self.splite_height).grid(column=1, row=1, sticky=sticky_all)
        ttk.Button(splite_area, text='スプライトエリアのりサイズ', command=self.resize_splite).grid(column=0, row=2, columnspan=2,sticky=sticky_all)
        ttk.Button(splite_area, text='スプライト画像の保存', command=self.save_splite).grid(column=0, row=3, columnspan=2, sticky=sticky_all)
        splite_area.pack(fill='both')

        self.preview_canvas = tk.Canvas(master=preview_frame)
        self.preview_canvas.grid(row=0, column=0, sticky=sticky_all)
        xscroll = tk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        xscroll.grid(row=1, column=0, sticky=(tk.E, tk.W))
        yscroll = tk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        yscroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.preview_canvas.configure(xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        self.splite_canvas = tk.Canvas(master=splite_frame)
        self.splite_canvas.grid(row=0, column=0, sticky=sticky_all)
        xscroll = tk.Scrollbar(splite_frame, orient=tk.HORIZONTAL, command=self.splite_canvas.xview)
        xscroll.grid(row=1, column=0, sticky=(tk.E, tk.W))
        yscroll = tk.Scrollbar(splite_frame, orient=tk.VERTICAL, command=self.splite_canvas.yview)
        yscroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.splite_canvas.configure(xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
        self.draw_splite_line()
        splite_frame.columnconfigure(0, weight=1)
        splite_frame.rowconfigure(0, weight=1)

        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

    def save(self):
        file_path = filedialog.asksaveasfilename(title='ファイル名の入力')
        if file_path:
            self.src.save(file_path)

    def save_splite(self):
        file_path = filedialog.asksaveasfilename(title='スプライト画像の保存')
        if file_path:
            self.splite_canvas.delete('splite_line')
            start_x, start_y, end_x, end_y = self.splite_canvas.bbox('all')
            root = self.winfo_toplevel()
            from_root_x, from_root_y = self.splite_canvas.winfo_rootx(), self.splite_canvas.winfo_rooty()
            grab = ImageGrab.grab()
            img = grab.crop((
                from_root_x+start_x,
                from_root_y+start_y,
                from_root_x+end_x,
                from_root_y+end_y
            ))
            img.save(file_path)
            self.draw_splite_line()

    def resize_splite(self):
        width = self.splite_width.get()
        height = self.splite_height.get()
        self.splite_canvas.delete('splite_line')
        self.splite_canvas.delete('splite_image')
        self.splite_list = [[None for _ in range(int(width))] for _ in range(int(height))]
        self.draw_splite_line()

    def draw_splite_line(self):
        for y, row in enumerate(self.splite_list):
            for x, col in enumerate(row):
                self.splite_canvas.create_rectangle(
                    x * settings.CELL_WIDTH,
                    y * settings.CELL_HEIGHT,
                    x * settings.CELL_WIDTH+settings.CELL_WIDTH,
                    y*settings.CELL_HEIGHT+settings.CELL_HEIGHT,
                    tag='splite_line'

                )

    def read(self):
        file_path = filedialog.askopenfilename(title='読み込む画像')
        if file_path:
            self.src = Image.open(file_path)
            self.preview_canvas.delete('preview')
            self.draw()

    def resize(self):
        self.preview_canvas.delete('preview')
        width = eval(self.resize_width.get())
        height = eval(self.resize_height.get())
        self.draw(resize_width=width, resize_height=height)

    def draw(self, resize_width=None, resize_height=None):
        if resize_width and resize_height:
            self.src = self.src.resize((resize_width, resize_height))
        width, height = self.src.size
        self.image_width.set(width)
        self.image_height.set(height)
        self.resize_width.set(width)
        self.resize_height.set(height)

        yoko = width // settings.CELL_WIDTH
        tate = height // settings.CELL_HEIGHT
        self.images = [[None for x in range(yoko)] for y in range(tate)]
        for y in range(tate):
            for x in range(yoko):
                box = (
                    x * settings.CELL_WIDTH,
                    y * settings.CELL_HEIGHT,
                    x * settings.CELL_WIDTH + settings.CELL_WIDTH,
                    y * settings.CELL_HEIGHT + settings.CELL_HEIGHT
                )
                image = ImageTk.PhotoImage(self.src.crop(box))
                self.images[y][x] = image
                self.preview_canvas.create_image(x * settings.CELL_WIDTH, y * settings.CELL_HEIGHT, image=image, anchor='nw', tag='preview')
                self.preview_canvas.create_rectangle(
                    x * settings.CELL_WIDTH,
                    y * settings.CELL_HEIGHT,
                    x * settings.CELL_WIDTH+settings.CELL_WIDTH,
                    y*settings.CELL_HEIGHT+settings.CELL_HEIGHT,
                    tag='preview'

                )
                # スクロール領域の更新。動的に、現在のキャンバスの最大サイズを取得して設定する
                self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
                self._images.append(image)

    def click_image(self, event):
        root = self.winfo_toplevel()
        canvas_x = self.preview_canvas.canvasx(event.x)
        canvas_y = self.preview_canvas.canvasy(event.y)
        items = self.preview_canvas.find_closest(canvas_x, canvas_y)
        if items:
            image = self.preview_canvas.itemcget(items[0], 'image')
            self.dragged = DragToplevel(root, image, event.x_root, event.y_root)
            self.drag_id = root.bind('<Motion>', lambda e: self.dragged.move(e.x_root, e.y_root))

    def release(self, event):
        if self.dragged:
            root = self.winfo_toplevel()
            root.unbind('<Motion>',  self.drag_id)
            xr, yr = event.x_root, event.y_root
            x2, y2 = self.splite_canvas.winfo_rootx(), self.splite_canvas.winfo_rooty()
            w2, h2 = self.splite_canvas.winfo_width(), self.splite_canvas.winfo_height()

            if xr >= x2 and xr < x2 + w2 and yr >= y2 and yr < y2 + h2:
                rel_x, rel_y = self.abs_xy_to_layer_xy(xr-x2, yr-y2)
                self.splite_list[rel_y][rel_x] = self.dragged.image
                self.splite_canvas.create_image(
                    rel_x*settings.CELL_WIDTH,
                    rel_y*settings.CELL_HEIGHT,
                    image=self.dragged.image,
                    anchor='nw',
                    tag='splite_image'
                )

            self.dragged.destroy()
            self.dragged = None
            self.drag_id = None

    def abs_xy_to_layer_xy(self, click_x, click_y):
        """絶対座標を元にレイヤ内でのxyを返す"""
        click_x /= settings.CELL_WIDTH
        click_y /= settings.CELL_HEIGHT
        for y, row in enumerate(self.splite_list):
            for x, col in enumerate(row):
                if x <= click_x <= x + 1:
                    if y <= click_y <= y + 1:
                        return x, y


def main():
    root = tk.Tk()
    app = ImgFrame(master=root)
    app.pack(fill='both', expand=True)
    root.mainloop()


if __name__ == '__main__':
    main()