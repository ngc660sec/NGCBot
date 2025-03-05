import DbServer.DbDomServer as Dds
import Config.ConfigServer as Cs
from OutPut.outPut import op


class DbPointServer:
    def __init__(self):
        pass

    def addPoint(self, wxId, roomId, point):
        """
        增加积分
        :param wxId: 微信ID
        :param roomId 群聊ID
        :param point: 积分
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnPointDbPath())
        try:
            cursor.execute(f'UPDATE Point SET point=point+{int(point)} WHERE wxId=? AND roomId=?', (wxId, roomId))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 查询积分出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def reducePoint(self, wxId, roomId, point):
        """
        扣除积分
        :param wxId: 微信ID
        :param roomId 群聊ID
        :param point:积分
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnPointDbPath())
        try:
            cursor.execute(f'UPDATE Point SET point=point-{int(point)} WHERE wxId=? AND roomId=?', (wxId, roomId))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 扣除积分出现错误,  错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def searchPointUser(self, wxId, roomId):
        """
        查询用户是否在积分数据库
        :param wxId:
        :param roomId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnPointDbPath())
        try:
            cursor.execute('SELECT wxId FROM Point WHERE wxId=? AND roomId=?', (wxId, roomId))
            result = cursor.fetchone()
            Dds.closeDb(conn, cursor)
            if result:
                return result[0]
            else:
                return False
        except Exception as e:
            op(f'[-]: 查询积分出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def searchUserPoint(self, wxId, roomId):
        """
        查询积分
        :param wxId: 微信ID
        :param roomId 群聊ID
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnPointDbPath())
        try:
            cursor.execute('SELECT poInt FROM Point WHERE wxId=? AND roomId=?', (wxId, roomId))
            result = cursor.fetchone()
            Dds.closeDb(conn, cursor)
            if result:
                return result[0]
            else:
                return False
        except Exception as e:
            op(f'[-]: 查询积分出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def initUserPoint(self, wxId, roomId):
        """
        初始化积分数据库用户
        :param wxId:
        :param roomId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnPointDbPath())
        try:
            cursor.execute('INSERT INTO Point VALUES (?, ?, ?)', (wxId, roomId, 0))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 初始化积分数据库用户出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False
