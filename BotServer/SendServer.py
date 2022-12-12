from Output.output import output
import requests
import time
import json
import yaml
import os


class SendServer:

    def __init__(self):
        # 初始化读取配置文件
        current_path = os.path.dirname(__file__)
        config = yaml.load(open(current_path + '/../config/config.yaml', encoding='UTF-8'), yaml.Loader)
        self.ip = config['IP']
        self.port = config['PORT']

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

    def send(self, uri, data):
        base_data = {
            "id": self.get_id(),
            "type": "null",
            "roomid": "null",
            "wxid": "null",
            "content": "null",
            "nickname": "null",
            "ext": "null",
        }
        base_data.update(data)
        url = f'http://{self.ip}:{self.port}/{uri}'
        res = requests.post(url, json={"para": base_data}, timeout=5)
        return res.json()

    # 定义信息ID
    def get_id(self):
        return time.strftime("%Y%m%d%H%M%S")

    # 发送消息函数
    def send_msg(self, msg, wxid="null", roomid=None, nickname="null"):
        if "jpg" in msg or "png" in msg:
            msg_type = self.PIC_MSG
        elif roomid:
            msg_type = self.AT_MSG
        else:
            msg_type = self.TXT_MSG
        if roomid is None:
            roomid = "null"
        qs = {
            "id": self.get_id(),
            "type": msg_type,
            "roomid": roomid,
            "wxid": wxid,
            "content": msg,
            "nickname": nickname,
            "ext": "null",
        }
        output(f"[*] >> 发送消息: {qs}")
        return json.dumps(qs)

    # 通用文件发送函数
    def send_file_room(self, file, roomid):
        output("Sending Files")
        data = {
            "id": self.get_id(),
            "type": self.ATTATCH_FILE,
            "roomid": "null",
            "content": file,
            "wxid": roomid,
            "nickname": "null",
            "ext": "null",
        }
        url = f"http://{self.ip}:{self.port}/api/sendattatch"
        res = requests.post(url, json={"para": data}, timeout=5)
        if res.status_code == 200 and res.json()["status"] == "SUCCSESSED":
            output("[*] >> 文件发送成功")
        else:
            output(f"[ERROR] >> 出现错误，错误信息：{res.text}")

    # 图片发送函数
    def send_img_room(self, msg, roomid):
        output("Sending Photos")
        data = {
            "id": self.get_id(),
            "type": self.PIC_MSG,
            "roomid": "null",
            "content": msg,
            "wxid": roomid,
            "nickname": "null",
            "ext": "null",
        }
        url = f"http://{self.ip}:{self.port}/api/sendpic"
        res = requests.post(url, json={"para": data}, timeout=5)
        if res.status_code == 200 and res.json()["status"] == "SUCCSESSED":
            output("[*] >> 图片发送成功!")
        else:
            output(f"[ERROR] >> 出现错误，错误信息：{res.text}")

    # 获取所有群的wxid
    def get_memberid(self, ):
        uri = 'api/getmemberid'
        data = {
            'type': self.CHATROOM_MEMBER,
            'content': 'op:list member'
        }
        output(self.send(uri, data))
        # return self.send(uri, data)

    # 获取指定群的成员的昵称 或 微信好友的昵称 # 或群聊名字
    def get_member_nick(self, roomid, wxid):
        uri = "api/getmembernick"
        data = {"type": self.CHATROOM_MEMBER_NICK, "wxid": wxid, "roomid": roomid or "null"}
        respJson = self.send(uri, data)
        return json.loads(respJson["content"])["nick"]

    # 获取机器人微信ID和微信名字
    def get_personal_info(self, ):
        uri = "/api/get_personal_info"
        data = {
            "id": self.get_id(),
            "type": self.PERSONAL_INFO,
            "content": "op:personal info",
            "wxid": "null",
        }
        respJson = self.send(uri, data)
        wx_name = json.loads(respJson["content"])['wx_name']
        wx_id = json.loads(respJson["content"])['wx_id']
        return wx_name, wx_id

    # 判断关键词
    def judge_key_word(self, receive_keyword, keyword=None, key1=None, key2=None, in_bool=False, and_bool=False, ai_bool=False):
        # 只有一个关键词触发
        key = False
        try:
            if keyword and not in_bool and not ai_bool and not and_bool:
                key = True if [key for key in keyword if key == receive_keyword] else False
            # 判断包含，一个关键词触发
            elif keyword and in_bool and not ai_bool and not and_bool:
                key = True if [key for key in keyword if key in receive_keyword] else False
            # 判断相等，一个关键词触发
            elif keyword and and_bool and not in_bool and not ai_bool:
                key = True if [key for key in keyword if key == receive_keyword] else False
            # 判断包含，AI专用
            elif ai_bool:
                key = True if keyword in receive_keyword else False
            # 判断包含，两个关键词触发
            elif in_bool and and_bool:
                key1 = True if [key for key in key1 if key in receive_keyword] else False
                key2 = True if [key for key in key2 if key in receive_keyword] else False
                return True if key1 and key2 else False
        except Exception as e:
            output(e)
        return key

