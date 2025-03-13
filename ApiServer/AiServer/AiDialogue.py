from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
from tencentcloud.common.profile.http_profile import HttpProfile
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
from tencentcloud.common import credential
import Config.ConfigServer as Cs
from OutPut.outPut import op
import requests
import json


class AiDialogue:
    def __init__(self):
        configData = Cs.returnConfigData()
        self.systemAiRole = configData['AiConfig']['SystemAiRule']
        # OpenAI配置
        self.OpenAiConfig = {
            'OpenAiApi': configData['AiConfig']['OpenAiConfig']['OpenAiApi'],
            'OpenAiKey': configData['AiConfig']['OpenAiConfig']['OpenAiKey'],
            'OpenAiModel': configData['AiConfig']['OpenAiConfig']['OpenAiModel']
        }
        # 讯飞星火配置
        self.SparkAiConfig = {
            'SparkAiApi': configData['AiConfig']['SparkConfig']['SparkAiApi'],
            'SparkAiAppid': configData['AiConfig']['SparkConfig']['SparkAiAppid'],
            'SparkAiSecret': configData['AiConfig']['SparkConfig']['SparkAiSecret'],
            'SparkAiKey': configData['AiConfig']['SparkConfig']['SparkAiKey'],
            'SparkDomain': configData['AiConfig']['SparkConfig']['SparkDomain']
        }
        # 百度千帆配置
        self.QianfanAiConfig = {
            'QfAccessKey': configData['AiConfig']['QianFanConfig']['QfAccessKey'],
            'QfSecretKey': configData['AiConfig']['QianFanConfig']['QfSecretKey'],
            'QfAppid': configData['AiConfig']['QianFanConfig']['QfAppid'],
            'QfPicAccessKey': configData['AiConfig']['QianFanConfig']['QfPicAccessKey'],
            'QfPicSecretKey': configData['AiConfig']['QianFanConfig']['QfPicSecretKey'],
            'QfPicAppid': configData['AiConfig']['QianFanConfig']['QfPicAppid']
        }
        # 腾讯混元配置
        self.HunYuanAiConfig = {
            'HunYuanApi': configData['AiConfig']['HunYuanConfig']['HunYuanApi'],
            'HunYuanKey': configData['AiConfig']['HunYuanConfig']['HunYuanKey'],
            'HunYuanModel': configData['AiConfig']['HunYuanConfig']['HunYuanModel']
        }
        # KiMi配置
        self.KiMiConfig = {
            'KiMiApi': configData['AiConfig']['KiMiConfig']['KiMiApi'],
            'KiMiKey': configData['AiConfig']['KiMiConfig']['KiMiKey'],
            'KiMiModel': configData['AiConfig']['KiMiConfig']['KiMiModel']
        }
        # BigModel配置
        self.BigModelConfig = {
            'BigModelApi': configData['AiConfig']['BigModelConfig']['BigModelApi'],
            'BigModelKey': configData['AiConfig']['BigModelConfig']['BigModelKey'],
            'BigModelModel': configData['AiConfig']['BigModelConfig']['BigModelModel']
        }
        # DeepSeek配置
        self.DeepSeekConfig = {
            'DeepSeekApi': configData['AiConfig']['DeepSeekConfig']['DeepSeekApi'],
            'DeepSeekKey': configData['AiConfig']['DeepSeekConfig']['DeepSeekKey'],
            'DeepSeekModel': configData['AiConfig']['DeepSeekConfig']['DeepSeekModel']
        }
        # 本地Ollama配置
        self.OllamaConfig = {
            'OllamaApi': configData['AiConfig']['OllamaConfig']['OllamaApi'],
            'OllamaModel': configData['AiConfig']['OllamaConfig']['OllamaModel']
        }

        # 硅基流动配置
        self.SiliconFlowConfig = {
            'SiliconFlowApi': configData['AiConfig']['SiliconFlowConfig']['SiliconFlowApi'],
            'SiliconFlowKey': configData['AiConfig']['SiliconFlowConfig']['SiliconFlowKey'],
            'SiliconFlowModel': configData['AiConfig']['SiliconFlowConfig']['SiliconFlowModel']
        }
        # 火山配置
        self.VolcengineConfig = {
            'VolcengineApi': configData['AiConfig']['VolcengineConfig']['VolcengineApi'],
            'VolcengineKey': configData['AiConfig']['VolcengineConfig']['VolcengineKey'],
            'VolcengineModel': configData['AiConfig']['VolcengineConfig']['VolcengineModel'],
            'VolcengineAk': configData['AiConfig']['VolcengineConfig']['VolcengineAk'],
            'VolcengineSk': configData['AiConfig']['VolcengineConfig']['VolcengineSk'],
            'VolcengineReqKey': configData['AiConfig']['VolcengineConfig']['VolcengineReqKey'],
            'VolcenginePicModelVersion': configData['AiConfig']['VolcengineConfig']['VolcenginePicModelVersion']
        }
        # 通义配置
        self.QwenConfig = {
            'QwenApi': configData['AiConfig']['QwenConfig']['QwenApi'],
            'QwenModel': configData['AiConfig']['QwenConfig']['QwenModel'],
            'QwenKey': configData['AiConfig']['QwenConfig']['QwenKey'],
        }
        # 初始化消息列表
        self.userChatDicts = {}

        # AI优先级配置
        self.aiPriority = configData['AiConfig']['AiPriority']

    def getOpenAi(self, content, messages):
        """
        OpenAi对话接口
        :param content:
        :param messages:
        :return:
        """
        op(f'[*]: 正在调用OpenAi对话接口... ...')
        if not self.OpenAiConfig.get('OpenAiKey'):
            op(f'[-]: GPT模型未配置, 请检查相关配置!!!')
            return None, []
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": self.OpenAiConfig.get('OpenAiModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.OpenAiConfig.get('OpenAiKey')}",
        }
        try:
            resp = requests.post(url=self.OpenAiConfig.get('OpenAiApi'), headers=headers, json=data, timeout=15)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: Gpt对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getSparkAi(self, content):
        """
        星火大模型Ai 对话
        :param content: 对话内容
        :return:
        """
        op(f'[*]: 正在调用星火大模型对话接口... ...')
        SparkAppid = self.SparkAiConfig.get('SparkAiAppid')
        SparkSecret = self.SparkAiConfig.get('SparkAiSecret')
        SparkApiKey = self.SparkAiConfig.get('SparkAiKey')
        SparkApi = self.SparkAiConfig.get('SparkAiApi')
        SparkDomain = self.SparkAiConfig.get('SparkDomain')
        try:
            spark = ChatSparkLLM(
                spark_api_url=SparkApi,
                spark_app_id=SparkAppid,
                spark_api_key=SparkApiKey,
                spark_api_secret=SparkSecret,
                spark_llm_domain=SparkDomain,
                streaming=False,
            )
            messages = [ChatMessage(
                role='system',
                content=self.systemAiRole
            ), ChatMessage(
                role="user",
                content=content
            )]
            handler = ChunkPrintHandler()
            sparkObject = spark.generate([messages], callbacks=[handler])
            sparkContent = sparkObject.generations[0][0].text
            return sparkContent
        except Exception as e:
            op(f'[-]: 星火大模型对话接口出现错误, 错误信息: {e}')
            return None

    def getQianFanAi(self, content, messages):
        """
        千帆模型 Ai对话
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        op(f'[*]: 正在调用千帆大模型对话接口... ...')
        messages.append({"role": "user", "content": content})
        if not self.QianfanAiConfig.get('QfAccessKey') or not self.QianfanAiConfig.get('QfSecretKey'):
            op(f'[-]: 千帆大模型未配置, 请检查相关配置!!!')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

        def getAccessToken():
            try:
                headers = {
                    'Content-Type': 'application/json'
                }
                query = {
                    'grant_type': 'client_credentials',
                    'client_id': self.QianfanAiConfig.get('QfAccessKey'),
                    'client_secret': self.QianfanAiConfig.get('QfSecretKey'),
                }
                resp = requests.post('https://aip.baidubce.com/oauth/2.0/token', headers=headers, data=query)
                access_token = resp.json()['access_token']
                return access_token
            except Exception as e:
                op(f'[-]: 获取千帆模型AccessToken出现错误, 错误信息: {e}')
                return None

        def getAiContent(access_token, messages):
            try:
                url = f'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-4.0-turbo-8k?access_token={access_token}'
                data = {
                    'messages': messages
                }
                resp = requests.post(url, json=data)
                result = resp.json()['result']
                messages.append({"role": "assistant", "content": result})
                return result, [{"role": "system", "content": f'{self.systemAiRole}'}]
            except Exception as e:
                op(f'[-]: 请求千帆模型AccessToken出现错误, 错误信息: {e}')
                return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

        access_token = getAccessToken()
        if not access_token:
            op(f'[-]: 获取千帆模型AccessToken失败, 请检查千帆配置!!!')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

        aiContent = getAiContent(access_token, messages)
        if len(messages) == 21:
            del messages[1]
            del messages[2]
        return aiContent, messages

    def getHunYuanAi(self, content, messages):
        """
        腾讯混元模型 Ai对话接口
        :param content:
        :param messages:
        :return:
        """
        op(f'[*]: 正在调用混元对话接口... ...')
        if not self.HunYuanAiConfig.get('HunYuanKey'):
            op(f'[-]: 混元模型未配置, 请检查相关配置!!!')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": self.HunYuanAiConfig.get('HunYuanModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.HunYuanAiConfig.get('HunYuanKey')}",
        }
        try:
            resp = requests.post(url=self.HunYuanAiConfig.get('HunYuanApi'), headers=headers, json=data, timeout=15)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: 混元对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getKiMiAi(self, content, messages):
        op(f'[*]: 正在调用KiMi对话接口... ...')
        if not self.KiMiConfig.get('KiMiKey'):
            op(f'[-]: KiMi模型未配置, 请检查相关配置!!!')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": self.KiMiConfig.get('KiMiModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.KiMiConfig.get('KiMiKey')}",
        }
        try:
            resp = requests.post(url=self.KiMiConfig.get('KiMiApi'), headers=headers, json=data, timeout=15)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: KiMi对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getBigModel(self, content, messages):
        """
        BigModel
        :param OpenAiConfig: BigModel 配置字典
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        op(f'[*]: 正在调用BigModel对话接口... ...')
        if not self.BigModelConfig.get('BigModelKey'):
            op(f'[-]: BigModel模型未配置, 请检查相关配置!!!')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": self.BigModelConfig.get('BigModelModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.BigModelConfig.get('BigModelKey')}",
        }
        try:
            resp = requests.post(url=self.BigModelConfig.get('BigModelApi'), headers=headers, json=data, timeout=15)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: BigMode对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getDeepSeek(self, content, messages):
        """
        deepSeek
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        op(f'[*]: 正在调用DeepSeek对话接口... ...')
        if not self.DeepSeekConfig.get('DeepSeekKey'):
            op(f'[-]: DeepSeek模型未配置, 请检查相关配置!!!')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": self.DeepSeekConfig.get('DeepSeekModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.DeepSeekConfig.get('DeepSeekKey')}",
        }
        try:
            resp = requests.post(url=self.DeepSeekConfig.get('DeepSeekApi'), headers=headers, json=data, timeout=300)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: DeepSeek对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getOllama(self, content, messages):
        op(f'[*]: 正在调用Ollama本地对话接口... ...')
        if not self.OllamaConfig:
            op(f'[-]: Ollama本地模型未配置, 请检查相关配置!!!')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": self.OllamaConfig.get('OllamaModel'),
            'messages': messages,
            'stream': False
        }
        try:
            resp = requests.post(url=self.OllamaConfig.get('OllamaApi'), json=data)
            jsonData = resp.json()
            assistant_content = jsonData['message']['content'].split('</think>')[-1].strip()
            return assistant_content, []
        except Exception as e:
            op(f'[-]: Ollama本地对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getSiliconFlow(self, content, messages):
        """
        硅基流动
        :param content:
        :param messages:
        :return:
        """
        op(f'[*]: 正在调用硅基流动对话接口... ...')
        if not self.SiliconFlowConfig.get('SiliconFlowKey'):
            op(f'[-]: 硅基流动模型未配置, 请检查相关配置!!!')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": self.SiliconFlowConfig.get('SiliconFlowModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.SiliconFlowConfig.get('SiliconFlowKey')}",
        }
        try:
            resp = requests.post(url=self.SiliconFlowConfig.get('SiliconFlowApi'), headers=headers, json=data,
                                 timeout=300)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: 硅基对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getVolcengine(self, content, messages):
        """
        火山引擎
        :param content:
        :param messages:
        :return:
        """
        op(f'[*]: 正在调用火山引擎文本大模型接口... ...')
        if not self.VolcengineConfig.get('VolcengineKey'):
            op(f'[-]: 火山引擎文本大模型接口未配置')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]
        messages.append({"role": "user", "content": f'{content}'})
        headers = {
            "Authorization": f"{self.VolcengineConfig.get('VolcengineKey')}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.VolcengineConfig.get('VolcengineModel'),
            "messages": messages,
            "stream": False
        }
        try:
            resp = requests.post(self.VolcengineConfig.get('VolcengineApi'), headers=headers, json=data)
            jsonData = resp.json()
            assistant_content = jsonData.get('choices')[0].get('message').get('content')
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: 火山引擎文本大模型接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getQwen(self, content, messages):
        """
        通义千问对话
        :param content:
        :param messages:
        :return:
        """
        op(f'[*]: 正在调用通义千问大模型接口... ...')
        if not self.QwenConfig.get('QwenKey'):
            op(f'[-]: 通义千问接口未配置')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]
        messages.append({"role": "user", "content": f'{content}'})
        headers = {
            "Authorization": f"{self.QwenConfig.get('QwenKey')}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.QwenConfig.get('QwenModel'),
            "messages": messages,
            "stream": False
        }
        try:
            resp = requests.post(self.QwenConfig.get('QwenApi'), headers=headers, json=data)
            jsonData = resp.json()
            assistant_content = jsonData.get('choices')[0].get('message').get('content')
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: 通义千问接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getAi(self, content, sender):
        """
        处理优先级
        :param content:
        :return:
        """
        # 处理会话
        if sender not in self.userChatDicts:
            self.userChatDicts[sender] = [{"role": "system", "content": f'{self.systemAiRole}'}]
        result = ''
        for i in range(1, 12):
            aiModule = self.aiPriority.get(i)
            if aiModule == 'hunYuan':
                result, self.userChatDicts[sender] = self.getHunYuanAi(content, self.userChatDicts[sender])
            if aiModule == 'sparkAi':
                result = self.getSparkAi(content)
            if aiModule == 'openAi':
                result, self.userChatDicts[sender] = self.getOpenAi(content, self.userChatDicts[sender])
            if aiModule == 'qianFan':
                result, self.userChatDicts[sender] = self.getQianFanAi(content, self.userChatDicts[sender])
            if aiModule == 'kiMi':
                result, self.userChatDicts[sender] = self.getKiMiAi(content, self.userChatDicts[sender])
            if aiModule == 'bigModel':
                result, self.userChatDicts[sender] = self.getBigModel(content, self.userChatDicts[sender])
            if aiModule == 'deepSeek':
                result, self.userChatDicts[sender] = self.getDeepSeek(content, self.userChatDicts[sender])
            if aiModule == 'ollama':
                result, self.userChatDicts[sender] = self.getOllama(content, self.userChatDicts[sender])
            if aiModule == 'siliconFlow':
                result, self.userChatDicts[sender] = self.getSiliconFlow(content, self.userChatDicts[sender])
            if aiModule == 'volcengine':
                result, self.userChatDicts[sender] = self.getVolcengine(content, self.userChatDicts[sender])
            if aiModule == 'qwen':
                result, self.userChatDicts[sender] = self.getQwen(content, self.userChatDicts[sender])
            if not result:
                continue
            else:
                break
        if len(self.userChatDicts[sender]) == 21:
            del self.userChatDicts[sender][1]
            del self.userChatDicts[sender][2]
        return result




if __name__ == '__main__':
    messages = []
    Ad = AiDialogue()
    # print(Ad.getPicAi('画一只布尔猫'))
    while 1:
        print(Ad.getAi(input('>> '), '123'))
    # Ad.getAi(1)
    # while 1:
    #     content, messages = Ad.getHunYuanAi(input(), messages)
    #     print(content)
    # Ad.getHunYuanAi('1', [])
    # print(Ad.getQianFanPic('画一只赛博小狗'))
    # print(Ad.getSparkPic('画一只赛博小狗'))

    # print(Ad.getQianFanAi('你是谁', []))
    # print(Ad.getOpenAi())
    # print(Ad.getSparkAi('你是谁'))
    # while 1:
    #     print(Ad.getAi(input('>> ')))
