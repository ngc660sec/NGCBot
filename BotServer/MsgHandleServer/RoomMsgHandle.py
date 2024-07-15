from BotServer.BotFunction.AdministratorFunction import AdministratorFunction
from BotServer.BotFunction.AdminFunction import AdminFunction
from BotServer.BotFunction.HappyFunction import HappyFunction
from BotServer.BotFunction.PointFunction import PointFunction
from BotServer.BotFunction.InterfaceFunction import *
from ApiServer.AiServer.AiDialogue import AiDialogue
from BotServer.BotFunction.JudgeFuncion import *
from DbServer.DbMainServer import DbMainServer
import Config.ConfigServer as Cs
from threading import Thread
import re


class RoomMsgHandle:
    def __init__(self, wcf):
        """
        超级管理员功能 所有功能+管理员操作
        管理员功能 积分功能+娱乐功能
        白名单群聊功能 积分功能免费
        黑名单群聊功能 所有功能无法使用 管理员以及超管除外
        普通群聊功能 所有功能正常使用
        :param wcf:
        """
        self.wcf = wcf
        self.Ad = AiDialogue()
        self.Dms = DbMainServer()
        self.Hf = HappyFunction(self.wcf)
        self.Pf = PointFunction(self.wcf)
        self.Af = AdminFunction(self.wcf)
        self.Asf = AdministratorFunction(self.wcf)
        configData = Cs.returnConfigData()
        self.Administrators = configData['Administrators']
        self.aiWenKeyWords = configData['functionKeyWord']['aiWenWord']
        self.aiWenPoint = configData['pointConfig']['functionPoint']['awIp']
        self.threatBookWords = configData['functionKeyWord']['threatBookWord']
        self.threatBookPoint = configData['pointConfig']['functionPoint']['wbIp']
        self.md5KeyWords = configData['functionKeyWord']['md5Words']
        self.md5Point = configData['pointConfig']['functionPoint']['md5']
        self.signKeyWord = configData['pointConfig']['sign']['word']
        self.searchPointKeyWord = configData['pointConfig']['queryPointWord']
        self.aiMsgPoint = configData['pointConfig']['functionPoint']['aiPoint']
        self.aiPicKeyWords = configData['functionKeyWord']['aiPic']
        self.aiPicPoint = configData['pointConfig']['functionPoint']['aiPicPoint']
        self.joinRoomMsg = configData['customMsg']['joinRoomMsg']
        self.joinRoomCardData = configData['customMsg']['JoinRoomCard']

    def mainHandle(self, msg):
        roomId = msg.roomid
        sender = msg.sender
        # 白名单群聊功能
        if judgeWhiteRoom(roomId):
            # 超管功能以及管理功能
            self.AdminFunction(msg)
            # 积分功能
            Thread(target=self.Pf.mainHandle, args=(msg,)).start()
            # 娱乐功能
            Thread(target=self.Hf.mainHandle, args=(msg,)).start()
        # 黑名单群聊功能
        elif judgeBlackRoom(roomId):
            # 超管功能以及管理功能
            self.AdminFunction(msg)
            # 超管和管理才能使用娱乐和积分功能
            if sender in self.Administrators or judgeAdmin(sender, roomId):
                Thread(target=self.Asf.mainHandle, args=(msg,)).start()
                Thread(target=self.Af.mainHandle, args=(msg,)).start()
        # 推送群聊功能
        elif judgePushRoom(roomId):
            # 超管功能以及管理功能
            self.AdminFunction(msg)
            # 入群欢迎
            Thread(target=self.JoinRoomWelcome, args=(msg,)).start()
            # 娱乐功能 和 积分功能
            Thread(target=self.HappyFunction, args=(msg,)).start()

        # 普通群聊功能
        else:
            # 超管功能以及管理功能
            self.AdminFunction(msg)
            # 娱乐功能 和 积分功能
            Thread(target=self.HappyFunction, args=(msg,)).start()

    def JoinRoomWelcome(self, msg):
        """
        进群欢迎
        :param msg:
        :return:
        """
        try:
            ret = 0
            content = msg.content.strip()
            wx_names = None
            if '二维码' in content:
                wx_names = re.search(r'"(?P<wx_names>.*?)"通过扫描', content)
            elif '邀请' in content:
                wx_names = re.search(r'邀请"(?P<wx_names>.*?)"加入了', content)
            if wx_names:
                wx_names = wx_names.group('wx_names')
                if '、' in wx_names:
                    wx_names = wx_names.split('、')
                else:
                    wx_names = [wx_names]
            for wx_name in wx_names:
                for roomIds, data in self.joinRoomCardData.items():
                    roomIdLists = roomIds.split(',')
                    for roomId in roomIdLists:
                        if msg.roomid == roomId:
                            name = data.get('name')
                            account = data.get('account')
                            title = data.get('title').format(wx_name)
                            digest = data.get('digest')
                            url = data.get('url')
                            thumbUrl = data.get('thumbUrl')
                            ret = self.wcf.send_rich_text(name, account, title, digest, url, thumbUrl, roomId)

                if not ret:
                    joinRoomMsg = f'@{wx_name} ' + self.joinRoomMsg.replace("\\n", "\n")
                    self.wcf.send_text(msg=joinRoomMsg, receiver=msg.roomid)
        except Exception as e:
            pass

    def HappyFunction(self, msg):
        """
        娱乐功能
        :param msg:
        :return:
        """
        # 娱乐功能
        Thread(target=self.Hf.mainHandle, args=(msg,)).start()
        # 超管和普通管理不需要积分调用积分功能
        if msg.sender in self.Administrators or judgeAdmin(msg.sender, msg.roomid):
            # 积分功能
            Thread(target=self.Pf.mainHandle, args=(msg,)).start()
        else:
            # 普通用户需要积分调用此功能
            Thread(target=self.PointFunction, args=(msg.sender, msg.roomid, msg.content.strip(), msg)).start()

    def AdminFunction(self, msg):
        """
        超级管理员以及管理员功能
        :param msg:
        :return:
        """
        # 超级管理员功能
        if msg.sender in self.Administrators:
            self.Asf.mainHandle(msg)
        # 管理员功能 超管也可以调用
        if judgeAdmin(msg.sender, msg.roomid) or msg.sender in self.Administrators:
            self.Af.mainHandle(msg)

    def PointFunction(self, sender, roomId, content, msg):
        """
        积分功能 需要积分充足使用,
        开发者必看: 如果加上积分功能 在后续的一系列调用链都要加上
        :param roomId:
        :param sender:
        :param content:
        :param msg:
        :return:
        """
        atUserLists, noAtMsg = getAtData(self.wcf, msg)
        senderPoint = self.Dms.searchPoint(sender, roomId)
        lock = 0
        pointLock = 0
        # 埃文IPV4地址查询
        if judgeSplitAllEqualWord(content, self.aiWenKeyWords):
            pointLock = 1
            if judgePointFunction(senderPoint, self.aiWenPoint):
                self.Dms.reducePoint(sender, roomId, self.aiWenPoint)
                lock = 1
        # 微步IPV4查询
        elif judgeSplitAllEqualWord(content, self.threatBookWords):
            pointLock = 1
            if judgePointFunction(senderPoint, self.threatBookPoint):
                self.Dms.reducePoint(sender, roomId, self.threatBookPoint)
                lock = 1
        # CMD5查询
        elif judgeSplitAllEqualWord(content, self.md5KeyWords):
            pointLock = 1
            if judgePointFunction(senderPoint, self.md5Point):
                self.Dms.reducePoint(sender, roomId, self.md5Point)
                lock = 1
        # Ai对话
        elif judgeAtMe(self.wcf.self_wxid, content, atUserLists) and not judgeOneEqualListWord(noAtMsg,
                                                                                               self.aiPicKeyWords):
            pointLock = 1
            if judgePointFunction(senderPoint, self.aiMsgPoint):
                self.Dms.reducePoint(sender, roomId, self.aiMsgPoint)
                lock = 1
        # Ai画图
        elif judgeAtMe(self.wcf.self_wxid, content, atUserLists) and judgeOneEqualListWord(noAtMsg, self.aiPicKeyWords):
            pointLock = 1
            if judgePointFunction(senderPoint, self.aiPicPoint):
                self.Dms.reducePoint(sender, roomId, self.aiPicPoint)
                lock = 1
        # 签到
        elif judgeEqualWord(content, self.signKeyWord):
            pointLock = 1
            lock = 1
        # 签到口令提示
        elif judgeEqualWord(content, '签到'):
            pointLock = 1
            lock = 1
        # 查询积分
        elif judgeEqualListWord(content, self.searchPointKeyWord):
            pointLock = 1
            lock = 1
        if lock:
            Thread(target=self.Pf.mainHandle, args=(msg,)).start()
        else:
            if pointLock:
                self.wcf.send_text(
                    f'@{self.wcf.get_alias_in_chatroom(sender, roomId)} 积分不足, 请签到或祈求管理员施舍 ~~~',
                    receiver=roomId, aters=sender)
