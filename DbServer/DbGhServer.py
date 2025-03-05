import DbServer.DbDomServer as Dds
import Config.ConfigServer as Cs
from OutPut.outPut import op


class DbGhServer:
    def __init__(self):
        pass

    def addWhiteGh(self, ghId, ghName):
        """
        添加白名单公众号
        :param ghName:
        :param ghId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnGhDbPath())
        try:
            cursor.execute('INSERT INTO whiteGh VALUES (?, ?)', (ghId, ghName))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 添加白名单公众号出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def delWhiteGh(self, ghId):
        """
        删除白名单公众号
        :param ghId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnGhDbPath())
        try:
            cursor.execute('SELECT ghId FROM whiteGh WHERE ghId=?', (ghId,))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 删除白名单公众号出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def searchWhiteGh(self, ghId):
        """
        查询白名单公众号
        :param ghId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnGhDbPath())
        try:
            cursor.execute('SELECT ghId FROM whiteGh WHERE ghId=?', (ghId,))
            result = cursor.fetchone()
            Dds.closeDb(conn, cursor)
            if result:
                return result
            else:
                return ''
        except Exception as e:
            op(f'[-]: 查询白名单公众号出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return ''

    def addBlackGh(self, ghId, ghName):
        """
        添加黑名单公众号
        :param ghName:
        :param ghId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnGhDbPath())
        try:
            cursor.execute('INSERT INTO blackGh VALUES (?, ?)', (ghId, ghName))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 添加黑名单公众号出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def delBlackGh(self, ghId):
        """
        删除黑名单公众号
        :param ghId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnGhDbPath())
        try:
            cursor.execute('SELECT ghId FROM blackGh WHERE ghId=?', (ghId,))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 删除黑名单公众号出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return False

    def searchBlackGh(self, ghId):
        """
        查询黑名单公众号
        :param ghId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnGhDbPath())
        try:
            cursor.execute('SELECT ghId FROM blackGh WHERE ghId=?', (ghId,))
            result = cursor.fetchone()
            Dds.closeDb(conn, cursor)
            if result:
                return result
            else:
                return ''
        except Exception as e:
            op(f'[-]: 查询黑名单公众号出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return ''

    def showBlackGh(self, ):
        """
        查看所有黑名单公众号
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomDbPath())
        dataDict = dict()
        try:
            cursor.execute('SELECT ghId, ghName FROM blackGh')
            result = cursor.fetchall()
            Dds.closeDb(conn, cursor)
            if result:
                for res in result:
                    dataDict[res[0]] = res[1]
            return dataDict
        except Exception as e:
            op(f'[-]: 查看黑名单公众号出现错误, 错误信息: {e}')
            Dds.closeDb(conn, cursor)
            return dataDict
