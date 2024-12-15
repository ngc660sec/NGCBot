import yaml
import os


def returnConfigPath():
    """
    返回配置文件夹路径555
    :return:
    """
    current_path = os.path.dirname(__file__)
    current_list_path = current_path.split('\\')[0:-1]
    configPath = '/'.join(current_list_path) + '/Config/'
    return configPath


def returnConfigData():
    """
    返回配置文件数据（YAML格式）
    :return:
    """
    current_path = returnConfigPath()
    configData = yaml.load(open(current_path + '/Config.yaml', mode='r', encoding='UTF-8'), yaml.Loader)
    return configData


def returnFingerConfigData():
    """
    返回指纹配置文件数据
    :return:
    """
    current_path = returnConfigPath()
    configData = yaml.load(open(current_path + '/Finger.yaml', mode='r', encoding='UTF-8'), yaml.Loader)
    return configData


def returnFeishuConfigData():
    """
    返回飞书配置文件数据
    :return:
    """
    current_path = returnConfigPath()
    configData = yaml.load(open(current_path + '/Feishu.yaml', mode='r', encoding='UTF-8'), yaml.Loader)
    return configData


def saveFeishuConfigData(configData):
    """
    保存飞书配置
    :param configData:
    :return:
    """
    current_path = returnConfigPath()
    with open(current_path + '/Feishu.yaml', mode='w') as file:
        yaml.dump(configData, file)


def returnUserDbPath():
    return returnConfigPath() + 'User.db'


def returnRoomDbPath():
    return returnConfigPath() + 'Room.db'


def returnGhDbPath():
    return returnConfigPath() + 'Gh.db'


def returnPointDbPath():
    return returnConfigPath() + 'Point.db'
