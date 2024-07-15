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
        self.configData = Cs.returnConfigData()

    def initUser(self, wxId, roomId, ):
        """
        初始化数据库用户
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
            signPoint = self.configData['pointConfig']['sign']['point']
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
        try:
            if self.Dss.clearSign():
                return True
            return False
        except Exception as e:
            op(f'[-]: 清除签到表出现错误, 错误信息: {e}')
            return False

    def addAdmin(self, wxId, roomId):
        """
        添加管理员
        :param wxId:
        :param roomId:
        :return:
        """
        try:
            if not self.Dus.searchAdmin(wxId, roomId):
                return self.Dus.addAdmin(wxId, roomId)
            op(f'[-]: 添加管理员出现错误, 错误信息: 当前管理员已存在')
            return False
        except Exception as e:
            op(f'[-]: 添加管理员出现错误, 错误信息: {e}')
            return False

    def delAdmin(self, wxId, roomId):
        """
        删除管理员
        :param wxId:
        :param roomId:
        :return:
        """
        try:
            return self.Dus.delAdmin(wxId, roomId)
        except Exception as e:
            op(f'[-]: 删除管理员出现错误, 错误信息: {e}')
            return False

    def searchAdmin(self, wxId, roomId):
        """
        搜索管理员
        :param wxId:
        :param roomId:
        :return:
        """
        try:
            return self.Dus.searchAdmin(wxId, roomId)
        except Exception as e:
            op(f'[-]: 搜索管理员出现错误, 错误信息: {e}')
            return False

    def addWhiteRoom(self, roomId, roomName):
        """
        添加白名单群聊
        :param roomName:
        :param roomId:
        :return:
        """
        try:
            if not self.Drs.searchWhiteRoom(roomId=roomId):
                if self.Drs.addWhiteRoom(roomId, roomName):
                    return True
            return False
        except Exception as e:
            op(f'[-]: 添加白名单群聊出现错误, 错误信息: {e}')
            return False

    def delWhiteRoom(self, roomId):
        """
        移出白名单群聊
        :param roomId:
        :return:
        """
        try:
            return self.Drs.delWhiteRoom(roomId=roomId)
        except Exception as e:
            op(f'[-]: 移出白名单群聊出现错误, 错误信息: {e}')
            return False

    def showWhiteRoom(self, ):
        """
        查看所有白名单群聊
        :return:
        """
        try:
            return self.Drs.showWhiteRoom()
        except Exception as e:
            op(f'[-]: 查看所有白名单群聊出现错误, 错误信息: {e}')
            return dict()

    def searchWhiteRoom(self, roomId):
        """
        搜索白名单群聊
        :return:
        """
        try:
            return self.Drs.searchWhiteRoom(roomId)
        except Exception as e:
            op(f'[-]: 搜索白名单群聊出现错误, 错误信息: {e}')
            return False

    def addBlackRoom(self, roomId, roomName):
        """
        添加黑名单群聊
        :param roomName:
        :param roomId:
        :return:
        """
        try:
            if not self.Drs.searchBlackRoom(roomId=roomId):
                if self.Drs.addBlackRoom(roomId, roomName):
                    return True
            return False
        except Exception as e:
            op(f'[-]: 添加黑名单群聊出现错误, 错误信息: {e}')
            return False

    def delBlackRoom(self, roomId):
        """
        移出黑名单群聊
        :param roomId:
        :return:
        """
        try:
            return self.Drs.delBlackRoom(roomId=roomId)
        except Exception as e:
            op(f'[-]: 移出黑名单群聊出现错误, 错误信息: {e}')
            return False

    def showBlackRoom(self, ):
        """
        查看所有黑名单群聊
        :return:
        """
        try:
            return self.Drs.showBlackRoom()
        except Exception as e:
            op(f'[-]: 查看所有黑名单群聊出现错误, 错误信息: {e}')
            return dict()

    def searchBlackRoom(self, roomId):
        """
        搜索黑名单群聊
        :return:
        """
        try:
            return self.Drs.searchBlackRoom(roomId)
        except Exception as e:
            op(f'[-]: 搜索黑名单群聊出现错误, 错误信息: {e}')
            return False

    def addPushRoom(self, roomId, roomName):
        """
        添加推送群聊
        :param roomName:
        :param roomId:
        :return:
        """
        try:
            if not self.Drs.searchPushRoom(roomId=roomId):
                if self.Drs.addPushRoom(roomId, roomName):
                    return True
            return False
        except Exception as e:
            op(f'[-]: 添加推送群聊出现错误, 错误信息: {e}')
            return False

    def delPushRoom(self, roomId):
        """
        移出推送群聊
        :param roomId:
        :return:
        """
        try:
            return self.Drs.delPushRoom(roomId=roomId)
        except Exception as e:
            op(f'[-]: 移出推送群聊出现错误, 错误信息: {e}')
            return False

    def showPushRoom(self, ):
        """
        查看所有推送群聊
        :return:
        """
        try:
            return self.Drs.showPushRoom()
        except Exception as e:
            op(f'[-]: 查看所有推送群聊出现错误, 错误信息: {e}')
            return dict()

    def addBlackGh(self, ghId, ghName):
        """
        添加黑名单公众号
        :return:
        """
        try:
            return self.Dgs.addBlackGh(ghId=ghId, ghName=ghName)
        except Exception as e:
            op(f'[-]: 添加黑名单公众号出现错误, 错误信息: {e}')
            return False

    def delBlackGh(self, ghId):
        """
        删除黑名单公众号
        :param ghId:
        :return:
        """
        try:
            return self.Dgs.delBlackGh(ghId, )
        except Exception as e:
            op(f'[-]: 移出黑名单公众号出现错误, 错误信息: {e}')
            return False

    def showBlackGh(self, ):
        """
        查看黑名单群聊
        :return:
        """
        try:
            return self.Dgs.showBlackGh()
        except Exception as e:
            op(f'[-]: 查看黑名单公众号出现错误, 错误信息: {e}')
            return dict()


if __name__ == '__main__':
    Ds = DbMainServer()
    # print(Ds.clearSign())
    print(Ds.searchPoint('sender', 'roomid'))