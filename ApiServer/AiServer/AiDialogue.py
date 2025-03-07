from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
from tencentcloud.common.profile.http_profile import HttpProfile
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from volcengine.visual.VisualService import VisualService
from sparkai.core.messages import ChatMessage
from tencentcloud.common import credential
import ApiServer.AiServer.sparkPicApi as sPa
import FileCache.FileCacheServer as Fcs
import Config.ConfigServer as Cs
from OutPut.outPut import op
import requests
import base64
import time
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
            'HunYuanSecretId': configData['AiConfig']['HunYuanConfig']['HunYuanSecretId'],
            'HunYuanSecretKey': configData['AiConfig']['HunYuanConfig']['HunYuanSecretKey'],
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
        # 豆包配置
        self.DouBaoConfig = {
            'DouBaoApi': configData['AiConfig']['DouBaoConfig']['DouBaoApi'],
            'DouBaoKey': configData['AiConfig']['DouBaoConfig']['DouBaoKey'],
            'DouBaoModel': configData['AiConfig']['DouBaoConfig']['DouBaoModel'],
            'DouBaoAk': configData['AiConfig']['DouBaoConfig']['DouBaoAk'],
            'DouBaoSk': configData['AiConfig']['DouBaoConfig']['DouBaoSk'],
            'DouBaoReqKey': configData['AiConfig']['DouBaoConfig']['DouBaoReqKey'],
            'DouBaoPicModelVersion': configData['AiConfig']['DouBaoConfig']['DouBaoPicModelVersion']
        }

        # 初始化消息列表
        self.openAiMessages = [{"role": "system", "content": f'{self.systemAiRole}'}]
        self.qianFanMessages = [{"role": "system", "content": f'{self.systemAiRole}'}]
        self.hunYuanMessages = [{"Role": "system", "Content": f'{self.systemAiRole}'}]
        self.kimiMessages = [{"Role": "system", "Content": f'{self.systemAiRole}'}]
        self.bigModelMessages = [{"role": "system", "Content": f'{self.systemAiRole}'}]
        self.deepSeekMessages = [{"role": "system", "content": f'{self.systemAiRole}'}]
        self.ollamaMessages = [{"role": "system", "content": f'{self.systemAiRole}'}]
        self.siliconFlowMessages = [{"role": "system", "content": f'{self.systemAiRole}'}]
        self.douBaoMessages = [{"role": "system", "content": f'{self.systemAiRole}'}]

        # AI优先级配置
        self.aiPriority = configData['AiConfig']['AiPriority']
        self.aiPicPriority = configData['AiConfig']['AiPicPriority']

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

    def getSparkPic(self, content):
        """
        星火大模型 图像生成
        :param content:
        :return:
        """
        op(f'[*]: 正在调用星火大模型图像生成接口... ...')
        try:
            res = sPa.main(content, self.SparkAiConfig.get('SparkAiAppid'), self.SparkAiConfig.get('SparkAiKey'),
                           self.SparkAiConfig.get('SparkAiSecret'))
            savePath = sPa.parser_Message(res)
            return savePath
        except Exception as e:
            op(f'[-]: 星火大模型图像生成出现错误, 错误信息: {e}')
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
            return None, []

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
                return result, messages
            except Exception as e:
                op(f'[-]: 请求千帆模型AccessToken出现错误, 错误信息: {e}')
                return None, messages

        access_token = getAccessToken()
        if not access_token:
            op(f'[-]: 获取千帆模型AccessToken失败, 请检查千帆配置!!!')
            return None, messages

        aiContent = getAiContent(access_token, messages)
        if len(messages) == 21:
            del messages[1]
            del messages[2]
        return aiContent, messages

    def getQianFanPic(self, content):
        """
        千帆模型生成图片
        :param content:
        :return:
        """
        op(f'[*]: 正在调用千帆模型图片生成接口... ...')

        def getAccessToken():
            try:
                headers = {
                    'Content-Type': 'application/json'
                }
                query = {
                    'grant_type': 'client_credentials',
                    'client_id': self.QianfanAiConfig.get('QfPicAccessKey'),
                    'client_secret': self.QianfanAiConfig.get('QfPicSecretKey'),
                }
                resp = requests.post('https://aip.baidubce.com/oauth/2.0/token', headers=headers, data=query)
                access_token = resp.json()['access_token']
                return access_token
            except Exception as e:
                op(f'[-]: 获取千帆模型AccessToken出现错误, 错误信息: {e}')
                return None

        def getTaskId(content, accessToken):
            try:
                url = f'https://aip.baidubce.com/rpc/2.0/ernievilg/v1/txt2imgv2?access_token={accessToken}'
                data = {
                    "prompt": content,
                    "width": 1024,
                    "height": 1024,
                    "image_num": 1,
                }
                resp = requests.post(url, json=data)
                json_data = resp.json()
                task_id = json_data['data']['task_id']
                return task_id
            except Exception as e:
                op(f'[-]: 千帆模型Ai图像生成出现错误, 错误信息: {e}')
                return None

        def getPicUrl(task_id, accessToken):
            try:
                url = f'https://aip.baidubce.com/rpc/2.0/ernievilg/v1/getImgv2?access_token={accessToken}'
                data = {
                    'task_id': task_id
                }
                resp = requests.post(url, json=data)
                json_data = resp.json()
                if json_data['data']['task_status'] == 'SUCCESS':
                    sub_task_result_list = json_data['data']['sub_task_result_list']
                    final_image_list = sub_task_result_list[0]['final_image_list']
                    img_url = final_image_list[0]['img_url']
                    return img_url
            except Exception as e:
                op(f'[-]: 千帆模型Ai图像生成出现错误, 错误信息: {e}')

        def downloadImg(imgUrl):
            try:
                save_path = Fcs.returnAiPicFolder() + '/' + str(int(time.time() * 1000)) + '.jpg'
                resp = requests.get(url=imgUrl)
                imgContent = resp.content
                with open(save_path, mode='wb') as f:
                    f.write(imgContent)
                return save_path
            except Exception as e:
                op(f'[-]: 千帆模型Ai图像下载出现错误, 错误信息: {e}')
                return None

        accessToken = getAccessToken()
        if accessToken:
            task_id = getTaskId(content, accessToken)
            if task_id:
                time.sleep(20)
                imgUrl = getPicUrl(task_id, accessToken)
                if imgUrl:
                    savePath = downloadImg(imgUrl)
                    return savePath
                return None

    def getHunYuanAi(self, content, messages):
        """
        腾讯混元模型 Ai对话接口
        :param content:
        :param messages:
        :return:
        """
        try:
            op(f'[*]: 正在调用混元模型对话接口... ...')
            cred = credential.Credential(self.HunYuanAiConfig.get('HunYuanSecretId'),
                                         self.HunYuanAiConfig.get('HunYuanSecretKey'))
            httpProfile = HttpProfile()
            httpProfile.endpoint = "hunyuan.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = hunyuan_client.HunyuanClient(cred, "ap-beijing", clientProfile)
            req = models.ChatCompletionsRequest()
            messages.append({'Role': 'user', 'Content': content})
            params = {
                "Model": self.HunYuanAiConfig.get('HunYuanModel'),
                "Messages": messages,
            }
            req.from_json_string(json.dumps(params))
            Choices = str(client.ChatCompletions(req).Choices[0])
            jsonData = json.loads(Choices)
            Message = jsonData['Message']
            messages.append({'Role': Message['Role'], 'Content': Message['Content']})
            content = Message['Content']
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            if content:
                return content, messages
            return None, []
        except TencentCloudSDKException as e:
            op(f'[-]: 腾讯混元Ai对话接口出现错误, 错误信息: {e}')
            return None, messages

    def getKiMiAi(self, content, messages):
        op(f'[*]: 正在调用KiMi对话接口... ...')
        if not self.KiMiConfig.get('KiMiKey'):
            op(f'[-]: KiMi模型未配置, 请检查相关配置!!!')
            return None, []
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
            return None, []
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
            return None, []
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
            return None, []
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
            return None, []

    def getSiliconFlow(self, content, messages):
        op(f'[*]: 正在调用硅基流动对话接口... ...')
        if not self.SiliconFlowConfig.get('SiliconFlowKey'):
            op(f'[-]: 硅基流动模型未配置, 请检查相关配置!!!')
            return None, []
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

    def getDouBao(self, content, messages):
        op(f'[*]: 正在调用豆包文本大模型接口... ...')
        if not self.DouBaoConfig.get('DouBaoKey'):
            op(f'[-]: 豆包文本大模型接口未配置')
            return None, self.douBaoMessages[0]
        messages.append({"role": "user", "content": f'{content}'})
        headers = {
            "Authorization": f"{self.DouBaoConfig.get('DouBaoKey')}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.DouBaoConfig.get('DouBaoModel'),
            "messages": messages,
            "stream": False
        }
        try:
            resp = requests.post(self.DouBaoConfig.get('DouBaoApi'), headers=headers, json=data)
            jsonData = resp.json()
            assistant_content = jsonData.get('choices')[0].get('message').get('content')
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: 豆包文本大模型接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getDouBaoPic(self, content):
        op(f'[*]: 正在调用豆包文生图模型... ...')
        if not self.DouBaoConfig.get('DouBaoAk'):
            op(f'[-]: 豆包文生图模型未配置, 请检查相关配置!!!')
            return None
        visual_service = VisualService()
        visual_service.set_ak(self.DouBaoConfig.get('DouBaoAk'))
        visual_service.set_sk(self.DouBaoConfig.get('DouBaoSk'))
        data = {
            'req_key': self.DouBaoConfig.get('DouBaoReqKey'),
            'model_version': self.DouBaoConfig.get('DouBaoPicModelVersion'),
            'prompt': content,
        }
        try:
            resp = visual_service.cv_process(data)
            binaryDataBase64 = resp.get('data').get('binary_data_base64')[0]
            picPath = Fcs.returnAiPicFolder() + '/' + str(int(time.time() * 1000)) + '.jpg'
            with open(picPath, 'wb') as f:
                f.write(base64.b64decode(binaryDataBase64))
            return picPath
        except Exception as e:
            op(f'[-]: 豆包文生图模型出现错误, 错误信息: {e}')
            return None

    def getAi(self, content):
        """
        处理优先级
        :param content:
        :return:
        """
        result = ''
        for i in range(1, 11):
            aiModule = self.aiPriority.get(i)
            if aiModule == 'hunYuan':
                result, self.hunYuanMessages = self.getHunYuanAi(content, self.hunYuanMessages)
            if aiModule == 'sparkAi':
                result = self.getSparkAi(content)
            if aiModule == 'openAi':
                result, self.openAiMessages = self.getOpenAi(content, self.openAiMessages)
            if aiModule == 'qianFan':
                result, self.qianFanMessages = self.getQianFanAi(content, self.qianFanMessages)
            if aiModule == 'kiMi':
                result, self.kimiMessages = self.getKiMiAi(content, self.kimiMessages)
            if aiModule == 'bigModel':
                result, self.bigModelMessages = self.getBigModel(content, self.bigModelMessages)
            if aiModule == 'deepSeek':
                result, self.deepSeekMessages = self.getDeepSeek(content, self.deepSeekMessages)
            if aiModule == 'ollama':
                result, self.ollamaMessages = self.getOllama(content, self.deepSeekMessages)
            if aiModule == 'siliconFlow':
                result, self.siliconFlowMessages = self.getSiliconFlow(content, self.siliconFlowMessages)
            if aiModule == 'douBao':
                result, self.douBaoMessages = self.getDouBao(content, self.douBaoMessages)
            if not result:
                continue
            else:
                break
        return result

    def getPicAi(self, content):
        """
        处理优先级
        :param content:
        :return:
        """
        picPath = ''
        for i in range(1, 4):
            aiPicModule = self.aiPicPriority.get(i)
            if aiPicModule == 'sparkAi':
                picPath = self.getSparkPic(content)
            if aiPicModule == 'qianFan':
                picPath = self.getQianFanPic(content)
            if aiPicModule == 'douBao':
                picPath = self.getDouBaoPic(content)
            if not picPath:
                continue
            else:
                break
        return picPath


if __name__ == '__main__':
    messages = []
    Ad = AiDialogue()
    # print(Ad.getPicAi('画一只布尔猫'))
    while 1:
        print(Ad.getAi(input('>> ')))
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
