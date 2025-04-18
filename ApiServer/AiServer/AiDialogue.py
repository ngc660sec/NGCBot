from ApiServer.AiServer.AiLLMDialogue import AiLLMDialogue
from Config.ConfigData import *
from OutPut.outPut import op
import requests


class AiDialogue:
    def __init__(self):
        configData = Cs.returnConfigData()
        self.Ald = AiLLMDialogue()
        # 初始化消息列表
        self.userChatDicts = {}

    def getOpenAi(self, content, messages):
        """
        OpenAi对话接口
        :param content:
        :param messages:
        :return:
        """
        op(f'[*]: 正在调用OpenAi对话接口... ...')
        if not getOpenAiConfig().get('OpenAiKey'):
            op(f'[-]: GPT模型未配置, 请检查相关配置!!!')
            return None, []
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": getOpenAiConfig().get('OpenAiModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {getOpenAiConfig().get('OpenAiKey')}",
        }
        try:
            resp = requests.post(url=getOpenAiConfig().get('OpenAiApi'), headers=headers, json=data, timeout=15)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: Gpt对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]

    def getSparkAi(self, content, messages):
        """
        星火大模型Ai 对话
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        op(f'[*]: 正在调用星火大模型对话接口... ...')
        if not getSparkConfig().get('SparkAiApi'):
            op(f'[-]: 星火大模型未配置, 请检查相关配置!!!')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": getSparkConfig().get('SparkModel'),
            "messages": messages,
            "tools": [
                {
                    "type": "web_search",
                    "web_search": {
                        "enable": True
                    }
                }
            ]
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {getSparkConfig().get('SparkAiKey')}",
        }
        try:
            resp = requests.post(url=getSparkConfig().get('SparkAiApi'), headers=headers, json=data, timeout=15)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: 星火大模型接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]

    def getQianFanAi(self, content, messages):
        """
        千帆模型 Ai对话
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        op(f'[*]: 正在调用千帆大模型对话接口... ...')
        messages.append({"role": "user", "content": content})
        if not getQianFanConfig().get('QfAccessKey') or not getQianFanConfig().get('QfSecretKey'):
            op(f'[-]: 千帆大模型未配置, 请检查相关配置!!!')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]

        def getAccessToken():
            try:
                headers = {
                    'Content-Type': 'application/json'
                }
                query = {
                    'grant_type': 'client_credentials',
                    'client_id': getQianFanConfig().get('QfAccessKey'),
                    'client_secret': getQianFanConfig().get('QfSecretKey'),
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
                    'messages': messages[1::],
                    'system': getSystemAiRole(),
                }
                resp = requests.post(url, json=data)
                result = resp.json()['result']
                messages.append({"role": "assistant", "content": result})
                return result, messages
            except Exception as e:
                op(f'[-]: 请求千帆模型AccessToken出现错误, 错误信息: {e}')
                return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]

        access_token = getAccessToken()
        if not access_token:
            op(f'[-]: 获取千帆模型AccessToken失败, 请检查千帆配置!!!')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]

        aiContent, messages = getAiContent(access_token, messages)
        return aiContent, messages

    def getHunYuanAi(self, content, messages):
        """
        腾讯混元模型 Ai对话接口
        :param content:
        :param messages:
        :return:
        """
        op(f'[*]: 正在调用混元对话接口... ...')
        if not getHunYuanConfig().get('HunYuanKey'):
            op(f'[-]: 混元模型未配置, 请检查相关配置!!!')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": getHunYuanConfig().get('HunYuanModel'),
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
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: 混元对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]

    def getKiMiAi(self, content, messages):
        """
        KiMi模型
        :param content:
        :param messages:
        :return:
        """
        op(f'[*]: 正在调用KiMi对话接口... ...')
        if not getKiMiConfig().get('KiMiKey'):
            op(f'[-]: KiMi模型未配置, 请检查相关配置!!!')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": getKiMiConfig().get('KiMiModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{getKiMiConfig().get('KiMiKey')}",
        }
        try:
            resp = requests.post(url=getKiMiConfig().get('KiMiApi'), headers=headers, json=data, timeout=15)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: KiMi对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]

    def getBigModel(self, content, messages):
        """
        BigModel
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        op(f'[*]: 正在调用BigModel对话接口... ...')
        if not getBigModelConfig().get('BigModelKey'):
            op(f'[-]: BigModel模型未配置, 请检查相关配置!!!')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": getBigModelConfig().get('BigModelModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {getBigModelConfig().get('BigModelKey')}",
        }
        try:
            resp = requests.post(url=getBigModelConfig().get('BigModelApi'), headers=headers, json=data, timeout=15)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: BigMode对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]

    def getDeepSeek(self, content, messages):
        """
        deepSeek
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        op(f'[*]: 正在调用DeepSeek对话接口... ...')
        if not getDeepSeekConfig().get('DeepSeekKey'):
            op(f'[-]: DeepSeek模型未配置, 请检查相关配置!!!')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": getDeepSeekConfig().get('DeepSeekModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {getDeepSeekConfig().get('DeepSeekKey')}",
        }
        try:
            resp = requests.post(url=getDeepSeekConfig().get('DeepSeekApi'), headers=headers, json=data, timeout=300)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: DeepSeek对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]

    def getOllama(self, content, messages):
        op(f'[*]: 正在调用Ollama本地对话接口... ...')
        if not getOllamaConfig().get('OllamaModel'):
            op(f'[-]: Ollama本地模型未配置, 请检查相关配置!!!')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": getOllamaConfig().get('OllamaModel'),
            'messages': messages,
            'stream': False
        }
        try:
            resp = requests.post(url=getOllamaConfig().get('OllamaApi'), json=data)
            jsonData = resp.json()
            assistant_content = jsonData['message']['content'].split('</think>')[-1].strip()
            return assistant_content, []
        except Exception as e:
            op(f'[-]: Ollama本地对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]

    def getSiliconFlow(self, content, messages):
        """
        硅基流动
        :param content:
        :param messages:
        :return:
        """
        op(f'[*]: 正在调用硅基流动对话接口... ...')
        if not getSiliconFlowConfig().get('SiliconFlowKey'):
            op(f'[-]: 硅基流动模型未配置, 请检查相关配置!!!')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": getSiliconFlowConfig().get('SiliconFlowModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {getSiliconFlowConfig().get('SiliconFlowKey')}",
        }
        try:
            resp = requests.post(url=getSiliconFlowConfig().get('SiliconFlowApi'), headers=headers, json=data,
                                 timeout=300)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: 硅基对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]

    def getVolcengine(self, content, messages):
        """
        火山引擎
        :param content:
        :param messages:
        :return:
        """
        op(f'[*]: 正在调用火山引擎文本大模型接口... ...')
        if not getVolcengineConfig().get('VolcengineKey'):
            op(f'[-]: 火山引擎文本大模型接口未配置')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]
        messages.append({"role": "user", "content": f'{content}'})
        headers = {
            "Authorization": f"Bearer {getVolcengineConfig().get('VolcengineKey')}",
            "Content-Type": "application/json"
        }
        data = {
            "model": getVolcengineConfig().get('VolcengineModel'),
            "messages": messages,
            "stream": False
        }
        try:
            resp = requests.post(getVolcengineConfig().get('VolcengineApi'), headers=headers, json=data)
            jsonData = resp.json()
            assistant_content = jsonData.get('choices')[0].get('message').get('content')
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: 火山引擎文本大模型接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]

    def getQwen(self, content, messages):
        """
        通义千问对话
        :param content:
        :param messages:
        :return:
        """
        op(f'[*]: 正在调用通义千问大模型接口... ...')
        if not getQwenConfig().get('QwenKey'):
            op(f'[-]: 通义千问接口未配置')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]
        messages.append({"role": "user", "content": f'{content}'})
        headers = {
            "Authorization": f"Bearer {getQwenConfig().get('QwenKey')}",
            "Content-Type": "application/json"
        }
        data = {
            "model": getQwenConfig().get('QwenModel'),
            "messages": messages,
            "stream": False,
            "enable_search": True
        }
        try:
            resp = requests.post(getQwenConfig().get('QwenApi'), headers=headers, json=data)
            jsonData = resp.json()
            assistant_content = jsonData.get('choices')[0].get('message').get('content')
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: 通义千问接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{getSystemAiRole()}'}]

    def getAi(self, content, sender, systemMessage=None):
        """
        处理优先级
        :param system_messages:
        :param sender:
        :param content:
        :return:
        """
        # 处理会话
        if sender not in self.userChatDicts:
            self.userChatDicts[sender] = [{"role": "system", "content": f'{getSystemAiRole()}'}]
            if systemMessage:
                self.userChatDicts[sender] = systemMessage
        result = ''
        for i in range(1, 15):
            aiModule = getaiPriority().get(i)
            if aiModule == 'hunYuan':
                result, self.userChatDicts[sender] = self.getHunYuanAi(content, self.userChatDicts[sender])
            if aiModule == 'sparkAi':
                result, self.userChatDicts[sender] = self.getSparkAi(content, self.userChatDicts[sender])
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
            if aiModule == 'coze':
                result = self.Ald.getCoze(content, sender)
            if aiModule == 'dify':
                result = self.Ald.getDify(content, sender)
            if aiModule == 'fastgpt':
                result = self.Ald.getFastGpt(content, sender)
            if not result:
                continue
            else:
                break
        if len(self.userChatDicts[sender]) == 21:
            del self.userChatDicts[sender][1]
            del self.userChatDicts[sender][2]
        return result.strip()


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
