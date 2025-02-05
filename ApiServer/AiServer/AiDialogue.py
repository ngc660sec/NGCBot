from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
from tencentcloud.common.profile.http_profile import HttpProfile
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
from tencentcloud.common import credential
import ApiServer.AiServer.sparkPicApi as sPa
import FileCache.FileCacheServer as Fcs
import Config.ConfigServer as Cs
from OutPut.outPut import op
import requests
import time
import json
import ollama


class AiDialogue:
    def __init__(self):

        configData = Cs.returnConfigData()
        self.systemAiRole = configData['apiServer']['aiConfig']['systemAiRule']
        self.openAiConfig = {'openAiApi': configData['apiServer']['aiConfig']['openAi']['openAiApi'],
                             'openAiKey': configData['apiServer']['aiConfig']['openAi']['openAiKey']}
        self.sparkAiConfig = {'sparkAiApi': configData['apiServer']['aiConfig']['sparkApi']['sparkAiApi'],
                              'sparkAiAppid': configData['apiServer']['aiConfig']['sparkApi']['sparkAiAppid'],
                              'sparkAiSecret': configData['apiServer']['aiConfig']['sparkApi']['sparkAiSecret'],
                              'sparkAiKey': configData['apiServer']['aiConfig']['sparkApi']['sparkAiKey'],
                              'sparkDomain': configData['apiServer']['aiConfig']['sparkApi']['sparkDomain']}
        self.qianfanAiConfig = {
            'qfAccessKey': configData['apiServer']['aiConfig']['qianFan']['qfAccessKey'],
            'qfSecretKey': configData['apiServer']['aiConfig']['qianFan']['qfSecretKey'],
            'qfAppid': configData['apiServer']['aiConfig']['qianFan']['qfAppid'],
            'qfPicAccessKey': configData['apiServer']['aiConfig']['qianFan']['qfPicAccessKey'],
            'qfPicSecretKey': configData['apiServer']['aiConfig']['qianFan']['qfPicSecretKey'],
            'qfPicAppid': configData['apiServer']['aiConfig']['qianFan']['qfPicAppid'],
        }
        self.hunYuanAiConfig = {
            'hunYuanSecretId': configData['apiServer']['aiConfig']['hunYuan']['hunYuanSecretId'],
            'hunYuanSecretKey': configData['apiServer']['aiConfig']['hunYuan']['hunYuanSecretKey']
        }
        self.kiMiConfig = {
            'kiMiApi': configData['apiServer']['aiConfig']['kiMi']['kiMiApi'],
            'kiMiKey': configData['apiServer']['aiConfig']['kiMi']['kiMiKey']
        }
        self.bigModelConfig = {
            'bigModelApi': configData['apiServer']['aiConfig']['bigModel']['bigModelApi'],
            'bigModelKey': configData['apiServer']['aiConfig']['bigModel']['bigModelKey'],
        }
        self.deepSeekConfig = {
            'deepSeekApi': configData['apiServer']['aiConfig']['deepSeek']['deepSeekApi'],
            'deepSeekKey': configData['apiServer']['aiConfig']['deepSeek']['deepSeekKey'],
        }
        self.localDeepSeekModel = configData['apiServer']['aiConfig']['localDeepSeek']['deepSeekmodel']
        self.openAiMessages = [{"role": "system", "content": f'{self.systemAiRole}'}]
        self.qianFanMessages = [{"role": "system", "content": f'{self.systemAiRole}'}]
        self.hunYuanMessages = [{"Role": "system", "Content": f'{self.systemAiRole}'}]
        self.kimiMessages = [{"Role": "system", "Content": f'{self.systemAiRole}'}]
        self.bigModelMessages = [{"role": "system", "Content": f'{self.systemAiRole}'}]
        self.deepSeekMessages = [{"role": "system", "content": f'{self.systemAiRole}'}]
        self.aiPriority = configData['apiServer']['aiConfig']['aiPriority']
        self.aiPicPriority = configData['apiServer']['aiConfig']['aiPicPriority']

    def getOpenAi(self, content, messages):
        op(f'[*]: 正在调用OpenAi对话接口... ...')
        """
        Open Ai对话
        :param OpenAiConfig: OpenAi 配置字典
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        if not self.openAiConfig.get('openAiKey'):
            op(f'[-]: GPT模型未配置, 请检查相关配置!!!')
            return None, []
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.openAiConfig.get('openAiKey')}",
        }
        try:
            resp = requests.post(url=self.openAiConfig.get('openAiApi'), headers=headers, json=data, timeout=15)
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
        SparkAppid = self.sparkAiConfig.get('sparkAiAppid')
        SparkSecret = self.sparkAiConfig.get('sparkAiSecret')
        SParkApiKey = self.sparkAiConfig.get('sparkAiKey')
        SParkApi = self.sparkAiConfig.get('sparkAiApi')
        SParkDomain = self.sparkAiConfig.get('sparkDomain')
        try:
            spark = ChatSparkLLM(
                spark_api_url=SParkApi,
                spark_app_id=SparkAppid,
                spark_api_key=SParkApiKey,
                spark_api_secret=SparkSecret,
                spark_llm_domain=SParkDomain,
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
            res = sPa.main(content, self.sparkAiConfig.get('sparkAiAppid'), self.sparkAiConfig.get('sparkAiKey'),
                           self.sparkAiConfig.get('sparkAiSecret'))
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
        if not self.qianfanAiConfig.get('qfAccessKey') or not self.qianfanAiConfig.get('qfSecretKey'):
            op(f'[-]: 千帆大模型未配置, 请检查相关配置!!!')
            return None, []

        def getAccessToken():
            try:
                headers = {
                    'Content-Type': 'application/json'
                }
                query = {
                    'grant_type': 'client_credentials',
                    'client_id': self.qianfanAiConfig.get('qfAccessKey'),
                    'client_secret': self.qianfanAiConfig.get('qfSecretKey'),
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
                    'client_id': self.qianfanAiConfig.get('qfPicAccessKey'),
                    'client_secret': self.qianfanAiConfig.get('qfPicSecretKey'),
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
            cred = credential.Credential(self.hunYuanAiConfig.get('hunYuanSecretId'),
                                         self.hunYuanAiConfig.get('hunYuanSecretKey'))
            httpProfile = HttpProfile()
            httpProfile.endpoint = "hunyuan.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = hunyuan_client.HunyuanClient(cred, "ap-beijing", clientProfile)
            req = models.ChatCompletionsRequest()
            messages.append({'Role': 'user', 'Content': content})
            params = {
                "Model": "hunyuan-pro",
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
        op(f'[*]: 正在调用kiMi对话接口... ...')
        """
        kiMi Ai对话
        :param OpenAiConfig: kiMi 配置字典
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        if not self.kiMiConfig.get('kiMiKey'):
            op(f'[-]: kiMi模型未配置, 请检查相关配置!!!')
            return None, []
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": "moonshot-v1-8k",
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.kiMiConfig.get('kiMiKey')}",
        }
        try:
            resp = requests.post(url=self.kiMiConfig.get('kiMiApi'), headers=headers, json=data, timeout=15)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: kiMi对话接口出现错误, 错误信息: {e}')
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
        if not self.bigModelConfig.get('bigModelKey'):
            op(f'[-]: BigModel模型未配置, 请检查相关配置!!!')
            return None, []
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": "glm-4-plus",
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.bigModelConfig.get('bigModelKey')}",
        }
        try:
            resp = requests.post(url=self.bigModelConfig.get('bigModelApi'), headers=headers, json=data, timeout=15)
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
        op(f'[*]: 正在调用deepSeek对话接口... ...')
        if not self.deepSeekConfig.get('deepSeekKey'):
            op(f'[-]: deepSeek模型未配置, 请检查相关配置!!!')
            return None, []
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": "deepseek-chat",
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.deepSeekConfig.get('deepSeekKey')}",
        }
        try:
            resp = requests.post(url=self.deepSeekConfig.get('deepSeekApi'), headers=headers, json=data, timeout=300)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: deepSeek对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getLocalDeepSeek(self, content, messages):
        """
        deepSeek
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        op(f'[*]: 正在调用deepSeek本地对话接口... ...')
        if not self.localDeepSeekModel:
            op(f'[-]: deepSeek本地模型未配置, 请检查相关配置!!!')
            return None, []
        messages.append({"role": "user", "content": f'{content}'})
        try:
            resp = ollama.chat(model=self.localDeepSeekModel, messages=messages)
            assistant_content = resp.message.content
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: deepSeek本地对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getAi(self, content):
        """
        处理优先级
        :param content:
        :return:
        """
        result = ''
        for i in range(1, 9):
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
            if aiModule == 'localDeepSeek':
                result, self.deepSeekMessages = self.getLocalDeepSeek(content, self.deepSeekMessages)
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
        for i in range(1, 3):
            aiPicModule = self.aiPicPriority.get(i)
            if aiPicModule == 'sparkAi':
                picPath = self.getSparkPic(content)
            if aiPicModule == 'qianFan':
                picPath = self.getQianFanPic(content)
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
