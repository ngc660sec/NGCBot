from meme_generator import get_meme, get_meme_keys
import FileCache.FileCacheServer as Fcs
import Config.ConfigServer as Cs
from OutPut.outPut import op
import lz4.block as lb
import requests
import asyncio
import random
import time
import os
import re


class HappyApi:
    def __init__(self):
        """
        不要直接调用此类
        娱乐功能Api文件
        """
        # 读取配置文件
        configData = Cs.returnConfigData()
        # 读取系统版权设置
        self.systemCopyright = configData['SystemConfig']['SystemCopyright']
        self.picUrlList = configData['FunctionConfig']['HappyFunctionConfig']['PicConfig']['PicApi']
        self.videoUrlList = configData['FunctionConfig']['HappyFunctionConfig']['VideoConfig']['VideoApi']
        self.dogApi = configData['FunctionConfig']['HappyFunctionConfig']['DogConfig']['DogApi']
        self.fishApi = configData['FunctionConfig']['HappyFunctionConfig']['FishConfig']['FishApi']
        self.kfcApi = configData['FunctionConfig']['HappyFunctionConfig']['KfcConfig']['KfcApi']
        self.shortPlayApi = configData['FunctionConfig']['HappyFunctionConfig']['ShortPlayConfig']['ShortPlayApi']
        self.dyVideoAnalysisApi = configData['FunctionConfig']['HappyFunctionConfig']['DyVideoAnalysisConfig'][
            'DyVideoAnalysisAPi']
        self.wechatVideoApi = configData['FunctionConfig']['HappyFunctionConfig']['WechatVideoConfig']['WechatVideoApi']
        self.taLuoApi = configData['FunctionConfig']['HappyFunctionConfig']['TaLuoConfig']['TaLuoApi']
        self.musicApi = configData['FunctionConfig']['HappyFunctionConfig']['MusicConfig']['MusicApi']

        # API密钥配置
        self.dpKey = configData['KeyConfig']['DpConfig']['DpKey']

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

    def getMusic(self, musicName):
        op(f'[*]: 正在调用点歌接口... ...')
        musicApi = self.musicApi[0]
        try:
            jsonData = requests.get(musicApi.format(musicName), verify=True, timeout=30).json()
            songName = jsonData.get('title')
            singerName = jsonData.get('singer')
            songPic = jsonData.get('cover')
            dataUrl = jsonData.get('link')
            playUrl = jsonData.get('music_url')
            xml_message = f"""<msg>
            <appmsg appid="wx485a97c844086dc9" sdkver="0">
                <title>{songName}</title>
                <des>{singerName}</des>
                <action></action>
                <type>3</type>
                <showtype>0</showtype>
                <mediatagname></mediatagname>
                <messageext></messageext>
                <messageaction></messageaction>
                <content></content>
                <contentattr>0</contentattr>
                <url>{dataUrl}</url>
                <lowurl>{playUrl}</lowurl>
                <dataurl>{playUrl}</dataurl>
                <lowdataurl>{playUrl}</lowdataurl>
                <appattach>
                    <totallen>0</totallen>
                    <attachid></attachid>
                    <emoticonmd5></emoticonmd5>
                    <fileext></fileext>
                </appattach>
                <extinfo></extinfo>
                <sourceusername></sourceusername>
                <sourcedisplayname></sourcedisplayname>
                <commenturl></commenturl>
                <songalbumurl>{songPic}</songalbumurl>
                <md5></md5>
            </appmsg>
            <fromusername>wxid_hqdtktnqvw8e21</fromusername>
            <scene>0</scene>
            <appinfo>
                <version>29</version>
                <appname>摇一摇搜歌</appname>
            </appinfo>
            <commenturl></commenturl>
        </msg>\x00"""
            # 将文本编码成字节
            text_bytes = xml_message.encode('utf-8')
            # 使用 lz4 压缩
            compressed_data = lb.compress(text_bytes, store_size=False, mode="high_compression")
            # 将压缩后的数据转为十六进制字符串，以便存储到数据库
            compressed_data_hex = compressed_data.hex()
            return compressed_data_hex
        except Exception as e:
            op(f'[-]: 点歌API出现错误, 错误信息: {e}')
            return None

    def getTaLuo(self, ):
        """
        塔罗牌占卜
        :return:
        """
        op(f'[*]: 正在调用塔罗牌占卜接口... ...')
        try:
            jsonData = requests.get(self.taLuoApi.format(self.dpKey), verify=True).json()
            code = jsonData.get('code')
            if code == 200:
                savePath = Fcs.returnPicCacheFolder() + '/' + str(int(time.time() * 1000)) + '.jpg'
                result = jsonData.get('result')
                Pai_Yi_deduction = result.get('Pai_Yi_deduction')
                core_prompt = result.get('core_prompt')
                Knowledge_expansion = result.get('Knowledge_expansion')
                Card_meaning_extension = result.get('Card_meaning_extension')
                e_image = result.get('e_image')
                picPath = self.downloadFile(e_image, savePath)
                content = f'描述: {Pai_Yi_deduction}\n\n建议: {core_prompt}\n\n描述: {Knowledge_expansion}\n\n建议: {Card_meaning_extension}'
                return content, picPath
            return '', ''
        except Exception as e:
            op(f'[-]: 塔罗牌占卜接口出现错误, 错误信息: {e}')
            return '', ''

    def getWechatVideo(self, objectId, objectNonceId):
        """
        微信视频号处理下载, 返回Url
        :param objectId:
        :param objectNonceId:
        :return:
        """
        op(f'[*]: 正在调用视频号API接口... ...')
        try:
            jsonData = requests.get(self.wechatVideoApi.format(self.dpKey, objectId, objectNonceId), verify=True,
                                    timeout=500).json()
            code = jsonData.get('code')
            if code == 200:
                videoData = jsonData.get('data')
                description = videoData.get('description').replace("\n", "")
                nickname = videoData.get('nickname')
                videoUrl = videoData.get('url')
                content = f'视频描述: {description}\n视频作者: {nickname}\n视频链接: {videoUrl}'
                return content
            elif code == 202:
                time.sleep(200)
                return self.getWechatVideo(objectId, objectNonceId)
            return None
        except Exception as e:
            op(f'[-]: 视频号API接口出现错误, 错误信息: {e}')
            return None

    def getVideoAnalysis(self, videoText):
        """
        抖音视频解析去水印
        :param videoText: 短视频连接或者分享文本
        :return: 视频地址
        """
        op(f'[*]: 正在调用视频解析去水印API接口... ....')
        try:
            douUrl = re.search(r'(https?://[^\s]+)', videoText).group()
            jsonData = requests.get(self.dyVideoAnalysisApi.format(self.dpKey, douUrl), verify=True).json()
            code = jsonData.get('code')
            if code == 200:
                videoData = jsonData.get('data')
                videoUrl = videoData.get('video_url')
                savePath = Fcs.returnVideoCacheFolder() + '/' + str(int(time.time() * 1000)) + '.mp4'
                savePath = self.downloadFile(videoUrl, savePath)
                if savePath:
                    return savePath
            return None
        except Exception as e:
            op(f'[-]: 视频解析去水印API出现错误, 错误信息: {e}')
            return None

    def getShortPlay(self, playName):
        """
        短剧搜索
        :param playName: 短剧名称
        :return:
        """
        op(f'[*]: 正在调用短剧搜索API接口... ...')
        content = f'🔍搜索内容: {playName}\n'
        try:
            jsonData = requests.get(self.shortPlayApi.format(playName), verify=True).json()
            statusCode = jsonData.get('code')
            if statusCode != 200:
                return False
            dataList = jsonData.get('data')
            if not dataList:
                content += '💫搜索的短剧不存在哦 ~~~\n'
            else:
                for data in dataList:
                    content += f'🌟{data.get("name")}\n'
                    content += f'🔗{data.get("link")}\n\n'
            content += f"{self.systemCopyright + '整理分享，更多内容请戳 #' + self.systemCopyright if self.systemCopyright else ''}\n{time.strftime('%Y-%m-%d %X')}"
            return content
        except Exception as e:
            op(f'[-]: 短剧搜索API出现错误, 错误信息: {e}')
            return False

    def getPic(self, ):
        """
        美女图片下载
        :return:
        """
        op(f'[*]: 正在调用美女图片Api接口... ...')
        picUrl = random.choice(self.picUrlList)
        savePath = Fcs.returnPicCacheFolder() + '/' + str(int(time.time() * 1000)) + '.jpg'
        picPath = self.downloadFile(picUrl, savePath)
        if not picPath:
            for picUrl in self.picUrlList:
                picPath = self.downloadFile(picUrl, savePath)
                if picPath:
                    break
                continue
        return picPath

    def getVideo(self, ):
        """
        美女视频下载
        :return:
        """
        op(f'[*]: 正在调用美女视频Api接口... ...')
        videoUrl = random.choice(self.videoUrlList)
        savePath = Fcs.returnVideoCacheFolder() + '/' + str(int(time.time() * 1000)) + '.mp4'
        videoPath = self.downloadFile(videoUrl, savePath)
        if not videoPath:
            for videoUrl in self.videoUrlList:
                videoPath = self.downloadFile(videoUrl, savePath)
                if videoPath:
                    break
                continue
        return videoPath

    def getFish(self, ):
        """
        摸鱼日历下载
        :return:
        """
        op(f'[*]: 正在调用摸鱼日历Api接口... ...')
        savePath = Fcs.returnFishCacheFolder() + '/' + str(int(time.time() * 1000)) + '.jpg'
        try:
            jsonData = requests.get(self.fishApi, timeout=30).json()
            fishUrl = jsonData.get('data')['url']
            fishPath = self.downloadFile(url=fishUrl, savePath=savePath)
            if not fishPath:
                for i in range(2):
                    fishPath = self.downloadFile(self.fishApi, savePath)
                    if fishPath:
                        break
                    continue
            if not fishPath:
                op(f'[-]: 摸鱼日历接口出现错误, 请检查！')
            return fishPath
        except Exception as e:
            op(f'[-]: 摸鱼日历接口出现错误, 错误信息: {e}')

    def getKfc(self, ):
        """
        疯狂星期四
        :return:
        """
        op(f'[*]: 正在调用KFC疯狂星期四Api接口... ... ')
        try:
            jsonData = requests.get(url=self.kfcApi, timeout=30).json()
            result = jsonData.get('text')
            if result:
                return result
            return None
        except Exception as e:
            op(f'[-]: KFC疯狂星期四Api接口出现错误, 错误信息: {e}')
            return None

    def getDog(self, ):
        """
        舔狗日记Api接口
        :return:
        """
        op(f'[*]: 正在调用舔狗日记Api接口... ... ')
        try:
            jsonData = requests.get(url=self.dogApi.format(self.dpKey), timeout=30).json()
            result = jsonData.get('result')
            if result:
                content = result.get('content')
                if content:
                    return content
            return None
        except Exception as e:
            op(f'[-]: 舔狗日记Api接口出现错误, 错误信息: {e}')
            return None

    def getEmoticon(self, avatarPathList, memeKey=None):
        """
        表情包Api接口
        :param memeKey: 消息内容
        :param avatarPathList: 头像列表
        :return:
        """
        op(f'[*]: 正在调用表情包Api接口... ...')
        if not avatarPathList:
            op(f'[-]: 表情包Api接口出现错误, 错误信息: avatarPathList不能为空')
            return
        if not avatarPathList:
            raise 'avatarPathList None'
        if not memeKey:
            memeKey = random.choices(get_meme_keys())[0]

        savePath = Fcs.returnPicCacheFolder() + '/' + str(int(time.time() * 1000)) + '.gif'
        try:
            async def makeEmo():
                meme = get_meme(memeKey)
                result = await meme(images=avatarPathList, texts=[], args={"circle": False})
                with open(savePath, "wb") as f:
                    f.write(result.getvalue())

            loop = asyncio.new_event_loop()
            loop.run_until_complete(makeEmo())
            # 图片大小判断 如果大于1mb 就以图片形式发送
            file_size_bytes = os.path.getsize(savePath)
            size_limit_bytes = 1024 * 1024
            sizeBool = file_size_bytes <= size_limit_bytes
            return savePath, sizeBool
        except Exception as e:
            op(f'[-]: 表情包Api接口出现错误, 错误信息: {e}')
            return None, None


if __name__ == '__main__':
    Ha = HappyApi()
    print(Ha.getDog())
    # print(Ha.getKfc())
    # Ha.getEmoticon('C:/Users/Administrator/Desktop/NGCBot V2.2/avatar.jpg')
    # print(Ha.getShortPlay('霸道总裁爱上我'))
    # print(Ha.getPic())
    # print(Ha.getVideoAnalysis(
    #     '3.84 复制打开抖音，看看【SQ的小日常的作品】师傅：门可以让我踹吗 # 情侣 # 搞笑 # 反转... https://v.douyin.com/iydr37xU/ bAg:/ F@H.vS 01/06'))
    # print(Ha.getWechatVideo('14258814955767007275', '14776806611926650114_15_140_59_32_1735528000805808'))
    # print(Ha.getTaLuo())
    # print(Ha.getFish())
    # print(Ha.getMusic('晴天'))
