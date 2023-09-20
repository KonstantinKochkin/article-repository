from tkinter import *
from tkinter import ttk
from tkinter.font import *
from sqlite import *
import sqlite as sql
from textwrap import wrap
import time
import utils
from utils import APPNAME, RUNTIME_ERROR, IMG2
from tkinter.messagebox import showinfo, showerror, showwarning

test = None

PAGES = "pages"
nPAGES = 6
ANY = "<любая>"
sFIND = "find"
sFAVOURITE = "favourite"
sLASTS = "lasts"


class Findframe(Frame):

    class Table(Frame):

        # *******************************************Table.functions*************************************
        def getWidths(self):
            widths = {}
            for i in self.changing_columns:
                column = self.columns[i]
                widths[column] = self.tree.column(column, "width")
            return widths

        # Перенос текста при изменении ширины столбцов
        def wrapText(self):
            self.tree.update()
            for cnum in self.changing_columns:
                column = self.columns[cnum]
                width = self.tree.column(column, "width")
                if width != self.tree.saved_widths[column]:
                    self.tree.saved_widths[column] = width
                    for ind, idx in enumerate(self.tree.get_children()):
                        try:
                            wrapped_text = '\n'.join(wrap(self.data[ind][cnum],
                                                          width // self.width_char))
                            self.tree.set(idx, column, wrapped_text)
                            # print(self.tree.item(idx))
                        except (TypeError, AttributeError):
                            pass

        # Перенос текста значений строки таблицы при обновлении
        def convert(self, row):
            wrap_row = self.columns[:]
            wrap_row[nID] = row[nID]
            wrap_row[nDATE] = row[nDATE]
            wrap_row[nPAGES] = f"{row[nPAGEBEGIN]}-{row[nPAGEEND]}" if row[nPAGEBEGIN] else ""
            for cnum in self.changing_columns:
                width = self.tree.column(self.columns[cnum], "width")
                wrap_row[cnum] = utils.wrapText(
                    row[cnum], width, self.width_char)
            return wrap_row

        # Заполнение таблицы
        def fillTable(self):
            self.tree.delete(*self.tree.get_children())
            graytag = False
            n_fav_list = self.master.getNFavList()
            for idx, row in enumerate(self.data):
                tags = []
                if graytag:
                    tags.append("gray")
                if self.data[idx][n_fav_list] == 1:
                    tags.append("favourite")
                self.tree.insert(
                    "", END, f"I{idx}", values=self.convert(row), tags=tags)
                graytag = not graytag

        def Default(self):
            self.focus_row = -1
            self.master.but["state"] = "disable"
            self.master.but["background"] = "SystemButtonFace"
            self.master.but["text"] = "Открыть файл"
            self.master.frame.heading2["text"] = ""
            self.master.frame.subject2["text"] = ""
            self.master.frame.publication2["text"] = ""
            self.master.frame.author2["text"] = ""
            self.master.frame.date2["text"] = ""
            self.master.frame.like_but["text"] = "Добавить в Избранное"
            self.master.frame.like_but["state"] = "disable"
            self.master.frame.like_but["background"] = "SystemButtonFace"
            self.master.frame.note.text.delete("1.0", END)
            self.master.frame.note.text["state"] = "disable"

            self.master.frame.columnconfigure(3, weight=0)
            self.master.frame.note.text.pack_forget()
            self.master.frame.note.buts.pack_forget()
            self.master.frame.note.add_but.pack_forget()
            if self.master.image:
                self.master.frame.note.image_lab.pack()
            self.master.frame.pack(fill=X, expand=False,
                                   after=self.master.but_lab)
            self.master.frame.note.grid(rowspan=5)

        # Обновление данных
        def updateTable(self):
            self.Default()

            keywords = self.findline.keywords
            if len(keywords) == 0:
                keywords = []
            else:
                keywords = list(keyword.strip() for keyword in keywords.split(",")
                                if len(keyword.strip()) != 0)

            subject = self.findline.subjectVar.get()
            subject = subject if (subject != ANY) else ""
            try:
                self.data = sql.select(self.tree.ord_column, self.tree.select_opt,
                                       keywords, subject)  # *10
                self.fillTable()
            except Exception as ex:
                showerror(RUNTIME_ERROR, str(ex))

        def headerClick(self, ord_column):
            if self.master.state != sFIND:
                return
            if ord_column == self.tree.ord_column:
                self.tree.select_opt = "DESC" if (
                    self.tree.select_opt == "ASC") else "ASC"
            else:
                self.tree.ord_column = ord_column
                self.tree.select_opt = "ASC"
            self.updateTable()

        def findButtonClick(self):
            keywords = self.findline.text.get(
                "1.0", END).strip().lower().replace("'", '"')
            if keywords != self.findline.keywords:
                self.findline.keywords = keywords
                self.updateTable()
                self.findline.but["bg"] = "SystemButtonFace"

        def comboboxSelect(self, x):
            subject = self.findline.subjectVar.get()
            if subject != self.findline.subject:
                self.findline.subject = subject
                self.findline.keywords = self.findline.text.get(
                    "1.0", END).strip().lower()
                self.updateTable()

        def getFavourite(self):
            self.Default()
            try:
                self.data = sql.selectFavourite(
                    self.master.master.getFavListID())
                self.fillTable()
            except Exception as ex:
                showerror(RUNTIME_ERROR, str(ex))

        def getLasts(self):
            self.Default()
            try:
                self.data = sql.selectLasts()
                self.fillTable()
            except Exception as ex:
                showerror(RUNTIME_ERROR, str(ex))

        def updateSubject(self):
            try:
                subjects = sql.getSubjects()
                subjects.insert(0, ANY)
                self.findline.combobox["values"] = subjects
                self.findline.subjectVar.set("<любая>")
                self.findline.subject = ""
            except Exception as ex:
                showerror(RUNTIME_ERROR, str(ex))

        def keyRelease(self, ev=None):
            keywords = self.findline.text.get("1.0", END).strip().lower()
            if keywords != self.findline.keywords:
                self.findline.but["bg"] = "SteelBlue1"
            else:
                self.findline.but["bg"] = "SystemButtonFace"
            if self.findline.text.get("end - 2 chars") == '\n':
                self.findline.text.delete("end - 2 chars")
                self.findButtonClick()


# =========================================Table.__init__=========================================#

        def __init__(self, master=None):
            super().__init__(master)

            self.columns = [ID, HEADER, SUBJECTS,
                            DATE, PUBLICATION, AUTHOR, PAGES]
            self.changing_columns = [nHEADER, nSUBJECTS, nPUBLICATION, nAUTHOR]
            self.width_char = 7.4
            self.focus_row = -1
            f10 = Font(family="Helvetica", size=10)
            f11 = Font(family="Helvetica", size=11)
            f11i = Font(family="Helvetica", size=11, slant=ITALIC)
            f13 = Font(family="Helvetica", size=30)
            f13i = Font(family="Helvetica", size=13, slant=ITALIC)

            # Создание строки поиска
            self.findline = Frame(self)
            self.findline.pack(fill=X)
            self.findline.keywords = ""
            self.findline.subjectVar = StringVar()
            self.findline.subjectVar.set(ANY)
            self.findline.subject = self.findline.subjectVar.get()

            self.findline.lab1 = Label(
                self.findline, text='Выберите\nтематику:', font=f10)

            self.findline.combobox = ttk.Combobox(self.findline, font=f13i, state="readonly",
                                                  textvariable=self.findline.subjectVar)

            self.findline.combobox.bind(
                "<<ComboboxSelected>>", self.comboboxSelect)

            self.findline.lab2 = Label(self.findline, font=f10,
                                       text="Введите фразы для\nпоиска через запятую:")

            self.findline.text = Text(self.findline, height=2, width=15, font=f11i, wrap="word",
                                      undo="true")

            self.findline.text.bind("<KeyRelease>", self.keyRelease)
            self.findline.text.bind("<B3-ButtonRelease>",
                                    lambda ev: self.master.master.contextMenu(ev, self.keyRelease))
            self.findline.text.bind(
                "<Control-KeyPress>", self.master.master.controlRelease)

            self.findline.but = Button(self.findline, text="Поиск", font=f11, borderwidth=8,
                                       padx=10, command=lambda: self.findButtonClick())

            self.findline.lab1.grid(row=0, column=0)
            self.findline.combobox.grid(
                row=0, column=1, pady=5, padx=5, sticky=EW)
            self.findline.lab2.grid(row=0, column=2, pady=5)
            self.findline.text.grid(row=0, column=3, sticky=EW)
            self.findline.but.grid(row=0, column=4, padx=10)
            self.findline.columnconfigure(1, weight=2)
            self.findline.columnconfigure(3, weight=1)

            # Создание таблицы
            self.tree = ttk.Treeview(
                self, columns=self.columns, show="headings", height=3)
            ttk.Style().configure('Treeview', rowheight=52)
            ttk.Style().configure('Treeview', font=f10)

            self.tree.tag_configure('favourite', background="#ffcccc")
            self.tree.tag_configure('gray', background="#ddeeee")
            self.tree.bind("<B1-Motion>", lambda e: self.wrapText())
            self.tree.bind("<Configure>", lambda e: self.wrapText())
            self.tree.bind("<Double-Button-1>",
                           lambda e: self.master.butClick())
            self.tree.ord_column = ID
            self.tree.select_opt = "ASC"

            self.tree.heading(
                ID, text="№", command=lambda: self.headerClick(ID))
            self.tree.heading(HEADER, text="Заголовок",
                              command=lambda: self.headerClick(HEADER))
            self.tree.heading(SUBJECTS, text="Тематика",
                              command=lambda: self.headerClick(SUBJECTS))
            self.tree.heading(DATE, text="Дата",
                              command=lambda: self.headerClick(DATE))
            self.tree.heading(PUBLICATION, text="Публикация в",
                              command=lambda: self.headerClick(PUBLICATION))
            self.tree.heading(AUTHOR, text="Авторы",
                              command=lambda: self.headerClick(AUTHOR))
            self.tree.heading(PAGES, text="Страницы")

            self.tree.column(ID, width=30, minwidth=30, stretch=False)
            self.tree.column(HEADER, width=300, minwidth=100)
            self.tree.column(SUBJECTS, width=300, minwidth=100)
            self.tree.column(DATE, width=80, minwidth=40, stretch=False)
            self.tree.column(PUBLICATION, width=250, minwidth=100)
            self.tree.column(AUTHOR, width=200, minwidth=100)
            self.tree.column(PAGES, width=70, minwidth=50, stretch=False)

            self.tree.saved_widths = self.getWidths()

            # Полоса прокрутки
            self.vertscroll = ttk.Scrollbar(self, command=self.tree.yview)
            self.tree["yscroll"] = self.vertscroll.set

            self.vertscroll.pack(side=RIGHT, fill=Y)
            self.tree.pack(fill=BOTH, expand=True)


# *******************************************Findframe.functions**********************************#
    # Информация о статье
    def showArticle(self):
        if test:
            print("showArticle", self.table.focus_row)
        if self.table.focus_row == -1:
            return
        width = self.frame.heading2.winfo_width()
        data = self.table.data
        tree = self.table.tree
        irow = self.table.focus_row
        width_char = 11

        self.frame.heading2["text"] = utils.wrapText(
            data[irow][nHEADER], width, width_char)
        self.frame.subject2["text"] = utils.wrapText(
            data[irow][nSUBJECTS], width, width_char)
        self.frame.publication2["text"] = utils.wrapText(data[irow][nPUBLICATION], width,
                                                         width_char)
        self.frame.author2["text"] = utils.wrapText(
            data[irow][nAUTHOR], width, width_char)
        self.frame.date2["text"] = data[irow][nDATE]

    def updateContextFavMenu(self, i=None, val=None):
        if test:
            print("updateContextFavMenu")
        if i is not None and val is not None:
            self.master.contain_lists[i].set(val)
            return

        datarow = self.table.data[self.table.focus_row]
        for idx, fav_list in enumerate(self.master.fav_lists):
            self.master.contain_lists[idx].set(datarow[nFIRST_FAV_LIST + idx])

    # Выбор строки таблицы
    def selectArticle(self, ev):
        if test:
            print("selectArticle")
        if not self.table.tree.focus():
            return
        self.table.focus_row = int(self.table.tree.focus()[1:])
        datarow = self.table.data[self.table.focus_row]
        self.but["text"] = "Открыть файл ({})".format(
            datarow[nFILE].split(':')[1])
        if self.but["state"] == "disabled":
            self.but["state"] = "normal"
            self.but["background"] = "pale green"
            self.frame.like_but["state"] = "normal"
            self.frame.note.text["state"] = "normal"

        if datarow[self.getNFavList()] == 1:
            self.frame.like_but["text"] = "Убрать из *{}*".format(
                self.master.getFavListName())
            self.frame.like_but["background"] = "light salmon"
        else:
            self.frame.like_but["text"] = "Добавить в *{}*".format(
                self.master.getFavListName())
            self.frame.like_but["background"] = "SystemButtonFace"

        self.lab["text"] = "Последнее открытие : " + str(datarow[nLASTOPEN])

        if datarow[nNOTE]:
            self.frame.columnconfigure(3, weight=2)
            self.frame.note.add_but.pack_forget()
            if self.image:
                self.frame.note.image_lab.pack_forget()
            self.frame.note.text.pack(fill=BOTH, expand=True)
            self.frame.note.text.delete("1.0", END)
            self.frame.note.text.insert(END, str(datarow[nNOTE]))
            self.frame.note.text.edit_reset()       # сбросить undo
            self.frame.note.text.edit_modified(0)   #
            self.frame.note.buts.pack(fill=X)
            self.frame.note.fill_but.state = 0
        else:
            self.frame.columnconfigure(3, weight=0)
            self.frame.note.text.pack_forget()
            self.frame.note.buts.pack_forget()
            if self.image:
                self.frame.note.image_lab.pack()
            self.frame.note.add_but.pack(fill=X, side=BOTTOM)
        self.frame.note.fill_but.state = 0
        self.frame.note.fill_but["text"] = "Развернуть"
        self.frame.pack(fill=X, expand=False)
        self.frame.note.grid(rowspan=5)
        self.update()

        self.updateContextFavMenu()

        self.showArticle()
        self.update()
        self.table.tree.see(self.table.tree.focus())

    def frameConfigure(self, ev):
        if test:
            print("frameConfigure", ev.width, ev.widget.width)
        if ev.width != ev.widget.width:
            ev.widget.width = ev.width
            self.showArticle()

    def butClick(self):
        if not self.table.tree.focus():
            return
        datarow = self.table.data[self.table.focus_row]
        utils.openFile(*datarow[nFILE].split(":"))
        time_str = time.strftime("%Y.%m.%d %H:%M")
        try:
            sql.updateDate(datarow[nID], time_str)
            datarow[nLASTOPEN] = time_str
            self.lab["text"] = "Последнее открытие : " + time_str
        except Exception as ex:
            showerror(RUNTIME_ERROR, str(ex))

    def likeButClick(self):
        datarow = self.table.data[self.table.focus_row]
        n_fav_list = self.getNFavList()
        try:
            if datarow[n_fav_list] == 1:
                sql.updateFavourite(
                    self.master.getFavListID(), datarow[nID], 0)
                datarow[n_fav_list] = 0
                self.updateContextFavMenu(self.master.cur_favor.get(), 0)
                self.frame.like_but["text"] = "Добавить в *{}*".format(
                    self.master.getFavListName())
                self.frame.like_but["background"] = "SystemButtonFace"
                tags = self.table.tree.item(self.table.tree.focus())["tags"]
                if "favourite" in tags:
                    tags.remove("favourite")
                    self.table.tree.item(self.table.tree.focus(), tags=tags)
                if self.state == sFAVOURITE:
                    self.table.getFavourite()
            else:
                sql.updateFavourite(
                    self.master.getFavListID(), datarow[nID], 1)
                datarow[n_fav_list] = 1
                self.updateContextFavMenu(self.master.cur_favor.get(), 1)
                self.frame.like_but["text"] = "Убрать из *{}*".format(
                    self.master.getFavListName())
                self.frame.like_but["background"] = "light salmon"
                tags = list(self.table.tree.item(
                    self.table.tree.focus(), "tags"))
                tags.append("favourite")
                self.table.tree.item(self.table.tree.focus(), tags=tags)
        except Exception as ex:
            showerror(RUNTIME_ERROR, str(ex))

    def contextFavMenuClick(self, i):
        if i == self.master.cur_favor.get():
            self.likeButClick()
            return
        datarow = self.table.data[self.table.focus_row]
        n_fav_list = nFIRST_FAV_LIST + i
        try:
            if datarow[n_fav_list] == 1:
                sql.updateFavourite(
                    self.master.getFavListID(i), datarow[nID], 0)
                datarow[n_fav_list] = 0
            else:
                sql.updateFavourite(
                    self.master.getFavListID(i), datarow[nID], 1)
                datarow[n_fav_list] = 1
        except Exception as ex:
            showerror(RUNTIME_ERROR, str(ex))

    def findframeON(self):
        for item in self.master.slaves():
            item.pack_forget()
        ttk.Style().theme_use("vista")
        self.pack(fill=BOTH, expand=True)

    def selectFindMenu(self):
        self.findframeON()
        self.state = sFIND
        self.table.findline.pack(fill=X, before=self.table.tree)
        self._root().title(f"Поиск - {APPNAME}")
        self.table.updateSubject()
        self.table.updateTable()

    def selectFavouriteMenu(self):
        self.findframeON()
        self.state = sFAVOURITE
        self.table.findline.pack_forget()
        self._root().title(f"Избранное - {APPNAME}")
        self.table.getFavourite()

    def selectLastsMenu(self):
        self.findframeON()
        self.state = sLASTS
        self.table.findline.pack_forget()
        self._root().title(f"Недавно просмотренные - {APPNAME}")
        self.table.getLasts()

    def saveNoteClick(self):
        try:
            datarow = self.table.data[self.table.focus_row]
            text = self.frame.note.text.get("1.0", END).strip()
            sql.updateNote(datarow[nID], text)
            datarow[nNOTE] = text
            self.frame.note.focus_set()
            showinfo(f"Результат операции - {APPNAME}", "Заметка записана!")
        except Exception as ex:
            showerror(RUNTIME_ERROR, str(ex))

    def addButClick(self):
        self.frame.columnconfigure(3, weight=2)
        self.frame.note.add_but.pack_forget()
        if self.image:
            self.frame.note.image_lab.forget()
        self.frame.note.text.pack(fill=BOTH, expand=True)
        self.frame.note.text.delete("1.0", END)
        self.frame.note.buts.pack(fill=X)
        self.update()
        self.showArticle()

    def fillButClick(self):
        if self.frame.note.fill_but.state == 0:
            self.frame.note.fill_but.state = 1
            self.frame.note.fill_but["text"] = "Свернуть"
            self.frame.pack(fill=BOTH, expand=True)
            self.frame.note.grid(rowspan=6)
        else:
            self.frame.note.fill_but.state = 0
            self.frame.note.fill_but["text"] = "Развернуть"
            self.frame.pack(fill=X, expand=False)
            self.frame.note.grid(rowspan=5)

    def showFavouriteList(self, like_but):
        if time.time() - like_but.last_enter_time >= 1:
            self.master.context_fav_menu.post(like_but.winfo_rootx() + 95,
                                              like_but.winfo_rooty() + 10)

    def mouseEnterLikeBut(self, ev):
        if ev.widget["state"] != "disabled":
            ev.widget.last_enter_time = time.time()
            self.after(1000, lambda: self.showFavouriteList(ev.widget))

    def mouseLeaveLikeBut(self, ev):
        ev.widget.last_enter_time += 600000  # + неделя

    def getNFavList(self):
        return nFIRST_FAV_LIST + self.master.cur_favor.get()


# =========================================Findframe.__init__=============================================

    def __init__(self, master):
        super().__init__(master)
        self.state = sFIND

        f11 = Font(family="Helvetica", size=11, weight=NORMAL, slant=ROMAN,
                   underline=False, overstrike=False)
        f12i = Font(family="Helvetica", size=12, weight=NORMAL, slant=ITALIC,
                    underline=False, overstrike=False)
        f14i = Font(family="Arial", size=14, weight=NORMAL, slant=ITALIC,
                    underline=False, overstrike=False)

        try:
            self.image = PhotoImage(file=IMG2)
        except Exception as ex:
            self.image = None
            showwarning(f"Ограничение интерфейса - {APPNAME}",
                        f"Картинка '{IMG2}' не отображается.\n" + str(ex))
            self.focus_force()

        # кнопка открытия файла статьи и время последнего открытия
        self.but_lab = Frame(self)
        self.but = Button(self.but_lab, text="Открыть файл", font=f12i, command=self.butClick,
                          borderwidth=10, state="disabled")
        self.lab = Label(self.but_lab, text="Последнее открытие ", font=f11)

        # Нижняя половина виджета
        self.frame = Frame(self, relief=RAISED, borderwidth=10)
        self.but.pack(side=RIGHT, expand=True)
        self.lab.pack(side=LEFT)
        self.but_lab.pack(side=TOP, fill=X)
        self.frame.pack(side=TOP, fill=X)

        self.frame.columnconfigure([1, 2], weight=1, minsize=150)
        self.frame.rowconfigure([6], weight=1)

        self.frame.heading1 = Label(self.frame, font=f11, text="Заголовок:  ")
        self.frame.heading2 = Label(self.frame, font=f14i, relief=SUNKEN, borderwidth=4, width=40,
                                    fg="DarkOrchid4")
        self.frame.heading1.grid(row=1, column=0, sticky=E)
        self.frame.heading2.grid(
            row=1, column=1, columnspan=2, sticky=EW, pady=10)

        self.frame.subject1 = Label(self.frame, font=f11, text="Тематика:  ")
        self.frame.subject2 = Label(self.frame, font=f14i, relief=SUNKEN, borderwidth=4, width=40,
                                    fg="DeepSkyBlue4")
        self.frame.subject1.grid(row=2, column=0, sticky=E)
        self.frame.subject2.grid(
            row=2, column=1, columnspan=2, sticky=EW, pady=10)

        self.frame.publication1 = Label(
            self.frame, font=f11, text="Пубиликация в:  ")
        self.frame.publication2 = Label(self.frame, font=f14i, relief=SUNKEN, borderwidth=4,
                                        width=40, fg="DarkOrange4")
        self.frame.publication1.grid(row=3, column=0, sticky=E)
        self.frame.publication2.grid(
            row=3, column=1, columnspan=2, sticky=EW, pady=10)

        self.frame.author1 = Label(self.frame, font=f11, text="Авторы:  ")
        self.frame.author2 = Label(self.frame, font=f14i, relief=SUNKEN, borderwidth=4, width=40,
                                   fg="green4")
        self.frame.author1.grid(row=4, column=0, sticky=E)
        self.frame.author2.grid(
            row=4, column=1, columnspan=2, sticky=EW, pady=10)

        self.frame.date1 = Label(self.frame, font=f11,
                                 text="Дата публикации:  ")
        self.frame.date2 = Label(
            self.frame, font=f14i, relief=SUNKEN, borderwidth=4, width=10)
        self.frame.date1.grid(row=5, column=0, sticky=E)
        self.frame.date2.grid(row=5, column=1, sticky=W, pady=10)

        self.frame.like_but = Button(self.frame, font=f11, text="Добавить в Избранное", borderwidth=10,
                                     command=self.likeButClick, state="disabled")
        self.frame.like_but.grid(row=5, column=2, sticky=E)

        self.frame.note = Frame(self.frame, relief=SUNKEN, borderwidth=4)
        self.frame.note.grid(row=1, rowspan=5, column=3,
                             sticky=NSEW, pady=7, padx=7)
        self.frame.note.lab = Label(self.frame.note, text="Заметки", font=f11)
        self.frame.note.lab.pack()
        self.frame.note.text = Text(
            self.frame.note, height=10, width=20, wrap="word", undo="true")
        self.frame.note.buts = Frame(self.frame.note)
        self.frame.note.save_but = Button(self.frame.note.buts, text="Сохранить", borderwidth=4,
                                          command=self.saveNoteClick, font=f11)
        self.frame.note.save_but.pack(side=LEFT, fill=X, expand=True)
        self.frame.note.fill_but = Button(self.frame.note.buts, text="Развернуть", borderwidth=4,
                                          command=self.fillButClick, font=f11)
        self.frame.note.fill_but.state = 0
        self.frame.note.fill_but.pack(side=RIGHT)
        self.frame.note.add_but = Button(self.frame.note, text="Добавить заметку", borderwidth=8,
                                         command=self.addButClick, font=f11)
        if self.image:
            self.frame.note.image_lab = Label(
                self.frame.note, image=self.image)
            self.frame.note.image_lab.pack()

        self.frame.note.text.bind(
            "<B3-ButtonRelease>", self.master.contextMenu)
        self.frame.note.text.bind(
            "<Control-KeyPress>", self.master.controlRelease)
        self.frame.like_but.last_enter_time = 0
        self.frame.like_but.bind("<Enter>", self.mouseEnterLikeBut)
        self.frame.like_but.bind("<Leave>", self.mouseLeaveLikeBut)

        # фрейм с таблицей и поиском
        self.table = self.Table(self)
        self.table["relief"] = RIDGE
        self.table["borderwidth"] = 10
        self.table.tree.bind("<<TreeviewSelect>>", self.selectArticle)
        self.frame.width = self.frame.winfo_width()
        self.frame.bind("<Configure>", self.frameConfigure)

        self.table.pack(fill=BOTH, expand=True, before=self.but_lab)
