import sqlite3


def openDb(dbPath, ):
    conn = sqlite3.connect(database=dbPath, )
    cursor = conn.cursor()
    return conn, cursor


def closeDb(conn, cursor):
    cursor.close()
    conn.close()