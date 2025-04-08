import Config.ConfigServer as Cs


def getOpenAiConfig():
    """
    获取OpenAi配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return {
        'OpenAiApi': configData['AiConfig']['OpenAiConfig']['OpenAiApi'],
        'OpenAiKey': configData['AiConfig']['OpenAiConfig']['OpenAiKey'],
        'OpenAiModel': configData['AiConfig']['OpenAiConfig']['OpenAiModel']
    }


def getSparkConfig():
    """
    获取星火配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return {
        'SparkAiApi': configData['AiConfig']['SparkConfig']['SparkAiApi'],
        'SparkAiKey': configData['AiConfig']['SparkConfig']['SparkAiKey'],
        'SparkModel': configData['AiConfig']['SparkConfig']['SparkModel'],
    }


def getQianFanConfig():
    """
    获取千帆配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return {
        'QfAccessKey': configData['AiConfig']['QianFanConfig']['QfAccessKey'],
        'QfSecretKey': configData['AiConfig']['QianFanConfig']['QfSecretKey'],
        'QfPicAccessKey': configData['AiConfig']['QianFanConfig']['QfPicAccessKey'],
        'QfPicSecretKey': configData['AiConfig']['QianFanConfig']['QfPicSecretKey'],
    }


def getHunYuanConfig():
    """
    获取混元配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return {
        'HunYuanApi': configData['AiConfig']['HunYuanConfig']['HunYuanApi'],
        'HunYuanKey': configData['AiConfig']['HunYuanConfig']['HunYuanKey'],
        'HunYuanModel': configData['AiConfig']['HunYuanConfig']['HunYuanModel'],
        'HunYuanSecretId': configData['AiConfig']['HunYuanConfig']['HunYuanSecretId'],
        'HunYuanSecretKey': configData['AiConfig']['HunYuanConfig']['HunYuanSecretKey'],
        'HunYuanPicStyle': configData['AiConfig']['HunYuanConfig']['HunYuanPicStyle'],
        'HunYuanPicChatModel': configData['AiConfig']['HunYuanConfig']['HunYuanPicChatModel']
    }


def getKiMiConfig():
    """
    获取KiMi配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return {
        'KiMiApi': configData['AiConfig']['KiMiConfig']['KiMiApi'],
        'KiMiKey': configData['AiConfig']['KiMiConfig']['KiMiKey'],
        'KiMiModel': configData['AiConfig']['KiMiConfig']['KiMiModel'],
        'KiMiPicModel': configData['AiConfig']['KiMiConfig']['KiMiPicModel']
    }


def getBigModelConfig():
    """
    获取BigModel配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return {
        'BigModelApi': configData['AiConfig']['BigModelConfig']['BigModelApi'],
        'BigModelKey': configData['AiConfig']['BigModelConfig']['BigModelKey'],
        'BigModelModel': configData['AiConfig']['BigModelConfig']['BigModelModel'],
        'BigModelPicApi': configData['AiConfig']['BigModelConfig']['BigModelPicApi'],
        'BigModelPicModel': configData['AiConfig']['BigModelConfig']['BigModelPicModel'],
    }


def getDeepSeekConfig():
    """
    获取DeepSeek配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return {
        'DeepSeekApi': configData['AiConfig']['DeepSeekConfig']['DeepSeekApi'],
        'DeepSeekKey': configData['AiConfig']['DeepSeekConfig']['DeepSeekKey'],
        'DeepSeekModel': configData['AiConfig']['DeepSeekConfig']['DeepSeekModel']
    }


def getOllamaConfig():
    """
    获取Ollama配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return {
        'OllamaApi': configData['AiConfig']['OllamaConfig']['OllamaApi'],
        'OllamaModel': configData['AiConfig']['OllamaConfig']['OllamaModel']
    }


def getSiliconFlowConfig():
    """
    获取硅基流动配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return {
        'SiliconFlowApi': configData['AiConfig']['SiliconFlowConfig']['SiliconFlowApi'],
        'SiliconFlowKey': configData['AiConfig']['SiliconFlowConfig']['SiliconFlowKey'],
        'SiliconFlowModel': configData['AiConfig']['SiliconFlowConfig']['SiliconFlowModel']
    }


def getVolcengineConfig():
    """
    获取火山引擎配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return {
        'VolcengineApi': configData['AiConfig']['VolcengineConfig']['VolcengineApi'],
        'VolcengineKey': configData['AiConfig']['VolcengineConfig']['VolcengineKey'],
        'VolcengineModel': configData['AiConfig']['VolcengineConfig']['VolcengineModel'],
        'VolcengineAk': configData['AiConfig']['VolcengineConfig']['VolcengineAk'],
        'VolcengineSk': configData['AiConfig']['VolcengineConfig']['VolcengineSk'],
        'VolcengineReqKey': configData['AiConfig']['VolcengineConfig']['VolcengineReqKey'],
        'VolcenginePicModelVersion': configData['AiConfig']['VolcengineConfig']['VolcenginePicModelVersion'],
        'VolcenginePicChatModel': configData['AiConfig']['VolcengineConfig']['VolcenginePicChatModel'],
    }


def getQwenConfig():
    """
    获取通义千问配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return {
        'QwenApi': configData['AiConfig']['QwenConfig']['QwenApi'],
        'QwenModel': configData['AiConfig']['QwenConfig']['QwenModel'],
        'QwenKey': configData['AiConfig']['QwenConfig']['QwenKey'],
        'QwenPicApi': configData['AiConfig']['QwenConfig']['QwenPicApi'],
        'QwenPicModel': configData['AiConfig']['QwenConfig']['QwenPicModel'],
        'QwenPicChatModel': configData['AiConfig']['QwenConfig']['QwenPicChatModel'],
    }


def getCozeConfig():
    """
    获取扣子配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return {
        'CozeToken': configData['AiConfig']['CozeConfig']['CozeToken'],
        'CozeBotId': configData['AiConfig']['CozeConfig']['CozeBotId'],
    }


def getDifyConfig():
    """
    获取Dify配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return {
        'DifyApi': configData['AiConfig']['DifyConfig']['DifyApi'],
        'DifyKey': configData['AiConfig']['DifyConfig']['DifyKey'],
    }


def getFastGptConfig():
    """
    获取FastGpt配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return {
        'FastgptApi': configData['AiConfig']['FastgptConfig']['FastgptApi'],
        'FastgptKey': configData['AiConfig']['FastgptConfig']['FastgptKey'],
        'FastgptAppid': configData['AiConfig']['FastgptConfig']['FastAppid']
    }


def getSystemAiRole():
    """
    获取系统Ai角色配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return configData['AiConfig']['SystemAiRule']


def getaiPriority():
    """
    获取Ai优先级配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return configData['AiConfig']['AiPriority']


def getaiPicPriority():
    """
    获取Ai画图优先级配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return configData['AiConfig']['AiPicPriority']


def getaiPicDiaPriority():
    """
    获取Ai图文对话优先级配置信息
    :return:
    """
    configData = Cs.returnConfigData()
    return configData['AiConfig']['AiPicDiaPriority']
