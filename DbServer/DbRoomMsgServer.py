import DbServer.DbDomServer as Dds
import Config.ConfigServer as Cs
from OutPut.outPut import op


class DbRoomMsgServer:
    def __init__(self):
        pass

    def searchRoomTable(self, tableName):
        """
        查询群聊数据表
        :param tableName: 表名, 就是群聊ID
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomMsgDbPath())
        try:
            cursor.execute('SELECT name FROM sqlite_master WHERE type=? AND name=?', ('table', tableName))
            result = cursor.fetchone()
            Dds.closeDb(conn, cursor)
            if result:
                return True
            return False
        except Exception as e:
            op(f'[-]: 查询群聊数据表出现错误, 错误信息: {e}')
            return False

    def addRoomTable(self, tableName):
        """
        增加群聊数据表
        :param tableName: 表名，就是群聊ID
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomMsgDbPath())
        try:
            Dds.createTable(cursor, tableName,
                            "msgTime TEXT DEFAULT (DATE('now')), msgType INT, wxId TEXT, wxName TEXT, msgId TEXT, "
                            "content TEXT")

            return True
        except Exception as e:
            op(f'[-]: 增加群聊数据表出现错误, 错误信息: {e}')
            return False

    def addRoomContent(self, tableName, msgType, wxId, wxName, msgId, Content):
        """
        增加群聊对话内容
        :param tableName:
        :param msgType:
        :param wxId:
        :param wxName:
        :param msgId:
        :param Content:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomMsgDbPath())
        try:
            conn.execute(f'INSERT INTO `{tableName}` (msgType, wxId, wxName, msgId, content) VALUES (?, ?, ?, ?, ?)',
                         (msgType, wxId, wxName, msgId, Content))
            conn.commit()
            Dds.closeDb(conn, cursor)
            return True
        except Exception as e:
            op(f'[-]: 增加群聊对话内容出现错误, 错误信息: {e}')
            return False

    def showRoomContent(self, tableName):
        """
        查看当日群聊所有对话内容
        :param tableName:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomMsgDbPath())
        try:
            result = ''
            cursor.execute(f"SELECT wxId, wxName, Content FROM `{tableName}` WHERE DATE(msgTime) = DATE('now')")
            data = cursor.fetchall()
            for lineMsg in data:
                result += f'{lineMsg[0]},{lineMsg[1]},{lineMsg[2]}\n'
            return result.strip()
        except Exception as e:
            op(f'[-]: 查看当日群聊所有对话内容出现错误, 错误信息: {e}')
            return None

    def showRoomCount(self, tableName):
        """
        查看当日群聊聊天总数和人数
        :param tableName:
        :return: 返回发言总数和发言人数
        """
        conn, cursor = Dds.openDb(Cs.returnRoomMsgDbPath())
        try:
            cursor.execute(f"SELECT COUNT(*) AS total_count, COUNT(DISTINCT wxId) AS user_count FROM `{tableName}` WHERE DATE(msgTime) = DATE('now')")
            result = cursor.fetchone()
            if result:
                return result[0], result[1]
            return None, None
        except Exception as e:
            op(f'[-]: 查查看当日群聊聊天总数和人数出现错误, 错误信息: {e}')
            return None, None

    def searchRoomContent(self, tableName, msgId):
        """
        查找群聊某一对话内容, 根据MsdId查找
        :param tableName:
        :param msgId:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomMsgDbPath())
        try:
            cursor.execute(f'SELECT msgType, wxId, wxName, content FROM `{tableName}` WHERE msgId=?', (msgId,))
            data = cursor.fetchone()
            if data:
                return data
            return None
        except Exception as e:
            op(f'[-]: 查询群聊对话内容出现错误, 错误信息: {e}')
            return None

    def roomMsgRanking(self, tableName):
        """
        当日群聊消息排行榜
        :param tableName:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomMsgDbPath())
        try:
            cursor.execute(
                f"SELECT wxId, wxName, COUNT(*) AS message_count FROM `{tableName}` WHERE DATE(msgTime) = DATE('now') GROUP BY wxId ORDER BY message_count DESC LIMIT 10")
            data = cursor.fetchall()
            return data
        except Exception as e:
            op(f'[-]: 生成当日群聊消息排行榜出现错误, 错误信息: {e}')
            return None

    def roomMsgRowingList(self, tableName):
        """
        群聊划水榜（所有消息）
        :param tableName:
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomMsgDbPath())
        try:
            cursor.execute(
                f"SELECT wxId, wxName, COUNT(*) AS message_count FROM `{tableName}` GROUP BY wxId ORDER BY message_count ASC LIMIT 10")
            data = cursor.fetchall()
            return data
        except Exception as e:
            op(f'[-]: 生成群聊划水榜（所有消息）出现错误, 错误信息: {e}')
            return None

    def roomMsgTypeRanking(self, tableName):
        """
        当日群聊消息类型排行榜
        :param tableName:
        :return: ((消息类型, 总条数), (消息类型2, 总条数))
        """
        conn, cursor = Dds.openDb(Cs.returnRoomMsgDbPath())
        try:
            cursor.execute(
                f"SELECT msgType, COUNT(*) AS type_count FROM `{tableName}` WHERE DATE(msgTime) = DATE('now') GROUP BY msgType ORDER BY type_count DESC")
            data = cursor.fetchall()
            if data:
                return data
            return None
        except Exception as e:
            op(f'[-]: 生成当日群聊消息类型排行榜出现错误, 错误信息: {e}')
            return None

    def clearRoomMsgTableData(self, ):
        """
        清除群聊消息所有表的数据
        :return:
        """
        conn, cursor = Dds.openDb(Cs.returnRoomMsgDbPath())
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            for table in tables:
                tableName = table[0]
                cursor.execute(f'DELETE FROM `{tableName}`')
                conn.commit()
            return True
        except Exception as e:
            op(f'[-]: 清除群聊消息所有表数据出现错误, 错误信息: {e}')
            conn.rollback()  # 回滚事务
            return False

if __name__ == '__main__':
    Rms = DbRoomMsgServer()
    Rms.addRoomTable('123456@chatroom')
    # Rms.addRoomContent('123456@chatroom', 1, '123456', 'test', '123456', '123456内容2')
    # Rms.addRoomContent('123456@chatroom', 1, '33333', 'test3', '33333', '33333内容')
    print(Rms.showRoomContent('123456@chatroom'))
    # print(Rms.searchRoomContent('123456@chatroom', '11111'))
    # print(Rms.roomMsgRanking('123456@chatroom'))
    # print(Rms.showRoomCount('123456@chatroom'))
    # print(Rms.roomMsgTypeRanking('123456@chatroom'))
    # print(Rms.RoomMsgRowingList('123456@chatroom'))
