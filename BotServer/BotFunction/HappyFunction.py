from ApiServer.ApiMainServer import ApiMainServer
from BotServer.BotFunction.JudgeFuncion import *
import Config.ConfigServer as Cs


class HappyFunction:
    def __init__(self, wcf):
        self.wcf = wcf
        self.Ams = ApiMainServer()
        configData = Cs.returnConfigData()
        self.picKeyWords = configData['functionKeyWord']['picWord']
        self.videoKeyWords = configData['functionKeyWord']['videoWord']
        self.fishKeyWords = configData['functionKeyWord']['fishWord']
        self.kfcKeyWords = configData['functionKeyWord']['kfcWord']
        self.dogKeyWords = configData['functionKeyWord']['dogWord']
        self.morningPageKeyWords = configData['functionKeyWord']['morningPageWord']
        self.eveningPageKeyWords = configData['functionKeyWord']['eveningPageWord']
        self.helpKeyWords = configData['functionKeyWord']['helpMenu']

    def mainHandle(self, message):
        content = message.content.strip()
        sender = message.sender
        roomId = message.roomid
        msgType = message.type
        senderName = self.wcf.get_alias_in_chatroom(sender, roomId)
        if msgType == 1:
            # 美女图片
            if judgeEqualListWord(content, self.picKeyWords):
                picPath = self.Ams.getGirlPic()
                if not picPath:
                    self.wcf.send_text(
                        f'@{senderName} 美女图片接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_image(picPath, receiver=roomId)
            # 美女视频
            elif judgeEqualListWord(content, self.videoKeyWords):
                videoPath = self.Ams.getGirlVideo()
                if not videoPath:
                    self.wcf.send_text(
                        f'@{senderName} 美女视频接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_file(videoPath, receiver=roomId)

            # 摸鱼日历
            elif judgeEqualListWord(content, self.fishKeyWords):
                fishPath = self.Ams.getFish()
                if not fishPath:
                    self.wcf.send_text(
                        f'@{senderName} 摸鱼日历接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_file(fishPath, receiver=roomId)

            # 疯狂星期四
            elif judgeEqualListWord(content, self.kfcKeyWords):
                kfcText = self.Ams.getKfc()
                if not kfcText:
                    self.wcf.send_text(
                        f'@{senderName} KFC疯狂星期四接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(
                    f'@{senderName} {kfcText}',
                    receiver=roomId, aters=sender)

            # 舔狗日记
            elif judgeEqualListWord(content, self.dogKeyWords):
                dogText = self.Ams.getDog()
                if not dogText:
                    self.wcf.send_text(
                        f'@{senderName} 舔狗日记接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(
                    f'@{senderName} {dogText}',
                    receiver=roomId, aters=sender)
            # 早报
            elif judgeEqualListWord(content, self.morningPageKeyWords):
                morningPage = self.Ams.getMorningNews()
                if not morningPage:
                    self.wcf.send_text(
                        f'@{senderName} 早报接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(morningPage, receiver=roomId)
            # 晚报
            elif judgeEqualListWord(content, self.eveningPageKeyWords):
                eveningPage = self.Ams.getEveningNews()
                if not eveningPage:
                    self.wcf.send_text(
                        f'@{senderName} 晚报接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(eveningPage, receiver=roomId)
            # 帮助菜单
            elif judgeEqualListWord(content, self.helpKeyWords):
                helpMsg = '[爱心]=== NGCBot菜单 ===[爱心]\n'
                helpMsg += '【一、积分功能】\n1.1、Ai画图(@机器人 画一张xxxx)\n1.2、Ai对话(@机器人即可)\n1.3、IP溯源(溯源 ip)\n1.4、IP威胁查询(ip查询 ip)\n1.5、CMD5查询(cmd5查询 xxx)\n1.6、签到(签到)\n1.7、积分查询(积分查询)\n\n'
                helpMsg += '【二、娱乐功能】\n2.1、美女图片(图片)\n2.2、美女视频(视频)\n2.3、摸鱼日历(摸鱼日历)\n2.4、舔狗日记(舔我)\n2.5、早报(早报)\n2.6、晚报(晚报)\n'
                helpMsg += '[爱心]=== NGCBot菜单 ===[爱心]\n'
                self.wcf.send_text(f'@{senderName}\n{helpMsg}', receiver=roomId, aters=sender)
