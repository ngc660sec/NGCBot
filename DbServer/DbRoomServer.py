import DbServer.DbDomServer as Dds
import Config.ConfigServer as Cs
from OutPut.outPut import op


class DbRoomServer:
    def __init__(self):
        pass

    def addWhiteRoom(self, roomId, roomName):
        """
        新增白名单群聊
        :param roomName:
        :param roomId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomDbPath())
        try:
            cursor.execute('INSERT INTO whiteRoom VALUES (?, ?)', (roomId, roomName))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 新增白名单群聊出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def delWhiteRoom(self, roomId):
        """
        删除白名单群聊
        :param roomId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomDbPath())
        try:
            cursor.execute('DELETE FROM whiteRoom WHERE roomId=?', (roomId,))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 删除白名单群聊出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def searchWhiteRoom(self, roomId):
        """
        查询白名单群聊
        :param roomId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomDbPath())
        try:
            cursor.execute('SELECT roomName FROM whiteRoom WHERE roomId=?', (roomId,))
            result = cursor.fetchone()
            Dds.closeDb(conn, cursor)
            if result:
                return True
            return False
        except Exception as e:
            op(f'[-]: 查询白名单群聊出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def showWhiteRoom(self, ):
        """
        查看所有白名单群聊
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomDbPath())
        dataDict = dict()
        try:
            cursor.execute('SELECT roomId, roomName FROM whiteRoom')
            result = cursor.fetchall()
            Dds.closeDb(conn, cursor)
            if result:
                for res in result:
                    dataDict[res[0]] = res[1]
            return dataDict
        except Exception as e:
            op(f'[-]: 查看所有白名单群聊出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return dataDict

    def addBlackRoom(self, roomId, roomName):
        """
        新增黑名单群聊
        :param roomName:
        :param roomId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomDbPath())
        try:
            cursor.execute('INSERT INTO blackRoom VALUES (?, ?)', (roomId, roomName))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 新增黑名单群聊出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def delBlackRoom(self, roomId):
        """
        删除黑名单群聊
        :param roomId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomDbPath())
        try:
            cursor.execute('DELETE FROM blackRoom WHERE roomId=?', (roomId,))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 删除黑名单群聊出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def searchBlackRoom(self, roomId):
        """
        查询黑名单群聊
        :param roomId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomDbPath())
        try:
            cursor.execute('SELECT roomName FROM blackRoom WHERE roomId=?', (roomId,))
            result = cursor.fetchone()
            Dds.closeDb(conn, cursor)
            if result:
                return result
            else:
                return False
        except Exception as e:
            op(f'[-]: 查询黑名单群聊出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def showBlackRoom(self, ):
        """
        查看所有黑名单群聊
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomDbPath())
        dataDict = dict()
        try:
            cursor.execute('SELECT roomId, roomName FROM blackRoom')
            result = cursor.fetchall()
            Dds.closeDb(conn, cursor)
            if result:
                for res in result:
                    dataDict[res[0]] = res[1]
            return dataDict
        except Exception as e:
            op(f'[-]: 查看所有黑名单群聊出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return dataDict

    def addPushRoom(self, roomId, roomName):
        """
        新增推送群聊
        :param roomName:
        :param roomId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomDbPath())
        try:
            cursor.execute('INSERT INTO pushRoom VALUES (?, ?)', (roomId, roomName))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 新增推送群聊出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def delPushRoom(self, roomId):
        """
        删除推送群聊
        :param roomId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomDbPath())
        try:
            cursor.execute('DELETE FROM pushRoom WHERE roomId=?', (roomId,))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 删除推送群聊出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def searchPushRoom(self, roomId):
        """
        查询推送群聊
        :param roomId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomDbPath())
        try:
            cursor.execute('SELECT roomName FROM pushRoom WHERE roomId=?', (roomId,))
            result = cursor.fetchone()
            Dds.closeDb(conn, cursor)
            if result:
                return result
            else:
                return False
        except Exception as e:
            op(f'[-]: 查询推送群聊出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def showPushRoom(self, ):
        """
        查看所有推送群聊
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomDbPath())
        dataDict = dict()
        try:
            cursor.execute('SELECT roomId, roomName FROM pushRoom')
            result = cursor.fetchall()
            Dds.closeDb(conn, cursor)
            if result:
                for res in result:
                    dataDict[res[0]] = res[1]
            return dataDict
        except Exception as e:
            op(f'[-]: 查看所有黑名单群聊出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return dataDict
