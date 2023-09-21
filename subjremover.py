from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo, showwarning, showerror
import sqlite as sql
from utils import APPNAME, RUNTIME_ERROR


# TODO при получении фокуса окном сбрасывать выбранную тематику
class Subjremover(Toplevel):

    def select(self, ev):
        self.count = 0
        try:
            for articles in sql.selectArtSubject(subject=self.subjectVar.get()):
                if self.subjectVar.get() in articles[0].split(", "):
                    self.count += 1
            if self.count == 0:
                self.lab["text"] = "Cтатей с выбранной тематикой не найдено."
                self.but.configure(bg="pale green")
            else:
                last1 = 'а' if self.count % 10 == 1 else 'о'
                last2 = 'ья' if self.count % 10 == 1 else 'ьи' if 1 < self.count % 10 < 5 else 'ей'
                self.lab["text"] = f"Найден{last1} {self.count} стат{last2} с выбранной тематикой."
                self.but.configure(bg="salmon")
            self.but.configure(state="normal")
        except Exception as ex:
            showerror(RUNTIME_ERROR, str(ex))

    def butClick(self):
        if self.count == 0:
            try:
                sql.removeSubject(self.subjectVar.get())
                self.destroy()
                showinfo(
                    f"Результат операции - {APPNAME}", "Тематика успешно удалена!")
            except Exception as ex:
                showerror(RUNTIME_ERROR, str(ex))
        else:
            showwarning(f"Результат операции - {APPNAME}", parent=self,
                        message=("Тематика не может быть удалена!\nУдалите все статьи, " +
                                 "относящиеся к выбранной тематике или открепите тематику от всех статей."))

    def __init__(self, master):
        super().__init__(master)

        self.title(f"Удаление тематики - {APPNAME}")
        lab = Label(self, text="Выберите тематику для удаления",
                    font=("Helvetica", 12))
        lab.pack(padx=20, pady=10, anchor=W)

        self.subjectVar = StringVar()
        combo = ttk.Combobox(self, values=sql.getSubjects(), textvariable=self.subjectVar,
                             width=60, font=("Helvetica", 13), state="readonly")
        self.option_add('*TCombobox*Listbox.font', ("Helvetica", 13))
        combo.pack(fill=Y, padx=20)
        combo.bind("<<ComboboxSelected>>", self.select)

        self.lab = Label(self, font=("Helvetica", 12))
        self.lab.pack(padx=20, pady=20, anchor=W)

        self.but = Button(self, font=("Helvetica", 12), text="Удалить тематику", state="disable",
                          borderwidth=8, padx=10, pady=3, command=self.butClick)
        self.but.pack(pady=5)

        self.resizable(False, False)
        self.update()
        self.geometry("{width}x{height}+{x}+{y}".format(width=self.winfo_width(),
                                                        height=self.winfo_height(),
                                                        x=self.master.winfo_rootx()+300,
                                                        y=self.master.winfo_rooty()+150))
