from datetime import datetime

from BotServer.BotFunction.InterfaceFunction import *
from ApiServer.ApiMainServer import ApiMainServer
from BotServer.BotFunction.JudgeFuncion import *
import Config.ConfigServer as Cs


class HappyFunction:
    def __init__(self, wcf):
        """
        娱乐功能
        :param wcf:
        """
        self.wcf = wcf
        self.Ams = ApiMainServer()
        configData = Cs.returnConfigData()

        # 娱乐功能关键词配置
        self.picKeyWords = configData['FunctionConfig']['HappyFunctionConfig']['PicConfig']['PicKeyWords']
        self.videoKeyWords = configData['FunctionConfig']['HappyFunctionConfig']['VideoConfig']['VideoKeyWords']
        self.fishKeyWords = configData['FunctionConfig']['HappyFunctionConfig']['FishConfig']['FishKeyWords']
        self.kfcKeyWords = configData['FunctionConfig']['HappyFunctionConfig']['KfcConfig']['KfcKeyWords']
        self.dogKeyWords = configData['FunctionConfig']['HappyFunctionConfig']['DogConfig']['DogKeyWords']
        self.shortPlayWords = configData['FunctionConfig']['HappyFunctionConfig']['ShortPlayConfig'][
            'ShortPlayKeyWords']
        self.morningPageKeyWords = configData['FunctionConfig']['HappyFunctionConfig']['MorningPageConfig'][
            'MorningPageKeyWords']
        self.eveningPageKeyWords = configData['FunctionConfig']['HappyFunctionConfig']['EveningPageConfig'][
            'EveningPageKeyWords']
        self.helpKeyWords = configData['FunctionConfig']['HappyFunctionConfig']['HelpMenuConfig']['HelpMenuKeyWords']
        self.taLuoWords = configData['FunctionConfig']['HappyFunctionConfig']['TaLuoConfig']['TaLuoKeyWords']
        self.musicWords = configData['FunctionConfig']['HappyFunctionConfig']['MusicConfig']['MusicKeyWords']
        self.dyVideoAnalysisKeyWords = configData['FunctionConfig']['HappyFunctionConfig']['DyVideoAnalysisConfig']['DyVideoAnalysisKeyWords']
        self.emoHelpKeyWords = configData['EmoConfig']['EmoHelp']
        self.emoKeyWords = configData['EmoConfig']['EmoKeyWords']
        self.emoOneKeyWordsData = configData['EmoConfig']['OnePicEmo']
        self.emoTwoKeyWordsData = configData['EmoConfig']['TwoPicEwo']
        self.emoRandomKeyWords = configData['EmoConfig']['EmoRandomKeyWords']
        # 自定义回复关键词字典
        self.customKeyWords = configData['CustomConfig']

    def mainHandle(self, message):
        content = message.content.strip()
        sender = message.sender
        roomId = message.roomid
        msgType = message.type
        atUserLists, noAtMsg = getAtData(self.wcf, message)
        avatarPathList = []
        if msgType == 1:
            # 美女图片
            if judgeEqualListWord(content, self.picKeyWords):
                picPath = self.Ams.getGirlPic()
                if not picPath:
                    self.wcf.send_text(
                        f'@{getIdName(self.wcf, sender, roomId)} 美女图片接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_image(picPath, receiver=roomId)
            # 美女视频
            elif judgeEqualListWord(content, self.videoKeyWords):
                videoPath = self.Ams.getGirlVideo()
                if not videoPath:
                    self.wcf.send_text(
                        f'@{getIdName(self.wcf, sender, roomId)} 美女视频接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_file(videoPath, receiver=roomId)

            # 摸鱼日历
            elif judgeEqualListWord(content, self.fishKeyWords):
                fishPath = self.Ams.getFish()
                if not fishPath:
                    self.wcf.send_text(
                        f'@{getIdName(self.wcf, sender, roomId)} 摸鱼日历接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_image(fishPath, receiver=roomId)

            # 疯狂星期四
            elif judgeEqualListWord(content, self.kfcKeyWords):
                kfcText = self.Ams.getKfc()
                if not kfcText:
                    self.wcf.send_text(
                        f'@{getIdName(self.wcf, sender, roomId)} KFC疯狂星期四接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(
                    f'@{getIdName(self.wcf, sender, roomId)} {kfcText}',
                    receiver=roomId, aters=sender)

            # 舔狗日记
            elif judgeEqualListWord(content, self.dogKeyWords):
                dogText = self.Ams.getDog()
                if not dogText:
                    self.wcf.send_text(
                        f'@{getIdName(self.wcf, sender, roomId)} 舔狗日记接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(
                    f'@{getIdName(self.wcf, sender, roomId)} {dogText}',
                    receiver=roomId, aters=sender)
            # 早报
            elif judgeEqualListWord(content, self.morningPageKeyWords):
                morningPage = self.Ams.getMorningNews()
                if not morningPage:
                    self.wcf.send_text(
                        f'@{getIdName(self.wcf, sender, roomId)} 早报接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(morningPage, receiver=roomId)
            # 晚报
            elif judgeEqualListWord(content, self.eveningPageKeyWords):
                eveningPage = self.Ams.getEveningNews()
                if not eveningPage:
                    self.wcf.send_text(
                        f'@{getIdName(self.wcf, sender, roomId)} 晚报接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(eveningPage, receiver=roomId)
            # 短剧搜索
            elif judgeSplitAllEqualWord(content, self.shortPlayWords):
                playName = content.split(' ')[-1]
                content = self.Ams.getShortPlay(playName)
                if content:
                    self.wcf.send_text(f'@{getIdName(self.wcf, sender, roomId)}\n{content}', receiver=roomId,
                                       aters=sender)
            # 抖音视频解析
            elif judgeInListWord(content, self.dyVideoAnalysisKeyWords):
                videoPath = self.Ams.getVideoAnalysis(content)
                if videoPath:
                    self.wcf.send_file(path=videoPath, receiver=roomId)
            # 点歌
            elif judgeSplitAllEqualWord(content, self.musicWords):
                musicName = content.split(' ')[1::]
                musicHexData = self.Ams.getMusic(musicName)
                if not musicHexData:
                    self.wcf.send_text(f'@{getIdName(self.wcf, sender, roomId)} 点歌接口出现错误, 请稍后再试 ~~~',
                                       receiver=roomId, aters=sender)
                    return
                result = self.wcf.query_sql('MSG0.db', "SELECT * FROM MSG where type = 49  limit 1")
                local_id = result[0].get("localId") if result else None
                if not local_id:
                    self.wcf.send_text(f'@{getIdName(self.wcf, sender, roomId)} 点歌接口出现错误, 请稍后再试 ~~~',
                                       receiver=roomId, aters=sender)
                    return
                MsgSvrID = f"10{int(datetime.now().timestamp() * 1000)}"
                self.wcf.query_sql('MSG0.db',
                                   f"UPDATE MSG SET  CompressContent = x'{musicHexData}', MsgSvrID = {MsgSvrID} WHERE LocalID = {int(local_id)};")
                self.wcf.forward_msg(int(MsgSvrID), receiver=roomId)
            # 塔罗牌
            elif judgeEqualListWord(content, self.taLuoWords):
                content, picPath = self.Ams.getTaLuo()
                if content and picPath:
                    self.wcf.send_image(path=picPath, receiver=roomId)
                    self.wcf.send_text(f'@{getIdName(self.wcf, sender, roomId)}\n\n{content}', receiver=roomId,
                                       aters=sender)
                else:
                    self.wcf.send_text(
                        f'@{getIdName(self.wcf, sender, roomId)}\n塔罗牌占卜接口出现错误, 请联系超管查看控制台输出 ~~~',
                        receiver=roomId, aters=sender)

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
            # 自定义回复
            elif judgeEqualListWord(content, self.customKeyWords.keys()):
                for keyWord in self.customKeyWords.keys():
                    if judgeEqualWord(content, keyWord):
                        replyMsgLists = self.customKeyWords.get(keyWord)
                        for replyMsg in replyMsgLists:
                            self.wcf.send_text(replyMsg, receiver=roomId)
            # 表情菜单
            elif judgeEqualListWord(content, self.emoHelpKeyWords):
                msg = '【单人表情】使用方法: \n表情 表情选项\n@某人 表情选项\n单人表情选项如下: \n'
                for oneEmoKey in self.emoOneKeyWordsData.keys():
                    msg += oneEmoKey + '\n'
                msg += '【双人表情】使用方法: \n表情选项@某人 \n双人表情选项如下\n'
                for twoEmoKey in self.emoTwoKeyWordsData.keys():
                    msg += twoEmoKey + '\n'
                self.wcf.send_text(f'@{getIdName(self.wcf, sender, roomId)}\n{msg}', receiver=roomId, aters=sender)
            # 帮助菜单
            elif judgeEqualListWord(content, self.helpKeyWords):
                helpMsg = '[爱心]=== NGCBot菜单 ===[爱心]\n'
                helpMsg += '【一、积分功能】\n1.1、Ai画图(@机器人 画一张xxxx)\n1.2、Ai对话(@机器人即可)\n1.3、IP溯源(溯源 ip)\n1.4、IP威胁查询(ip查询 ip)\n1.5、CMD5查询(md5查询 xxx)\n1.6、签到(签到)\n1.7、积分查询(积分查询)\n\n'
                helpMsg += '【二、娱乐功能】\n2.1、美女图片(图片)\n2.2、美女视频(视频)\n2.3、摸鱼日历(摸鱼日历)\n2.4、舔狗日记(舔我)\n2.5、早报(早报)\n2.6、晚报(晚报)\n2.6、表情列表(表情列表)\n2.7、随机表情(随机表情, 有几率报错)\n'
                helpMsg += '[爱心]=== NGCBot菜单 ===[爱心]\n'
                self.wcf.send_text(f'@{getIdName(self.wcf, sender, roomId)}\n{helpMsg}', receiver=roomId, aters=sender)
        elif msgType == 49:
            # 视频号解析
            objectId, objectNonceId = getWechatVideoData(content)
            if objectId and objectNonceId:
                msg = self.Ams.getWechatVideo(objectId, objectNonceId)
                if msg:
                    self.wcf.send_text(f'@{getIdName(self.wcf, sender, roomId)}\n{msg}', receiver=roomId, aters=sender)
