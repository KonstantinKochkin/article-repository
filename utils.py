from textwrap import wrap
import subprocess
import os.path
import os
import tkinter.filedialog as fd
import tkinter.messagebox as mb
from Crypto.Cipher import AES
import uuid
import distutils.file_util as fu

APPNAME = "Хранитель статей"
RUNTIME_ERROR = "Ошибка выполнения - " + APPNAME
IMG1 = os.path.join("images", "katyusha_xs.png")
IMG2 = os.path.join("images", "katyusha_s.png")
IMG3 = os.path.join("images", "katyusha_m.png")

pdf_application = str()
doc_application = str()
key = str()
tempdirname = str()


def setKey(newkey):
    global key
    key = newkey


def setTempdirname(dname):
    global tempdirname
    tempdirname = dname


def resetAll():
    global pdf_application
    global doc_application
    pdf_application = ""
    doc_application = ""


def setPdfReader():
    global pdf_application
    new_pdf_application = fd.askopenfilename(
        filetypes=[("Приложения (exe)", "*.exe")],
        title="Выбор программы для открытия файлов формата pdf",
        initialdir=os.path.normpath("C:\\Program Files (x86)"))
    if new_pdf_application:
        pdf_application = new_pdf_application
        return True
    return False


def setDocReader():
    global doc_application
    new_doc_application = fd.askopenfilename(
        filetypes=[("Приложения (exe)", "*.exe")],
        title="Выбор программы для открытия файлов формата docx и doc",
        initialdir=os.path.normpath("C:\\Program Files"))
    if new_doc_application:
        doc_application = new_doc_application
        return True
    return False


# Расширение .ky добавится только если его еще нет
def encrypt(filename, newfilename=None):
    global key
    try:
        with open(filename, "rb") as inp:
            cipher_aes = AES.new(key, AES.MODE_EAX)
            ciphertext, tag = cipher_aes.encrypt_and_digest(inp.read())

            if not newfilename:
                newfilename = filename
            if os.path.splitext(newfilename)[1] != ".ky":
                newfilename += ".ky"

            with open(newfilename, "wb") as out:
                out.write(cipher_aes.nonce)
                out.write(tag)
                out.write(ciphertext)
        return newfilename
    except Exception as ex:
        raise Exception("Невозможно зашифровать файл.\n  " + str(ex))


# если расширение filename не .ky файл просто копируется
# если расширение newfilename .ky - оно убирается
def decrypt(filename, newfilename=None):
    try:
        if newfilename and os.path.splitext(newfilename)[1] == ".ky":
            newfilename = os.path.splitext(newfilename)[0]

        if os.path.splitext(filename)[1] != ".ky":
            if not newfilename:
                return filename
            else:
                fu.copy_file(filename, newfilename)

        global key
        with open(filename, "rb") as inp:
            nonce = inp.read(16)
            tag = inp.read(16)
            cipher_aes = AES.new(key, AES.MODE_EAX, nonce)

            if not newfilename:
                newfilename = os.path.splitext(filename)[0]

            with open(newfilename, "wb") as out:
                out.write(cipher_aes.decrypt_and_verify(inp.read(), tag))
        return newfilename
    except Exception as ex:
        raise Exception("Невозможно расшифровать файл.\n  " + str(ex))


def openFile(filename, real_exten=None):
    try:
        if os.path.isabs(filename):
            filepath = filename
        else:
            filepath = os.path.join(os.getcwd(), "resurces", filename)

        if not os.path.exists(filepath):
            raise Exception(f'Файл "{filepath}" не существует!')

        extension = os.path.splitext(filepath)[1]

        if extension == ".ky":
            extension = real_exten
            tempfilename = str(uuid.uuid4()) + real_exten
            tempfilepath = os.path.join(tempdirname, tempfilename)
            filepath = decrypt(filepath, tempfilepath)

        if (extension == ".doc" or extension == ".docx") and doc_application:
            subprocess.Popen([doc_application, filepath])
        elif extension == ".pdf" and pdf_application:
            subprocess.Popen([pdf_application, filepath])
        else:
            try:
                os.startfile(filepath)
            except FileNotFoundError as ex:
                raise Exception(
                    f'Файл "{filepath}" не существует!\n' + str(ex))
            except:  # TODO если не сопоставлен формат файла приложению
                if extension == ".doc" or extension == ".docx":
                    if setDocReader():
                        subprocess.Popen([doc_application, filepath])
                elif extension == ".pdf":
                    if setPdfReader():
                        subprocess.Popen([pdf_application, filepath])
    except Exception as ex:
        mb.showerror(RUNTIME_ERROR, "Невозможно открыть файл.\n  " + str(ex))


def wrapText(text, width, width_char):
    try:
        wrapped_text = '\n'.join(wrap(text, width // width_char))
    except (TypeError, AttributeError):
        wrapped_text = text
    return wrapped_text


def checkText(text: str):
    return not ("'" in text)


class CheckFail(Exception):
    pass


def check(conditional: bool, widget, message: str):
    if not conditional:
        widget.focus_set()
        mb.showwarning(
            f"Проверка данных - {APPNAME}", message, parent=widget.master)
        raise CheckFail


def checkpass(password):
    if len(password) < 16:
        return False

    try:
        key = bytes(password[:16], "utf-8")

        iv = key[9:25]
        cipher_aes = AES.new(key, AES.MODE_EAX, iv)
        ciphertext = cipher_aes.encrypt(bytes(password*3, "utf-8"))

        if ciphertext == (
            b'\xbe\x82\xf9\x1a\x17\xda\x90z\xeb\xf97.\xdb\xe1\xf9(\xa0\xd7w\x85X\xa9\x01' +
            b'\x95\xfd\xb0aTl\t\x02K\xccN:V+z\xb1y\xafC\x7f{\x03\xe3' +
            b'\x9f\xb8}\xd8Hr.\xefB@\xce\x1ay\xbc\x98\xaf\xcd\xecO\x16\x1d\xac\x0c' +
            b'sf\xe4\x15\xce\xc4?\xca\xf2#\xc4\x0fDqN\x19^ztAu\x9f\xe4' +
            b"\x04\xef\xab'\xd9\x8f\x8aF\x8f/\x97\xea\xf4\x99\xaa\xddw\x9f\xc53X\xd7"
        ):
            setKey(key)
            return True
    except Exception as ex:
        mb.showerror(RUNTIME_ERROR, "Авторизация невозможна.\n  " + str(ex))
    return False
