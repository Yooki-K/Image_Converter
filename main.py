import os
from PIL import Image as im
import windnd as wd
from tkinter import *
from tkinter import font, ttk, messagebox, filedialog


# pyinstaller -w main.py -i D:\mixed_file\daima\Python\Image_FC\icon_im.ico

class W(Tk):
    def __init__(self):
        super().__init__()
        self.f = font.Font(family='楷体', size=15)
        self.title('图片格式转换1.0')
        self.wm_attributes('-topmost', 1)  # 置顶
        self.box1 = ['.*']
        self.box2 = ['.jpeg', '.jpg', '.png', '.ico']
        self.is_delete = BooleanVar(value=False)
        self.input_path = StringVar()
        self.input_name = StringVar()
        self.is_renamee = BooleanVar(value=False)
        # 控件
        self.f1 = Frame(self)
        self.lb_path = Label(self.f1, text='路径', font=self.f)
        self.inp = Entry(self.f1, bd=3, font=self.f, textvariable=self.input_path)
        self.list_path = Button(self.f1, text='…', command=self.get_dir)
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

    # 转换
    def edit(self):
        l = []
        if self.com_f2.get() == '':
            messagebox.showwarning('警告', '转换后格式为空')
            return
        i = 0
        if str(self.listbox.curselection()) != '()':
            for x in self.listbox.selection_get().split('\n'):
                print(x)
                try:
                    image = im.open(os.path.join(self.input_path.get(), x))
                except FileNotFoundError:
                    messagebox.showerror('Error', os.path.join(self.input_path.get(), x) + '不存在')
                    return
                name = x.split('.')[0] + self.com_f2.get()
                if self.is_renamee.get():
                    name = os.path.join(self.input_path.get(), self.inp_name.get() + '_' + str(i) + self.com_f2.get())
                while os.path.exists(name):
                    i += 1
                    name = os.path.join(self.input_path.get(), self.inp_name.get() + '_' + str(i) + self.com_f2.get())
                print(name)
                try:
                    image.save(name)
                except OSError:
                    image = image.convert('RGB')
                    image.save(name)
                finally:
                    l.append(name)
                    if self.is_delete.get():
                        os.remove(x)
        else:
            for x in self.listbox.get(0, END):
                if os.path.splitext(x)[1] == self.com_f1.get() or self.com_f1.get() == '.*':
                    print(x)
                    try:
                        image = im.open(x)
                    except FileNotFoundError:
                        messagebox.showerror('Error', x + '不存在')
                        return
                    name = x.split('.')[0] + self.com_f2.get()
                    if self.is_renamee.get():
                        name = os.path.join(self.input_path.get(),
                                            self.inp_name.get() + '_' + str(i) + self.com_f2.get())
                    while os.path.exists(name):
                        i += 1
                        name = os.path.join(self.input_path.get(),
                                            self.inp_name.get() + '_' + str(i) + self.com_f2.get())
                    print(name)
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


if __name__ == '__main__':
    w = W()
