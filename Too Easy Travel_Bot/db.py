import sqlite3


def set_table() -> None:
    """
    Создает структуру таблицы, если её нет в базе данных.
    """
    with sqlite3.connect("user_history.db") as con:
        cur = con.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS users_search (user_id INTEGER, command TEXT, "
                    "date DATETIME, result TEXT)")


def set_data(user_id: int, result: str, date: str, command: str) -> None:
    """
    Записывает в базу данных результаты поиска.
    :param user_id: пользователя чата
    :param result: текущего поиска
    :param date: дата и время поиска
    :param command: наименование текущей команды
    """
    with sqlite3.connect("user_history.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO users_search (user_id, result, date, command) VALUES (?, ?, ?, ?)",
                    (user_id, result, date, command,))


def get_history(user_id: int) -> object:
    """
    Возвращает результаты поиска одного пользователя.
    :param user_id: пользователя чата.
    :return: данные из БД.
    """
    with sqlite3.connect("user_history.db") as con:
        cur = con.cursor()
        cur.execute("SELECT date, command, result FROM  users_search WHERE user_id = ? ORDER BY date DESC LIMIT 5", (user_id,))
        result = cur.fetchall()
        return result