from BotServer.BotFunction.InterfaceFunction import *
import FileCache.FileCacheServer as Fcs
import Config.ConfigServer as Cs
from OutPut.outPut import op
from threading import Timer
import json
import requests
import time


class goFishingGame:
    """
    钓鱼游戏
    """

    def __init__(self):
        configData = Cs.returnConfigData()
        self.Administrators = configData['SystemConfig']['wxid_7bizfilssbwi22']
        self.fishingApi = configData['FunctionConfig']['GameFunctionConfig']['FishingConfig']['FishingApi']

    def _post(self, endpoint, data):
        """通用 POST 请求方法"""
        url = f"{self.fishingApi}{endpoint}"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=data)
        return response

