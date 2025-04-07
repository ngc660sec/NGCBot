from ApiServer.AiServer.AiLLMDialogue import AiLLMDialogue
import Config.ConfigServer as Cs
from OutPut.outPut import op
from ApiServer.InterFaceServer import *
import requests

class AiGraphicDialogue:
    def __init__(self):
        """
        AI 图文对话
        """
        configData = Cs.returnConfigData()
        self.systemAiRole = configData['AiConfig']['SystemAiRule']
        self.aiPicDiaPriority = configData['AiConfig']['AiPicDiaPriority']

        self.Ald = AiLLMDialogue()

        # 通义配置
        self.QwenConfig = {
            'QwenApi': configData['AiConfig']['QwenConfig']['QwenApi'],
            'QwenPicChatModel': configData['AiConfig']['QwenConfig']['QwenPicChatModel'],
            'QwenKey': configData['AiConfig']['QwenConfig']['QwenKey'],
        }
        # 火山配置
        self.VolcengineConfig = {
            'VolcengineApi': configData['AiConfig']['VolcengineConfig']['VolcengineApi'],
            'VolcengineKey': configData['AiConfig']['VolcengineConfig']['VolcengineKey'],
            'VolcenginePicChatModel': configData['AiConfig']['VolcengineConfig']['VolcenginePicChatModel'],
        }
        # 腾讯混元配置
        self.HunYuanAiConfig = {
            'HunYuanApi': configData['AiConfig']['HunYuanConfig']['HunYuanApi'],
            'HunYuanKey': configData['AiConfig']['HunYuanConfig']['HunYuanKey'],
            'HunYuanPicChatModel': configData['AiConfig']['HunYuanConfig']['HunYuanPicChatModel']
        }
        # KiMi配置
        self.KiMiConfig = {
            'KiMiApi': configData['AiConfig']['KiMiConfig']['KiMiApi'],
            'KiMiKey': configData['AiConfig']['KiMiConfig']['KiMiKey'],
            'KiMiPicModel': configData['AiConfig']['KiMiConfig']['KiMiPicModel']
        }

    def getQwenPicDia(self, content, base64FileContent):
        """
        通义千问 图文对话
        :param content:
        :param base64FileContent:
        :return:
        """
        op(f'[*]: 正在调用通义千问图文对话接口... ...')
        if not self.QwenConfig.get('QwenKey'):
            op(f'[-]: 通义千问接口未配置')
            return None
        headers = {
            "Authorization": f"Bearer {self.QwenConfig.get('QwenKey')}",
            "Content-Type": "application/json"
        }
        messages = [
            {
                'role': 'system', 'content': [{'type': 'text', 'text': self.systemAiRole}]
            },
            {
                'role': 'user', 'content': [{'type': 'image_url', 'image_url': {'url': base64FileContent},}, {'type': 'text', 'text': content}]
            }
        ]
        data = {
            'model': self.QwenConfig.get('QwenPicChatModel'),
            'messages': messages
        }
        try:
            resp = requests.post(self.QwenConfig.get('QwenApi'), headers=headers, json=data)
            jsonData = resp.json()
            content = jsonData['choices'][0]['message']['content']
            return content
        except Exception as e:
            op(f'[-]: 通义千问图文对话接口出现错误, 错误信息: {e}')
            return None

    def getVolcenginePicDia(self, content, base64FileContent):
        """
        火山图文对话
        :param content:
        :param base64FileContent:
        :return:
        """
        op(f'[*]: 正在调用火山图文对话接口... ...')
        if not self.VolcengineConfig.get('VolcengineKey'):
            op(f'[-]: 火山接口未配置')
            return None
        headers = {
            "Authorization": f"Bearer {self.VolcengineConfig.get('VolcengineKey')}",
            "Content-Type": "application/json"
        }
        messages = [
            {'role': 'user', 'content': [{'type': 'text', 'text': content}, {'type': 'image_url', 'image_url': {'url': base64FileContent}}]},
        ]
        data = {
            'model': self.VolcengineConfig.get('VolcenginePicChatModel'),
            'messages': messages
        }
        try:
            resp = requests.post(self.VolcengineConfig.get('VolcengineApi'), headers=headers, json=data)
            jsonData = resp.json()
            content = jsonData['choices'][0]['message']['content']
            return content
        except Exception as e:
            op(f'[-]: 火山图文对话接口出现错误, 错误信息: {e}')
            return None
    def getHunYuanPicDia(self, content, base64FileContent):
        """
        混元图文对话
        :param content:
        :param base64FileContent:
        :return:
        """
        op(f'[*]: 正在调用混元图文对话接口... ...')
        if not self.HunYuanAiConfig.get('HunYuanKey'):
            op(f'[-]: 混元模型未配置, 请检查相关配置!!!')
            return None
        messages = [
            {'role': 'user', 'content': [{'type': 'text', 'text': content}, {'type': 'image_url', 'image_url': {'url': base64FileContent}}]},
        ]
        data = {
            "model": self.HunYuanAiConfig.get('HunYuanPicChatModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.HunYuanAiConfig.get('HunYuanKey')}",
        }
        try:
            resp = requests.post(url=self.HunYuanAiConfig.get('HunYuanApi'), headers=headers, json=data, timeout=15)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            if assistant_content:
                return assistant_content
            return None
        except Exception as e:
            op(f'[-]: 混元图文对话接口出现错误, 错误信息: {e}')
            return None

    def getKiMiPicDia(self, content, base64FileContent):
        """
        KiMi图文对话
        :param content:
        :param base64FileContent:
        :return:
        """
        op(f'[*]: 正在调用KiMi图文对话对话接口... ...')
        if not self.KiMiConfig.get('KiMiKey'):
            op(f'[-]: KiMi模型未配置, 请检查相关配置!!!')
            return None
        messages = [
            {'role': 'system', 'content': self.systemAiRole},
            {'role': 'user', 'content': [{'type': 'image_url', 'image_url': {'url': base64FileContent}}, {'type': 'text', 'text': content}]},
        ]
        data = {
            "model": self.KiMiConfig.get('KiMiPicModel'),
            "messages": messages,
            'temperature': 0.3
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.KiMiConfig.get('KiMiKey')}",
        }
        try:
            resp = requests.post(url=self.KiMiConfig.get('KiMiApi'), headers=headers, json=data, timeout=15)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            if assistant_content:
                return assistant_content
            return None
        except Exception as e:
            op(f'[-]: KiMi对话接口出现错误, 错误信息: {e}')
            return None

    def getAiPicDia(self, content, imagePath, sender=None):
        """
        AI图文对话回复
        :param content:
        :param imagePath:
        :return:
        """
        base64FileContent = Ifa.encodeImage(imagePath)
        if not base64FileContent:
            op(f'[-]: 图片不存在或图片编码错误!!!')
            return None
        result = ''
        for i in range(1, 7):
            aiPicDiaModel = self.aiPicDiaPriority.get(i)
            if aiPicDiaModel == 'qwen':
                result = self.getQwenPicDia(content, base64FileContent)
            if aiPicDiaModel == 'volcengine':
                result = self.getVolcenginePicDia(content, base64FileContent)
            if aiPicDiaModel == 'hunyuan':
                result = self.getHunYuanPicDia(content, base64FileContent)
            if aiPicDiaModel == 'kimi':
                result = self.getKiMiPicDia(content, base64FileContent)
            if aiPicDiaModel == 'coze':
                result = self.Ald.getCoze(content=content, userId=sender, filePath=imagePath)
            if aiPicDiaModel == 'dify':
                result = self.Ald.getDify(content=content, userId=sender, filePath=imagePath)
            if not result:
                continue
            else:
                break
        return result


if __name__ == '__main__':
    Agd = AiGraphicDialogue()
    # base64FileContent = Agd.encodeImage('C:/Users/admin/Desktop/NGCBot-Beta/FileCache/aiPicCacheFolder/1741946224356.jpg')
    print(Agd.getAiPicDia('这张照片描述了什么',
                            'C:/Users/admin/Desktop/NGCBot-Beta/FileCache/aiPicCacheFolder/1741946224356.jpg'))


