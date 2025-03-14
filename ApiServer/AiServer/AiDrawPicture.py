from volcengine.visual.VisualService import VisualService
import FileCache.FileCacheServer as Fcs
import Config.ConfigServer as Cs
from OutPut.outPut import op
import requests
import base64
import time


class AiDrawPicture:
    def __init__(self):
        configData = Cs.returnConfigData()
        self.systemAiRole = configData['AiConfig']['SystemAiRule']
        # 百度千帆配置
        self.QianfanAiConfig = {
            'QfAccessKey': configData['AiConfig']['QianFanConfig']['QfAccessKey'],
            'QfSecretKey': configData['AiConfig']['QianFanConfig']['QfSecretKey'],
            'QfAppid': configData['AiConfig']['QianFanConfig']['QfAppid'],
            'QfPicAccessKey': configData['AiConfig']['QianFanConfig']['QfPicAccessKey'],
            'QfPicSecretKey': configData['AiConfig']['QianFanConfig']['QfPicSecretKey'],
            'QfPicAppid': configData['AiConfig']['QianFanConfig']['QfPicAppid']
        }
        # 豆包配置
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
            'QwenPicApi': configData['AiConfig']['QwenConfig']['QwenPicApi'],
            'QwenPicModel': configData['AiConfig']['QwenConfig']['QwenPicModel'],
            'QwenKey': configData['AiConfig']['QwenConfig']['QwenKey'],
        }
        # 智谱配置
        self.BigModelConfig = {
            'BigModelPicApi': configData['AiConfig']['BigModelConfig']['BigModelPicApi'],
            'BigModelPicModel': configData['AiConfig']['BigModelConfig']['BigModelPicModel'],
            'BigModelKey': configData['AiConfig']['BigModelConfig']['BigModelKey'],
        }

        # 初始化消息列表
        self.userChatDicts = {}

        # AI画图优先级配置
        self.aiPicPriority = configData['AiConfig']['AiPicPriority']

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

    def getVolcenginePic(self, content):
        op(f'[*]: 正在调用火山引擎文生图模型... ...')
        if not self.VolcengineConfig.get('VolcengineAk'):
            op(f'[-]: 火山引擎文生图模型未配置, 请检查相关配置!!!')
            return None
        visual_service = VisualService()
        visual_service.set_ak(self.VolcengineConfig.get('VolcengineAk'))
        visual_service.set_sk(self.VolcengineConfig.get('VolcengineSk'))
        data = {
            'req_key': self.VolcengineConfig.get('VolcengineReqKey'),
            'model_version': self.VolcengineConfig.get('VolcenginePicModelVersion'),
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
            op(f'[-]: 火山引擎文生图模型出现错误, 错误信息: {e}')
            return None

    def getQwenPic(self, content):
        """
        通义千问文生图
        :param content:
        :return:
        """
        op(f'[*]: 正在调用通义千问文生图模型... ...')

        def getTaskStatus(taskId):
            headers = {
                'Authorization': self.QwenConfig.get('QwenKey')
            }
            taskApi = f'https://dashscope.aliyuncs.com/api/v1/tasks/{taskId}'
            try:
                resp = requests.get(taskApi, headers=headers)
                jsonData = resp.json()
                output = jsonData.get('output')
                task_status = output.get('task_status')
                if task_status == 'FAILED':
                    return None
                results = output.get('results')
                actual_prompt = results[0].get('actual_prompt')
                imgUrl = results[0].get('url')
                if imgUrl:
                    return imgUrl
            except Exception:
                return None

        if not self.QwenConfig.get('QwenKey'):
            op(f'[-]: 通义千问文生图模型未配置, 请检查相关配置!!!')
            return None
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.QwenConfig.get('QwenKey'),
            'X-DashScope-Async': 'enable'
        }
        data = {
            'model': self.QwenConfig.get('QwenPicModel'),
            'input': {
                'prompt': content
            },
            'parameters': {
                'size': '1024*1024',
                'n': 1
            }
        }
        try:
            resp = requests.post(self.QwenConfig.get('QwenPicApi'), headers=headers, json=data)
            jsonData = resp.json()
            task_id = jsonData.get('output').get('task_id')
            if not task_id:
                return None
            imgUrl = ''
            for i in range(10):
                imgUrl = getTaskStatus(task_id)
                time.sleep(5)
                if imgUrl:
                    break
            if not imgUrl:
                return None
            savePath = Fcs.returnAiPicFolder() + '/' + str(int(time.time() * 1000)) + '.jpg'
            imgPath = self.downloadFile(imgUrl, savePath)
            if imgPath:
                return imgPath
            return None
        except Exception as e:
            op(f'[-]: 火山引擎文生图模型出现错误, 错误信息: {e}')
            return None

    def getBigModelPic(self, content):
        """
        智谱文生图
        :param content:
        :return:
        """
        op(f'[*]: 正在调用智谱文生图模型... ...')
        if not self.BigModelConfig.get('BigModelKey'):
            op(f'[-]: 智谱文生图模型未配置, 请检查相关配置!!!')
            return None
        try:
            headers = {
                "Authorization": self.BigModelConfig.get('BigModelKey'),
                "Content-Type": "application/json"
            }
            data = {
                "model": self.BigModelConfig.get('BigModelPicModel'),
                "prompt": content,
            }
            resp = requests.post(self.BigModelConfig.get('BigModelPicApi'), headers=headers, json=data)
            ImgUrl = resp.json()['data'][0]['url']
            savePath = Fcs.returnAiPicFolder() + '/' + str(int(time.time() * 1000)) + '.jpg'
            imgPath = self.downloadFile(ImgUrl, savePath)
            if imgPath:
                return imgPath
            return None
        except Exception as e:
            op(f'[-]: 智谱文生图模型出现错误, 错误信息: {e}')
            return None

    def getPicAi(self, content):
        """
        处理优先级
        :param content:
        :return:
        """
        picPath = ''
        for i in range(1, 5):
            aiPicModule = self.aiPicPriority.get(i)
            if aiPicModule == 'qianFan':
                picPath = self.getQianFanPic(content)
            if aiPicModule == 'volcengine':
                picPath = self.getVolcenginePic(content)
            if aiPicModule == 'qwen':
                picPath = self.getQwenPic(content)
            if aiPicModule == 'bigModel':
                picPath = self.getBigModelPic(content)
            if not picPath:
                continue
            else:
                break
        return picPath


if __name__ == '__main__':
    Adp = AiDrawPicture()
    print(Adp.getPicAi('一只可爱的布尔猫'))
