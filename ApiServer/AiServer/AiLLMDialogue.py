from ApiServer.InterFaceServer import *
import Config.ConfigServer as Cs
from OutPut.outPut import op
import requests
import time
import json

class AiLLMDialogue:
    def __init__(self):
        configData = Cs.returnConfigData()
        self.systemAiRole = configData['AiConfig']['SystemAiRule']
        self.CozeUserSession = {}
        self.DifyUserSession = {}
        # Coze配置
        self.CozeConfig = {
            'CozeToken': configData['AiConfig']['CozeConfig']['CozeToken'],
            'CozeBotId': configData['AiConfig']['CozeConfig']['CozeBotId'],
        }
        # Dify配置
        self.DifyConfig = {
            'DifyApi': configData['AiConfig']['DifyConfig']['DifyApi'],
            'DifyKey': configData['AiConfig']['DifyConfig']['DifyKey'],
        }
        # Fastgpt配置
        self.FastgptConfig = {
            'FastgptApi': configData['AiConfig']['FastgptConfig']['FastgptApi'],
            'FastgptKey': configData['AiConfig']['FastgptConfig']['FastgptKey'],
            'FastgptAppid': configData['AiConfig']['FastgptConfig']['FastAppid']
        }

    def getCoze(self, content, userId, filePath=None):
        """
        扣子对话接口
        :param content:
        :param userId:
        :return:
        """
        if not filePath:
            op(f'[*]: 正在调用扣子会话接口... ...')
        else:
            op(f'[*]: 正在调用扣子图文对话接口... ...')
        headers = {
            'Authorization': self.CozeConfig['CozeToken'],
            'Content-Type': 'application/json'
        }
        if not self.CozeConfig.get('CozeBotId'):
            op(f'[-]: Coze接口未配置, 请检查相关配置！')
            return None
        def createChat():
            """
            创建扣子会话
            :return:
            """
            createChatApi = 'https://api.coze.cn/v1/conversation/create'
            try:
                resp = requests.post(createChatApi, headers=headers)
                jsonData = resp.json()
                conversationId = jsonData.get('data').get('id')
                if conversationId:
                    return conversationId
                return None
            except Exception as e:
                op(f'[-]: 创建扣子会话出现错误, 错误信息: {e}')
                return None

        def uploadFile(filePath):
            """
            上传扣子文件
            :param filePath:
            :return:
            """
            uploadFileApi = 'https://api.coze.cn/v1/files/upload'
            headers = {
                'Authorization': self.CozeConfig['CozeToken'],
            }
            try:
                with open(filePath, mode='rb') as f:
                    files = {
                        'file': (filePath, f)
                    }
                    resp = requests.post(uploadFileApi, headers=headers, files=files)
                    jsonData = resp.json()
                    fileId = jsonData.get('data').get('id')
                    return fileId
            except Exception as e:
                op(f'[-]: 上传扣子文件出现错误, 错误信息: {e}')
                return None

        def sendChat(conversationId, userId, content):
            """
            发起扣子对话
            :param conversationId:
            :param userId:
            :return:
            """
            sendChatApi = f'https://api.coze.cn/v3/chat?conversation_id={conversationId}'
            additional_messages = [
                {
                    'content': content,
                    'content_type': 'text',
                    'role': 'user',
                    'type': 'question'
                }
            ]
            if filePath:
                fileId = uploadFile(filePath)
                content = [
                    {
                        'type': 'text',
                        'text': content
                    },
                    {
                        'type': 'image',
                        'file_id': fileId
                    }
                ]
                additional_messages = [{
                    'content': json.dumps(content),
                    'content_type': 'object_string',
                    'role': 'user',
                    'type': 'answer'
                }]
            data = {
                'bot_id': self.CozeConfig['CozeBotId'],
                'user_id': userId,
                'stream': False,
                'additional_messages': additional_messages
            }
            try:
                resp = requests.post(sendChatApi, headers=headers, json=data)
                jsonData = resp.json()
                chatId = jsonData.get('data').get('id')
                if chatId:
                    return chatId
                return None
            except Exception as e:
                op(f'[-]: 发起扣子对话出现错误, 错误信息: {e}')
                return None

        def retrieveChat(conversationId, chatId):
            """
            查看对话详情状态
            :param conversationId:
            :param chatId:
            :return:
            """
            retrieveChatApi = f'https://api.coze.cn/v3/chat/retrieve?conversation_id={conversationId}&chat_id={chatId}'
            try:
                resp = requests.get(retrieveChatApi, headers=headers)
                jsonData = resp.json()
                status = jsonData.get('data').get('status')
                if status != 'completed':
                    return False
                return True
            except Exception as e:
                op(f'[-]: 查看扣子对话详情状态出现错误, 错误信息: {e}')
                return False


        def showChatMessage(conversationId, chatId):
            """
            查看扣子对话内容
            :param conversationId:
            :param chatId:
            :return:
            """
            showChatMessageApi = f'https://api.coze.cn/v3/chat/message/list?conversation_id={conversationId}&chat_id={chatId}'
            try:
                resp = requests.get(showChatMessageApi, headers=headers)
                jsonData = resp.json()
                dataList = jsonData.get('data')
                for data in dataList:
                    type = data.get('type')
                    content_type = data.get('content_type')
                    if type == 'answer' and content_type == 'text':
                        content = data.get('content').strip()
                        return content
                return None
            except Exception as e:
                op(f'[-]: 查看扣子对话内容出现错误, 错误信息: {e}')
                return None
        if userId not in self.CozeUserSession.keys():
            conversationId = createChat()
            if not conversationId:
                return None
            self.CozeUserSession[userId] = conversationId

        chatId = sendChat(conversationId=self.CozeUserSession[userId], userId=userId, content=content)
        messageState = False
        if not chatId:
            return None
        for i in range(10):
            messageState = retrieveChat(conversationId=self.CozeUserSession[userId], chatId=chatId)
            if messageState:
                break
            time.sleep(3)
        if not messageState:
            return None
        message = showChatMessage(conversationId=self.CozeUserSession[userId], chatId=chatId)
        if ('##' in message and '![' in message) or '](http' in message:
            message = Ifa.textToCard(title=content, mdContent=message)
        return message

    def getDify(self, content, userId, filePath=None):
        """
        Dify对话接口
        :param content:
        :param userId:
        :return:
        """
        if not filePath:
            op(f'[*]: 正在调用Dify会话接口... ...')
        else:
            op(f'[*]: 正在调用Dify图文对话接口... ...')
        if not self.DifyConfig.get('DifyKey'):
            op(f'[-]: Dify接口未配置')
            return None
        headers = {
            'Authorization': self.DifyConfig['DifyKey'],
            'Content-Type': 'application/json'
        }

        def uploadFile(filePath):
            headers = {
                "Authorization": f"{self.DifyConfig.get('DifyKey')}",
            }
            file_name = filePath.split('/')[-1]
            file_extension = file_name.split('.')[-1].lower()
            supported_types = {
                'png': 'image/png',
                'jpeg': 'image/jpeg',
                'jpg': 'image/jpeg',
                'webp': 'image/webp',
                'gif': 'image/gif'
            }
            try:
                if file_extension not in supported_types:
                    op(f"[-]: 不支持的文件类型: {file_extension}. 仅支持: {', '.join(supported_types.keys())}")
                    return None
                mime_type = supported_types[file_extension]
                with open(filePath, 'rb') as file:
                    files = {
                        'file': (file_name, file, mime_type),
                    }
                    data = {
                        'user': f"{userId}"
                    }
                    resp = requests.post(url='https://api.dify.ai/v1/files/upload', headers=headers, files=files,
                                         data=data)
                    jsondata = resp.json()
                    picid = jsondata['id']
                    return picid
            except Exception as e:
                op(f'[-]: Dify上传文件出现错误, 错误信息: {e}')
                return None

        def getDifyMessage(content, userId, conversation_id, picid=None):
            if not conversation_id:
                conversation_id = ''
            data = {
                "query": content,
                "inputs": {},
                "response_mode": "blocking",
                "user": f"{userId}",
                "conversation_id": f"{conversation_id}",
            }
            if picid:
                data = {
                    "query": content,
                    "inputs": {},
                    "response_mode": "blocking",
                    "user": f"{userId}",
                    "conversation_id": f"{conversation_id}",
                    "files": [
                        {
                            "type": "image",
                            "transfer_method": "local_file",
                            "upload_file_id": f"{picid}"
                        }
                    ]
                }
            try:
                resp = requests.post(url=self.DifyConfig.get('DifyApi'), headers=headers, json=data, timeout=60)
                json_data = resp.json()
                assistant_content = json_data['answer']
                if not conversation_id:
                    self.DifyUserSession[userId] = json_data["conversation_id"]
                return assistant_content
            except Exception as e:
                op(f'[-]: Dify对话接口出现错误, 错误信息: {e}')
                return None

        if filePath:
            picid = uploadFile(filePath)
            if not picid:
                return None
            message = getDifyMessage(content, userId, self.DifyUserSession.get(userId), picid)
        else:
            message = getDifyMessage(content, userId, self.DifyUserSession.get(userId))
        if ('##' in message and '![' in message) or '](http' in message:
            message = Ifa.textToCard(title=content, mdContent=message)
        return message

    def getFastgpt(self, content, userId):
        """
        Dify对话接口
        :param content:
        :param userId:
        :return:
        """
        op(f'[*]: 正在调用Fastgpt会话接口... ...')
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.FastgptConfig.get('FastgptKey')}",
        }
        if not self.FastgptConfig.get('FastgptKey'):
            op(f'[-]: Fastgpt模型未配置, 请检查相关配置!!!')
            return None
        data = {
            "chatId": f"{userId}",
            "stream": False,
            "detail": False,
            "messages": [
                {
                    "role": "user",
                    "content": f"{content}"
                }]
        }
        try:
            resp = requests.post(url=self.FastgptConfig.get('FastgptApi'), headers=headers, json=data, timeout=15)
            json_data = resp.json()
            assistant_content = json_data.get('choices')[0].get('message').get('content')
            return assistant_content
        except Exception as e:
            op(f'[-]: Fastgpt对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

if __name__ == '__main__':
    AlD = AiLLMDialogue()
    print(AlD.getCoze('这张图描述了什么', 'wxid_123', filePath='C:\\Users\\admin\\Desktop\\NGCBot-Beta\\FileCache\\picCacheFolder\\1742899976449.jpg'))
    # print(AlD.getDify('用友U8有什么漏洞', 'wxid_333'))
    # print(AlD.getFastgpt('你好', 'wxid_333'))