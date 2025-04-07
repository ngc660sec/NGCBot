from OutPut.outPut import op
import os


def returnCachePath():
    """
    返回缓存文件夹路径
    :return:
    """
    current_path = os.path.dirname(__file__)
    current_list_path = current_path.split('\\')[0:-1]
    fileCachePath = '/'.join(current_list_path) + '/FileCache'
    return fileCachePath


def returnPicCacheFolder():
    """
    返回图片缓存文件夹
    :return:
    """
    return returnCachePath() + '/picCacheFolder'


def returnVideoCacheFolder():
    """
    返回视频缓存文件夹
    :return:
    """
    return returnCachePath() + '/videoCacheFolder'


def returnFishCacheFolder():
    """
    返回摸鱼日历缓存文件夹
    :return:
    """
    return returnCachePath() + '/FishCacheFolder'


def returnGaoDeCacheFolder():
    """
    返回高德地图缓存文件夹
    :return:
    """
    return returnCachePath() + '/gaodeCacheFolder'


def returnAiPicFolder():
    """
    返回Ai生成图像缓存文件夹
    :return:
    """
    return returnCachePath() + '/aiPicCacheFolder'


def returnAvatarFolder():
    """
    返回微信头像缓存文件夹
    :return:
    """
    return returnCachePath() + '/weChatAvatarFolder'


def returnGameFolder():
    """
    返回游戏缓存文件夹
    :return:
    """
    return returnCachePath() + '/gameCacheFolder'

def returnAudioFolder():
    """
    返回语音缓存文件夹
    :return:
    """
    return returnCachePath() + '/audioCacheFolder'

def clearCacheFolder():
    """
    清空缓存文件夹所有文件
    :return:
    """
    if os.path.exists(returnAiPicFolder()):
        file_lists = []
        file_lists += [returnPicCacheFolder() + '/' + file for file in os.listdir(returnPicCacheFolder())]
        file_lists += [returnVideoCacheFolder() + '/' + file for file in os.listdir(returnVideoCacheFolder())]
        file_lists += [returnFishCacheFolder() + '/' + file for file in os.listdir(returnFishCacheFolder())]
        file_lists += [returnGaoDeCacheFolder() + '/' + file for file in os.listdir(returnGaoDeCacheFolder())]
        file_lists += [returnAiPicFolder() + '/' + file for file in os.listdir(returnAiPicFolder())]
        file_lists += [returnAvatarFolder() + '/' + file for file in os.listdir(returnAvatarFolder())]
        file_lists += [returnGameFolder() + '/' + file for file in os.listdir(returnGameFolder())]
        file_lists += [returnAudioFolder() + '/' + file for file in os.listdir(returnAudioFolder())]
        for rm_file in file_lists:
            os.remove(rm_file)
        return True
    else:
        initCacheFolder()
        clearCacheFolder()


def initCacheFolder():
    """
    初始化缓存文件夹
    :return:
    """
    if not os.path.exists(returnPicCacheFolder()):
        os.mkdir(returnPicCacheFolder())
    if not os.path.exists(returnVideoCacheFolder()):
        os.mkdir(returnVideoCacheFolder())
    if not os.path.exists(returnFishCacheFolder()):
        os.mkdir(returnFishCacheFolder())
    if not os.path.exists(returnGaoDeCacheFolder()):
        os.mkdir(returnGaoDeCacheFolder())
    if not os.path.exists(returnAiPicFolder()):
        os.mkdir(returnAiPicFolder())
    if not os.path.exists(returnAvatarFolder()):
        os.mkdir(returnAvatarFolder())
    if not os.path.exists(returnGameFolder()):
        os.mkdir(returnGameFolder())
    if not os.path.exists(returnAudioFolder()):
        os.mkdir(returnAudioFolder())
        op(f'[+]: 初始化缓存文件夹成功!!!')


if __name__ == '__main__':
    initCacheFolder()
    # print(returnCachePath())
    clearCacheFolder()
