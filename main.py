import os
from datetime import datetime
from re import search
from PIL import Image as im, ImageTk, ImageFilter
import windnd as wd
from tkinter import *
from tkinter import font, ttk, messagebox, filedialog
from queue import PriorityQueue as pQueue, Empty, Queue


# venv\Scripts\pyinstaller -w main.py -i D:\mixed_file\daima\Python\Image_FC\icon_im.ico

def save(image, name):
    if image is None:
        messagebox.showerror('出错', '对图片无操作')
        return
    try:
        temp = name.split('.')
        if image.format == 'JPEG':
            name = temp[0] + '.jpg'
        else:
            name = temp[0] + '.' + image.format
        image.save(name)
    except OSError as e:
        print(e)
    finally:
        name = name.replace('\\', '/')
        messagebox.showinfo('提示', '成功生成' + name)


def rgb_to_hex(rgb, mode):
    """
    将rgb转十六进制
    Args:
        rgb: rgb颜色
    Returns: 十六进制
    """
    color = '#'
    length = 3
    if mode == 'L':
        rgb = (rgb, rgb, rgb)
    if mode == 'RGB':
        length = len(rgb)
    if mode == 'RGBA':
        length = len(rgb) - 1
    for i in range(length):
        # 将R、G、B分别转化为16进制拼接转换并大写  hex() 函数用于将10进制整数转换成16进制，以字符串形式表示
        color += str(hex(rgb[i]))[-2:].replace('x', '0')
    return color


def print_fjx(num=20):
    print(''.join(['-'] * num))


def center(e: ttk, width, height):
    e.geometry(
        '%dx%d+%d+%d' % (width, height, (e.winfo_screenwidth() - width) / 2, (e.winfo_screenheight() - height) / 2))


class DIJKSTRA:
    def __init__(self, p1: tuple, p2: tuple, image: im.Image):
        super().__init__()
        self.p1 = p1
        self.p2 = p2
        self.image = image
        self.min_x = min(self.p1[0], self.p2[0])
        self.max_x = max(self.p1[0], self.p2[0])
        self.min_y = min(self.p1[1], self.p2[1])
        self.max_y = max(self.p1[1], self.p2[1])

    def judgeIsRange(self, p):
        if p[0] < self.min_x or p[0] > self.max_x or p[1] < self.min_y or p[1] > self.max_y:
            return False
        return True

    def getNextStep(self, p):
        res = []
        ps = [(p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1)]
        for p_ in ps:
            if self.judgeIsRange(p_):
                r, g, b, o = self.image.getpixel(p_)
                if r == g == b:
                    res.append({'pos': p_, 'value': (256 - r) / 100})
        return res

    def twoToOne(self, p: tuple, w):
        return (p[0] - self.min_x) + (p[1] - self.min_y) * w

    # 用优先队列实现的dijkstra算法
    def run(self):
        w = self.max_x - self.min_x + 1
        h = self.max_y - self.min_y + 1
        n = w * h
        visited = [False] * n
        parents = [self.p1] * n
        pq = pQueue()  # 优先队列中的元素为[cost, v, u]形式，cost是该路径的花销， v是去往的结点，u是原始结点
        t = {}
        pq.put([0, self.p1, (-1, -1)])
        while len(t) < n:
            # 从优先队列中找出未被确定的最短路径
            # print(''.join(['-'] * 20))
            # print('pq length:%d' % pq.qsize())
            try:
                minPath = pq.get(timeout=1.5)
                while visited[self.twoToOne(minPath[1], w)]:
                    minPath = pq.get(timeout=1.5)
            except Empty:
                break
            minP = minPath[1]
            # print('get (%d,%d)' % minP)
            # print('%d-%d:' % (len(t), n) + str(len(t) / n * 100) + '%')
            visited[self.twoToOne(minP, w)] = True
            t[minP] = minPath[0]
            parents[self.twoToOne(minP, w)] = minPath[2]
            # 从该最短路径的结点开始找邻边，入队
            for edge in self.getNextStep(minP):
                if not visited[self.twoToOne(edge['pos'], w)]:
                    pq.put([edge['value'] + t[minP], edge['pos'], minP])
                    # print('put (%d,%d)' % edge['pos'])
        temp = self.p2
        result = [temp]
        while True:
            pat = parents[self.twoToOne(temp, w)]
            if pat == (-1, -1):
                break
            result.append(pat)
            temp = pat
        print_fjx()
        print('begin:', self.p1)
        print('end:', self.p2)
        print("w,h=%d,%d" % (w, h))
        print('point number:%d' % n)
        print_fjx()
        return result


class EW(Toplevel):
    x1 = -1
    x2 = -1
    y1 = -1
    y2 = -1
    delta = 0
    pre_x = 0
    pre_y = 0
    pos_x = 0
    pos_y = 0
    start_point = (-1, -1)
    pre_point = (-1, -1)
    rect = None

    def __init__(self, path):
        super().__init__()
        max_w = 1400
        max_h = 700
        min_w = 1000
        # self.wm_attributes('-topmost', 1)  # 置顶
        self.iconbitmap('icon_im.ico')
        self.title('yooki图片处理面板——' + path)
        self.path = path
        self.input_w = StringVar()
        self.bl = StringVar()
        self.ys = StringVar()
        self.mes = StringVar()
        self.image = im.open(path)
        self.image_src = im.open(path)
        self.pre_image = None
        self.res_image = None
        self.image_sobel = None
        self.percent = 1
        self.state = 1
        self.first = True
        self.placeholder = 'width or percent or width x height'
        if self.image.size[0] > max_w:
            self.percent = max_w / self.image.size[0]
            self.percent = (int(self.percent * 100) - int(self.percent * 100) % 5) / 100
            self.delta = (self.percent - 1) * 100 / 5
            h_size = int(self.image.size[1] * self.percent)
            self.image = self.image.resize((max_w, h_size), im.ANTIALIAS)
        if self.image.size[1] > max_h:
            self.percent = max_h / self.image.size[1] * self.percent
            self.percent = (int(self.percent * 100) - int(self.percent * 100) % 5) / 100
            self.delta = (self.percent - 1) * 100 / 5
            w_size = int(self.image.size[0] * self.percent)
            self.image = self.image.resize((w_size, max_h), im.ANTIALIAS)
        print(self.percent, self.delta)
        self.f1 = Frame(self)
        self.f11 = Frame(self.f1)
        self.f12 = Frame(self.f1)
        self.imageTk = ImageTk.PhotoImage(self.image)
        self.rs = Button(self.f12, text='Resize', command=self.getData)
        self.img = Canvas(self, width=self.image.size[0], height=self.image.size[1])
        self.image_ = self.img.create_image(0, 0, anchor='nw', image=self.imageTk)
        self.color = Canvas(self.f12, width=20, height=20, bg='white')
        self.txt_bl = Label(self.f12, textvariable=self.bl)
        self.txt_ys = Label(self.f12, textvariable=self.ys)
        self.txt_mes = Label(self.f11, textvariable=self.mes, anchor='w')
        self.print('Welcome!')
        self.bl.set("%d x %d %d" % (self.image_src.size[0], self.image_src.size[1], self.percent * 100) + '%')
        w, h = self.image.size
        h += 35
        if w < min_w:
            w = min_w
        center(self, w, h)
        self.inp_w = Entry(self.f12, bd=3, textvariable=self.input_w, width=30)
        self.inp_w.insert(0, self.placeholder)
        self.stateBox = ttk.Combobox(self.f12, values=['crop mode', 'select auto mode', 'select line mode', 'mat mode'])
        self.stateBox.current(0)
        # 绑定
        self.img.bind("<ButtonPress-1>", self.leftMousePress)
        self.img.bind("<ButtonPress-3>", self.rightMousePress)
        self.img.bind("<ButtonPress-2>", self.midMousePress)
        self.img.bind("<B1-Motion>", self.leftMouseMove)
        self.img.bind("<B2-Motion>", self.midMouseMove)
        self.img.bind("<Motion>", self.MouseMove)
        self.inp_w.bind("<FocusIn>", self.on_focus_in)
        self.inp_w.bind("<FocusOut>", self.on_focus_out)
        self.inp_w.bind("<Return>", self.getData)
        self.img.bind("<MouseWheel>", self.MouseWheel)
        self.stateBox.bind("<<ComboboxSelected>>", self.stateBoxClick)
        self.bind('<Key>', self.printKey)
        self.bind('<Control-Shift-C>', self.clip)

        # 布局
        self.img.pack(side='top', expand='yes')
        # self.txt_mes.pack(fill='both',side='left')
        self.txt_mes.pack(padx=5)
        self.stateBox.grid(row=0, column=1)
        self.txt_bl.grid(row=0, column=2)
        self.color.grid(row=0, column=3)
        self.txt_ys.grid(row=0, column=4)
        self.inp_w.grid(row=0, column=5, padx=5)
        self.rs.grid(row=0, column=6)
        self.f11.pack(side='left')
        self.f12.pack()
        self.f1.pack(side='bottom', fill='x')

        self.mainloop()

    def on_focus_in(self, *args):
        if self.input_w.get() == self.placeholder:
            self.inp_w.delete('0', 'end')

    def on_focus_out(self, *args):
        if not self.inp_w.get():
            self.inp_w.insert(0, self.placeholder)

    def leftMousePress(self, event):
        x = event.x - self.pos_x
        y = event.y - self.pos_y
        if self.state == 1:
            self.clear_mode1()
        if self.state in [2, 3] and self.start_point == (-1, -1):
            self.start_point = (x, y)
        if self.state == 2 and self.x1 != -1 and self.y1 != -1:
            dij = DIJKSTRA((self.x1, self.y1), (x, y), self.image)
            parents = dij.run()
            print('find path ok')
            self.pre_image = self.image.copy()
            self.pre_point = (self.x1, self.y1)
            for parent in parents:
                self.image.putpixel(parent, (255, 0, 0))
            print('draw path ok(%d)' % len(parents))
            self.print('Draw point number is %d' % len(parents))
            # print('parents:', parents)
            self.imageTk = ImageTk.PhotoImage(self.image)
            self.img.itemconfig(self.image_, image=self.imageTk)
        if self.state == 3 and self.x1 != -1 and self.y1 != -1:
            min_x = min(self.x1, x)
            max_x = max(self.x1, x)
            min_y = min(self.y1, y)
            max_y = max(self.y1, y)
            w, h = self.image.size
            dy = [-1, 0, 1]
            if x == self.x1:
                [self.image.putpixel((x, y_), (255, 0, 0)) for y_ in range(min_y, max_y + 1)]
            if y == self.y1:
                [self.image.putpixel((x_, y), (255, 0, 0)) for x_ in range(min_x, max_x + 1)]
            else:
                k = (y - self.y1) / (x - self.x1)
                m = y - k * x
                a, b = (None, None)
                if abs(k) > 1:
                    a = (x - self.x1) / (y - self.y1)
                    b = -m / k
                if abs(k) <= 1:
                    if k < 0:
                        self.image.putpixel((min_x, max_y), (255, 0, 0))
                    else:
                        self.image.putpixel((min_x, min_y), (255, 0, 0))
                    for x_ in range(min_x + 1, max_x + 1):
                        y_ = int(k * x_ + m)
                        self.image.putpixel((x_, y_), (255, 0, 0))
                        while x_ >= 0:
                            isInRed = False
                            xx = x_ - 1
                            for j in range(3):
                                yy = y_ + dy[j]
                                if xx < 0 or xx >= w or yy < 0 or yy >= h: continue
                                if self.image.getpixel((xx, yy))[:3] == (255, 0, 0):
                                    isInRed = True
                                    break
                            if isInRed: break
                            if not isInRed:
                                if k < 0:
                                    y_ += 1
                                else:
                                    y_ -= 1
                                if y_ < 0 or y_ >= h: break
                                x_ -= 1
                                self.image.putpixel((x_, y_), (255, 0, 0))
                else:
                    if k < 0:
                        self.image.putpixel((max_x, min_y), (255, 0, 0))
                    else:
                        self.image.putpixel((min_x, min_y), (255, 0, 0))
                    for y_ in range(min_y + 1, max_y + 1):
                        x_ = int(a * y_ + b)
                        self.image.putpixel((x_, y_), (255, 0, 0))
                        while y_ >= 0:
                            isInRed = False
                            yy = y_ - 1
                            for j in range(3):
                                xx = x_ + dy[j]
                                if xx < 0 or xx >= w or yy < 0 or yy >= h: continue
                                if self.image.getpixel((xx, yy))[:3] == (255, 0, 0):
                                    isInRed = True
                                    break
                            if isInRed: break
                            if not isInRed:
                                if k < 0:
                                    x_ += 1
                                else:
                                    x_ -= 1
                                if x_ < 0 or x_ >= w: break
                                y_ -= 1
                                self.image.putpixel((x_, y_), (255, 0, 0))

            self.imageTk = ImageTk.PhotoImage(self.image)
            self.img.itemconfig(self.image_, image=self.imageTk)
        if self.state == 4:
            self.mat(x, y)
        self.x1 = x
        self.y1 = y
        pass

    # 创建右键菜单
    def rightMousePress(self, event):
        menu = Menu(self, tearoff=0)
        if self.state == 1:
            menu.add_command(label="Crop", command=self.clip)
            menu.add_separator()
            menu.add_command(label="Back", command=self.clear_mode1)
        if self.state in [2, 3]:
            menu.add_command(label="AutoRound", command=self.autoRound)
            menu.add_separator()
            menu.add_command(label="Back", command=self.clear_mode2)
            menu.add_separator()
            menu.add_command(label="restart", command=self.clear_restart)
            menu.add_separator()
            menu.add_command(label="Clear", command=self.clear_all)
        if self.state == 4:
            menu.add_command(label="Back", command=self.clear_mode3)
            menu.add_separator()
            menu.add_command(label="Save", command=self.saveResultImage)
        menu.post(event.x_root, event.y_root)

    def midMousePress(self, event):
        self.pre_x = event.x
        self.pre_y = event.y

    def leftMouseMove(self, event):
        x = event.x - self.pos_x
        y = event.y - self.pos_y
        if self.state == 1:
            self.clear_mode1()
            self.x2 = x
            self.y2 = y
            self.rect = self.img.create_rectangle(self.x1, self.y1, self.x2, self.y2, tag='rect')
            self.print('Rectangle is (%d, %d, %d, %d)' % (self.x1, self.y1, self.x2, self.y2))

    def midMouseMove(self, event):
        self.pos_x += event.x - self.pre_x
        self.pos_y += event.y - self.pre_y
        self.print('Position of the picture is (%d , %d)' % (self.pos_x, self.pos_y))
        self.img.move(self.image_, event.x - self.pre_x, event.y - self.pre_y)
        if self.rect is not None:
            self.img.move(self.rect, event.x - self.pre_x, event.y - self.pre_y)
        self.pre_x = event.x
        self.pre_y = event.y

    def MouseMove(self, event):
        w, h = self.image.size
        x = event.x - self.pos_x
        y = event.y - self.pos_y
        if x >= w or y >= h or x < 0 or y < 0:
            return
        color = self.image.getpixel((x, y))
        self.color.delete(ALL)
        self.color.create_rectangle(0, 0, 20, 20, fill=rgb_to_hex(color, self.image.mode))
        if self.image.mode == 'L':
            self.ys.set('({0},{0},{0},255)'.format(color))
        if self.image.mode == 'RGB':
            self.ys.set('(%d,%d,%d,255)' % color)
        if self.image.mode == 'RGBA':
            self.ys.set('(%d,%d,%d,%d)' % color)

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
        # 0.75->0.85 * 0.85/0.75

        self.image = self.image.resize(
            (int(self.image_src.size[0] * percent), int(self.image_src.size[1] * percent)), im.ANTIALIAS)
        self.imageTk = ImageTk.PhotoImage(self.image)
        self.img.itemconfig(self.image_, image=self.imageTk)
        self.bl.set("%d x %d %d" % (
            int(self.image_src.size[0] * percent), int(self.image_src.size[1] * percent), round(percent * 100)) + '%')

    def stateBoxClick(self, *args):
        self.state = self.stateBox.current() + 1
        if self.state == 1:
            self.clear_mode1()
        if self.state in [2, 3]:
            if self.image_sobel is None:
                self.image = self.sobel(self.image)
                self.imageTk = ImageTk.PhotoImage(self.image)
                self.img.itemconfig(self.image_, image=self.imageTk)
            self.clear_restart()
        self.print('Start ' + self.stateBox.get())

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

    def clip(self):
        if self.rect is None:
            return
        name = self.path.split('.')[0] + '_.' + self.path.split('.')[1]
        img = self.image.crop((self.x1, self.y1, self.x2, self.y2))
        img = img.resize((int(img.size[0] / self.percent), int(img.size[1] / self.percent)), im.ANTIALIAS)
        img.format = self.image.format
        save(img, name)

    def autoRound(self):
        print('start point:', self.start_point)
        print('end point:', (self.x1, self.y1))
        w, h = self.image.size
        numberList = [self.start_point[0], self.start_point[1], w - self.start_point[0], h - self.start_point[1]]
        index = numberList.index(min(numberList))
        if index == 0:
            [self.image.putpixel((x, self.start_point[1]), (255, 0, 0)) for x in range(numberList[index])]
        if index == 1:
            [self.image.putpixel((self.start_point[0], x), (255, 0, 0)) for x in range(numberList[index])]
        if index == 2:
            [self.image.putpixel((x, self.start_point[1]), (255, 0, 0)) for x in range(self.start_point[0], w)]
        if index == 3:
            [self.image.putpixel((self.start_point[0], x), (255, 0, 0)) for x in range(self.start_point[1], h)]
        numberList = [self.x1, self.y1, w - self.x1, h - self.y1]
        index = numberList.index(min(numberList))
        if index == 0:
            [self.image.putpixel((x, self.y1), (255, 0, 0)) for x in range(numberList[index])]
        if index == 1:
            [self.image.putpixel((self.x1, x), (255, 0, 0)) for x in range(numberList[index])]
        if index == 2:
            [self.image.putpixel((x, self.y1), (255, 0, 0)) for x in range(self.x1, w)]
        if index == 3:
            [self.image.putpixel((self.x1, x), (255, 0, 0)) for x in range(self.y1, h)]
        self.imageTk = ImageTk.PhotoImage(self.image)
        self.img.itemconfig(self.image_, image=self.imageTk)
        self.clear_restart()

    def mat(self, x, y):
        print_fjx()
        print('begin mat')
        self.pre_image = self.image.copy()
        self.res_image = self.image_src.convert('RGBA')
        q = Queue()
        q.put((x, y))
        color1 = self.image.getpixel((x, y))
        color2 = self.res_image.getpixel((x, y))
        self.image.putpixel((x, y), (color1[0], color1[1], color1[2], 0))
        self.res_image.putpixel((x, y), (color2[0], color2[1], color2[2], 0))
        dx = [-1, 0, 0, 1]
        dy = [0, 1, -1, 0]
        w, h = self.res_image.size
        while not q.empty():
            u = q.get()
            for i in range(4):
                xx = u[0] + dx[i]
                yy = u[1] + dy[i]
                if 0 <= xx < w and h > yy >= 0:
                    color1 = self.image.getpixel((xx, yy))
                    color2 = self.res_image.getpixel((xx, yy))
                    if color2[3] != 0 and color1[:3] != (255, 0, 0):
                        q.put((xx, yy))
                        self.res_image.putpixel((xx, yy), (color2[0], color2[1], color2[2], 0))
                        self.image.putpixel((xx, yy), (color1[0], color1[1], color1[2], 0))
        print('end mat')
        self.res_image.show()
        self.imageTk = ImageTk.PhotoImage(self.image)
        self.img.itemconfig(self.image_, image=self.imageTk)

    def saveResultImage(self):
        temp = self.path.split('.')
        fileName = temp[0] + '_.png'
        save(self.res_image, fileName)

    # 清除矩形框
    def clear_mode1(self):
        self.print('Clear clip rectangle!')
        if self.rect is not None:
            self.img.delete(self.rect)
            self.rect = None

    # 清除上个选择点
    def clear_mode2(self):
        if self.pre_point == (-1, -1): return
        self.x1 = self.pre_point[0]
        self.y1 = self.pre_point[1]
        self.image = self.pre_image.copy()
        self.imageTk = ImageTk.PhotoImage(self.image)
        self.img.itemconfig(self.image_, image=self.imageTk)
        self.print('Clear the last selected point!')

    # 重新开始选择
    def clear_restart(self):
        self.x1 = -1
        self.y1 = -1
        self.start_point = (-1, -1)
        self.print('Restart selection!')
        pass

    # 清除所有选择点
    def clear_all(self):
        self.x1 = -1
        self.y1 = -1
        self.start_point = (-1, -1)
        self.image = self.image_sobel.copy()
        self.imageTk = ImageTk.PhotoImage(self.image)
        self.img.itemconfig(self.image_, image=self.imageTk)
        self.print('Clear all selected point!')

    # 清除上一次抠图
    def clear_mode3(self):
        if self.pre_image is None: return
        self.image = self.pre_image.copy()
        self.imageTk = ImageTk.PhotoImage(self.image)
        self.img.itemconfig(self.image_, image=self.imageTk)
        self.print('Clear the last matting!')

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

    # 边缘检测
    def sobel(self, image: im.Image):
        image_ = image.convert('L')
        # image__ = image_.filter(ImageFilter.EDGE_ENHANCE_MORE)
        image___ = image_.filter(ImageFilter.FIND_EDGES)
        image___ = image___.convert('RGBA')
        self.image_sobel = image___
        return image___

    def print(self, mes):
        self.mes.set(mes)


class W(Tk):  # 图片预览
    ew = None
    width = 588
    height = 320
    panel_width = 208

    def __init__(self):
        super().__init__()
        # self.config(bg='black')
        self.f = font.Font(family='楷体', size=13)
        self.title('yooki图片处理器v5.2') # version
        self.iconbitmap('icon_im.ico')
        center(self, self.width - self.panel_width, self.height)
        self.resizable(0, 0)  # 固定窗口
        # self.attributes('-topmost', 1)  # 置顶
        # self.attributes("-alpha", 0.95) # 设置透明度
        self.box1 = ['.*', '.jpg', '.png', '.jpeg']
        self.box2 = ['.jpg', '.png', '.jpeg', '.ico(128,128)', '.ico(64,64)', '.ico(32,32)', 'ico(16,16)']
        self.is_delete = BooleanVar(value=False)
        self.input_path = StringVar()
        self.input_name = StringVar()
        self.is_renamee = BooleanVar(value=False)

        # 控件
        self.ff1 = Frame(self)
        self.f1 = Frame(self.ff1)
        self.lb_path = Label(self.f1, text='路径', font=self.f)
        self.inp = Entry(self.f1, bd=3, font=self.f, textvariable=self.input_path)
        self.list_path = Button(self.f1, text='…', command=self.get_dir, font=self.f)
        self.clear = Button(self.f1, text="清空", command=self.f_clear, font=self.f)
        self.listbox = Listbox(self.ff1, bd=5, font=self.f, selectmode=EXTENDED, height=11)
        self.f2 = Frame(self.ff1)
        self.f3 = Frame(self.ff1)
        self.lb_format1 = Label(self.f2, text='由格式', font=self.f)
        self.lb_format2 = Label(self.f2, text='转换至格式', font=self.f)
        self.com_f1 = ttk.Combobox(self.f2, values=self.box1, font=self.f, width=10)
        self.com_f2 = ttk.Combobox(self.f2, values=self.box2, font=self.f, width=10)
        self.sure = Button(self.f3, text='转换', command=self.edit, font=self.f)
        self.is_rename = Checkbutton(self.f3, text='是否批量重命名文件', variable=self.is_renamee, command=self.set_is_rename,
                                     font=self.f)
        self.is_clear = Checkbutton(self.f3, text='是否删除原文件', variable=self.is_delete, font=self.f)
        self.inp_name = Entry(self.f3, bd=3, font=self.f, textvariable=self.input_name, state=DISABLED)
        self.txt_panel = Label(self, text='右键预览图片', font=self.f)
        self.panel = Canvas(self, width=self.panel_width, height=self.panel_width, bg='white')
        self.image = None
        self.imageTK = None
        self.image_ = None

        # 布局
        self.f1.pack()
        self.listbox.pack(fill='x')
        self.lb_path.grid(row=0, column=0)
        self.inp.grid(row=0, column=1)
        self.list_path.grid(row=0, column=2)
        self.clear.grid(row=0, column=3)
        self.f2.pack()
        self.lb_format1.grid(row=0, column=0)
        self.com_f1.grid(row=0, column=1)
        self.lb_format2.grid(row=0, column=2)
        self.com_f2.grid(row=0, column=3)
        self.is_rename.grid(row=0, column=0, sticky="w")
        self.inp_name.grid(row=0, column=1, sticky="w")
        self.is_clear.grid(row=1, column=0, sticky="w")
        self.sure.grid(row=1, column=1, sticky="w")
        self.f3.pack(fill='x')
        self.ff1.pack(side='left')
        self.txt_panel.pack(side='top')
        self.panel.pack(pady=3)

        # 绑定
        self.demo()

        self.mainloop()

    def demo(self):
        wd.hook_dropfiles(self, func=self.dragged_files)
        self.com_f1.set(self.box1[0])
        self.com_f2.set(self.box2[0])
        self.inp.bind("<Return>", self.local_list)
        self.listbox.bind('<Double-Button-1>', self.listboxLeftBD)
        self.listbox.bind('<Button-3>', self.listBoxRightClick)

    def listboxLeftBD(self, *args):
        try:
            cur = self.listbox.curselection()
            value = self.listbox.get(cur)
            if len(self.input_path.get()) != 0:
                value = os.path.join(self.input_path.get(), value)
            self.ew = EW(value)
        except TclError:
            pass

    def listBoxRightClick(self, *args):
        try:
            cur = self.listbox.curselection()
            value = self.listbox.get(cur[0])
            path = self.input_path.get()
            if path != '':
                value = path + '/' + value
            self.image = im.open(value)
            w, h = self.image.size
            ww, hh = (w, h)
            x, y = ((self.panel_width - w) / 2, (self.panel_width - h) / 2)
            if w > h:
                if w > self.panel_width:
                    ww = self.panel_width
                    hh = self.panel_width / w * h
                    x = 0
                    y = (self.panel_width - hh) / 2
            else:
                if h > self.panel_width:
                    hh = self.panel_width
                    ww = self.panel_width / h * w
                    x = (self.panel_width - ww) / 2
                    y = 0
            self.image = self.image.resize((int(ww), int(hh)), im.ANTIALIAS)
            self.imageTK = ImageTk.PhotoImage(self.image)
            self.image_ = self.panel.create_image(x, y, anchor='nw')
            self.panel.itemconfig(self.image_, image=self.imageTK)
            self.geometry('%dx%d' % (self.width, self.height))
        except TclError:
            pass

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
                format_ = self.com_f2.get()
                if format_ == '.png':
                    image.convert('RGBA')
                if '.ico' in format_:
                    res = search('\((\d+),(\d+)\)', format_)
                    a = int(res.group(1))
                    image = image.resize((a, a), im.ANTIALIAS)
                    format_ = '.ico'
                name = x.split('.')[0] + format_
                if self.is_renamee.get():
                    name = self.rename(self.input_path.get(), self.inp_name.get())
                try:
                    if '.ico' == format_:
                        image.save(name, sizes=[(a, a)])
                    else:
                        image.save(name)
                    l.append('成功--' + name)
                except OSError as e:
                    print(e)
                    l.append('失败--' + name)
                finally:
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
                    format_ = self.com_f2.get()
                    if format_ == '.png':
                        image.convert('RGBA')
                    if '.ico' in format_:
                        res = search('\((\d+),(\d+)\)', format_)
                        a = int(res.group(1))
                        image = image.resize((a, a), im.ANTIALIAS)
                        format_ = '.ico'
                    name = x.split('.')[0] + format_
                    path_one = os.path.split(x)[0]
                    if self.is_renamee.get():
                        name = self.rename(path_one, self.inp_name.get())
                    try:
                        if '.ico' == format_:
                            image.save(name, sizes=[(a, a)])
                        else:
                            image.save(name)
                        l.append('成功--' + name)
                    except OSError as e:
                        print(e)
                        l.append('失败--' + name)
                    finally:
                        if self.is_delete.get():
                            os.remove(x)
        messagebox.showinfo('转换成功', '\n'.join(l))

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
                except ValueError:
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
            except ValueError:
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
    pass
