from BotServer.SendServer import SendServer
from Api_Server.Api_Server_Main import Api_Server_Main
from Recv_Msg_Dispose.Thread_function import Thread_function
from Db_Server.Db_User_Server import Db_User_Server
from concurrent.futures import ThreadPoolExecutor
import yaml
import os


class FriendMsg_dispose:
    def __init__(self):
        # 初始化核心参数
        self.senderid = 'null'
        self.nickname = 'null'
        self.msgJson = ''
        self.sendmsg = ''
        self.keyword = ''

        # 读取配置文件
        current_path = os.path.dirname(__file__)
        config = yaml.load(open(current_path + '/../config/config.yaml', encoding='UTF-8'), yaml.Loader)

        # 读取超级管理员配置
        self.administrators = config['Administrators']

        # 获取关键词
        self.cache_words = config['System_Config']['Cache_Config_Word']
        self.help_menu_words = config['System_Config']['Help_Menu']
        self.system_copyright = config['System_Config']['System_Copyright']
        self.show_white_room_words = config['Key_Word']['Show_WhiteRoom_Word']

        # 实例化消息发送服务
        self.Ss = SendServer()

        # 实例化接口服务类
        self.Asm = Api_Server_Main()

        # 实例化用户操作类
        self.Dus = Db_User_Server()

        # 多线程处理接收消息
        self.Tf = Thread_function()

        # 线程池
        self.pool = ThreadPoolExecutor(10)

    def get_information(self, msgJson, senderid, ws):
        self.senderid = senderid
        self.nickname = self.Ss.get_member_nick(wxid=senderid, roomid='null')
        self.keyword = msgJson['content'].replace('\u2005', '')
        self.process_information(ws)

    # 好友消息处理
    def process_information(self, ws):
        # 注入消息转发给好友
        if self.senderid in self.administrators and self.keyword:
            self.pool.submit(self.Tf.retransmission_msg, ws, self.keyword)

        # 好友消息消息转发主人
        if self.senderid not in self.administrators and self.keyword:
            self.pool.submit(self.Tf.retransmission_boos, ws, self.keyword, self.nickname)

        # 清除缓存
        if self.judge_keyword(keyword=self.keyword,
                              custom_keyword=self.cache_words, ) and self.senderid in self.administrators:
            self.pool.submit(self.Tf.clear_temps, ws, self.senderid)

        # 查看白名单群聊
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.show_white_room_words):
            self.pool.submit(self.Tf.show_white_rooms, ws, self.senderid)

        # AI对话
        elif self.keyword:
            self.pool.submit(self.Tf.friend_ai, ws, self.keyword, self.senderid, self.nickname)

    # 判断关键词
    def judge_keyword(self, keyword, custom_keyword, split_bool=False, one_bool=False):
        # 分割触发
        if split_bool:
            keyword = keyword.split(' ')
            for ckw in custom_keyword:
                for kw in keyword:
                    if ckw == kw:
                        return True
        # 单个触发
        elif one_bool:
            return True if keyword.strip() == custom_keyword.strip() else False
        # 单个循环触发
        elif keyword and custom_keyword and not split_bool and not one_bool:
            return True if [ckw for ckw in custom_keyword if ckw == keyword] else False
