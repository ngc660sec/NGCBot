from BotServer.SendServer import SendServer
from Api_Server.Api_Server_Main import Api_Server_Main
from Cache.Cache_Server import Cache_Server
import yaml
import re
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

        # 获取关键词
        self.cache_words = config['System_Config']['Cache_Config_Word']
        self.help_menu_words = config['System_Config']['Help_Menu']
        self.system_copyright = config['System_Config']['System_Copyright']

        # 实例化消息发送服务
        self.Ss = SendServer()

        # 实例化接口服务类
        self.Asm = Api_Server_Main()

        # 实例化缓存操作类
        self.Cs = Cache_Server()

    def get_information(self, msgJson, senderid, ws):
        self.senderid = senderid
        self.nickname = self.Ss.get_member_nick(wxid=senderid, roomid='null')
        self.keyword = msgJson['content'].replace('\u2005', '')
        self.process_information(ws)

    def process_information(self, ws):
        # 清除缓存
        if self.judge_keyword(keyword=self.keyword, custom_keyword=self.cache_words, ):
            msg = self.Cs.delete_file()
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid))
            return
        # 帮助菜单
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.help_menu_words):
            msg = f"NGCBot功能菜单\n【积分功能】\n【1】、微步威胁IP查询\n\n您可在群内发送信息【WHOIS查询 qq.com】不需要@本Bot哦\n\n【娱乐功能】\n" \
                  f"【1】、美女图片\n【2】、美女视频\n【3】、舔狗日记\n【4】、摸鱼日历\n【5】、星座查询\n【6】、AI对话\n【7】、手机号归属地查询\n【8】、WHOIS信息查询\n" \
                  f"【9】、备案查询\n【10】、后缀名查询\n\n您可以在群内发送消息【查询运势 白羊座】进行查询【其它功能类似】，或@本Bot进行AI对话哦\n\n需要调出帮助菜单，回复即可【帮助菜单】\n" \
                  f"{'By: #' + self.system_copyright if self.system_copyright else ''}"
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid))
            return
        # AI对话
        elif self.keyword:
            if self.keyword:
                msg = self.Asm.get_ai(keyword=self.keyword)
                ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid))
            else:
                return

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



