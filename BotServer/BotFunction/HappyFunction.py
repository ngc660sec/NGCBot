from BotServer.BotFunction.InterfaceFunction import *
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
        self.emoHelpKeyWords = configData['emoConfig']['emoHelp']
        self.emoKeyWords = configData['emoConfig']['emoKeyWord']
        self.emoOneKeyWordsData = configData['emoConfig']['onePicEmo']
        self.emoTwoKeyWordsData = configData['emoConfig']['twoPicEwo']
        self.emoRandomKeyWords = configData['emoConfig']['emoRandomKeyWord']

    def mainHandle(self, message):
        content = message.content.strip()
        sender = message.sender
        roomId = message.roomid
        msgType = message.type
        atUserLists, noAtMsg = getAtData(self.wcf, message)
        senderName = self.wcf.get_alias_in_chatroom(sender, roomId)
        avatarPathList = []
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
            # 随机表情
            elif judgeEqualListWord(content, self.emoRandomKeyWords):
                avatarPathList.append(getUserPicUrl(self.wcf, sender))
                emoPath, sizeBool = self.Ams.getEmoticon(avatarPathList)
                if not emoPath:
                    return
                if sizeBool:
                    self.wcf.send_emotion(path=emoPath, receiver=roomId)
                else:
                    self.wcf.send_image(path=emoPath, receiver=roomId)
            # 表情包功能 不@制作表情
            elif not atUserLists and judgeSplitAllEqualWord(content, self.emoKeyWords):
                avatarPathList.append(getUserPicUrl(self.wcf, sender))
                emoMeme = self.emoOneKeyWordsData.get(content.split(' ')[-1])
                emoPath, sizeBool = self.Ams.getEmoticon(avatarPathList, emoMeme)
                if not emoPath:
                    return
                if sizeBool:
                    self.wcf.send_emotion(path=emoPath, receiver=roomId)
                else:
                    self.wcf.send_image(path=emoPath, receiver=roomId)
            # 表情包功能 @制作对方表情
            elif atUserLists and judgeSplitAllEqualWord(noAtMsg, self.emoKeyWords):
                for atUser in atUserLists:
                    avatarPathList.append(getUserPicUrl(self.wcf, atUser))
                    break
                emoMeme = self.emoOneKeyWordsData.get(noAtMsg.split(' ')[-1])
                emoPath, sizeBool = self.Ams.getEmoticon(avatarPathList, emoMeme)
                if not emoPath:
                    return
                if sizeBool:
                    self.wcf.send_emotion(path=emoPath, receiver=roomId)
                else:
                    self.wcf.send_image(path=emoPath, receiver=roomId)
            # 表情包功能 @对方制作双人表情
            elif atUserLists and judgeEqualListWord(noAtMsg, self.emoTwoKeyWordsData.keys()):
                avatarPathList.append(getUserPicUrl(self.wcf, sender))
                avatarPathList.append(getUserPicUrl(self.wcf, atUserLists[0]))
                emoMeme = self.emoTwoKeyWordsData.get(noAtMsg.split(' ')[-1])
                emoPath, sizeBool = self.Ams.getEmoticon(avatarPathList, emoMeme)
                if not emoPath:
                    return
                if sizeBool:
                    self.wcf.send_emotion(path=emoPath, receiver=roomId)
                else:
                    self.wcf.send_image(path=emoPath, receiver=roomId)
            # 表情菜单
            elif judgeEqualListWord(content, self.emoHelpKeyWords):
                msg = '【单人表情】使用方法: \n表情 表情选项\n@某人 表情选项\n单人表情选项如下: \n'
                for oneEmoKey in self.emoOneKeyWordsData.keys():
                    msg += oneEmoKey + '\n'
                msg += '【双人表情】使用方法: \n表情选项@某人 \n双人表情选项如下\n'
                for twoEmoKey in self.emoTwoKeyWordsData.keys():
                    msg += twoEmoKey + '\n'
                self.wcf.send_text(f'@{senderName}\n{msg}', receiver=roomId, aters=sender)
            # 帮助菜单
            elif judgeEqualListWord(content, self.helpKeyWords):
                helpMsg = '[爱心]=== NGCBot菜单 ===[爱心]\n'
                helpMsg += '【一、积分功能】\n1.1、Ai画图(@机器人 画一张xxxx)\n1.2、Ai对话(@机器人即可)\n1.3、IP溯源(溯源 ip)\n1.4、IP威胁查询(ip查询 ip)\n1.5、CMD5查询(md5查询 xxx)\n1.6、签到(签到)\n1.7、积分查询(积分查询)\n\n'
                helpMsg += '【二、娱乐功能】\n2.1、美女图片(图片)\n2.2、美女视频(视频)\n2.3、摸鱼日历(摸鱼日历)\n2.4、舔狗日记(舔我)\n2.5、早报(早报)\n2.6、晚报(晚报)\n2.6、表情列表(表情列表)\n2.7、随机表情(随机表情, 有几率报错)\n'
                helpMsg += '[爱心]=== NGCBot菜单 ===[爱心]\n'
                self.wcf.send_text(f'@{senderName}\n{helpMsg}', receiver=roomId, aters=sender)
