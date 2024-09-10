import DbServer.DbDomServer as Dds
import Config.ConfigServer as Cs
from OutPut.outPut import op


class DbInitServer:
    def __init__(self):
        self.userDb = Cs.returnUserDbPath()
        self.pointDb = Cs.returnPointDbPath()
        self.roomDb = Cs.returnRoomDbPath()
        self.ghDb = Cs.returnGhDbPath()

    def createTable(self, cursor, table_name, columns):
        """
        :param table_name:  要创建的表名
        :param columns:  要创建的字段名 要符合SQL语法
        :return:
        """
        try:
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
            )
            return True
        except Exception as e:
            op(f'[-]: 创建数据表出现错误, 错误信息: {e}')
            return False

    def initDb(self, ):
        # 初始化用户数据库 用户表 管理员表
        userConn, userCursor = Dds.openDb(self.userDb)
        self.createTable(userCursor, 'User', 'wxId varchar(255), wxName varchar(255)')
        self.createTable(userCursor, 'Admin', 'wxId varchar(255), roomId varchar(255)')
        Dds.closeDb(userConn, userCursor)

        # 初始化积分数据库 积分数据表 签到表
        pointConn, pointCursor = Dds.openDb(self.pointDb)
        self.createTable(pointCursor, 'Point', 'wxId varchar(255), roomId varchar(255), poInt int(32)')
        self.createTable(pointCursor, 'Sign', 'wxId varchar(255), roomId varchar(255)')
        Dds.closeDb(pointConn, pointCursor)

        # 初始化群聊数据库 黑名单群聊数据表 白名单群聊数据表 推送群聊数据表 所有群聊数据表
        roomConn, roomCursor = Dds.openDb(self.roomDb)
        self.createTable(roomCursor, 'whiteRoom', 'roomId varchar(255), roomName varchar(255)')
        self.createTable(roomCursor, 'blackRoom', 'roomId varchar(255), roomName varchar(255)')
        self.createTable(roomCursor, 'pushRoom', 'roomId varchar(255), roomName varchar(255)')
        self.createTable(roomCursor, 'Room', 'roomId varchar(255), roomName varchar(255)')
        Dds.closeDb(roomConn, roomCursor)

        # 初始化公众号数据库 白名单公众号 黑名单公众号
        ghConn, ghCursor = Dds.openDb(self.ghDb)
        self.createTable(ghCursor, 'whiteGh', 'ghId varchar(255), ghName varchar(255)')
        self.createTable(ghCursor, 'blackGh', 'ghId varchar(255), ghName varchar(255)')
        Dds.closeDb(ghConn, ghCursor)
        op(f'[+]: 数据库初始化成功！！！')


if __name__ == '__main__':
    Dis = DbInitServer()
    Dis.initDb()
