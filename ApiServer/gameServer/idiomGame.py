from BotServer.BotFunction.InterfaceFunction import *
import FileCache.FileCacheServer as Fcs
import Config.ConfigServer as Cs
from OutPut.outPut import op
from threading import Timer
import requests
import time

"""
看图猜成语
"""


class idiomGame:
    def __init__(self, wcf):
        self.wcf = wcf
        configData = Cs.returnConfigData()
        # 存储游戏状态
        self.GameSession = {}
        self.idiomKey = configData['KeyConfig']['DpConfig']['DpKey']
        self.idiomApi = configData['FunctionConfig']['GameFunctionConfig']['IdiomGameConfig']['IdiomApi']
        self.idiomStartGameKeyWord = configData['FunctionConfig']['GameFunctionConfig']['IdiomGameConfig'][
            'StartGameKeyWord']
        self.idiomStopGameKeyWord = configData['FunctionConfig']['GameFunctionConfig']['IdiomGameConfig'][
            'StopGameKeyWord']
        # 添加答案处理锁
        self.answerLock = {}
        # 添加定时器存储
        self.timerDict = {}
        # 游戏轮数
        self.gameRound = configData['FunctionConfig']['GameFunctionConfig']['IdiomGameConfig']['GameRound']

    def downloadFile(self, url, savePath):
        """
        通用下载文件函数
        :param url:
        :param savePath:
        :return:
        """
        try:
            content = requests.get(url, timeout=30, verify=True).content
            if len(content) < 200:
                return None
            with open(savePath, mode='wb') as f:
                f.write(content)
            return savePath
        except Exception as e:
            op(f'[-]: 通用下载文件函数出现错误, 错误信息: {e}')
            return None

    def clearTimer(self, roomId):
        """
        清理定时器
        :param roomId: 群聊ID
        """
        if roomId in self.timerDict and self.timerDict[roomId]:
            self.timerDict[roomId].cancel()
            self.timerDict[roomId] = None

    def getGameData(self, roomId):
        """
        获取或更新游戏数据
        :param roomId:
        :return:
        """
        try:
            resp = requests.get(self.idiomApi.format(self.idiomKey), timeout=30)
            jsonData = resp.json()
            result = jsonData.get('result')
            savePath = f'{Fcs.returnPicCacheFolder()}/{int(time.time() * 1000)}.jpg'
            imgPath = self.downloadFile(result.get('imglink'), savePath)
            if result:
                # 重置游戏数据，包括时间
                self.GameSession[roomId] = {
                    'chengyu': result.get('chengyu'),
                    'pingyin': result.get('pingyin'),
                    'jieshi': result.get('jieshi'),
                    'chuchu': result.get('chuchu'),
                    'lizi': result.get('lizi'),
                    'imglink': imgPath,
                    'errorNumber': 0,
                    'time': time.time(),  # 每次获取新数据时重置时间
                    'active': True,
                    'round': 1
                }
                # 初始化答案锁
                self.answerLock[roomId] = False
                return True
            return False
        except Exception as e:
            op(f'[-]: 获取成语游戏数据出现错误, 错误信息: {e}')
            return False

    def checkAnswer(self, roomId, userId, answer):
        """
        检查答案
        :param roomId: 群聊ID
        :param userId: 用户ID
        :param answer: 答案
        """
        if not (roomId in self.GameSession and self.GameSession[roomId].get('active', False)):
            return

        # 检查答案锁
        if self.answerLock.get(roomId, False):
            return

        session = self.GameSession[roomId]
        if answer == session['chengyu']:
            # 设置答案锁
            self.answerLock[roomId] = True
            # 清理当前定时器
            self.clearTimer(roomId)
            used_time = round(time.time() - session['time'], 2)
            self.wcf.send_text(f"@{getIdName(self.wcf, userId, roomId)} 恭喜你答对了！\n"
                               f"成语：{answer}\n"
                               f"用时：{used_time}秒", receiver=roomId)
            self.nextRound(roomId)
        else:
            session['errorNumber'] += 1
            if session['errorNumber'] == 3:
                # 获取成语的第一个和最后一个字
                chengyu = session['chengyu']
                hint = f"{chengyu[0]} ? ? {chengyu[-1]}"
                self.wcf.send_text(f"@{getIdName(self.wcf, userId, roomId)} 答案不正确，这是一个提示：{hint}",
                                   receiver=roomId)

            if session['errorNumber'] >= 10:
                # 设置答案锁
                self.answerLock[roomId] = True
                # 清理当前定时器
                self.clearTimer(roomId)
                self.wcf.send_text(f"错误次数达到10次！正确答案是：{session['chengyu']}\n"
                                   f"拼音：{session['pingyin']}\n"
                                   f"释义：{session['jieshi']}\n"
                                   f"出处：{session['chuchu']}\n"
                                   f"例子：{session['lizi']}", receiver=roomId)
                self.nextRound(roomId)

    def timeOut(self, roomId):
        """
        超时处理
        :param roomId: 群聊ID
        """
        if roomId in self.GameSession and self.GameSession[roomId].get('active', False):
            # 检查答案锁
            if self.answerLock.get(roomId, False):
                return

            # 设置答案锁
            self.answerLock[roomId] = True
            session = self.GameSession[roomId]
            self.wcf.send_text(f"时间到！正确答案是：{session['chengyu']}\n"
                               f"拼音：{session['pingyin']}\n"
                               f"释义：{session['jieshi']}\n"
                               f"出处：{session['chuchu']}\n"
                               f"例子：{session['lizi']}", receiver=roomId)
            self.nextRound(roomId)

    def startGame(self, roomId, content):
        """
        开始游戏
        :param roomId: 群聊ID
        :param content: 消息内容
        :return:
        """
        if content == self.idiomStartGameKeyWord:
            # 检查是否有游戏在进行
            if roomId in self.GameSession and self.GameSession[roomId].get('active', False):
                self.wcf.send_text("当前群已有游戏在进行中！", receiver=roomId)
                return

            # 清理可能存在的旧定时器
            self.clearTimer(roomId)

            # 获取游戏数据
            if self.getGameData(roomId):
                session = self.GameSession[roomId]
                # 发送图片和提示
                self.wcf.send_text(f"第{session['round']}/{self.gameRound}轮游戏开始！", receiver=roomId)
                self.wcf.send_image(session['imglink'], receiver=roomId)
                self.wcf.send_text(
                    f"请根据图片猜测成语，发送答案即可~\n(60秒内未答对或错误次数达到10次将公布答案)\n(如要结束游戏，请输入: {self.idiomStopGameKeyWord})",
                    receiver=roomId)

                # 设置新定时器
                self.timerDict[roomId] = Timer(60, self.timeOut, args=(roomId,))
                self.timerDict[roomId].start()
            else:
                self.wcf.send_text("游戏启动失败，请稍后再试！", receiver=roomId)

    def nextRound(self, roomId):
        """
        进入下一轮
        :param roomId: 群聊ID
        """
        if roomId in self.GameSession:
            currentRound = self.GameSession[roomId]['round'] + 1

            if currentRound > self.gameRound:
                # 清理定时器
                self.clearTimer(roomId)
                self.wcf.send_text("游戏结束！感谢参与！", receiver=roomId)
                self.GameSession[roomId]['active'] = False
            else:
                # 清理旧定时器
                self.clearTimer(roomId)

                if self.getGameData(roomId):
                    self.GameSession[roomId]['round'] = currentRound
                    self.GameSession[roomId]['time'] = time.time()
                    session = self.GameSession[roomId]
                    self.wcf.send_text(f"第{session['round']}/{self.gameRound}轮游戏开始！", receiver=roomId)
                    self.wcf.send_image(session['imglink'], receiver=roomId)
                    self.wcf.send_text("请根据图片猜测成语，发送答案即可~\n(60秒内未答对或错误次数达到10次将公布答案)",
                                       receiver=roomId)
                    # 设置新定时器
                    self.timerDict[roomId] = Timer(60, self.timeOut, args=(roomId,))
                    self.timerDict[roomId].start()
                else:
                    self.wcf.send_text("游戏启动失败，请稍后再试！", receiver=roomId)
                    return

    def stopGame(self, roomId, content):
        """
        手动停止游戏
        :param roomId: 群聊ID
        :param content: 消息内容
        """
        if content == self.idiomStopGameKeyWord:
            if roomId in self.GameSession and self.GameSession[roomId].get('active', False):
                # 清理定时器
                self.clearTimer(roomId)
                session = self.GameSession[roomId]
                self.wcf.send_text(f"游戏已手动停止！当前答案是：{session['chengyu']}", receiver=roomId)
                self.GameSession[roomId]['active'] = False
            else:
                self.wcf.send_text("当前群没有进行中的游戏！", receiver=roomId)

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
            self.startGame(roomId, content)
            return

        # 处理结束游戏命令
        if content == self.idiomStopGameKeyWord:
            self.stopGame(roomId, content)
            return

        # 判断是否为成语（四个汉字）
        if len(content) == 4 and all('\u4e00' <= char <= '\u9fff' for char in content):
            # 处理答案判断
            if roomId in self.GameSession and self.GameSession[roomId].get('active', False):
                self.checkAnswer(roomId, sender, content)
