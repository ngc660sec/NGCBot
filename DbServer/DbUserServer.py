import DbServer.DbDomServer as Dds
import Config.ConfigServer as Cs
from OutPut.outPut import op


class DbUserServer:
    def __init__(self):
        pass

    def addAdmin(self, wxId, roomId):
        """
        增加管理员
        :param wxId: 微信ID
        :param roomId: 群聊ID
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnUserDbPath())
        try:
            cursor.execute('INSERT INTO Admin VALUES (?, ?)', (wxId, roomId))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 增加管理员出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def delAdmin(self, wxId, roomId):
        """
        删除管理员
        :param wxId: 微信ID
        :param roomId: 群聊ID
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnUserDbPath())
        try:
            cursor.execute('DELETE FROM Admin WHERE wxId=? AND roomId=?', (wxId, roomId))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 删除管理员出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def searchAdmin(self, wxId, roomId):
        """
        查询管理员
        :param wxId: 微信ID
        :param roomId: 群聊ID
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnUserDbPath())
        try:
            cursor.execute('SELECT wxId FROM Admin WHERE wxId=? AND roomId=?', (wxId, roomId))
            result = cursor.fetchone()
            Dds.closeDb(conn, cursor)
            if result:
                return True
            else:
                return False
        except Exception as e:
            op(f'[-]: 查询管理员出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False
