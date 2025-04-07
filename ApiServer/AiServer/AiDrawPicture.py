from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
from tencentcloud.common.profile.http_profile import HttpProfile
from volcengine.visual.VisualService import VisualService
from tencentcloud.common import credential
import FileCache.FileCacheServer as Fcs
from ApiServer.InterFaceServer import *
import Config.ConfigServer as Cs
from OutPut.outPut import op
import requests
import base64
import time
import json



class AiDrawPicture:
    def __init__(self):
        configData = Cs.returnConfigData()
        self.systemAiRole = configData['AiConfig']['SystemAiRule']
        # 百度千帆配置
        self.QianfanAiConfig = {
            'QfPicAccessKey': configData['AiConfig']['QianFanConfig']['QfPicAccessKey'],
            'QfPicSecretKey': configData['AiConfig']['QianFanConfig']['QfPicSecretKey'],
        }
        # 豆包配置
        self.VolcengineConfig = {
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
        # 腾讯混元配置
        self.HunYuanAiConfig = {
            'HunYuanSecretId': configData['AiConfig']['HunYuanConfig']['HunYuanSecretId'],
            'HunYuanSecretKey': configData['AiConfig']['HunYuanConfig']['HunYuanSecretKey'],
            'HunYuanPicStyle': configData['AiConfig']['HunYuanConfig']['HunYuanPicStyle'],
        }

        # 初始化消息列表
        self.userChatDicts = {}

        # AI画图优先级配置
        self.aiPicPriority = configData['AiConfig']['AiPicPriority']

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
                'Authorization': f"Bearer {self.QwenConfig.get('QwenKey')}"
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
            'Authorization': f"Bearer {self.QwenConfig.get('QwenKey')}",
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
            imgPath = Ifa.downloadFile(imgUrl, savePath)
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
                "Authorization": f"Bearer {self.BigModelConfig.get('BigModelKey')}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.BigModelConfig.get('BigModelPicModel'),
                "prompt": content,
            }
            resp = requests.post(self.BigModelConfig.get('BigModelPicApi'), headers=headers, json=data)
            ImgUrl = resp.json()['data'][0]['url']
            savePath = Fcs.returnAiPicFolder() + '/' + str(int(time.time() * 1000)) + '.jpg'
            imgPath = Ifa.downloadFile(ImgUrl, savePath)
            if imgPath:
                return imgPath
            return None
        except Exception as e:
            op(f'[-]: 智谱文生图模型出现错误, 错误信息: {e}')
            return None

    def getHunYuanPic(self, content):
        """
        混元文生图
        :param content:
        :return:
        """

        def getJobId(jobId, client):
            """
            查询Job ID
            :param jobId:
            :return:
            """

            try:
                params = {
                    "JobId": jobId
                }
                req = models.QueryHunyuanImageJobRequest()
                req.from_json_string(json.dumps(params))
                resp = client.QueryHunyuanImageJob(req)
                jsonData = json.loads(resp.to_json_string())
                resultImages = jsonData.get('ResultImage')
                if not resultImages:
                    return None
                else:
                    return resultImages[0]
            except Exception as e:
                op(f'[-]: 查询混元JobId出现错误, 错误信息: {e}')
                return None
        try:
            op(f'[*]: 正在调用混元文生图模型... ...')
            if not self.HunYuanAiConfig.get('HunYuanSecretId'):
                op(f'[-]: 混元文生图模型未配置, 请检查相关配置!!!')
                return None
            cred = credential.Credential(self.HunYuanAiConfig.get('HunYuanSecretId'),
                                         self.HunYuanAiConfig.get('HunYuanSecretKey'))
            httpProfile = HttpProfile()
            httpProfile.endpoint = "hunyuan.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = hunyuan_client.HunyuanClient(cred, "ap-guangzhou", clientProfile)
            req = models.SubmitHunyuanImageJobRequest()
            params = {
                "Prompt": content,
                "Style": self.HunYuanAiConfig.get('HunYuanPicStyle')
            }
            req.from_json_string(json.dumps(params))
            resp = client.SubmitHunyuanImageJob(req)
            jobId = json.loads(resp.to_json_string()).get('JobId')
            imageUrl = ''
            if jobId:
                for i in range(5):
                    imageUrl = getJobId(jobId, client)
                    if not imageUrl:
                        time.sleep(10)
                        continue
                    else:
                        break
            if not imageUrl:
                return None
            filePath = Fcs.returnAiPicFolder() + '/' + str(int(time.time() * 1000)) + '.jpg'
            imgPath = Ifa.downloadFile(imageUrl, filePath)
            if imgPath:
                return imgPath
            return None
        except Exception as e:
            op(f'[-]: 混元文生图模型出现错误, 错误信息: {e}')
            return None

    def getPicAi(self, content):
        """
        处理优先级
        :param content:
        :return:
        """
        picPath = ''
        for i in range(1, 6):
            aiPicModule = self.aiPicPriority.get(i)
            if aiPicModule == 'qianFan':
                picPath = self.getQianFanPic(content)
            if aiPicModule == 'volcengine':
                picPath = self.getVolcenginePic(content)
            if aiPicModule == 'qwen':
                picPath = self.getQwenPic(content)
            if aiPicModule == 'bigModel':
                picPath = self.getBigModelPic(content)
            if aiPicModule == 'hunYuan':
                picPath = self.getHunYuanPic(content)
            if not picPath:
                continue
            else:
                break
        return picPath


if __name__ == '__main__':
    Adp = AiDrawPicture()
    # print(Adp.getPicAi('一只可爱的布尔猫'))
    print(Adp.getHunYuanPic('一个穿着超短裙的JK妹妹的全身照, 黑丝白袜小皮鞋'))