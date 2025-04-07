import FileCache.FileCacheServer as Fcs
import Config.ConfigServer as Cs
from OutPut.outPut import op
import lz4.block as lb
import requests
import datetime
import urllib3
import base64
import time


class InterFaceApi:
    def __init__(self):
        # 忽略HTTPS告警
        urllib3.disable_warnings()
        # 读取配置文件
        configData = Cs.returnConfigData()
        # 读取系统版权设置
        self.systemCopyright = configData['SystemConfig']['SystemCopyright']
        self.FireFlyCardConfig = configData['FunctionConfig']['InterFaceConfig']['FireFlyCardConfig']
        self.CozeConfig = {
            'CozeToken': configData['AiConfig']['CozeConfig']['CozeToken'],
        }

    def getMdContentCode(self, mdContent):
        """
        提取markDown文本中 ``` ``` 代码段的内容
        :param mdContent:
        :return:
        """

    def textToCard(self, title, mdContent):
        """
        流光卡片生成
        :param title:
        :param mdContent
        :return:
        """
        print(int(len(mdContent)))
        data = {
            "form": {
                "icon": self.FireFlyCardConfig.get('icon'),
                "date": self.returnNowTime(),
                "title": title,
                "content": mdContent.strip(),
                "author": self.systemCopyright,
                "textCount": "字数",
                "qrCodeTitle": self.FireFlyCardConfig.get('qrCodeTitle'),
                "qrCodeText": self.FireFlyCardConfig.get('qrCodeText'),
                "qrcodeImg": self.FireFlyCardConfig.get('qrcodeImg'),
                "pagination": "01",
                "textCountNum": int(len(mdContent)),
            },
            "style": {
                "align": "left",
                "backgroundName": "light-blue-color-12",
                "backShadow": "",
                "font": "Alibaba-PuHuiTi-Regular",
                "width": 550,
                "ratio": "Auto",
                "height": 0,
                "fontScale": 1,
                "padding": "30px",
                "borderRadius": "15px",
                "backgroundAngle": "55deg",
                "lineHeights": {
                    "content": ""
                },
                "letterSpacings": {
                    "content": ""
                }
            },
            "switchConfig": {
                "showIcon": True,
                "showDate": True,
                "showTitle": True,
                "showContent": True,
                "showAuthor": True,
                "showTextCount": True,
                "showQRCode": True,
                "showPageNum": False,
                "showWatermark": False,
                "showTGradual": True
            },
            "temp": "tempEasy",
            "language": "zh"
        }
        try:
            resp = requests.post(self.FireFlyCardConfig.get('FireFlyCardApi'), json=data, verify=False, timeout=60)
            content = resp.content
            savePath = Fcs.returnPicCacheFolder() + '/' + str(int(time.time() * 1000)) + '.jpg'
            with open(savePath, mode='wb') as f:
                f.write(content)
            return savePath
        except Exception as e:
            op(f'[-]: 生成流光卡片出现错误, 错误信息: {e}')
            return False

    def returnNowTime(self, ):
        """
        返回当前时间
        :return:  2023年10月5日星期四 14：05
        """
        now = datetime.datetime.now()
        weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        formatted_time = f"{now.year}年{now.month}月{now.day}日{weekdays[now.weekday()]} {now.hour}：{now.minute:02d}"
        return formatted_time

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

    def encodeImage(self, imagePath):
        """
        返回Base64编码的文件内容
        :param imagePath:
        :return:
        """
        try:
            fileExt = imagePath.split('.')[-1]
            with open(imagePath, 'rb') as f:
                base64FileContent = base64.b64encode(f.read()).decode("utf-8")
                if 'png' in fileExt:
                    return f'data:image/png;base64,{base64FileContent}'
                if 'jpg' in fileExt:
                    return f'data:image/jpg;base64,{base64FileContent}'
                if 'webp' in fileExt:
                    return f'data:webp;base64,{base64FileContent}'
                if 'gif' in fileExt:
                    return f'data:image/gif;base64,{base64FileContent}'
        except Exception as e:
            op(f'[-]: 返回Base64编码的文件内容出现错误, 错误信息: {e}')
            return None

    def getAudioMsg(self, audioPath):
        """
        获取语音的文本内容，使用扣子接口
        :param audioPath:
        :return:
        """
        audioApi = 'https://api.coze.cn/v1/audio/transcriptions'
        headers = {
            'Authorization': self.CozeConfig.get("CozeToken"),
        }
        try:
            with open(audioPath, mode='rb') as f:
                files = {
                    'file': (audioPath, f, 'audio/mpeg')
                }
                resp = requests.post(audioApi, headers=headers, files=files)
                jsonData = resp.json()
                data = jsonData.get('data')
                text = data.get('text')
                if text:
                    return text
                return None
        except Exception as e:
            op(f'[-]: AI语音回复出现错误, 错误信息: {e}')
            return None

    def returnMusicXml(self, songName, singerName, dataUrl, playUrl, songPic):
        """
        返回音乐卡片XML数据
        :param songName:  音乐名字
        :param singerName: 歌手名字
        :param dataUrl: 音乐数据链接
        :param playUrl: 音乐播放链接
        :param songPic: 音乐背景图
        :return:
        """
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