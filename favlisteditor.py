
from tkinter import *
from tkinter.messagebox import showinfo, showerror
from tkinter.messagebox import askokcancel
import sqlite as sql
from utils import APPNAME, RUNTIME_ERROR


# TODO задать ограничени по колличеству списков < 10
class Favlisteditor(Toplevel):

    def isValid(self, string):  # TODO найти нужную функцию для поиска символов
        if self.mode == "new":
            if len(string) == 0:
                self.but.config(state="disabled", bg="SystemButtonFace")
            else:
                self.but.config(state="normal", bg="pale green")
        else:
            if string == self.fav_list_name:
                self.save_but.config(state="disabled", bg="SystemButtonFace")
            else:
                self.save_but.config(state="normal", bg="pale green")

        return len(string) <= 30 \
            and not any(ch in string for ch in r"!@#$%^&*()+=|\'/?.,:;~`{}[]")
        # TODO выдавать предупреждение что достигнута максимальная длина имени

    def create(self):
        try:
            name = self.entry.get().strip()
            sql.newFavList(name)
            showinfo(f"Создание нового списка избранных - {APPNAME}",
                     f'Список избранных "{name}" успешно создан!', parent=self)
            self.master.loadFavList(True)
            self.destroy()
        except Exception as ex:
            showerror(RUNTIME_ERROR, str(ex), parent=self)

    def edit(self):
        try:
            name = self.entry.get().strip()
            sql.updateFavListName(self.master.getFavListID(), name)
            showinfo(f"Изменение списка избранных - {APPNAME}",
                     f'Список избранных "{name}" успешно переименован!', parent=self)
            self.master.loadFavList()
            self.destroy()
        except Exception as ex:
            showerror(RUNTIME_ERROR, str(ex), parent=self)

    def remove(self):
        if not askokcancel(f"Подтверждение операции - {APPNAME}", (f'Вы действительно хотите ' +
                           f'удалить список избранных "{self.fav_list_name}"'), parent=self):
            return
        try:
            sql.removeFavList(self.fav_list_name)
            showinfo(f"Изменение списка избранных - {APPNAME}",
                     f'Список избранных "{self.fav_list_name}" был успешно удален!', parent=self)
            self.master.loadFavList(True)
            self.destroy()
        except Exception as ex:
            showerror(RUNTIME_ERROR, str(ex), parent=self)

    def __init__(self, master, mode):  # mode = {new, edit}
        super().__init__(master)

        self.mode = mode
        self.grab_set()
        self.transient(self.master)

        self.lab = Label(self, text="    Название списка:",
                         font=("Helvetica", 12))
        self.entry = Entry(self, width=50, validate="key",
                           font=self.master.f12i)
        self.lab.grid(row=1, column=0, pady=20, sticky=E)
        self.entry.grid(row=1, column=1, padx=20, pady=20)

        if mode == "new":
            self.title(f"Новый список избранных - {APPNAME}")
            self.but = Button(self, text="Создать", font=("Helvetica", 12), borderwidth=7,
                              padx=20, state="disabled", command=self.create)
            self.but.grid(row=2, column=0, columnspan=2, pady=10)
        elif mode == "edit":
            self.title(f"Изменение списка избранных - {APPNAME}")
            lab0 = Label(self, text="    Текущее название списка:",
                         font=("Helvetica", 12))
            entry0 = Entry(self, width=50, font=self.master.f12i)
            self.lab["text"] = "    Новое название списка:"

            self.fav_list_name = self.master.getFavListName()
            self.entry.insert("0", self.fav_list_name)
            entry0.insert("0", self.fav_list_name)
            entry0["state"] = "readonly"

            lab0.grid(row=0, column=0, pady=10)
            entry0.grid(row=0, column=1, padx=20, pady=10)
            self.save_but = Button(self, text="Переименовать", font=("Helvetica", 12), padx=20,
                                   borderwidth=7, state="disabled", command=self.edit)
            self.del_but = Button(self, text="Удалить", font=("Helvetica", 12), borderwidth=7,
                                  padx=20, bg="salmon", command=self.remove)
            self.save_but.grid(row=2, column=0, columnspan=2,
                               pady=10, padx=100, sticky="W")
            self.del_but.grid(row=2, column=0, columnspan=2,
                              pady=10, padx=100, sticky="E")
        else:
            self.master.master.destroy()

        self.entry["validatecommand"] = (self.register(self.isValid), "%P")
        self.resizable(False, False)
        self.update()
        self.geometry("{width}x{height}+{x}+{y}".format(width=self.winfo_width(),
                                                        height=self.winfo_height(),
                                                        x=self.master.winfo_rootx()+300,
                                                        y=self.master.winfo_rooty()+150))
