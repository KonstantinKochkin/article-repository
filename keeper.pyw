from tkinter import *
from tkinter import ttk
from tkinter.font import *
from tkinter.messagebox import showwarning, showerror, askyesnocancel
import tempfile
import os
import psutil
import time

import utils
from utils import APPNAME, RUNTIME_ERROR
import sqlite as sql
from findframe import Findframe
from addframe import Addframe
from subjremover import Subjremover
from favlisteditor import Favlisteditor


def fixed_map(option):
    return [elm for elm in ttk.Style().map('Treeview', query_opt=option)
            if elm[:2] != ('!disabled', '!selected')]


class Keeper(Frame):

    def removerDestroy(self, ev):
        if ev.widget == self.remover:
            self.removerIsOpen = False
            self.remover.destroy()
            self.findframe.selectFindMenu()

    def removeSubject(self):
        if not self.removerIsOpen:
            self.removerIsOpen = True
            self.remover = Subjremover(self)
            self.remover.bind("<Destroy>", self.removerDestroy)
        else:
            self.remover.focus_set()

    def editAtricle(self):
        try:
            self.findframe.pack_info()
        except TclError:
            showwarning("Изменение статьи", ('Статья не выбрана!\n' +
                                             'Для выбора статьи нажмите на раздел меню "Выбор статей"' +
                                             ', выберите одну из предложенных групп и укажите статью.')  )
            return
        table = self.findframe.table
        if table.focus_row == -1:
            showwarning("Изменение статьи",
                        'Статья не выбрана!\nВыберите статью из таблицы.')
        else:
            self.addframe.updateArticle(table.data[table.focus_row])

    # Контекстное меню
    def contextMenu(self, ev, backcall=None):
        self.event = ev
        self.backcall = backcall
        try:    # копирование и вырезание
            ev.widget.selection_get()
            self.context_menu.entryconfig(0, state="normal")
            self.context_menu.entryconfig(2, state="normal")
        except TclError:
            self.context_menu.entryconfig(0, state="disabled")
            self.context_menu.entryconfig(2, state="disabled")

        try:    # вставка
            self.clipboard_get()
            self.context_menu.entryconfig(1, state="normal")
        except TclError:
            self.context_menu.entryconfig(1, state="disabled")

        # выделить все
        if len(self.event.widget.get("1.0", "end")) > 1:
            self.context_menu.entryconfig(3, state="normal")
        else:
            self.context_menu.entryconfig(3, state="disabled")

        if self.event.widget.edit_modified():  # undo
            self.context_menu.entryconfig(5, state="normal")
        else:
            self.context_menu.entryconfig(5, state="disabled")

        try:    # redo
            self.event.widget.edit_redo()
            self.event.widget.edit_undo()
            self.context_menu.entryconfig(6, state="normal")
        except:
            self.context_menu.entryconfig(6, state="disabled")

        self.context_menu.post(ev.x_root, ev.y_root)

    def copy(self):
        self.clipboard_clear()
        self.clipboard_append(self.event.widget.selection_get())
        if self.backcall:
            self.backcall()

    def past(self):
        try:
            self.event.widget.delete("sel.first", "sel.last")
        except:
            pass
        self.event.widget.insert("insert", self.clipboard_get())
        if self.backcall:
            self.backcall()

    def cut(self):
        self.copy()
        self.event.widget.delete("sel.first", "sel.last")
        if self.backcall:
            self.backcall()  # вызовется второй раз

    def undo(self):
        try:
            self.event.widget.edit_undo()
        except:
            pass
        if self.backcall:
            self.backcall()

    def redo(self):
        try:
            self.event.widget.edit_redo()
        except:
            pass
        if self.backcall:
            self.backcall()

    def selectAll(self):
        self.event.widget.tag_add("sel", "1.0", "end")

    def controlRelease(self, ev, backcall=None):
        self.event = ev
        self.backcall = backcall
        if ev.keycode == 65 and ev.keysym.lower() != "a":
            self.selectAll()
        if ev.keycode == 67 and ev.keysym.lower() != "c":
            try:
                self.copy()
            except:
                pass
        elif ev.keycode == 86 and ev.keysym.lower() != "v":
            try:
                self.past()
            except:
                pass
        elif ev.keycode == 88 and ev.keysym.lower() != "x":
            try:
                self.cut()
            except:
                pass
        elif ev.keycode == 90:
            if ev.state == 5:      # Shift+Ctrl
                if ev.keysym.lower() != "z":
                    self.redo()
            else:
                self.undo()      # Ctrl

    def noteWDestroy(self):
        self.noteWIsOpen = False
        if self.noteW.text.get("1.0", "end").rstrip() == self.noteW.filetext:
            self.noteW.destroy()
            return True

        answer = askyesnocancel(f"Сохранение - {APPNAME}",
                                "Вы хотите сохранить замечания и предложения?", parent=self.noteW)
        if answer == True:
            with open("note.txt", 'w') as file:
                file.write(self.noteW.text.get("1.0", "end").rstrip())
            self.noteW.destroy()
            return True

        elif answer == False:
            self.noteW.destroy()
            return True

        else:
            self.noteWIsOpen = True
            return False

    def openNote(self):
        if not self.noteWIsOpen:
            self.noteWIsOpen = True
            self.noteW = Toplevel(self)
            self.noteW.title(f"Доработать - {APPNAME}")
            lab = Label(
                self.noteW, text="Окно для замечаний и предложений", font=("Helvetica", 12))
            lab2 = Label(
                self.noteW, text="Запрос на сохранения текста будет после закрытия окна")
            self.noteW.text = Text(
                self.noteW, font=self.f12i, wrap="word", undo=True)
            try:
                with open("note.txt") as file:
                    self.noteW.filetext = file.read().rstrip()
                    self.noteW.text.insert("1.0", self.noteW.filetext)
            except:
                self.noteW.filetext = ""
            lab.pack()
            self.noteW.text.pack(fill=BOTH, expand=True)
            lab2.pack(anchor=W)

            self.noteW.text.bind("<B3-ButtonRelease>", self.contextMenu)
            self.noteW.text.bind("<Control-KeyPress>", self.controlRelease)

            self.noteW.protocol("WM_DELETE_WINDOW", self.noteWDestroy)
        else:
            self.noteW.focus_set()

    def openFavListEditor(self, mode):  # mode = {new, edit}
        # TODO запретить удаление последнего списка
        self.fav_list_editor = Favlisteditor(self, mode)

    def getFavListID(self, i=None):
        if i == None:
            i = self.cur_favor.get()
        return self.fav_lists[i][0]

    def getFavListName(self, i=None):
        if i == None:
            i = self.cur_favor.get()
        return self.fav_lists[i][1]

    def loadFavList(self, setLastFavList=False):
        for fav_list in self.fav_lists:
            self.fav_menu.delete(0)
            self.context_fav_menu.delete(0)

        try:
            self.fav_lists = sql.getFavouriteLists()
            self.contain_lists = []
            for idx, fav_list in enumerate(self.fav_lists):
                self.fav_menu.insert_radiobutton(0, label=fav_list[1], variable=self.cur_favor,
                                                 value=idx)
                self.contain_lists.append(IntVar())
                self.context_fav_menu.add_checkbutton(
                    label=fav_list[1], variable=self.contain_lists[idx], onvalue=1, offvalue=0,
                    command=lambda idx=idx: self.findframe.contextFavMenuClick(idx))
            if setLastFavList:
                self.cur_favor.set(len(self.fav_lists)-1)
        except Exception as ex:
            showerror(RUNTIME_ERROR, str(ex))

        self.findframe.selectFindMenu()

    def keaper_destroy(self):
        if self.noteWIsOpen:
            self.noteW.focus_set()
            if self.noteWDestroy():
                self.master.destroy()
        else:
            self.master.destroy()

    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill=BOTH, expand=True)

        self.master.title(APPNAME)
        self.master.minsize(900, 760)
        self.f12i = Font(family="Helvetica", size=12,
                         weight=NORMAL, slant=ITALIC)

        self.findframe = Findframe(self)
        self.addframe = Addframe(self)
        self.removerIsOpen = False
        self.noteWIsOpen = False
        self.master.protocol("WM_DELETE_WINDOW", self.keaper_destroy)

        # Меню
        self.main_menu = Menu(self)
        self.master["menu"] = self.main_menu

        # Меню выбора статей
        self.show_menu = Menu(self.main_menu, tearoff=0, font=self.f12i)
        self.show_menu.add_command(
            label="Поиск", command=self.findframe.selectFindMenu)
        self.show_menu.add_command(
            label="Последние", command=self.findframe.selectLastsMenu)
        self.main_menu.add_cascade(label="Выбор статей", menu=self.show_menu)

        # Меню избранных и контекстное меню избранных
        self.fav_lists = []
        self.cur_favor = IntVar()
        self.cur_favor.set(0)
        self.cur_favor.trace_add("write", lambda v, x,
                                 m: self.findframe.selectFavouriteMenu())

        self.fav_menu = Menu(self.show_menu, tearoff=0, font=self.f12i)
        self.context_fav_menu = Menu(self, tearoff=0)
        self.loadFavList()
        self.fav_menu.add_separator()
        self.fav_menu.add_command(label="Добавить",
                                        command=lambda: Favlisteditor(self, "new"))
        self.fav_menu.add_command(label="Изменить",
                                        command=lambda: Favlisteditor(self, "edit"))
        self.show_menu.insert_cascade(1, label="Избранное", menu=self.fav_menu)

        # Меню обновления базы
        self.update_menu = Menu(self.main_menu, tearoff=0, font=self.f12i)
        self.update_menu.add_command(label="Загрузить новую статью",
                                     command=self.addframe.addMenuClick)
        self.update_menu.add_command(
            label="Изменить выбранную статью", command=self.editAtricle)
        self.update_menu.add_command(
            label="Удалить тематику", command=self.removeSubject)
        self.main_menu.add_cascade(
            label="Обновить базу", menu=self.update_menu)

        # Меню настроек
        self.setting_menu = Menu(self.main_menu, tearoff=0, font=self.f12i)
        self.setting_menu.add_command(label="Выбрать приложение для pdf файлов",
                                      command=utils.setPdfReader)
        self.setting_menu.add_command(label="Выбрать приложение для docx файлов",
                                      command=utils.setDocReader)
        self.setting_menu.add_command(label="Сбросить настройки",
                                      command=utils.resetAll)
        self.main_menu.add_cascade(label="Настройки", menu=self.setting_menu)
        self.main_menu.add_command(label="Доработать", command=self.openNote)

        self.update()
        self.master.geometry(
            f"{self.winfo_width()}x{self.winfo_height()}+200+100")

        # Контекствное меню
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy)
        self.context_menu.add_command(label="Вставить", command=self.past)
        self.context_menu.add_command(label="Вырезать", command=self.cut)
        self.context_menu.add_command(
            label="Выделить все", command=self.selectAll)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="<=Отменить", command=self.undo)
        self.context_menu.add_command(label="=>Вернуть", command=self.redo)
        self.event = None
        self.backcall = None


def comein(pas: str, window):
    if not utils.checkpass(pas):
        showwarning(f"Ошибка входа - {APPNAME}", parent=window,
                    message="Введен неверный пароль!\nПовторите попытку.")
        return

    window.destroy()
    root = Tk()
    root.option_add('*TCombobox*Listbox.font', ("Helvetica", 13))
    ttk.Style().map('Treeview', foreground=fixed_map('foreground'),
                    background=fixed_map('background'))

    with tempfile.TemporaryDirectory() as tempdir:
        try:
            utils.setTempdirname(tempdir)
            Keeper(root)
            root.mainloop()
        except Exception as ex:
            showerror(RUNTIME_ERROR,
                      "Запуск приложения не возможен.\n  " + str(ex))
        try:
            for child in psutil.Process(os.getpid()).children():
                child.terminate()
            while len(psutil.Process(os.getpid()).children()) > 0:
                time.sleep(0.1)
        except Exception as ex:
            showerror(
                RUNTIME_ERROR, "Закрытие редакторов завершилось с ошибкой.\n  " + str(ex))


welcome_window = Tk()
welcome_window.title(f"Вход - {APPNAME}")
welcome_window.geometry("500x210+500+300")
welcome_window.lab1 = Label(welcome_window, text=f"Добро пожаловать в\n{APPNAME}!",
                            font=("Helvetica", 20, ))
welcome_window.entry = Entry(
    welcome_window, show="♪", font=("Helvetica", 11), width=40)
welcome_window.lab2 = Label(
    welcome_window, text="   Введите пароль:", font=("Helvetica", 12))
welcome_window.but = Button(welcome_window, text="Войти", borderwidth=8, pady=2, padx=50,
                            font=("Helvetica", 12),
                            command=lambda: comein(welcome_window.entry.get(), welcome_window))
welcome_window.lab1.grid(row=0, column=0, columnspan=2)
welcome_window.lab2.grid(row=1, column=0, pady=30)
welcome_window.entry.grid(row=1, column=1, padx=20, pady=20)
welcome_window.but.grid(row=2, column=0, columnspan=2, pady=5)
welcome_window.entry.bind("<Return>",
                          lambda e: comein(welcome_window.entry.get(), welcome_window))
welcome_window.entry.focus_set()
welcome_window.mainloop()
