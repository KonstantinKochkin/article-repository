from tkinter import *
from tkinter import ttk
from tkinter.font import *
from sqlite import *
import sqlite as sql
from tkinter.filedialog import *
import os.path

from tkinter.messagebox import *
import tkinter.messagebox as mb
from time import strftime
import utils
import uuid
from utils import APPNAME, RUNTIME_ERROR, IMG1, IMG3, check, CheckFail


sNEW = "new"
sUPDATE = "update"


class Addframe(Frame):

    def addframeON(self):
        for item in self.master.slaves():
            item.pack_forget()
        self.pack(fill=BOTH, expand=True)
        style = ttk.Style().theme_use("clam")
        self.clear()
        self.updateSubjects()

    def addMenuClick(self):
        self.addframeON()
        self._root().title(f"Создание новой статьи - {APPNAME}")
        self.state = sNEW
        self.butframe.remove_but.pack_forget()
        self.butframe.clear_but.pack()

    def updateArticle(self, rowdata):
        self.addframeON()
        self._root().title(f"Редактирование статьи - {APPNAME}")
        self.state = sUPDATE

        self.id = rowdata[nID]

        self.head_text.insert("1.0", rowdata[nHEADER])

        subjects = rowdata[nSUBJECTS].split(',')
        for i in range(len(subjects)):
            if i > 0:
                self.butComboAddClick()
            self.subjectVars[i].set(subjects[i].strip())
            if (i < 2):
                self.comboSelect(i)

        self.publ_text.insert("1.0", rowdata[nPUBLICATION])

        self.author_text.insert("1.0", rowdata[nAUTHOR])

        date = rowdata[nDATE].split('.')
        self.year.set(date[0])
        self.month.set(date[1] if (len(date) > 1) else "")
        self.day.set(date[2] if (len(date) > 2) else "")

        self.filepath, self.file_exten = rowdata[nFILE].split(":")
        self.oldfilepath = os.path.join(os.getcwd(), "resurces", self.filepath)
        self.fname_lab["text"] = "<сохранен в базе>"
        self.file_frame.but["text"] = "Изменить файл"
        self.file_frame.show_but.pack(side=LEFT, before=self.file_frame.but)

        if rowdata[nPAGEBEGIN]:
            self.file_frame.entry.insert(
                "0", f"{rowdata[nPAGEBEGIN]}-{rowdata[nPAGEEND]}")

        if rowdata[nNOTE]:
            self.note.text.delete("1.0", END)
            self.big_image_on = False
            if self.small_image:
                self.imageframe.grid()
            self.note.text.insert("1.0", rowdata[nNOTE])
        self.butframe.remove_but.pack()
        self.butframe.clear_but.pack_forget()

        try:
            self.keywords_text.insert("1.0", getKeywords(self.id))
        except Exception as ex:
            mb.showerror(RUNTIME_ERROR, str(ex))
            self.addMenuClick()

    def butComboOffClick(self):
        self.subj_count -= 1
        self.subj_labs[self.subj_count].grid_remove()
        self.subj_combos[self.subj_count].grid_remove()
        self.but_combo_add.grid(row=self.subj_count+2)
        if self.subj_count == 1:
            self.but_combo_off.grid_remove()
        else:
            self.but_combo_off.grid(row=self.subj_count+1)

    def butComboAddClick(self):
        self.but_combo_off.grid(row=self.subj_count+2, column=5, padx=10)
        self.subj_labs[self.subj_count].grid()
        self.subj_combos[self.subj_count].grid()
        self.subjectVars[self.subj_count].set("")
        self.subj_count += 1
        if self.subj_count < 3:
            self.but_combo_add.grid(row=self.subj_count+2)
        else:
            self.but_combo_add.grid_remove()

    def comboSelect(self, i, ev=None):
        if ev:
            ev.widget.select_clear()
        values = list(self.subj_combos[i]["values"])
        if self.subjectVars[i].get() in values:
            values.remove(self.subjectVars[i].get())
        self.subj_combos[i+1]["values"] = values
        if self.subjectVars[i+1].get() == self.subjectVars[i].get():
            self.subjectVars[i+1].set("")
        if i == 0 and self.subjectVars[i+2].get() == self.subjectVars[i].get():
            self.subjectVars[i+2].set("")

    def fileButClick(self):
        newpath = askopenfilename(filetypes=[("Статьи (pdf, docx, doc)", "*.pdf;*.docx;*.doc"),
                                             ("Все файлы", "*.*")])
        if newpath:
            self.filepath = newpath
            self.file_exten = os.path.splitext(newpath)[1]
            self.fname_lab["text"] = os.path.basename(self.filepath)
            self.file_frame.but["text"] = "Изменить файл"
            self.file_frame.show_but.pack(
                side=LEFT, before=self.file_frame.but)

    def clear(self):
        self.head_text.delete("1.0", "end")
        self.head_text.focus_set()

        for sub in self.subjectVars:
            sub.set("")
        while self.subj_count > 1:
            self.butComboOffClick()

        self.publ_text.delete("1.0", "end")

        self.author_text.delete("1.0", "end")

        self.year.set("")
        self.month.set("")
        self.day.set("")

        self.filepath = ""
        self.fname_lab["text"] = "<не выбран>"
        self.file_frame.but["text"] = "Указать файл"
        self.file_frame.entry.delete("0", "end")
        self.file_frame.show_but.pack_forget()

        self.keywords_text.delete("1.0", "end")

        self.note.text.delete("1.0", "end")
        if self.image:
            self.note.text.image_create(END, image=self.image)
            self.big_image_on = True
            self.imageframe.grid_remove()
        elif self.small_image:
            self.imageframe.grid()
            self.big_image_on = False
        else:
            self.big_image_on = None

        self.id = None

    def deleteImage(self, ev):
        if self.big_image_on:
            self.note.text.delete("1.0", "end")
            self.big_image_on = False
            if self.small_image:
                self.imageframe.grid()

    def clearButClick(self):
        if askokcancel(f"Подтверждение операции - {APPNAME}",
                       f"Вы уверены, что хотите очистить все поля ввода и выбора?\n" +
                       "Если указан файл, он также будет сброшен.", parent=self):
            self.clear()

    def verificate(self):
        mes_forbidden_symbol = "Использование символа одинарной кавычки (') запрещено!"
        try:
            heading = self.head_text.get("1.0", "end").strip()
            check(heading != "", self.head_text,
                  'Поле "Заголовок" не может быть пустым!')

            check(utils.checkText(heading), self.head_text, mes_forbidden_symbol)

            utils.check(self.subjectVars[0].get().strip() != "", self.subj_combos[0],
                        ('Поле "Тематика 1" не может быть пустым!\n' +
                         'Выберите тематику из списка или введите новую.'))

            for i in range(self.subj_count):
                subject = self.subjectVars[i].get().strip()
                check(subject != "", self.subj_combos[i], f'Поле "Тематика {i+1}" ' +
                      'не может быть пустым!\nВыберите, введите или скройте тематику.')
                check(utils.checkText(subject),
                      self.subj_combos[i], mes_forbidden_symbol)

            difsubj = set(self.subjectVars[i].get().strip(
            ).lower() for i in range(self.subj_count))
            check(len(difsubj) == self.subj_count, self.subj_combos[1],
                  "Вы указали две одинаковые тематики!\nУберите или измените одну из них.")

            check(utils.checkText(self.publ_text.get("1.0", "end")), self.publ_text,
                  mes_forbidden_symbol)

            check(utils.checkText(self.author_text.get("1.0", "end")), self.author_text,
                  mes_forbidden_symbol)

            check(self.year.get() != "", self.year_combo,
                  "Необходимо указать год публикации!")

            if self.day.get() != "":
                check(self.month.get() != "", self.month_combo, "Указан день публикации, но " +
                      "не указан месяц!\nВыберите месяц или уберите день.")

            if self.state == sNEW:
                check(self.filepath != "", self.file_frame.but,
                      "Укажите файл статьи!")

            if self.file_frame.entry.get().strip() != "":
                pages = self.file_frame.entry.get().strip().split('-')

                if len(pages) == 1 and pages[0].isdigit() and int(pages[0]) > 0:
                    self.page_begin = self.page_end = int(pages[0])

                elif len(pages) == 2 and pages[0].isdigit() and pages[1].isdigit() \
                        and int(pages[0]) > 0 and int(pages[0]) <= int(pages[1]):
                    self.page_begin = int(pages[0])
                    self.page_end = int(pages[1])
                else:
                    check(False, self.file_frame.entry,
                          ('Неверный формат страниц!\nУкажите диапозон страниц, например, ' +
                           '"9-14", или номер одной страницы или оставте поле пустым.'))

            keywords = self.keywords_text.get("1.0", "end").strip()
            check(utils.checkText(keywords),
                  self.keywords_text, mes_forbidden_symbol)

            check(len(tuple(kw for kw in keywords.split(",") if kw.strip() != "")) >= 5,
                  self.keywords_text, "Введите как минимум 5 ключевых слов или фраз к статье!")

            check(utils.checkText(self.note.text.get("1.0", "end")), self.note.text,
                  mes_forbidden_symbol)

        except CheckFail:
            return False

        return True

    def updateSubjects(self):
        try:
            self.subjects = sql.getSubjects()
            self.subj_combos[0]["values"] = self.subjects
            self.comboSelect(0)
            self.comboSelect(1)
        except Exception as ex:
            mb.showerror(
                RUNTIME_ERROR, "Обновление тематик завершилось ошибкой.\n  " + str(ex))

    def articleCreate(self):
        newsubjects = []
        for i in range(self.subj_count):
            if self.subjectVars[i].get().strip() not in self.subjects:
                self.subj_combos[i].focus_set()
                if askokcancel(RUNTIME_ERROR, 'Вы уверены, что хотите создать новый ' +
                               'тематический раздел "{}"?'.format(self.subjectVars[i].get())):
                    newsubjects.append(self.subjectVars[i].get().strip())
                else:
                    return

        data = dict()
        if self.filepath and self.fname_lab["text"] != "<сохранен в базе>":
            newname = str(uuid.uuid4())
            newpath = os.path.join(os.getcwd(), "resurces", newname)

            try:
                newpath = utils.encrypt(self.filepath, newpath)
            except Exception as ex:
                showerror(RUNTIME_ERROR, str(ex))
                return

            data[FILE] = os.path.split(
                newpath)[1] + ":" + os.path.splitext(self.filepath)[1]
            if self.state == sUPDATE and self.oldfilepath != newpath:
                try:
                    os.remove(self.oldfilepath)
                except Exception as ex:
                    showerror(RUNTIME_ERROR,
                              "Невозможно удалить старый файл статьи по причине.\n  " + str(ex))
                    return

                self.oldfilepath = newpath
                self.filepath, self.file_exten = data[FILE].split(":")

        if len(newsubjects) != 0:
            for subj in newsubjects:
                try:
                    insertSubject(subj)
                except Exception as ex:
                    showerror(RUNTIME_ERROR, str(ex))
                    return

            self.updateSubjects()

        data[HEADER] = self.head_text.get("1.0", "end").strip()
        data[SUBJECTS] = ", ".join(self.subjectVars[i].get().strip()
                                   for i in range(self.subj_count))
        data[DATE] = ".".join(x for x in (
            self.year.get(), self.month.get(), self.day.get()) if x)
        data[PUBLICATION] = self.publ_text.get("1.0", "end").strip()
        data[AUTHOR] = self.author_text.get("1.0", "end").strip()
        if self.page_begin > 0:
            data[PAGEBEGIN] = self.page_begin
            data[PAGEEND] = self.page_end
        data[KEYWORDS] = self.keywords_text.get("1.0", "end").strip()
        data[NOTE] = self.note.text.get("1.0", "end").strip()
        if self.state == sNEW:
            data[LASTOPEN] = strftime("%Y.%m.%d %H:%M")

        try:
            if self.state == sNEW:
                insertArticle(data)
                mb.showinfo(
                    f"Обновление базы - {APPNAME}", "Статья успешно записана в базу!")
                self.clear()
            elif self.state == sUPDATE:
                updateArticle(self.id, data)
                mb.showinfo(
                    f"Обновление базы - {APPNAME}", "Статья успешно обновлена!")
                self.fname_lab["text"] = "<сохранен в базе>"
        except Exception as ex:
            mb.showerror(RUNTIME_ERROR, str(ex))
            try:
                os.remove(newpath)
            except Exception as ex:
                mb.showerror(RUNTIME_ERROR,
                             "Невозможно удалить только что загруженный файл статьи.\n  " + str(ex))

    def saveButClick(self):
        self.page_begin = 0
        self.page_end = 0
        if self.verificate():
            self.articleCreate()

    def removeButClick(self):
        if askokcancel(f"Подтверждение операции - {APPNAME}",
                       "Вы уверены, что хотите удалить статью из базы?"):
            try:
                removeArticle(self.id)
            except Exception as ex:
                mb.showerror(RUNTIME_ERROR, str(ex))
                return

            self.addMenuClick()
            try:
                os.remove(self.oldfilepath)
            except Exception as ex:
                mb.showerror(
                    RUNTIME_ERROR, "Невозможно удалить файл статьи.\n  " + str(ex))

    def __init__(self, master):
        super().__init__(master)

        self.pack()
        self.configure(background="CadetBlue1")
        ttk.Style().theme_use("clam")
        ttk.Style().configure('TCombobox', fieldbackground="PaleTurquoise1")

        try:
            self.image = PhotoImage(file=IMG3)
        except Exception as ex:
            self.image = None
            mb.showwarning(f"Ограничение интерфейса - {APPNAME}",
                           f"Картинка '{IMG3}' не отображается.\n  " + str(ex))
            self.focus_force()

        try:
            self.small_image = PhotoImage(file=IMG1, height=100)
        except Exception as ex:
            self.small_image = None
            mb.showwarning(f"Ограничение интерфейса - {APPNAME}",
                           f"Картинка '{IMG1}' не отображается.\n  " + str(ex))
            self.focus_force()

        f11 = Font(family="Helvetica", size=11)
        f12i = Font(family="Helvetica", size=12, slant=ITALIC)

        labopt = {"font": f11, "background": "CadetBlue1"}
        entropt = {"background": "PaleTurquoise1", "highlightthickness": 2,
                   "highlightbackground": "CadetBlue1", "highlightcolor": "gold", "font": f12i}
        textopt = {**entropt, "wrap": "word", "undo": "true"}

        self.state = sNEW
        self.id = None  # = getLastId() + 1
        self.subjectVars = [StringVar(), StringVar(), StringVar()]
        self.subj_count = 1
        self.subjects = []
        self.filepath = ""

        self.year = StringVar()
        self.month = StringVar()
        self.day = StringVar()

        self.columnconfigure(1, minsize=115)
        self.columnconfigure(2, minsize=115)
        self.columnconfigure(3, minsize=105)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(6, weight=2, minsize=150)
        # self.rowconfigure(0, weight=1)
        self.rowconfigure(9, minsize=65)
        self.rowconfigure(10, weight=1, minsize=105)

        self.imageframe = Frame(self, bg="CadetBlue1")
        self.imageframe.grid(row=7, rowspan=3, column=4,
                             columnspan=3, sticky=SE, pady=10, padx=10)
        Label(self.imageframe, image=self.small_image).pack(side=RIGHT)
        Label(self.imageframe, image=self.small_image).pack(side=LEFT)
        Label(self.imageframe, image=self.small_image).pack(side=LEFT)
        self.imageframe.grid_remove()

        self.head_lab = Label(self, text="Заголовок:", **labopt)
        self.head_text = Text(self, width=60, height=2, **textopt)
        self.head_lab.grid(row=1, column=0, sticky=E)
        self.head_text.grid(row=1, column=1, columnspan=4,
                            sticky=EW, pady=20, padx=15)

        self.subj_labs = list()
        self.subj_combos = list()

        for i in range(3):
            self.subj_labs.append(
                Label(self, text=f"Тематика {i+1}:", **labopt))
            self.subj_combos.append(ttk.Combobox(
                self, font=f12i, textvariable=self.subjectVars[i]))
            self.subj_labs[i].grid(row=2+i, column=0, sticky=E)
            self.subj_combos[i].grid(
                row=2+i, column=1, columnspan=4, sticky=EW, pady=10, padx=15)
            if i != 0:
                self.subj_labs[i].grid_remove()
                self.subj_combos[i].grid_remove()

        self.subj_combos[0].bind(
            "<<ComboboxSelected>>", lambda ev: self.comboSelect(0, ev))
        self.subj_combos[1].bind(
            "<<ComboboxSelected>>", lambda ev: self.comboSelect(1, ev))
        self.subj_combos[2].bind(
            "<<ComboboxSelected>>", lambda ev: ev.widget.select_clear())
        self.subj_combos[0].bind(
            "<KeyRelease>", lambda ev: self.comboSelect(0))
        self.subj_combos[1].bind(
            "<KeyRelease>", lambda ev: self.comboSelect(1))

        self.but_combo_off = Button(self, text="Скрыть", command=self.butComboOffClick,
                                    background="CadetBlue2", font=f11, borderwidth=4)
        self.but_combo_add = Button(self, text="Добавить тематику", command=self.butComboAddClick,
                                    background="CadetBlue2", font=f11, borderwidth=4)
        self.but_combo_add.grid(
            row=3, column=0, columnspan=5, sticky=EW, padx=15)

        self.publ_lab = Label(self, text="Публикация в:", **labopt)
        self.publ_text = Text(self, width=60, height=2, **textopt)
        self.publ_lab.grid(row=5, column=0, sticky=E)
        self.publ_text.grid(row=5, column=1, columnspan=4,
                            sticky=EW, pady=20, padx=15)

        self.author_lab = Label(self, text="Авторы:", **labopt)
        self.author_text = Text(self, width=60, height=2, **textopt)
        self.author_lab.grid(row=6, column=0, sticky=E)
        self.author_text.grid(row=6, column=1, columnspan=4,
                              sticky=EW, pady=20, padx=15)

        self.date_lab = Label(self, text="Дата публикации:", **labopt)
        self.year_combo = ttk.Combobox(self, font=f12i, textvariable=self.year, state="readonly",
                                       values=list(range(2000, 2031))+[""], width=5)
        self.month_combo = ttk.Combobox(self, font=f12i, textvariable=self.month, state="readonly",
                                        values=list(f"{i:02}" for i in range(1, 13))+[""], width=3)
        self.day_combo = ttk.Combobox(self, font=f12i, textvariable=self.day, state="readonly",
                                      values=list(f"{i:02}" for i in range(1, 32))+[""], width=3)
        self.year_lab = Label(self, text="Год", **labopt)
        self.month_lab = Label(self, text="Месяц", **labopt)
        self.day_lab = Label(self, text="День", **labopt)

        self.date_lab.grid(row=7, column=0, sticky=E)
        self.year_lab.grid(row=7, column=1, sticky=E)
        self.month_lab.grid(row=7, column=2, sticky=E)
        self.day_lab.grid(row=7, column=3, sticky=E)
        self.year_combo.grid(row=7, column=1, sticky=W, pady=20, padx=15)
        self.month_combo.grid(row=7, column=2, sticky=W, pady=20, padx=15)
        self.day_combo.grid(row=7, column=3, sticky=W, pady=20, padx=15)

        self.year_combo.bind("<<ComboboxSelected>>",
                             lambda ev: ev.widget.select_clear())
        self.month_combo.bind("<<ComboboxSelected>>",
                              lambda ev: ev.widget.select_clear())
        self.day_combo.bind("<<ComboboxSelected>>",
                            lambda ev: ev.widget.select_clear())

        self.file_lab = Label(self, text="Файл:", **labopt)
        self.file_frame = Frame(self, bg="CadetBlue1")
        self.fname_lab = Label(self, text="<не выбран>", **labopt)
        self.file_frame.but = Button(self.file_frame, font=f11, text="Указать файл", borderwidth=4,
                                     background="CadetBlue2", padx=10, command=self.fileButClick)
        self.file_frame.show_but = Button(self.file_frame, font=f11, text="Просмотр", borderwidth=4,
                                          background="CadetBlue2", padx=10,
                                          command=lambda: utils.openFile(self.filepath, self.file_exten))
        self.file_frame.page_lab = Label(
            self.file_frame, text="   Номера страниц:", **labopt)
        self.file_frame.entry = Entry(self.file_frame, width=10, **entropt)

        self.file_lab.grid(row=8, rowspan=2, column=0, sticky=NE, pady=10)
        self.fname_lab.grid(row=8, column=1, columnspan=6,
                            sticky=W, padx=15, pady=10)
        self.file_frame.grid(row=9, column=1, columnspan=6, sticky=NW, padx=15)
        self.file_frame.but.pack(side=LEFT)
        self.file_frame.page_lab.pack(side=LEFT)
        self.file_frame.entry.pack(side=LEFT)

        self.keywords_lab = Label(
            self, text="Ключевые\nслова и фразы\nчерез запятую:", **labopt)
        self.keywords_text = Text(self, width=60, height=5, **textopt)
        self.keywords_lab2 = Label(self, background="CadetBlue1",
                                   text=("Для лучшего поиска слова стоит вводить в " +
                                         "именительном падеже в единственном числе."))
        self.keywords_lab.grid(row=10, column=0, sticky=E)
        self.keywords_text.grid(
            row=10, column=1, columnspan=6, sticky=NSEW, padx=15)
        self.keywords_lab2.grid(
            row=11, column=1, columnspan=6, sticky=W, padx=15)

        self.note = Frame(self, bg="CadetBlue1", relief=RIDGE, borderwidth=6)
        self.note.lab = Label(self.note, text="Заметки", **labopt)
        self.note.text = Text(self.note, width=40, height=10, **textopt)
        self.note.lab.pack(fill=X)
        self.note.text.pack(fill=BOTH, expand=True)
        self.note.grid(column=6, row=0, rowspan=8, sticky=NSEW, pady=20)

        self.butframe = Frame(self, bg="CadetBlue1")
        self.butframe.save_but = Button(self.butframe, font=f11, text="Загрузить в базу",
                                        borderwidth=8, pady=5, background="SeaGreen1", padx=10, command=self.saveButClick)
        self.butframe.clear_but = Button(self.butframe, font=f11, text="Очистить все поля", borderwidth=8, pady=5,
                                         background="tan1", padx=10, command=self.clearButClick)
        self.butframe.remove_but = Button(self.butframe, font=f11, text="Удалить статью",
                                          borderwidth=8, pady=5, background="tomato", padx=10, command=self.removeButClick)
        self.butframe.save_but.pack(side=LEFT, padx=80)
        self.butframe.clear_but.pack(side=LEFT, padx=80)
        self.butframe.remove_but.pack(side=LEFT, padx=80)
        self.butframe.grid(column=0, columnspan=7, row=12, sticky=S, pady=20)

        self.head_text.bind("<B3-ButtonRelease>", self.master.contextMenu)
        self.head_text.bind("<Control-KeyPress>", self.master.controlRelease)
        self.publ_text.bind("<B3-ButtonRelease>", self.master.contextMenu)
        self.publ_text.bind("<Control-KeyPress>", self.master.controlRelease)
        self.author_text.bind("<B3-ButtonRelease>", self.master.contextMenu)
        self.author_text.bind("<Control-KeyPress>", self.master.controlRelease)
        self.keywords_text.bind("<B3-ButtonRelease>", self.master.contextMenu)
        self.keywords_text.bind("<Control-KeyPress>",
                                self.master.controlRelease)
        self.note.text.bind("<B3-ButtonRelease>", self.master.contextMenu)
        self.note.text.bind("<Control-KeyPress>", self.master.controlRelease)
        self.note.text.bind("<FocusIn>", self.deleteImage)
