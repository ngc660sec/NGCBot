from DbServer.DbRoomMsgServer import DbRoomMsgServer
from DbServer.DbPointServer import DbPointServer
from DbServer.DbUserServer import DbUserServer
from DbServer.DbRoomServer import DbRoomServer
from DbServer.DbSignServer import DbSignServer
from DbServer.DbInitServer import DbInitServer
from DbServer.DbGhServer import DbGhServer
import Config.ConfigServer as Cs
from OutPut.outPut import op


class DbMainServer:
    def __init__(self):
        self.Dps = DbPointServer()
        self.Dus = DbUserServer()
        self.Drs = DbRoomServer()
        self.Dss = DbSignServer()
        self.Dis = DbInitServer()
        self.Dgs = DbGhServer()
        self.Dms = DbRoomMsgServer()
        self.configData = Cs.returnConfigData()

    def searchRoomMsgTable(self, tableName):
        """
        查询群聊数据表
        :param tableName:
        :return:
        """
        return self.Dms.searchRoomTable(tableName)

    def addRoomTable(self, tableName):
        """
        增加群聊数据表
        :param tableName:
        :return:
        """
        return self.Dms.addRoomTable(tableName)

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
        if not self.Dms.searchRoomTable(tableName):
            self.Dms.addRoomTable(tableName)
        return self.Dms.addRoomContent(tableName, msgType, wxId, wxName, msgId, Content)

    def showRoomContent(self, tableName):
        """
        查看群聊所有对话内容
        :param tableName:
        :return:
        """
        return self.Dms.showRoomContent(tableName)

    def showRoomCount(self, tableName):
        """
        查看当日群聊聊天总数和人数
        :param tableName:
        :return:
        """
        return self.Dms.showRoomCount(tableName)

    def searchRoomContent(self, tableName, msgId):
        """
        查找群聊某一对话内容, 根据MsdId查找
        :param tableName:
        :param msgId:
        :return:
        """
        return self.Dms.searchRoomContent(tableName, msgId)

    def roomMsgRanking(self, tableName):
        """
        当日群聊消息排行榜
        :param tableName:
        :return:
        """
        return self.Dms.roomMsgRanking(tableName)

    def roomMsgRowingList(self, tableName):
        """
        群聊划水榜（所有消息）
        :param tableName:
        :return:
        """
        return self.Dms.roomMsgRowingList(tableName)

    def roomMsgTypeRanking(self, tableName):
        """
        当日群聊消息类型排行榜
        :param tableName:
        :return:
        """
        return self.Dms.roomMsgTypeRanking(tableName)

    def clearRoomMsgTableData(self, ):
        """
        清除群聊消息所有表的数据
        :return:
        """
        return self.Dms.clearRoomMsgTableData()

    def initUser(self, wxId, roomId, ):
        """
        初始化积分数据库用户
        :param wxId:
        :param roomId:
        :return:
        """
        # 初始化积分数据库用户
        try:
            if not self.Dps.searchPointUser(wxId=wxId, roomId=roomId):
                self.Dps.initUserPoint(wxId=wxId, roomId=roomId)
        except Exception as e:
            op(f'[-]: 初始化积分数据库用户出现错误, 错误信息: {e}')

    def addPoint(self, wxId, roomId, point):
        """
        增加用户积分
        :param wxId:
        :param roomId:
        :param point:
        :return:
        """
        try:
            self.initUser(wxId=wxId, roomId=roomId)
            if self.Dps.addPoint(wxId=wxId, roomId=roomId, point=point):
                return True
            return False
        except Exception as e:
            op(f'[-]: 增加用户积分出现错误, 错误信息: {e}')

    def reducePoint(self, wxId, roomId, point):
        """
        扣除用户积分
        :param wxId:
        :param roomId:
        :param point:
        :return:
        """
        try:
            self.initUser(wxId=wxId, roomId=roomId)
            if self.Dps.reducePoint(wxId=wxId, roomId=roomId, point=point):
                return True
            return False
        except Exception as e:
            op(f'[-]: 扣除用户积分出现错误, 错误信息: {e}')

    def searchPoint(self, wxId, roomId):
        """
        查询用户积分
        :param wxId:
        :param roomId:
        :return:
        """
        try:
            self.initUser(wxId=wxId, roomId=roomId)
            userPoint = self.Dps.searchUserPoint(wxId=wxId, roomId=roomId)
            return userPoint
        except Exception as e:
            op(f'[-]: 查询用户积分出现错误, 错误信息: {e}')
            return False

    def sign(self, wxId, roomId):
        """
        签到
        :param wxId:
        :param roomId:
        :return:
        """
        try:
            self.initUser(wxId, roomId)
            signPoint = self.configData['FunctionConfig']['PointFunctionConfig']['SignConfig']['SignPoint']
            if not self.Dss.searchSignUser(wxId=wxId, roomId=roomId):
                if self.Dss.addSignUser(wxId=wxId, roomId=roomId):
                    self.addPoint(wxId=wxId, roomId=roomId, point=signPoint)
                    return True
            return False
        except Exception as e:
            op(f'[-]: 签到功能出现错误, 错误信息: {e}')
            return False

    def clearSign(self, ):
        """
        清除签到表
        :return:
        """
        self.Dss.clearSign()

    def addAdmin(self, wxId, roomId):
        """
        添加管理员
        :param wxId:
        :param roomId:
        :return:
        """
        return self.Dus.addAdmin(wxId, roomId)

    def delAdmin(self, wxId, roomId):
        """
        删除管理员
        :param wxId:
        :param roomId:
        :return:
        """
        return self.Dus.delAdmin(wxId, roomId)

    def searchAdmin(self, wxId, roomId):
        """
        搜索管理员
        :param wxId:
        :param roomId:
        :return:
        """
        return self.Dus.searchAdmin(wxId, roomId)

    def addWhiteRoom(self, roomId, roomName):
        """
        添加白名单群聊
        :param roomName:
        :param roomId:
        :return:
        """
        self.Drs.addWhiteRoom(roomId, roomName)

    def delWhiteRoom(self, roomId):
        """
        移出白名单群聊
        :param roomId:
        :return:
        """
        return self.Drs.delWhiteRoom(roomId=roomId)

    def showWhiteRoom(self, ):
        """
        查看所有白名单群聊
        :return:
        """
        return self.Drs.showWhiteRoom()

    def searchWhiteRoom(self, roomId):
        """
        搜索白名单群聊
        :return:
        """
        return self.Drs.searchWhiteRoom(roomId)

    def addBlackRoom(self, roomId, roomName):
        """
        添加黑名单群聊
        :param roomName:
        :param roomId:
        :return:
        """
        self.Drs.addBlackRoom(roomId, roomName)

    def delBlackRoom(self, roomId):
        """
        移出黑名单群聊
        :param roomId:
        :return:
        """
        return self.Drs.delBlackRoom(roomId=roomId)

    def showBlackRoom(self, ):
        """
        查看所有黑名单群聊
        :return:
        """
        return self.Drs.showBlackRoom()

    def searchBlackRoom(self, roomId):
        """
        搜索黑名单群聊
        :return:
        """
        return self.Drs.searchBlackRoom(roomId)

    def addPushRoom(self, roomId, roomName):
        """
        添加推送群聊
        :param roomName:
        :param roomId:
        :return:
        """
        self.Drs.addPushRoom(roomId, roomName)

    def delPushRoom(self, roomId):
        """
        移出推送群聊
        :param roomId:
        :return:
        """
        return self.Drs.delPushRoom(roomId=roomId)

    def showPushRoom(self, ):
        """
        查看所有推送群聊
        :return:
        """
        return self.Drs.showPushRoom()

    def addBlackGh(self, ghId, ghName):
        """
        添加黑名单公众号
        :return:
        """
        return self.Dgs.addBlackGh(ghId=ghId, ghName=ghName)

    def delBlackGh(self, ghId):
        """
        删除黑名单公众号
        :param ghId:
        :return:
        """
        return self.Dgs.delBlackGh(ghId, )

    def showBlackGh(self, ):
        """
        查看黑名单群聊
        :return:
        """
        return self.Dgs.showBlackGh()


if __name__ == '__main__':
    Ds = DbMainServer()
    # print(Ds.clearSign())
    # print(Ds.searchPoint('sender', 'roomid'))
    print(Ds.showRoomContent('123456@chatroom'))