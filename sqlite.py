import sqlite3
import utils
import tempfile
import os.path

ID = "id"
HEADER = "header"
SUBJECTS = "subjects"
DATE = "date"
PUBLICATION = "publication"
AUTHOR = "author"
FILE = "path_to_file"
PAGEBEGIN = "page_begin_index"
PAGEEND = "page_end_index"
KEYWORDS = "keywords"
FAVORITE = "favourit"
LASTOPEN = "last_open"
NOTE = "note"

nID = 0              # в таблице и в data
nHEADER = 1          # в таблице и в data
nSUBJECTS = 2        # в таблице и в data
nDATE = 3            # в таблице и в data
nPUBLICATION = 4     # в таблице и в data
nAUTHOR = 5          # в таблице и в data
nFILE = 6            # в data
nPAGEBEGIN = 7       # в data
nPAGEEND = 8         # в data
nFAVOURITE = 9       # в data
nLASTOPEN = 10       # в data
nNOTE = 11           # в data
nFIRST_FAV_LIST = 12  # в data

dbname = "keeper.db.ky"
names = [ID, HEADER, SUBJECTS, DATE, PUBLICATION, AUTHOR, FILE,
         PAGEBEGIN, PAGEEND, FAVORITE, LASTOPEN, NOTE]


def getDBname():
    return dbname


def sqliteLower(val):
    # print(val)
    return val.lower()


def updateDate(idx, time):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute(
                f"UPDATE article SET {LASTOPEN}='{time}' WHERE {ID}='{idx}'")
            conn.commit()
            conn.close()
            utils.encrypt(dbname, getDBname())
    except Exception as ex:
        raise Exception("Обновление даты последнего открытия файла статьи \
завершилось ошибкой.\n  " + str(ex))


def updateFavourite(list_id, art_id, val):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute(f"UPDATE favourite_links SET linked='{val}' " +
                      f"WHERE article_id='{art_id}' AND list_id={list_id}")
            conn.commit()
            conn.close()
            utils.encrypt(dbname, getDBname())
    except Exception as ex:
        raise Exception(
            "Изменение списка избранного завершилось ошибкой.\n  " + str(ex))


def updateNote(idx, note):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute(f"UPDATE article SET {NOTE}='{note}' WHERE {ID}='{idx}'")
            conn.commit()
            conn.close()
            utils.encrypt(dbname, getDBname())
    except Exception as ex:
        raise Exception(
            "Обновление заметки завершилось ошибкой.\n  " + str(ex))


def getSubjects():
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute("SELECT subject FROM subject")
            subjects = list(row[0] for row in c.fetchall())
            conn.close()
        return subjects
    except Exception as ex:
        raise Exception(
            "Получение списка тематик завершилось ошибкой.\n  " + str(ex))


def select(ord_col="id", opt="ASC", words=[], subject=""):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))

            conn = sqlite3.connect(dbname)
            conn.create_function("LOWER", 1, sqliteLower)

            c = conn.cursor()
            select = "SELECT article.id, " + ', '.join(names[1:])
            for row in c.execute("SELECT id FROM favourite_lists"):
                select += (f", MAX(CASE WHEN links.list_id = '{row[0]}' " +
                           f"THEN links.linked END) AS 'fl{row[0]}'")

            from_str = ("FROM article INNER JOIN favourite_links links " +
                        "ON article.id=links.article_id")

            wherenames = [HEADER, SUBJECTS, DATE,
                          PUBLICATION, AUTHOR, KEYWORDS]
            where = ""
            if len(words) > 0:
                keys = []
                for word in words:
                    keys.append((" OR ".join(f"LOWER({column}) LIKE '%{word}%'" for
                                             column in wherenames)) + f" OR article.id LIKE '%{word}%'")
                where = "WHERE " + " AND ".join(f"({key})" for key in keys)
            if subject != "":
                if where == "":
                    where = f"WHERE {SUBJECTS} LIKE '%{subject}%'"
                else:
                    where += f" AND {SUBJECTS} LIKE '%{subject}%'"

            data = []
            for row in c.execute(f"{select} {from_str} {where} " +
                                 f"GROUP BY article.id ORDER BY article.{ord_col} {opt}"):
                data.append(list(row))

            conn.close()
        return data

    except Exception as ex:
        raise Exception("Выборка статей завершилась ошибкой.\n" + str(ex))


def selectFavourite(list_id):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute(f"SELECT article_id FROM favourite_links " +
                      f"WHERE list_id={list_id} AND linked=1")
            article_ids = ', '.join(str(row[0]) for row in c.fetchall())
            where = f"WHERE article.id IN ({article_ids})"

            select = "SELECT article.id, " + ', '.join(names[1:])
            for row in c.execute("SELECT id FROM favourite_lists"):
                select += (f", MAX(CASE WHEN links.list_id = '{row[0]}' " +
                           f"THEN links.linked END) AS 'fl{row[0]}'")

            from_str = ("FROM article INNER JOIN favourite_links links " +
                        "ON article.id=links.article_id")

            data = []
            for row in c.execute(f"{select} {from_str} {where} GROUP BY article.id"):
                data.append(list(row))
            conn.close()
        return data
    except Exception as ex:
        raise Exception(
            "Получение статей списка избранных завершилось ошибкой.\n  " + str(ex))


def selectLasts():
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            select = "SELECT article.id, " + ", ".join(names[1:])
            for row in c.execute("SELECT id FROM favourite_lists"):
                select += (f", MAX(CASE WHEN links.list_id = '{row[0]}' " +
                           f"THEN links.linked END) AS 'fl{row[0]}'")

            from_str = ("FROM article INNER JOIN favourite_links links " +
                        "ON article.id=links.article_id")

            data = []
            for row in c.execute(f"{select} {from_str} GROUP BY article.id " +
                                 f"ORDER BY {LASTOPEN} DESC"):
                data.append(list(row))
            conn.close()
        return data
    except Exception as ex:
        raise Exception("Получение списка последних просмотренных статей " +
                        "завершилось ошибкой.\n  " + str(ex))


def getLastId():
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute("SELECT seq FROM sqlite_sequence WHERE name='article'")
            lastid = c.fetchone()[0]
            conn.close()
        return lastid
    except Exception as ex:
        raise Exception(
            "Получение номера последней статьи завершилось ошибкой.\n  " + str(ex))


def getKeywords(idx):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute(f"SELECT {KEYWORDS} FROM article WHERE {ID} = '{idx}'")
            keywords = c.fetchone()[0]
            conn.close()
        return keywords
    except Exception as ex:
        raise Exception(
            "Получение ключевых фраз завершилось ошибкой.\n  " + str(ex))


def insertSubject(subject):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute(f"INSERT INTO subject (subject) VALUES ('{subject}')")
            conn.commit()
            conn.close()
            utils.encrypt(dbname, getDBname())
    except Exception as ex:
        raise Exception(
            "Добавление новой тематики завершилось ошибкой.\n  " + str(ex))


def removeSubject(subject):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute(f"DELETE FROM subject WHERE subject='{subject}'")
            conn.commit()
            conn.close()
            utils.encrypt(dbname, getDBname())
    except Exception as ex:
        raise Exception("Удаление тематики завершилось ошибкой.\n  " + str(ex))


def insertArticle(data):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            names = ", ".join(data.keys())
            values = ", ".join(f"'{data[key]}'" for key in data)
            c.execute(f"INSERT INTO article ({names}) VALUES ({values})")
            art_id = c.execute(
                "SELECT seq FROM sqlite_sequence WHERE name='article'").fetchone()[0]
            links = tuple((art_id, row[0]) for row in c.execute(
                "SELECT id FROM favourite_lists"))
            c.executemany(
                "INSERT INTO favourite_links (article_id, list_id) VALUES (?, ?)", links)
            conn.commit()
            conn.close()
            utils.encrypt(dbname, getDBname())
    except Exception as ex:
        raise Exception(
            "Добавление новой статьи завершилось ошибкой.\n  " + str(ex))


def updateArticle(idx, data):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            values = ", ".join(f"{key}='{data[key]}'" for key in data)
            c.execute(f"UPDATE article SET {values} WHERE {ID}='{idx}'")
            conn.commit()
            conn.close()
            utils.encrypt(dbname, getDBname())
    except Exception as ex:
        raise Exception("Обновление статьи завершилось ошибкой.\n  " + str(ex))


def removeArticle(idx):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys=on")
            c.execute(f"DELETE FROM article WHERE {ID}='{idx}'")
            conn.commit()
            conn.close()
            utils.encrypt(dbname, getDBname())
    except Exception as ex:
        raise Exception("Удаление статьи завершилось ошибкой.\n  " + str(ex))


def getFavouriteLists():
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute("SELECT id, name FROM favourite_lists")
            lists = c.fetchall()[:]
            conn.close()
        return lists
    except Exception as ex:
        raise Exception(
            "Получение списков избранных завершилось ошибкой.\n  " + str(ex))


def newFavList(name):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute(f"INSERT INTO favourite_lists (name) VALUES ('{name}')")

            fav_list_id = c.execute(f"SELECT id FROM favourite_lists " +
                                    f"WHERE name='{name}'").fetchone()[0]
            links = list()
            for row in c.execute("SELECT id FROM article"):
                links.append((fav_list_id, row[0]))
            c.executemany(
                "INSERT INTO favourite_links (list_id, article_id) VALUES (?, ?)", links)
            conn.commit()
            conn.close()
            utils.encrypt(dbname, getDBname())
    except Exception as ex:
        raise Exception(
            "Создание нового списка избранного завершилось ошибкой.\n  " + str(ex))


def updateFavListName(idx, name):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute(
                f"UPDATE favourite_lists SET name='{name}' WHERE id='{idx}'")
            conn.commit()
            conn.close()
            utils.encrypt(dbname, getDBname())
    except Exception as ex:
        raise Exception(
            "Обновление названия списка избранных завершилось ошибкой.\n  " + str(ex))


def removeFavList(name):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys=on")
            c.execute(f"DELETE FROM favourite_lists WHERE name='{name}'")
            conn.commit()
            conn.close()
            utils.encrypt(dbname, getDBname())
    except Exception as ex:
        raise Exception(
            "Удаление списка избранного завершилось ошибкой.\n  " + str(ex))


def selectArtSubject(subject):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            dbname = utils.decrypt(
                getDBname(), os.path.join(tempdir, getDBname()))
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute(
                f"SELECT {SUBJECTS} FROM article WHERE {SUBJECTS} LIKE '%{subject}%'")
            data = c.fetchall()[:]
            conn.close()
        return data
    except Exception as ex:
        raise Exception(
            "Поиск статей по тематике завершился ошибкой.\n  " + str(ex))
