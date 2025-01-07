import sqlite3
from OutPut.outPut import op


def openDb(dbPath, ):
    conn = sqlite3.connect(database=dbPath, )
    cursor = conn.cursor()
    return conn, cursor


def closeDb(conn, cursor):
    cursor.close()
    conn.close()


def createTable(cursor, table_name, columns):
    """
    :param table_name:  要创建的表名
    :param columns:  要创建的字段名 要符合SQL语法
    :return:
    """
    try:
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns})"
        )
        return True
    except Exception as e:
        op(f'[-]: 创建数据表出现错误, 错误信息: {e}')
        return False