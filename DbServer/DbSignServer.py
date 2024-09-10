import DbServer.DbDomServer as Dds
import Config.ConfigServer as Cs
from OutPut.outPut import op


class DbSignServer:
    def __init__(self):
        """
        签到的增删
        """

    def searchSignUser(self, wxId, roomId):
        """
        查找签到人
        :param wxId: 微信ID
        :param roomId 群聊ID
        :return: True False
        """
        conn, cursor = Dds.openDb(Cs.returnPointDbPath())
        try:
            cursor.execute('SELECT wxId FROM Sign WHERE wxId=? AND roomId=?', (wxId, roomId))
            result = cursor.fetchone()
            if result:
                return True
            else:
                return False
        except Exception as e:
            op(f'[-]: 查找签到人出现错误, 错误信息: {e}')
            return False

    def addSignUser(self, wxId, roomId):
        """
        新增签到人
        :param wxId: 微信ID
        :param roomId 群聊ID
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnPointDbPath())
        try:
            cursor.execute('INSERT INTO Sign VALUES (?, ?)', (wxId, roomId))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            Dds.closeDb(conn, cursor)
            op(f'[-]: 新增签到人出现错误, 错误信息: {e}')
            return False

    def clearSign(self, ):
        """
        清除签到表
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnPointDbPath())
        try:
            cursor.execute('DELETE FROM Sign')
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            Dds.closeDb(conn, cursor)
            op(f'[-]: 清除签到表出现错误, 错误信息: {e}')
            return False
