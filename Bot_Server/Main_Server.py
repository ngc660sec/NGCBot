from Recv_Msg_Dispose.Friend_Msg_Dispose import Friend_Msg_Dispose
from Recv_Msg_Dispose.Room_Msg_Dispose import Room_Msg_Dispose
from Push_Server.Push_Main_Server import Push_Main_Server
from Cache.Cache_Main_Server import Cache_Main_Server
from Db_Server.Db_Point_Server import Db_Point_Server
from Db_Server.Db_Main_Server import Db_Main_Server
import xml.etree.ElementTree as ET
from threading import Thread
from cprint import cprint
from OutPut import OutPut
from queue import Empty
from wcferry import Wcf
import random
import yaml
import os
import re


class Main_Server:
    def __init__(self):
        # 读取配置文件
        current_path = os.path.dirname(__file__)
        config = yaml.load(open(current_path + '/../config/config.yaml', encoding='UTF-8'), yaml.Loader)

        self.JoinRoom_Msg = config['Function_Key_Word']['JoinRoom_Msg']
        self.AcceptFriend_Msg = config['Custom_Msg']['AcceptFriend_Msg']

        self.wcf = Wcf(port=random.randint(20000, 40000))
        # 判断登录
        self.is_login()

        # 实例化数据服务类并初始化
        self.Dms = Db_Main_Server(wcf=self.wcf)
        self.Dms.db_init()
        # 实例化积分数据类并初始化
        self.Dps = Db_Point_Server()
        self.Dps.db_init()
        Thread(target=self.Dms.query_all_users, name="获取所有的联系人").start()

        # 实例化定时推送类
        self.Pms = Push_Main_Server(wcf=self.wcf)
        Thread(target=self.Pms.run, name="定时推送服务").start()

        # 开启全局消息接收(不接收朋友圈消息)
        self.wcf.enable_receiving_msg()
        Thread(target=self.process_msg, name="GetMessage", args=(self.wcf,), daemon=True).start()

        # 实例化好友消息处理类
        self.Fms = Friend_Msg_Dispose(wcf=self.wcf)
        # 实例化群消息处理类
        self.Rms = Room_Msg_Dispose(wcf=self.wcf)
        # 实例化文件处理类
        self.Cms = Cache_Main_Server(wcf=self.wcf)
        self.Cms.init_cache()

        # 持续运行
        self.wcf.keep_running()

    # 判断登录
    def is_login(self):
        ret = self.wcf.is_login()
        if ret:
            userInfo = self.wcf.get_user_info()
            # 用户信息打印
            cprint.info(f"""
            \t========== NGCBot V2.0 ==========
            \t微信名：{userInfo.get('name')}
            \t微信ID：{userInfo.get('wxid')}
            \t手机号：{userInfo.get('mobile')}
            \t========== NGCBot V2.0 ==========       
            """.replace(' ', ''))

    # 处理接收到的消息
    def process_msg(self, wcf: Wcf):
        while wcf.is_receiving_msg():
            try:
                # 拿到每一条消息
                msg = wcf.get_msg()
                OutPut.outPut('[收到消息]: ' + str(msg))
                # 拿到推送群聊
                push_rooms = self.Dms.show_push_rooms()
                # 查询好友 是否在数据库,如果不在自动添加到数据库中
                Thread(target=self.main_judge, name="查询好友,群,公众号", args=(msg,)).start()
                # 群消息处理
                if msg.type == 10000:
                    OutPut.outPut(f'10000: {msg.content}')
                    if msg.roomid in push_rooms.keys() and msg.roomid:
                        # 进群欢迎
                        Thread(target=self.Join_Room, name="进群欢迎", args=(msg,)).start()
                    # 添加好友后回复
                    elif msg.sender and not msg.roomid and ('添加了' in msg.content or '以上是打招呼的内容' in msg.content):
                        Thread(target=self.Accept_Friend_Msg, name="加好友后自动回复", args=(msg,)).start()
                    elif '收到红包，请在手机上查看' in msg.content and not msg.roomid:
                        Thread(target=self.Fms.Msg_Dispose, name="好友消息处理", args=(msg,)).start()
                # 好友申请消息处理
                elif msg.type == 37:
                    # 自动同意好友申请
                    root_xml = ET.fromstring(msg.content.strip())
                    wx_id = root_xml.attrib["fromusername"]
                    OutPut.outPut(f'[*]: 接收到新的好友申请, 微信id为: {wx_id}')
                    v3 = root_xml.attrib["encryptusername"]
                    v4 = root_xml.attrib["ticket"]
                    scene = int(root_xml.attrib["scene"])
                    ret = self.wcf.accept_new_friend(v3=v3, v4=v4, scene=scene)
                    if ret:
                        OutPut.outPut(f'[+]: 好友 {self.wcf.get_info_by_wxid(wx_id).get("name")} 已自动通过 !')
                    else:
                        OutPut.outPut(f'[-]: 好友通过失败！！！')
                # 好友消息处理
                elif 'wxid_' in msg.sender and not msg.roomid:
                    Thread(target=self.Fms.Msg_Dispose, name="好友消息处理", args=(msg,)).start()
                # 群消息处理
                elif msg.roomid:
                    Thread(target=self.Rms.Msg_Dispose, name="群消息处理", args=(msg,)).start()
                # 公众号消息处理
                elif 'gh_' in msg.sender:
                    pass
                # 其它好友类消息 不是wxid_的
                else:
                    Thread(target=self.Fms.Msg_Dispose, name="好友消息处理", args=(msg,)).start()
            except Empty:
                # 消息为空 则从队列接着拿
                continue
            except Exception as e:
                # 打印异常
                OutPut.outPut(f'[-]: 出现错误, 错误信息: {e}')

    # 添加好友后自动回复
    def Accept_Friend_Msg(self, msg):
        send_msg = self.AcceptFriend_Msg.replace('\\n', '\n')
        self.wcf.send_text(msg=send_msg, receiver=msg.sender)

    # 判断群聊 公众号 好友是否在数据库中, 不在则添加好友
    def main_judge(self, msg):
        try:
            sender = msg.sender
            room_id = msg.roomid
            name_list = self.wcf.query_sql("MicroMsg.db",
                                           f"SELECT UserName, NickName FROM Contact WHERE UserName = '{sender}';")
            if not name_list:
                return
            name = name_list[0]['NickName']
            if 'wxid_' in sender:
                self.Dms.add_user(wx_id=sender, wx_name=name)
            elif '@chatroom' in msg.roomid:
                self.Dms.add_room(room_id=room_id, room_name=name)
            elif 'gh_' in sender:
                self.Dms.add_gh(gh_id=sender, gh_name=name)
        except Exception as e:
            OutPut.outPut(f'[-]: 判断群聊 公众号 好友是否在数据库中, 不在则添加好友逻辑出现错误，错误信息: {e}')

    # 进群欢迎
    def Join_Room(self, msg):
        OutPut.outPut(f'[*]: 正在调用进群欢迎功能... ...')
        try:
            content = msg.content.strip()
            wx_names = None
            if '二维码' in content:
                wx_names = re.search(r'"(?P<wx_names>.*?)"通过扫描', content)
            elif '邀请' in content:
                wx_names = re.search(r'邀请"(?P<wx_names>.*?)"加入了', content)

            if wx_names:
                wx_names = wx_names.group('wx_names')
                if '、' in wx_names:
                    wx_names = wx_names.split('、')
                else:
                    wx_names = [wx_names]
            for wx_name in wx_names:
                JoinRoom_msg = f'@{wx_name} ' + self.JoinRoom_Msg.replace("\\n", "\n")
                self.wcf.send_text(msg=JoinRoom_msg, receiver=msg.roomid)
        except Exception as e:
            pass


if __name__ == '__main__':
    Ms = Main_Server()
