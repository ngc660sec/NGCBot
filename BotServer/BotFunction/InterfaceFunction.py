import FileCache.FileCacheServer as Fcs
import xml.etree.ElementTree as ET
from OutPut.outPut import op
import requests
import time
import os
import re

def getUserLabel(wcf, sender):
    """
    获取用户所属的标签列表
    :param sender:
    :return:
    """
    try:
        userInfos = wcf.query_sql("MicroMsg.db", f'SELECT * FROM Contact WHERE UserName ="{sender}"')
        if not userInfos:
            return []
        userInfo = userInfos[0]
        labelLists = wcf.query_sql("MicroMsg.db", f"SELECT * FROM ContactLabel")
        userLabelIds = userInfo.get('LabelIDList').split(',')
        userLabels = []
        for labelDict in labelLists:
            labelId = labelDict.get('LabelId')
            labelName = labelDict.get('LabelName')
            for userLabelId in userLabelIds:
                if not userLabelId:
                    continue
                if int(userLabelId) == int(labelId):
                    userLabels.append(labelName)
        return userLabelIds
    except Exception as e:
        op(f'[-]: 获取用户所属的标签列表出现错误, 错误信息: {e}')

def getQuoteImageData(content):
    """
    提取引用图片消息的ID和 Type 以及 用户发送的内容
    :return:
    """
    try:
        root = ET.fromstring(content)
        refermsg = root.find('.//refermsg')
        title = root.find('.//title')
        if refermsg is not None:
            # 提取type和svrid
            typeValue = refermsg.find('type').text
            srvId = refermsg.find('svrid').text
            titleValue = title.text
            if typeValue and srvId:
                return int(typeValue), int(srvId), titleValue
            return None, None, None
    except Exception:
        return 0, None, None

def getQuoteMsgData(content):
    """
    提取引用消息 内容 引用内容 Type
    :param content:
    :return:
    """
    try:
        root = ET.fromstring(content)
        refermsg = root.find('.//refermsg')
        title = root.find('.//title')
        if refermsg is not None:
            # 提取type和引用Content
            typeValue = refermsg.find('type').text
            srvContent = refermsg.find('content').text
            titleValue = title.text
            if typeValue and srvContent:
                return int(typeValue), srvContent, titleValue
            return 0, None, None
    except Exception:
        return 0, None, None

def downloadQuoteImage(wcf, imageMsgId, extra):
    """
    下载引用消息的图片
    :param wcf:
    :param imageMsgId:
    :param extra:
    :return:
    """
    try:
        for i in range(0, 4):
            dbName = f'MSG{i}.db'
            data = wcf.query_sql(dbName, f'SELECT * FROM MSG WHERE MsgSvrID= {imageMsgId}')
            if not data:
                continue
            bytesExtra = data[0]['BytesExtra']
            bytesExtraStr = bytesExtra.decode('utf-8', errors='ignore')
            userHome = re.search(r'(?P<userHome>.*?/)wxid_', extra).group('userHome')
            datPath = re.search(r'}(?P<datPath>.*?.dat)', bytesExtraStr).group('datPath').replace('\\', '/')
            imgDatPath = userHome + datPath
            imgSavePath = wcf.download_image(imageMsgId, imgDatPath, Fcs.returnPicCacheFolder())
            return imgSavePath
    except Exception:
        return None


def getWithdrawMsgData(content):
    """
    提取撤回消息的 ID
    :param content:
    :return:
    """
    root = ET.fromstring(content)
    try:
        newMsgId = root.find(".//newmsgid").text
        replaceMsg = root.find(".//replacemsg").text
        if newMsgId and replaceMsg:
            if '撤回了一条消息' in replaceMsg:
                return newMsgId
    except Exception:
        return None

def getWechatVideoData(content):
    """
    处理微信视频号 提取objectId objectNonceId
    :param content:
    :return: objectId objectNonceId
    """
    try:
        root = ET.fromstring(content)
        finderFeed = root.find('.//finderFeed')
        objectId = finderFeed.find('./objectId').text
        objectNonceId = finderFeed.find('./objectNonceId').text
        return objectId, objectNonceId
    except Exception as e:
        op(f'[~]: 提取微信视频号ID出现错误, 错误信息: {e}, 不用管此报错 ~~~')
        return '', ''


def getAtData(wcf, msg):
    """
    处理@信息
    :param msg:
    :param wcf:
    :return:
    """
    noAtMsg = msg.content
    try:
        root_xml = ET.fromstring(msg.xml)
        atUserListsElement = root_xml.find('.//atuserlist')
        atUserLists = atUserListsElement.text.replace(' ', '').strip().strip(',').split(
            ',') if atUserListsElement is not None else None
        if not atUserLists:
            return '', ''
        atNames = []
        for atUser in atUserLists:
            atUserName = wcf.get_alias_in_chatroom(atUser, msg.roomid)
            atNames.append(atUserName)
        for atName in atNames:
            noAtMsg = noAtMsg.replace('@' + atName, '')
    except Exception as e:
        op(f'[~]: 处理@消息出现小问题, 仅方便开发调试, 不用管此报错: {e}')
        return '', ''
    return atUserLists, noAtMsg.strip()


def getIdName(wcf, Id=None, roomId=None, retry=0, max_retries=3):
    """
    获取好友或者群聊昵称
    :param wcf: 微信框架对象
    :param Id: 用户ID
    :param roomId: 群聊ID
    :param retry: 当前重试次数
    :param max_retries: 最大重试次数
    :return:
    """
    try:
        name_list = wcf.query_sql("MicroMsg.db", f"SELECT UserName, NickName FROM Contact WHERE UserName = '{Id}';")

        if not name_list and retry < max_retries:
            # 如果查询结果为空且未达到最大重试次数，则等待一秒后重试
            time.sleep(1)
            return getIdName(wcf, Id, roomId, retry + 1, max_retries)
        elif not name_list:
            # 达到最大重试次数但仍无法获取数据，返回原始ID
            op(f'[~]: 获取好友或者群聊昵称出现错误, 错误信息: 查询结果为空')
            return Id
        name = name_list[0]['NickName']
        if '@chatroom' not in Id:
            if name:
                return name
            nickName = wcf.get_alias_in_chatroom(Id, roomId)
            if not nickName:
                return Id
            return nickName
        else:
            return name
    except Exception as e:
        op(f'[~]: 获取好友或者群聊昵称出现错误, 错误信息: {e}')
        if retry < max_retries:
            # 如果发生异常且未达到最大重试次数，则等待一秒后重试
            time.sleep(1)
            return getIdName(wcf, Id, roomId, retry + 1, max_retries)
        else:
            # 达到最大重试次数但仍无法获取数据，返回原始ID
            return Id


def getUserPicUrl(wcf, sender):
    """
    获取好友头像下载地址
    :param sender:
    :param wcf:
    :return:
    """
    imgName = str(sender) + '.jpg'
    save_path = Fcs.returnAvatarFolder() + '/' + imgName

    if imgName in os.listdir(Fcs.returnAvatarFolder()):
        return save_path

    headImgData = wcf.query_sql("MicroMsg.db", f"SELECT * FROM ContactHeadImgUrl WHERE usrName = '{sender}';")
    try:
        if headImgData:
            if headImgData[0]:
                bigHeadImgUrl = headImgData[0]['bigHeadImgUrl']
                content = requests.get(url=bigHeadImgUrl, timeout=30).content
                with open(save_path, mode='wb') as f:
                    f.write(content)
                return save_path
    except Exception as e:
        op(f'[-]: 获取好友头像下载地址出现错误, 错误信息: {e}')
        return None


if __name__ == '__main__':
    getWithdrawMsgData('<sysmsg type="revokemsg"><revokemsg><session>47555703573@chatroom</session><msgid>1387587956</msgid><newmsgid>6452489353190914412</newmsgid><replacemsg><![CDATA["Vcnnn8h" 撤回了一条消息]]></replacemsg><announcement_id><![CDATA[]]></announcement_id></revokemsg></sysmsg>')
