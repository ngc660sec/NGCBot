from BotServer.BotFunction.InterfaceFunction import *
from BotServer.BotFunction.JudgeFuncion import *
from DbServer.DbMainServer import DbMainServer
import Config.ConfigServer as Cs


class AdminFunction:
    def __init__(self, wcf):
        """
        管理功能
        :param wcf:
        """
        self.wcf = wcf
        self.Dms = DbMainServer()
        configData = Cs.returnConfigData()
        self.addBlackRoomKeyWords = configData['adminFunctionWord']['addBlackRoomWord']
        self.delBlackRoomKeyWords = configData['adminFunctionWord']['delBlackRoomWord']
        self.addWhiteRoomKeyWords = configData['adminFunctionWord']['addWhiteRoomWord']
        self.delWhiteRoomKeyWords = configData['adminFunctionWord']['delWhiteRoomWord']
        self.addPushRoomKeyWords = configData['adminFunctionWord']['addPushRoomWord']
        self.delPushRoomKeyWords = configData['adminFunctionWord']['delPushRoomWord']
        self.addBlackGhKeyWords = configData['adminFunctionWord']['addBlackGhWord']
        self.delBlackGhKeyWords = configData['adminFunctionWord']['delBlackGhWord']
        self.delUserKeyWords = configData['adminFunctionWord']['delUserWord']
        self.addPointKeyWords = configData['pointConfig']['addPointWord']
        self.delPointKeyWords = configData['pointConfig']['delPointWord']

    def mainHandle(self, message):
        content = message.content.strip()
        sender = message.sender
        roomId = message.roomid
        msgType = message.type
        roomName = getIdName(self.wcf, roomId)
        senderName = self.wcf.get_alias_in_chatroom(sender, roomId)
        atUserLists, noAtMsg = getAtData(self.wcf, message)
        if msgType == 1:
            # 增加积分
            if judgeSplitAllEqualWord(noAtMsg, self.addPointKeyWords):
                if atUserLists:
                    point = noAtMsg.split(' ')[-1]
                    for atUser in atUserLists:
                        if self.Dms.addPoint(atUser, roomId, point):
                            self.wcf.send_text(
                                f'@{self.wcf.get_alias_in_chatroom(atUser, roomId)}\n 基于你的表现, 管理员施舍了你 {point} 分',
                                receiver=roomId, aters=atUser)
                        else:
                            self.wcf.send_text(
                                f'@{senderName}\n {self.wcf.get_alias_in_chatroom(atUser, roomId)} 用户积分添加失败, 请查看日志',
                                receiver=roomId, aters=sender)
            # 扣除积分
            elif judgeSplitAllEqualWord(noAtMsg, self.delPointKeyWords):
                if atUserLists:
                    point = noAtMsg.split(' ')[-1]
                    for atUser in atUserLists:
                        if self.Dms.reducePoint(atUser, roomId, point):
                            self.wcf.send_text(
                                f'@{self.wcf.get_alias_in_chatroom(atUser, roomId)}\n 基于你的表现, 管理员扣除了你 {point} 分',
                                receiver=roomId, aters=atUser)
                        else:
                            self.wcf.send_text(
                                f'@{senderName}\n {self.wcf.get_alias_in_chatroom(atUser, roomId)} 用户积分扣除失败, 请查看日志',
                                receiver=roomId, aters=atUser)
            # 添加白名单群聊
            elif judgeEqualListWord(content, self.addWhiteRoomKeyWords):
                if self.Dms.addWhiteRoom(roomId, roomName):
                    self.wcf.send_text(f'@{senderName} 添加白名单群聊成功 !!!', receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(f'@{senderName} 此群已在白名单中', receiver=roomId, aters=sender)
            # 移出白名单群聊
            elif judgeEqualListWord(content, self.delWhiteRoomKeyWords):
                if self.Dms.delWhiteRoom(roomId):
                    self.wcf.send_text(f'@{senderName} 移出白名单群聊成功 !!!', receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(f'@{senderName} 此群已移出白名单 !!!', receiver=roomId, aters=sender)
            # 添加黑名单群聊
            elif judgeEqualListWord(content, self.addBlackRoomKeyWords):
                if self.Dms.addBlackRoom(roomId, roomName):
                    self.wcf.send_text(f'@{senderName} 此群已拉黑 !!!', receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(f'@{senderName} 此群已在黑名单中 !!!', receiver=roomId, aters=sender)
            # 移出黑名单群聊
            elif judgeEqualListWord(content, self.delBlackRoomKeyWords):
                if self.Dms.delBlackRoom(roomId):
                    self.wcf.send_text(f'@{senderName} 移出黑名单成功 !!!', receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(f'@{senderName} 此群已移出黑名单 !!!', receiver=roomId, aters=sender)
            # 添加推送群聊
            elif judgeEqualListWord(content, self.addPushRoomKeyWords):
                if self.Dms.addPushRoom(roomId, roomName):
                    self.wcf.send_text(f'@{senderName} 开启推送服务成功 !!!', receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(f'@{senderName} 此群已开启推送服务 !!!', receiver=roomId, aters=sender)
            # 移出推送群聊
            elif judgeEqualListWord(content, self.delPushRoomKeyWords):
                if self.Dms.delPushRoom(roomId):
                    self.wcf.send_text(f'@{senderName} 此群已关闭推送服务 !!!', receiver=roomId, aters=sender)
            # 踢人
            elif judgeEqualListWord(noAtMsg, self.delUserKeyWords):
                for atWxId in atUserLists:
                    if self.wcf.del_chatroom_members(roomId, atWxId):
                        self.wcf.send_text(
                            f'@{self.wcf.get_alias_in_chatroom(atWxId, roomId)} 基于你的表现, 给你移出群聊的奖励',
                            receiver=roomId)
                    else:
                        self.wcf.send_text(
                            f'@{self.wcf.get_alias_in_chatroom(sender, roomId)} [{self.wcf.get_alias_in_chatroom(atWxId, roomId)}] 移出群聊失败',
                            receiver=roomId, aters=sender)
            # # 添加黑名单公众号 阉割
            # elif judgeEqualListWord(content, self.addBlackGhKeyWords):
            #     pass
            # # 移出黑名单公众号
            # elif judgeEqualListWord(content, self.delBlackGhKeyWords):
            #     pass

