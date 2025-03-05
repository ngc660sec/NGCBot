import yaml
import os


def returnConfigPath():
    """
    返回配置文件夹路径
    :return:
    """
    current_path = os.path.dirname(__file__)
    if '\\' in current_path:
        current_list_path = current_path.split('\\')[0:-1]
        configPath = '/'.join(current_list_path) + '/Config/'
        return configPath
    else:
        return current_path


def returnConfigData():
    """
    返回配置文件数据（YAML格式）
    :return:
    """
    current_path = returnConfigPath()
    configData = yaml.load(open(current_path + '/Config.yaml', mode='r', encoding='UTF-8'), yaml.Loader)
    return configData

def returnRoomMsgDbPath():
    return returnConfigPath() + 'RoomMsg.db'

def returnUserDbPath():
    return returnConfigPath() + 'User.db'


def returnRoomDbPath():
    return returnConfigPath() + 'Room.db'


def returnGhDbPath():
    return returnConfigPath() + 'Gh.db'



def returnPointDbPath():
    return returnConfigPath() + 'Point.db'
