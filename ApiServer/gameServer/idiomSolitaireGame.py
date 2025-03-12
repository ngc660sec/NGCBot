from BotServer.BotFunction.InterfaceFunction import *
import Config.ConfigServer as Cs
from OutPut.outPut import op
from threading import Timer
import requests
import time

"""
成语接龙游戏 没写完
"""


class idiomGame:
    def __init__(self, wcf):
        self.wcf = wcf
        configData = Cs.returnConfigData()
        # 存储游戏状态
        self.GameSession = {}
        # 添加答案处理锁
        self.answerLock = {}
        # 添加定时器存储
        self.timerDict = {}
        self.idiomKey = configData['KeyConfig']['DpConfig']['DpKey']
        self.idiomApi = configData['FunctionConfig']['GameFunctionConfig']['IdiomSolitaireConfig']['IdiomSolitaireApi']
        self.idiomStartGameKeyWord = configData['FunctionConfig']['IdiomSolitaireConfig']['IdiomGameConfig'][
            'StartGameKeyWord']
        self.idiomStopGameKeyWord = configData['FunctionConfig']['IdiomSolitaireConfig']['IdiomGameConfig'][
            'StopGameKeyWord']
        # 游戏轮数
        self.gameRound = configData['FunctionConfig']['GameFunctionConfig']['IdiomSolitaireConfig']['GameRound']

    def startGame(self, roomId):
        """
        开始游戏
        :param roomId:
        :return:
        """
        if roomId not in self.GameSession.keys():
            self.GameSession[roomId] = {
                'active': True,
                'round': 1,  # 游戏轮数
            }
        else:
            self.GameSession[roomId]['active'] = True
            self.GameSession[roomId]['round'] = 1
        params = {
            'AppSecret': self.idiomKey,
            'start': True,
            'mode': 'pinyin'
        }
        resp = requests.get(self.idiomApi, params=params)
        jsonData = resp.json()
        statusCode = jsonData.get('code')
        if statusCode != 200:
            op(f'[-]: 成语接龙游戏启动失败！')
            self.wcf.send_text("游戏启动失败，请稍后再试！", receiver=roomId)
            return
        result = jsonData.get('result')
        gameId = result.get('game_id')
        idiom = result.get('first_idiom')
        self.GameSession[roomId]['gameId'] = gameId
        self.GameSession[roomId]['idiom'] = idiom
        self.wcf.send_text('成语接龙游戏开始！请输入同音成语！', receiver=roomId)
        self.wcf.send_text(f'第一轮！\n成语：{idiom}\n请接龙！')

    def stopGame(self, roomId):
        """
        结束游戏
        :param roomId:
        :return:
        """
        if roomId in self.GameSession.keys():
            self.GameSession[roomId]['active'] = False
            self.wcf.send_text('成语接龙游戏已手动停止！', receiver=roomId)

    def checkAnswer(self, roomId, sender, answer):
        """
        检查答案
        :param roomId:
        :param sender:
        :param answer:
        :return:
        """
        if roomId not in self.GameSession.keys():
            return
        if self.GameSession[roomId].get('active', False) is False:
            return

    def mainHandle(self, message):
        """
        游戏主逻辑处理
        :param message: 消息对象
        :return:
        """
        content = message.content.strip()
        sender = message.sender
        roomId = message.roomid

        # 处理开始游戏命令
        if content == self.idiomStartGameKeyWord:
            self.startGame(roomId)
            return

        # 处理结束游戏命令
        if content == self.idiomStopGameKeyWord:
            self.stopGame(roomId)
            return

        # 判断是否为成语（四个汉字）
        if len(content) == 4 and all('\u4e00' <= char <= '\u9fff' for char in content):
            # 处理答案判断
            if roomId in self.GameSession and self.GameSession[roomId].get('active', False):
                self.checkAnswer(roomId, sender, content)
