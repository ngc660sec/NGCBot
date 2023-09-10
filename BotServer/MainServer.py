from Recv_Msg_Dispose.FriendMsg_dispose import FriendMsg_dispose
from Recv_Msg_Dispose.RoomMsg_dispose import RoomMsg_disposes
from Push_Server.Push_Main_Server import Push_Main_Server
from Db_Server.Db_User_Server import Db_User_Server
from concurrent.futures import ThreadPoolExecutor
from BotServer.SendServer import SendServer
from bs4 import BeautifulSoup
from Output.output import *
import websocket
import yaml
import json
import os


class MainServers:

    def __init__(self):
        # 初始化读取配置文件
        current_path = os.path.dirname(__file__)
        config = yaml.load(open(current_path + '/../Config/config.yaml', encoding='UTF-8'), yaml.Loader)
        self.ip = config['BotServer']['IP']
        self.port = config['BotServer']['PORT']
        self.system_copyright = config['System_Config']['System_Copyright']

        # 配置HOOK信息类型
        self.SERVER = f"ws://{self.ip}:{self.port}"
        self.HEART_BEAT = 5005
        self.RECV_TXT_MSG = 1
        self.RECV_TXT_CITE_MSG = 49
        self.RECV_PIC_MSG = 3
        self.USER_LIST = 5000
        self.GET_USER_LIST_SUCCSESS = 5001
        self.GET_USER_LIST_FAIL = 5002
        self.TXT_MSG = 555
        self.PIC_MSG = 500
        self.AT_MSG = 550
        self.CHATROOM_MEMBER = 5010
        self.CHATROOM_MEMBER_NICK = 5020
        self.PERSONAL_INFO = 6500
        self.DEBUG_SWITCH = 6000
        self.PERSONAL_DETAIL = 6550
        self.DESTROY_ALL = 9999
        self.JOIN_ROOM = 10000
        self.ATTATCH_FILE = 5003

        # 启动机器人
        self.ws = websocket.WebSocketApp(
            self.SERVER, on_open=self.on_open, on_message=self.on_message, on_error=self.on_error,
            on_close=self.on_close
        )

        # 实例化消息服务
        self.Ss = SendServer()

        # 实例化群消息处理类
        self.Rmd = RoomMsg_disposes()

        # 实例化好友消息处理
        self.Fmd = FriendMsg_dispose()

        # 实例化用户数据服务类
        self.Dus = Db_User_Server()

    # Robot初始化执行
    def on_open(self, ws):
        # 实例化实时监控类
        self.Pms = Push_Main_Server(ws=self.ws)
        pool = ThreadPoolExecutor(5)
        pool.submit(self.Pms.run)
        self.get_personal_info()

    # Robot 启动函数
    def Bot_start(self, ):
        self.ws.run_forever()

    # Robot 关闭执行
    def on_close(self, ws):
        output("The Robot is Closed...")

    # Robot 错误输出
    def on_error(self, ws, error):
        output(f"[ERROR]:出现 错误，错误信息：{error}")

    # 启动完成输出
    def handle_wxuser_list(self):
        output("Bot is Start!")

    # Robot 心跳输出
    def heartbeat(self, msgJson):
        output(f'[*]:{msgJson["content"]}')

    # DEBUG选择HOOK信息类型
    def debug_switch(self, ):
        qs = {
            "id": self.Ss.get_id(),
            "type": self.DEBUG_SWITCH,
            "content": "off",
            "wxid": "ROOT",
        }
        return json.dumps(qs)

    # 处理缺口
    def handle_nick(self, j):
        data = j.content
        i = 0
        for d in data:
            output(f"nickname:{d.nickname}")
            i += 1

    # 处理所有Roomid
    def hanle_memberlist(self, j):
        data = j.content
        i = 0
        for d in data:
            output(f"roomid:{d.roomid}")
            i += 1

    # 销毁全部接口
    def destroy_all(self, ):
        qs = {
            "id": self.Ss.get_id(),
            "type": self.DESTROY_ALL,
            "content": "none",
            "wxid": "node",
        }
        return json.dumps(qs)

    # 处理带引用的文字消息
    def handleMsg_cite(self, msgJson):
        msgXml = (
            msgJson["content"]["content"]
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
        )
        soup = BeautifulSoup(msgXml, "xml")
        msgJson = {
            "content": soup.select_one("title").text,
            "id": msgJson["id"],
            "id1": msgJson["content"]["id2"],
            "id2": "wxid_fys2fico9put22",
            "id3": "",
            "srvid": msgJson["srvid"],
            "time": msgJson["time"],
            "type": msgJson["type"],
            "wxid": msgJson["content"]["id1"],
        }
        self.handle_recv_msg(msgJson)

    # 选择消息类型
    def on_message(self, ws, message):
        j = json.loads(message)
        resp_type = j["type"]
        # switch结构
        action = {
            self.CHATROOM_MEMBER_NICK: self.handle_nick,
            self.PERSONAL_DETAIL: self.handle_recv_msg,
            self.AT_MSG: self.handle_recv_msg,
            self.DEBUG_SWITCH: self.handle_recv_msg,
            self.PERSONAL_INFO: self.handle_recv_msg,
            self.TXT_MSG: self.handle_recv_msg,
            self.PIC_MSG: self.handle_recv_msg,
            self.CHATROOM_MEMBER: self.hanle_memberlist,
            self.RECV_PIC_MSG: self.handle_recv_msg,
            self.RECV_TXT_MSG: self.handle_recv_msg,
            self.RECV_TXT_CITE_MSG: self.handleMsg_cite,
            self.HEART_BEAT: self.heartbeat,
            self.USER_LIST: self.handle_wxuser_list,
            self.GET_USER_LIST_SUCCSESS: self.handle_wxuser_list,
            self.GET_USER_LIST_FAIL: self.handle_wxuser_list,
            self.JOIN_ROOM: self.welcome_join,
        }
        action.get(resp_type, print)(j)

    # 获取获取微信通讯录用户名字和wxid,好友列表
    def get_wx_user_list(self, ):
        qs = {
            "id": self.Ss.get_id(),
            "type": self.USER_LIST,
            "content": "user list",
            "wxid": "null",
        }
        # Output(qs)
        return json.dumps(qs)

    def get_personal_info(self, ):
        # 获取本机器人的信息
        uri = "/api/get_personal_info"
        data = {
            "id": self.Ss.get_id(),
            "type": self.PERSONAL_INFO,
            "content": "op:personal info",
            "wxid": "null",
        }
        respJson = self.Ss.send(uri, data)
        wechatBotInfo = f"""

        NGCBot登录信息

        微信昵称：{json.loads(respJson["content"])['wx_name']}
        微信号：{json.loads(respJson["content"])['wx_code']}
        微信id：{json.loads(respJson["content"])['wx_id']}
        启动时间：{respJson['time']}
        {'By: ' + self.system_copyright if self.system_copyright else ''}
        """
        output(wechatBotInfo.strip())

    # 入群欢迎函数
    def welcome_join(self, msgJson):
        output(f"收到消息:{msgJson}")
        if "邀请" in msgJson["content"]["content"]:
            roomid = msgJson["content"]["id1"]
            nickname = msgJson["content"]["content"].split('"')[-2]
            msg = '\n欢迎新进群的小可爱[烟花]'
            roomid_list, room_names = self.Dus.show_white_room()
            if roomid in roomid_list:
                self.ws.send(self.Ss.send_msg(msg=msg, roomid=roomid, wxid='null',
                                              nickname=nickname))

    # 消息接收函数
    def handle_recv_msg(self, msgJson):
        if "wxid" not in msgJson and msgJson["status"] == "SUCCSESSED":
            if msgJson['type'] == 3:
                output(f"收到图片:{msgJson}")
            else:
                output(f"[*]:发送成功")
            return
        output(f"收到消息:{msgJson}")
        # 判断群聊消息还是私人消息
        if "@chatroom" in msgJson["wxid"]:
            # 获取群ID
            roomid = msgJson["wxid"]
            # 获取发送人ID
            senderid = msgJson["id1"]
        else:
            roomid = None
            nickname = "null"
            # 获取发送人ID
            senderid = msgJson["wxid"]


        # 获取发送者的名字
        nickname = self.Ss.get_member_nick(roomid, senderid)
        if roomid:
            # 处理微信群消息
            self.Rmd.get_information(msgJson=msgJson, roomid=roomid, senderid=senderid, nickname=nickname, ws=self.ws)
        else:
            # 处理通讯录好友发送的消息
            self.Fmd.get_information(msgJson=msgJson, senderid=senderid, ws=self.ws)


if __name__ == '__main__':
    Ms = MainServers()
    Ms.Bot_start()
