from ApiServer.gameServer.idiomGame import idiomGame

"""
需要传wcf到此处的接口
"""

class GameServer:
    def __init__(self, wcf):
        """
        游戏服务初始化
        :param wcf: wcf对象
        """
        self.wcf = wcf
        self.iG = idiomGame(wcf)