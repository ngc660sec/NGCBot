from ApiServer.AiServer.AiLLMDialogue import AiLLMDialogue
from ApiServer.InterFaceServer import *
from Config.ConfigData import *
from OutPut.outPut import op
import requests


class AiGraphicDialogue:
    def __init__(self):
        """
        AI 图文对话
        """
        self.Ald = AiLLMDialogue()

    def getQwenPicDia(self, content, base64FileContent):
        """
        通义千问 图文对话
        :param content:
        :param base64FileContent:
        :return:
        """
        op(f'[*]: 正在调用通义千问图文对话接口... ...')
        if not getQwenConfig().get('QwenKey'):
            op(f'[-]: 通义千问接口未配置')
            return None
        headers = {
            "Authorization": f"Bearer {getQwenConfig().get('QwenKey')}",
            "Content-Type": "application/json"
        }
        messages = [
            {
                'role': 'system', 'content': [{'type': 'text', 'text': getSystemAiRole()}]
            },
            {
                'role': 'user', 'content': [{'type': 'image_url', 'image_url': {'url': base64FileContent}, },
                                            {'type': 'text', 'text': content}]
            }
        ]
        data = {
            'model': getQwenConfig().get('QwenPicChatModel'),
            'messages': messages
        }
        try:
            resp = requests.post(getQwenConfig().get('QwenApi'), headers=headers, json=data)
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
        if not getVolcengineConfig().get('VolcengineKey'):
            op(f'[-]: 火山接口未配置')
            return None
        headers = {
            "Authorization": f"Bearer {getVolcengineConfig().get('VolcengineKey')}",
            "Content-Type": "application/json"
        }
        messages = [
            {'role': 'user', 'content': [{'type': 'text', 'text': content},
                                         {'type': 'image_url', 'image_url': {'url': base64FileContent}}]},
        ]
        data = {
            'model': getVolcengineConfig().get('VolcenginePicChatModel'),
            'messages': messages
        }
        try:
            resp = requests.post(getVolcengineConfig().get('VolcengineApi'), headers=headers, json=data)
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
        if not getHunYuanConfig().get('HunYuanKey'):
            op(f'[-]: 混元模型未配置, 请检查相关配置!!!')
            return None
        messages = [
            {'role': 'user', 'content': [{'type': 'text', 'text': content},
                                         {'type': 'image_url', 'image_url': {'url': base64FileContent}}]},
        ]
        data = {
            "model": getHunYuanConfig().get('HunYuanPicChatModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {getHunYuanConfig().get('HunYuanKey')}",
        }
        try:
            resp = requests.post(url=getHunYuanConfig().get('HunYuanApi'), headers=headers, json=data, timeout=15)
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
        if not getKiMiConfig().get('KiMiKey'):
            op(f'[-]: KiMi模型未配置, 请检查相关配置!!!')
            return None
        messages = [
            {'role': 'system', 'content': getSystemAiRole()},
            {'role': 'user', 'content': [{'type': 'image_url', 'image_url': {'url': base64FileContent}},
                                         {'type': 'text', 'text': content}]},
        ]
        data = {
            "model": getKiMiConfig().get('KiMiPicModel'),
            "messages": messages,
            'temperature': 0.3
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{getKiMiConfig().get('KiMiKey')}",
        }
        try:
            resp = requests.post(url=getKiMiConfig().get('KiMiApi'), headers=headers, json=data, timeout=15)
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
            aiPicDiaModel = getaiPicDiaPriority().get(i)
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
