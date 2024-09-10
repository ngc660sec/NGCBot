from BotServer.BotFunction.InterfaceFunction import *
from BotServer.BotFunction.JudgeFuncion import *
from DbServer.DbMainServer import DbMainServer
import Config.ConfigServer as Cs


class AdministratorFunction:
    def __init__(self, wcf):
        self.wcf = wcf
        self.Dms = DbMainServer()
        configData = Cs.returnConfigData()
        self.addAdminKeyWords = configData['adminFunctionWord']['addAdminWord']
        self.delAdminKeyWords = configData['adminFunctionWord']['delAdminWord']

    def mainHandle(self, message):
        sender = message.sender
        roomId = message.roomid
        msgType = message.type
        atUserLists, noAtMsg = getAtData(self.wcf, message)
        if msgType == 1:
            # 添加管理员
            if judgeEqualListWord(noAtMsg, self.addAdminKeyWords):
                if atUserLists:
                    for atUser in atUserLists:
                        if self.Dms.addAdmin(atUser, roomId):
                            self.wcf.send_text(
                                f'@{self.wcf.get_alias_in_chatroom(sender, roomId)}\n管理员 [{self.wcf.get_alias_in_chatroom(atUser, roomId)}] 添加成功',
                                receiver=roomId, aters=sender)
                        else:
                            self.wcf.send_text(
                                f'@{self.wcf.get_alias_in_chatroom(sender, roomId)}\n群成员 [{self.wcf.get_alias_in_chatroom(atUser, roomId)}] 已是管理员',
                                receiver=roomId, aters=sender)
            # 删除管理员
            elif judgeEqualListWord(noAtMsg, self.delAdminKeyWords):
                if atUserLists:
                    for atUser in atUserLists:
                        if self.Dms.delAdmin(atUser, roomId):
                            self.wcf.send_text(
                                f'@{self.wcf.get_alias_in_chatroom(sender, roomId)}\n管理员 [{self.wcf.get_alias_in_chatroom(atUser, roomId)}] 删除成功',
                                receiver=roomId, aters=sender)
                        else:
                            self.wcf.send_text(
                                f'@{self.wcf.get_alias_in_chatroom(sender, roomId)}\n群成员 [{self.wcf.get_alias_in_chatroom(atUser, roomId)}] 已不是管理员',
                                receiver=roomId, aters=sender)

