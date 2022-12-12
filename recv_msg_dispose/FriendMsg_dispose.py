from Db_server.Db_user_server import Db_user_server
from BotServer.SendServer import SendServer
from Get_api.Api_server import Api_server
from File.File_server import File_server
import yaml
import re
import os


class FriendMsg_dispose:
    def __init__(self):
        # 初始化核心参数
        self.senderid = 'null'
        self.roomid = 'null'
        self.nickname = 'null'
        self.msgJson = ''
        self.sendmsg = ''
        self.keyword = ''

        # 读取配置文件
        current_path = os.path.dirname(__file__)
        config = yaml.load(open(current_path + '/../config/config.yaml', encoding='UTF-8'), yaml.Loader)

        # 实例化消息发送服务
        self.Ss = SendServer()

        # 实例化API服务
        self.As = Api_server()

        # 实例化文件操作类
        self.Fs = File_server()

        # 实例化用户数据操作
        self.Dus = Db_user_server()

        # 获取超管用户
        self.Administrators = config['ADMINISTRATOR']

        # 获取管理员列表
        self.admins = list()

        # 获取关键词
        self.Key_Response = config['KEY_RESPONSE']
        # 获取帮助关键词回复
        self.help_keys = self.Key_Response['HELP']

        # 获取管理关键词
        self.admin_key_response = config['ADMIN_KEY_RESPONSE']
        # 获取查看管理员关键词
        self.show_admins_keys = self.admin_key_response['SHOW_ADMINS']
        # 获取查看所有特权群聊关键词
        self.show_privilege_rooms_keys = self.admin_key_response['SHOW_PRIVILEGE_ROOMS']
        # 获取查看所有拉黑群聊关键词
        self.show_black_rooms_keys = self.admin_key_response['SHOW_BLACK_ROOMS']
        # 获取清除缓存关键词
        self.refresh_cache_keys = self.admin_key_response['REFRESH_CACHE']

    def get_information(self, msgJson, senderid, ws):
        self.senderid = senderid
        self.nickname = self.Ss.get_member_nick(wxid=senderid, roomid=self.roomid)
        self.keyword = msgJson['content'].replace('\u2005', '')
        self.admins = self.Dus.query_admins()
        self.process_information(ws)

    def process_information(self, ws):
        # 测试专用
        if 'OK' == self.keyword:
            msg = 'OOK!'
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid))

        # 配置超管回复
        if self.senderid in self.Administrators:
            self.supertube_function(ws, )
            self.administrator_function(ws, )
            self.ordinary_user_function(ws, )
        # 配置管理员回复
        elif self.senderid in self.admins:
            self.administrator_function(ws, )
            self.ordinary_user_function(ws, )
        # 配置普通用户回复
        else:
            self.ordinary_user_function(ws, )

    # 配置超级管理员功能
    def supertube_function(self, ws):
        # 查看所有管理员
        if self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.show_admins_keys, in_bool=False):
            msg = self.Dus.show_all_admins()
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid))
        # 查看所有特权群聊
        if self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.show_privilege_rooms_keys):
            msg = self.Dus.show_all_privilege_rooms()
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid))
        # 查看所有黑名单群聊
        if self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.show_black_rooms_keys):
            msg = self.Dus.show_all_black_rooms()
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid))

    # 配置管理员功能
    def administrator_function(self, ws):
        # 清除缓存功能
        if self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.refresh_cache_keys, ):
            msg = self.Fs.delete_file()
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, ))

    # 配置普通用户功能
    def ordinary_user_function(self, ws):
        # 功能菜单回复
        if self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.help_keys, ):
            msg = '\tNGCBot功能菜单\t\n'
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, ))
        # AI回复
        elif self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.keyword, ai_bool=True):
            msg = self.As.get_xiaoai_msg(keyword=self.keyword)
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, ))
