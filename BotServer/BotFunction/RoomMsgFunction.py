from BotServer.BotFunction.InterfaceFunction import *
from ApiServer.ApiMainServer import ApiMainServer
from BotServer.BotFunction.JudgeFuncion import *
from DbServer.DbMainServer import DbMainServer
import Config.ConfigServer as Cs


class RoomMsgFunction:
    def __init__(self, wcf):
        """
        群聊消息功能类, 撤回消息检测, 群聊消息总结, 群聊消息排行榜
        :param wcf:
        """
        self.wcf = wcf
        self.Dms = DbMainServer()
        self.Ams = ApiMainServer()
        configData = Cs.returnConfigData()
        self.summarizeMsgKeyWords = configData['FunctionConfig']['RoomConfig']['SummarizeMsgKeyWords']
        self.speechListKeyWords = configData['FunctionConfig']['RoomConfig']['SpeechListWords']
        self.rowingListKeyWords = configData['FunctionConfig']['RoomConfig']['RowingListWords']

    def mainHandle(self, message):
        msgType = message.type
        msgId = message.id
        roomId = message.roomid
        sender = message.sender
        content = message.content.strip()
        senderName = getIdName(self.wcf, sender)

        # 把文本消息完整存入到数据库
        if msgType == 1:
            self.Dms.addRoomContent(roomId, msgType, sender, senderName, msgId, content)
            # 当日消息总结
            if judgeEqualListWord(content, self.summarizeMsgKeyWords):
                roomName = getIdName(self.wcf, roomId)
                aiContent = f'群聊名称: {roomName}\n{self.Dms.showRoomContent(roomId)}'
                aiMessages = [{
                    "role": "system",
                    "content": "你叫NGCBot, 是一个微信群聊消息总结小助手, 你会总结我给你的聊天数据集, 它的格式是群聊名称: TEST\n微信ID,微信名称,聊天内容\n.....你会将每一个人的聊天进行分析, 并根据聊天内容总结出这一天都聊了什么内容, 最后做出总结并且以人性化的口吻回答! 回复时不要用MarkDown语法并整理相关格式，多用微信的emoji表情进行回复，全程必须充满热情！",
                }]
                assistant_content, Mes = self.Ams.getDeepSeek(aiContent, aiMessages)
                if assistant_content:
                    self.wcf.send_text(assistant_content, receiver=roomId)
                else:
                    self.wcf.send_text(f'@{senderName} 请先配置DeepSeek模型！！！', receiver=roomId, aters=sender)
            # 群聊发言排行榜
            if judgeEqualListWord(content, self.speechListKeyWords):
                roomName = getIdName(self.wcf, roomId)
                msgCount, msgNumberCount = self.Dms.showRoomCount(roomId)
                msgTypeData = self.Dms.roomMsgTypeRanking(roomId)
                msg = f'🧑‍今日发言排行统计:\n群聊名称: 【{roomName}】\n📊 当日发言总数: {msgCount} 条\n👥当日发言人数: {msgNumberCount}\n\n📊 数据透视\n'
                for data in msgTypeData:
                    if data[0] == 1:
                        msg += f'- 💬文字消息：{data[1]} 条\n'
                    elif data[0] == 3:
                        msg += f'- 💬图片消息：{data[1]} 条\n'
                    elif data[0] == 47:
                        msg += f'- 💬表情包消息：{data[1]} 条\n'
                roomMsgData = self.Dms.roomMsgRanking(roomId)
                number = 1
                msg += '\n\n【发言排行榜】\n'
                for data in roomMsgData:
                    msg += f'{number}、「{data[1]}」- {data[2]}条\n'
                    number += 1
                self.wcf.send_text(msg, receiver=roomId)
            # 划水榜
            if judgeEqualListWord(content, self.rowingListKeyWords):
                roomName = getIdName(self.wcf, roomId)
                rowingListData = self.Dms.roomMsgRowingList(roomId)
                msg = f'🧑‍ 今日潜水榜:\n群聊名称: 【{roomName}】\n\n'
                number = 1
                for data in rowingListData:
                    msg += f'{number}、「{data[1]}」- {data[2]}条\n'
                    number += 1
                self.wcf.send_text(msg, receiver=roomId)
        if msgType == 10002:
            newMsgId = getWithdrawMsgData(content)
            if newMsgId:
                oldMsg = self.Dms.searchRoomContent(roomId, newMsgId)
                msg = f'拦截到一条撤回的消息\n发送ID: {oldMsg[1]}\n发送人: {oldMsg[2]}\n消息类型: {oldMsg[0]}\n消息类容: {oldMsg[3]}'
                self.wcf.send_text(msg, receiver=roomId)
        else:
            # 其它类型消息不存内容
            self.Dms.addRoomContent(roomId, msgType, sender, senderName, msgId, '其它类型消息')
