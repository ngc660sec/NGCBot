from ApiServer.AiServer.AiDialogue import AiDialogue
import ApiServer.pluginServer as Ps


class ApiMainServer:
    def __init__(self):
        """
        将所有插件服务全部注册在__init__.py文件中
        此文件做所有插件总体调用
        """
        # Ai对象实例化
        self.Ad = AiDialogue()

    def getMusic(self, musicName):
        """
        点歌API
        :param musicName:
        :return:
        """
        return Ps.Ha.getMusic(musicName)

    def getDeepSeek(self, content, message):
        """
        deepSeek
        :param content:
        :param message:
        :return:
        """
        return self.Ad.getDeepSeek(content, message)

    def getTaLuo(self):
        """
        塔罗牌占卜API
        :return:
        """
        return Ps.Ha.getTaLuo()

    def getWechatVideo(self, objectId, objectNonceId):
        """
        视频号处理
        :param objectId:
        :param objectNonceId:
        :return:
        """
        return Ps.Ha.getWechatVideo(objectId, objectNonceId)

    def getVideoAnalysis(self, videoText):
        """
        抖音视频解析去水印
        :param videoText:
        :return:
        """
        return Ps.Ha.getVideoAnalysis(videoText)

    def getShortPlay(self, playName):
        """
        短剧搜索API
        :param playName:
        :return:
        """
        return Ps.Ha.getShortPlay(playName)

    def getAiWen(self, ip):
        """
        埃文IP查询调用接口
        :param ip:
        :return:
        """
        return Ps.Pa.getAiWenIpv4(ip)

    def getCmd5(self, ciphertext):
        """
        MD5查询调用接口
        :param ciphertext:
        :return:
        """
        return Ps.Pa.getCmd5(ciphertext)

    def getMorningNews(self, ):
        """
        新闻早报调用接口
        :return:
        """
        return Ps.Na.getMorningNews()

    def getEveningNews(self, ):
        """
        新闻晚报调用接口
        :return:
        """
        return Ps.Na.getEveningNews()

    def getGirlPic(self, ):
        """
        美女图片调用接口
        :return:
        """
        return Ps.Ha.getPic()

    def getGirlVideo(self, ):
        """
        美女视频调用接口
        :return:
        """
        return Ps.Ha.getVideo()

    def getFish(self, ):
        """
        摸鱼日历调用接口
        :return:
        """
        return Ps.Ha.getFish()

    def getKfc(self, ):
        """
        疯狂星期四调用接口
        :return:
        """
        return Ps.Ha.getKfc()

    def getDog(self, ):
        """
        舔狗日记调用接口
        :return:
        """
        return Ps.Ha.getDog()

    def getAi(self, content):
        """
        Ai对话调用接口
        :param content:
        :return:
        """
        return self.Ad.getAi(content)

    def getAiPic(self, content):
        """
        Ai图像生成调用接口
        :return:
        """
        return self.Ad.getPicAi(content)

    def getEmoticon(self, avatarPathList, memeKey=None):
        """
        表情包生成接口
        :param avatarPathList:
        :param content:
        :return:
        """
        return Ps.Ha.getEmoticon(avatarPathList, memeKey)

if __name__ == '__main__':
    Ams = ApiMainServer()
    # print(Ams.getAiWen('1.14.145.103'))
    # print(Ams.getAi('你好'))
