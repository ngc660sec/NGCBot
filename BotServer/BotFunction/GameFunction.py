import Config.ConfigServer as Cs
from threading import Thread
from ApiServer.gameServer import *


class GameFunction:
    def __init__(self, wcf):
        """
        游戏方法 触发游戏
        :param wcf:
        """
        self.wcf = wcf
        configData = Cs.returnConfigData()
        self.Gs = GameServer(self.wcf)

    def mainHandle(self, message):
        msgType = message.type
        if msgType == 1:
            # 看图猜成语游戏
            Thread(target=self.Gs.iG.mainHandle, args=(message,)).start()
            # 成语接龙游戏
            Thread(target=self.Gs.iSG.mainHandle, args=(message, )).start()
