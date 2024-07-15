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

    def getAiWen(self, ip):
        """
        埃文IP查询调用接口
        :param ip:
        :return:
        """
        return Ps.Pa.getAiWenIpv4(ip)

    def getThreatBook(self, ip):
        """
        微步IP查询调用接口
        :param ip:
        :return:
        """
        return Ps.Pa.getThreatBook(ip)

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


if __name__ == '__main__':
    Ams = ApiMainServer()
    # print(Ams.getAiWen('1.14.145.103'))
    print(Ams.getAi('你好'))
