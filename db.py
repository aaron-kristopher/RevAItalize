from PyQt6.QtSql import QSqlDatabase


def open_connection():
    conn = QSqlDatabase.addDatabase("QSQLITE")
    conn.setDatabaseName("db.sqlite")
    return conn.open()
