import os
from datetime import datetime

from PIL import Image as im, ImageTk
import windnd as wd
from tkinter import *
from tkinter import font, ttk, messagebox, filedialog


# venv\Scripts\pyinstaller -w main.py -i D:\mixed_file\daima\Python\Image_FC\icon_im.ico

def save(image, name):
    try:
        image.save(name)
    except OSError:
        img = image.convert('RGB')
        img.save(name)
    finally:
        name = name.replace('\\', '/')
        messagebox.showinfo('提示', '成功生成' + name)


class EW(Toplevel):
    x1 = 0
    x2 = 0
    y1 = 0
    y2 = 0
    delta = 0
    pre_x = 0
    pre_y = 0
    rect = None

    def __init__(self, path):
        super().__init__()
        max_w = 1800
        max_h = 700
        self.attributes('-topmost', True)
        self.path = path
        self.f1 = Frame(self)
        self.image = im.open(path)
        self.image_src = im.open(path)
        self.percent = 1
        self.first = True
        if self.image.size[0] > max_w:
            self.percent = max_w / self.image.size[0]
            h_size = int(self.image.size[1] * max_w / self.image.size[0])
            self.image = self.image.resize((max_w, h_size), im.ANTIALIAS)
        if self.image.size[1] > max_h:
            self.percent = max_h / self.image.size[1] * self.percent
            w_size = int(self.image.size[0] * max_h / self.image.size[1])
            self.image = self.image.resize((w_size, max_h), im.ANTIALIAS)
        self.imageTk = ImageTk.PhotoImage(self.image)
        self.rs = Button(self.f1, text='Resize', command=self.getData)
        self.img = Canvas(self, width=self.image.size[0], height=self.image.size[1])
        self.image_ = self.img.create_image(0, 0, anchor='nw', image=self.imageTk)
        self.txt = self.img.create_text(5, 5, anchor='nw',
                                        text="%d x %d %d" % (
                                            self.image_src.size[0], self.image_src.size[1], self.percent * 100) + '%')
        self.geometry('%dx%d+%d+%d' % (
            self.image.size[0], self.image.size[1] + 30, (self.winfo_screenwidth() - self.image.size[0]) / 2,
            (self.winfo_screenheight() - self.image.size[1] - 30) / 2))
        self.input_w = StringVar()
        self.inp_w = Entry(self.f1, bd=3, textvariable=self.input_w, width=30)
        self.placeholder = '宽度or百分比or宽度x高度'
        self.inp_w.insert(0, self.placeholder)

        # 绑定
        self.img.bind("<ButtonPress-1>", self.leftMousePress)
        self.img.bind("<ButtonPress-3>", self.rightMousePress)
        self.img.bind("<ButtonPress-2>", self.midMousePress)
        self.img.bind("<B1-Motion>", self.leftMouseMove)
        self.img.bind("<B2-Motion>", self.midMouseMove)
        self.inp_w.bind("<FocusIn>", self.on_focus_in)
        self.inp_w.bind("<FocusOut>", self.on_focus_out)
        self.inp_w.bind("<Return>", self.getData)
        self.img.bind("<MouseWheel>", self.MouseWheel)
        self.bind('<Key>', self.printKey)
        self.bind('<Control-Shift-C>', self.clip)

        # 布局
        self.img.pack(fill='both', expand='yes')
        self.inp_w.grid(row=0, column=0)
        self.rs.grid(row=0, column=1)
        self.f1.pack(side='bottom')

        self.mainloop()

    def on_focus_in(self, event):
        if self.input_w.get() == self.placeholder:
            self.inp_w.delete('0', 'end')

    def on_focus_out(self, event):
        if not self.inp_w.get():
            self.inp_w.insert(0, self.placeholder)

    def leftMousePress(self, event):
        self.clear()
        self.x1 = event.x
        self.y1 = event.y
        pass

    # 创建右键菜单
    def rightMousePress(self, event):
        menu = Menu(self, tearoff=0)
        menu.add_command(label="Crop", command=self.clip)
        menu.add_separator()
        menu.add_command(label="Back", command=self.clear)
        menu.post(event.x_root, event.y_root)

    def midMousePress(self, event):
        self.pre_x = event.x
        self.pre_y = event.y

    def leftMouseMove(self, event):
        self.clear()
        self.x2 = event.x
        self.y2 = event.y
        self.rect = self.img.create_rectangle(self.x1, self.y1, self.x2, self.y2, tag='rect')
        pass

    def midMouseMove(self, event):
        self.img.move(self.image_, event.x - self.pre_x, event.y - self.pre_y)
        self.pre_x = event.x
        self.pre_y = event.y

    def MouseWheel(self, event):
        pre = (self.delta * 0.05 + 1)
        self.percent = self.percent / pre
        if event.delta > 0:
            self.delta = self.delta + 1
            self.img.scale('rect', 0, 0, 1.05, 1.05)
        else:
            self.delta = self.delta - 1
            self.img.scale('rect', 0, 0, 1 / 1.05, 1 / 1.05)
        percent = self.delta * 0.05 + 1
        self.percent = self.percent * percent
        self.image = self.image_src.resize(
            (int(self.image_src.size[0] * percent), int(self.image_src.size[1] * percent)), im.ANTIALIAS)
        self.imageTk = ImageTk.PhotoImage(self.image)
        self.img.itemconfig(self.image_, image=self.imageTk)
        self.img.itemconfig(self.txt, text="%d x %d %d" % (
            int(self.image_src.size[0] * percent), int(self.image_src.size[1] * percent), percent * 100) + '%')

    def printKey(self, event):
        if self.rect is not None:
            if event.keycode == 38:  # 上
                self.img.move(self.rect, 0, -1)
                self.y1 = self.y1 - 1
                self.y2 = self.y2 - 1
            elif event.keycode == 40:  # 下
                self.img.move(self.rect, 0, 1)
                self.y1 = self.y1 + 1
                self.y2 = self.y2 + 1
            elif event.keycode == 37:  # 左
                self.img.move(self.rect, -1, 0)
                self.x1 = self.x1 - 1
                self.x2 = self.x2 - 1
            elif event.keycode == 39:  # 右
                self.img.move(self.rect, 1, 0)
                self.x1 = self.x1 + 1
                self.x2 = self.x2 + 1
        pass

    def clip(self, e=None):
        if self.rect is None:
            return
        name = self.path.split('.')[0] + '_.' + self.path.split('.')[1]
        img = self.image.crop((self.x1, self.y1, self.x2, self.y2))
        img = img.resize((int(img.size[0] / self.percent), int(img.size[1] / self.percent)), im.ANTIALIAS)
        save(img, name)

    # 清除矩形框
    def clear(self):
        if self.rect is not None:
            self.img.delete(self.rect)
            self.rect = None

    def getData(self, e=None):
        s = self.input_w.get()
        try:
            ss = s.split('x')
            if len(ss) == 1:
                ss = s.split('X')
                if len(ss) == 1:
                    ss = s.split('*')
                    if len(ss) == 1:
                        v = int(s.replace('%', ''))
                        if s.find('%') != -1:
                            self.resize(v, None, 2)
                        else:
                            self.resize(v, None, 1)
                        return
            v1 = int(ss[0])
            v2 = int(ss[1])
            self.resize(v1, v2, 3)



        except ValueError:
            messagebox.showerror('Error', '请输入整数或百分比')

    def resize(self, d1, d2, Type):
        name = self.path.split('.')[0] + '__.' + self.path.split('.')[1]
        if Type == 1:
            w = d1
            h = self.image.size[1] * w / self.image.size[0]
        elif Type == 2:
            w = self.image_src.size[0] * d1 / 100
            h = self.image_src.size[1] * d1 / 100
        else:
            w = d1
            h = d2
        image = self.image_src.resize((int(w), int(h)), im.ANTIALIAS)
        save(image, name)


class W(Tk):
    ew = None

    def __init__(self):
        super().__init__()
        self.f = font.Font(family='楷体', size=15)
        self.title('图片格式转换4.0')
        self.wm_attributes('-topmost', 1)  # 置顶
        self.box1 = ['.*']
        self.box2 = ['.jpg', '.png', '.jpeg', '.ico']
        self.is_delete = BooleanVar(value=False)
        self.input_path = StringVar()
        self.input_name = StringVar()
        self.is_renamee = BooleanVar(value=False)

        # 控件
        self.f1 = Frame(self)
        self.lb_path = Label(self.f1, text='路径', font=self.f)
        self.inp = Entry(self.f1, bd=3, font=self.f, textvariable=self.input_path)
        self.list_path = Button(self.f1, text='…', command=self.get_dir)
        self.clear = Button(self.f1, text="清空", command=self.f_clear)
        self.listbox = Listbox(self, bd=5, font=self.f, selectmode=EXTENDED)
        self.f2 = Frame(self)
        self.f3 = Frame(self)
        self.lb_format1 = Label(self.f2, text='由格式', font=self.f)
        self.lb_format2 = Label(self.f2, text='转换至格式', font=self.f)
        self.com_f1 = ttk.Combobox(self.f2, values=self.box1)
        self.com_f2 = ttk.Combobox(self.f2, values=self.box2)
        self.sure = Button(self.f3, text='转换', command=self.edit)
        self.is_rename = Checkbutton(self.f3, text='是否批量重命名文件', variable=self.is_renamee, command=self.set_is_rename)
        self.is_clear = Checkbutton(self.f3, text='是否删除原文件', variable=self.is_delete)
        self.inp_name = Entry(self.f3, bd=3, font=self.f, textvariable=self.input_name, state=DISABLED)

        # 布局
        self.f1.pack(side='top')
        self.lb_path.grid(row=0, column=0)
        self.inp.grid(row=0, column=1)
        self.list_path.grid(row=0, column=2)
        self.clear.grid(row=0, column=3)
        self.listbox.pack(fill='both')
        self.f2.pack()
        self.lb_format1.grid(row=0, column=0)
        self.com_f1.grid(row=0, column=1)
        self.lb_format2.grid(row=0, column=2)
        self.com_f2.grid(row=0, column=3)
        self.is_rename.grid(row=0, column=0)
        self.inp_name.grid(row=0, column=1)
        self.sure.grid(row=0, column=2)
        self.is_clear.grid(row=0, column=3)
        self.f3.pack()
        self.demo()

        self.mainloop()

    def demo(self):
        wd.hook_dropfiles(self, func=self.dragged_files)
        self.com_f1.set(self.box1[0])
        self.com_f2.set(self.box2[0])
        self.inp.bind("<Return>", self.local_list)
        self.listbox.bind('<Double-Button-1>', self.listboxLeftBD)

    def listboxLeftBD(self, *args):
        cur = self.listbox.curselection()
        value = self.listbox.get(cur)
        if len(self.input_path.get()) != 0:
            value = os.path.join(self.input_path.get(), value)
        self.ew = EW(value)

    # 转换
    def edit(self):
        l = []
        if self.com_f2.get() == '':
            messagebox.showwarning('警告', '转换后格式为空')
            return
        i = 0
        if len(self.input_path.get()) != 0:  # 选择路径
            if str(self.listbox.curselection()) == '()':
                messagebox.showerror("Error", "请选择转换文件！")
                return
            for x in self.listbox.selection_get().split('\n'):
                x = os.path.join(self.input_path.get(), x)
                try:
                    image = im.open(x)
                except FileNotFoundError:
                    messagebox.showerror('Error', x + '不存在')
                    return
                name = x.split('.')[0] + self.com_f2.get()
                if self.is_renamee.get():
                    name = self.rename(self.input_path.get(), self.inp_name.get())
                try:
                    image.save(name)
                except OSError:
                    image = image.convert('RGB')
                    image.save(name)
                finally:
                    l.append(name)
                    if self.is_delete.get():
                        os.remove(x)
        else:  # 拖动文件
            for x in self.listbox.get(0, END):
                if os.path.splitext(x)[1] == self.com_f1.get() or self.com_f1.get() == '.*':
                    try:
                        image = im.open(x)
                    except FileNotFoundError:
                        messagebox.showerror('Error', x + '不存在')
                        return
                    path_one = os.path.split(x)[0]
                    name = os.path.splitext(x)[0] + self.com_f2.get()
                    if self.is_renamee.get():
                        name = self.rename(path_one, self.inp_name.get())
                    try:
                        image.save(name)
                    except OSError:
                        image = image.convert('RGB')
                        image.save(name)
                    finally:
                        l.append(name)
                        if self.is_delete.get():
                            os.remove(x)
        messagebox.showinfo('转换成功', '成功生成图片:\n' + '\n'.join(l))

    # 重命名
    def rename(self, path, pattern: str):
        i = 0
        time = datetime.now()
        name = pattern.replace('%Y', str(time.year))
        name = name.replace('%M', str(time.month))
        name = name.replace('%D', str(time.day))
        name = name.replace('%h', str(time.hour))
        name = name.replace('%m', str(time.minute))
        name = name.replace('%s', str(time.second))
        r = name.find("%f")
        if r != -1 and r + 2 < len(name):
            name = name.replace('%f', str(time.microsecond % pow(10, r)))
        else:
            name = name.replace('%f', str(time.microsecond))
        pattern = name
        name = pattern.replace('%d', str(i))
        while os.path.exists(os.path.join(path, name + self.com_f2.get())):
            i += 1
            name = pattern.replace('%d', str(i))
        return os.path.join(path, name + self.com_f2.get())

    # 获得路径文件列表
    def local_list(self, a):
        self.listbox.delete(0, END)
        p = self.input_path.get()
        try:
            l = os.listdir(p)
            for x in l:
                if os.path.isdir(os.path.join(p, x)):
                    continue
                self.listbox.insert(END, x)
                fmat = os.path.splitext(x)[1]
                try:
                    self.box1.remove(fmat)
                except ValueError as e:
                    print(e)
                    pass
                finally:
                    self.box1.append(fmat)
            self.com_f1['values'] = self.box1
        except FileNotFoundError:
            messagebox.showerror('Error', '系统找不到指定的路径')

    def dragged_files(self, files):
        for x in files:
            self.listbox.insert("end", x.decode('gbk'))
            fmat = os.path.splitext(x)[1]
            try:
                self.box1.remove(fmat)
            except Exception as e:
                print(e)
                pass
            finally:
                self.box1.append(fmat)
        self.com_f1['values'] = self.box1

    # 设置是否重命名
    def set_is_rename(self):
        if self.is_renamee.get():
            self.inp_name.config(state='normal')
        else:
            self.inp_name.config(state='disabled')

    # 获得路径
    def get_dir(self):
        dir_name = filedialog.askdirectory()
        self.input_path.set(dir_name)
        self.local_list(None)

    # 刷新
    def f_clear(self):
        self.inp.delete(0, END)
        self.inp_name.delete(0, END)
        self.listbox.delete(0, END)
        print("clear")


if __name__ == '__main__':
    w = W()
