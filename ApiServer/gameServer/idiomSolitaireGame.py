from BotServer.BotFunction.InterfaceFunction import *
import Config.ConfigServer as Cs
from OutPut.outPut import op
import requests

"""
成语接龙游戏
"""


class idiomSolitaireGame:
    def __init__(self, wcf):
        self.wcf = wcf
        configData = Cs.returnConfigData()
        # 存储游戏状态
        self.GameSession = {}
        self.idiomKey = configData['KeyConfig']['DpConfig']['DpKey']
        self.idiomApi = configData['FunctionConfig']['GameFunctionConfig']['IdiomSolitaireConfig']['IdiomSolitaireApi']
        self.idiomStartGameKeyWord = configData['FunctionConfig']['GameFunctionConfig']['IdiomSolitaireConfig'][
            'StartGameKeyWord']
        self.idiomStopGameKeyWord = configData['FunctionConfig']['GameFunctionConfig']['IdiomSolitaireConfig'][
            'StopGameKeyWord']
        # 游戏轮数
        self.gameRound = configData['FunctionConfig']['GameFunctionConfig']['IdiomSolitaireConfig']['GameRound']
        # 添加处理锁
        self.processing = {}
        # 添加答案队列
        self.answer_queue = {}

    def checkAnswer(self, roomId, userId, answer):
        """
        检查答案
        :param roomId:
        :param userId:
        :param answer:
        :return:
        """
        # 检查是否正在处理其他回答
        if self.processing.get(roomId, False):
            return
            
        # 设置处理锁
        self.processing[roomId] = True
        
        try:
            if roomId not in self.GameSession.keys():
                return
            if self.GameSession[roomId].get('active', False) is False:
                return
            
            # 处理队列中的所有答案
            while self.answer_queue[roomId]:
                # 取出队列中第一个答案
                user_id, user_answer = self.answer_queue[roomId].pop(0)
                
                params = {
                    'AppSecret': self.idiomKey,
                    'game_id': self.GameSession[roomId]['gameId'] if self.GameSession[roomId]['gameId'] else '',
                    'idiom': user_answer,
                }
                resp = requests.get(self.idiomApi, params=params)
                jsonData = resp.json()
                statusCode = jsonData.get('code')
                if statusCode != 200:
                    op(f'[-]: 成语接龙游戏答案判断失败！')
                    continue
                
                # 找到正确答案，更新游戏状态
                self.GameSession[roomId]['round'] += 1
                self.wcf.send_text(f'@{getIdName(self.wcf, user_id, roomId)} 接龙成功！', receiver=roomId)
                if self.GameSession[roomId].get('round', 0) > self.gameRound:
                    self.wcf.send_text('成语接龙游戏已结束！', receiver=roomId)
                    self.GameSession[roomId]['active'] = False
                    return
                result = jsonData.get('result')
                idiom = result.get('next_idiom')
                self.wcf.send_text(f'第{self.GameSession[roomId]["round"]}/{self.gameRound}轮！\n成语：{idiom}\n请接龙！', receiver=roomId)
                self.GameSession[roomId]['idiom'] = idiom
                
                # 清空剩余答案队列，进入下一轮
                self.answer_queue[roomId] = []
                break
        finally:
            # 释放处理锁
            self.processing[roomId] = False

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
        # 初始化答案队列
        self.answer_queue[roomId] = []
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
        self.wcf.send_text('成语接龙游戏开始！请输入同音成语！\n如需结束游戏，请发送【结束接龙】！', receiver=roomId)
        self.wcf.send_text(f'第一轮！\n成语：{idiom}\n请接龙！', receiver=roomId)

    def stopGame(self, roomId):
        """
        结束游戏
        :param roomId:
        :return:
        """
        if roomId in self.GameSession.keys():
            self.GameSession[roomId]['active'] = False
            self.wcf.send_text('成语接龙游戏已手动停止！', receiver=roomId)

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
                # 将答案加入队列
                if roomId not in self.answer_queue:
                    self.answer_queue[roomId] = []
                self.answer_queue[roomId].append((sender, content))
                # 触发答案检查
                self.checkAnswer(roomId, sender, content)
