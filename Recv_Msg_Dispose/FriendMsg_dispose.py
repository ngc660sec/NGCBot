from BotServer.SendServer import SendServer
from Api_Server.Api_Server_Main import Api_Server_Main
from Cache.Cache_Server import Cache_Server
from Db_Server.Db_User_Server import Db_User_Server
from Output import output
import yaml
import os
import re


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

        # 实例化缓存操作类
        self.Cs = Cache_Server()

        # 实例化用户操作类
        self.Dus = Db_User_Server()

    def get_information(self, msgJson, senderid, ws):
        self.senderid = senderid
        self.nickname = self.Ss.get_member_nick(wxid=senderid, roomid='null')
        self.keyword = msgJson['content'].replace('\u2005', '')
        self.process_information(ws)

    # 好友消息处理
    def process_information(self, ws):
        # 注入消息转发给好友
        if self.senderid in self.administrators and self.keyword:
            try:
                patten = re.search(r'给(?P<nickname>.*?)发消息 (?P<msg>.*)', self.keyword)
                print(patten)
                msg = patten.group('msg')
                nickname = patten.group('nickname')
                recv_user = self.Dus.show_userid(wx_name=nickname.strip())
                if recv_user:
                    msg = f'—— 来自主人的消息 ——[庆祝]\n\n{msg}\n\n—— 来自主人的消息 ——[庆祝]'
                    ws.send(self.Ss.send_msg(msg=msg, wxid=recv_user))
                    return
            except AttributeError:
                pass

        # 好友消息消息转发主人
        if self.senderid not in self.administrators and self.keyword:
            for administrator in self.administrators:
                msg = f'[太阳]收到来自【{self.nickname}】的消息\n\n{self.keyword}\n\n———— NGC BOT ————[爱心]'
                ws.send(self.Ss.send_msg(msg=msg, wxid=administrator))

        # 清除缓存
        if self.judge_keyword(keyword=self.keyword,
                              custom_keyword=self.cache_words, ) and self.senderid in self.administrators:
            msg = self.Cs.delete_file()
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid))
            return 
        # 查看白名单群聊
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.show_white_room_words):
            white_room_id, white_room_name = self.Dus.show_white_room()
            msg = '[爱心]【已开启推送服务群聊列表】[爱心]\n'
            for room_name in white_room_name:
                msg += f'[庆祝]【{room_name}】\n'
            ws.send(self.Ss.send_msg(msg=msg.strip(), wxid=self.senderid))
        # AI对话
        elif self.keyword:
            self.Dus.add_user(wx_id=self.senderid, wx_name=self.nickname)
            recv_msg = self.Asm.get_ai(keyword=self.keyword.strip().replace(' ', ''))
            if not recv_msg:
                recv_msg = '[嘿哈]本Bot听不懂你在说什么啦，不过我已经将消息通知给主人啦[转圈]'
            msg = f'———— NGC BOT ————[爱心]\n\n{recv_msg}\n\n———— NGC BOT ————[爱心]\n更多功能回复【help】查看'
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid))

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
