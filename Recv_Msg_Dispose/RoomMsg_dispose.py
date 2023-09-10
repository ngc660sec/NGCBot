from Recv_Msg_Dispose.Thread_function import Thread_function
from Api_Server.Api_Server_Main import Api_Server_Main
from Db_Server.Db_Point_Server import Db_Point_Server
from Db_Server.Db_User_Server import Db_User_Server
from concurrent.futures import ThreadPoolExecutor
from BotServer.SendServer import SendServer
import yaml
import os
import re


class RoomMsg_disposes:
    def __init__(self, ):
        # 初始化核心参数
        self.bot_wxid = None
        self.bot_name = None
        self.room_name = None
        self.at_nickname = None
        self.at_wxid = None
        self.roomid = 'null'
        self.senderid = 'null'
        self.nickname = 'null'
        self.msgJson = ''

        # 处理过的接收的消息
        self.keyword = ''

        # 实例化消息服务
        self.Ss = SendServer()

        # 实例化接口服务类
        self.Asm = Api_Server_Main()

        # 实例化用户数据操作类
        self.Dus = Db_User_Server()

        # 实例化积分数据类
        self.Dps = Db_Point_Server()

        # 多线程处理接收消息
        self.Tf = Thread_function()

        self.pool = ThreadPoolExecutor(100)

        # 读取配置文件
        current_path = os.path.dirname(__file__)
        config = yaml.load(open(current_path + '/../config/config.yaml', encoding='UTF-8'), yaml.Loader)

        # 读取超级管理员
        self.administrators = config['Administrators']

        # 读取关键词配置
        self.pic_words = config['Key_Word']['Pic_Word']
        self.video_words = config['Key_Word']['Video_Word']
        self.icp_words = config['Key_Word']['Icp_Word']
        self.suffix_words = config['Key_Word']['Suffix_Word']
        self.attribution_words = config['Key_Word']['Attribution_Word']
        self.whois_words = config['Key_Word']['Whois_Word']
        self.fish_words = config['Key_Word']['Fish_Word']
        self.wether_words = config['Key_Word']['Weather_Word']
        self.md5_keyword = config['Key_Word']['Md5_Words']
        self.dog_words = config['Key_Word']['Dog_Word']
        self.constellation_words = config['Key_Word']['Constellation_Word']
        self.morning_words = config['Key_Word']['Morning_Word']
        self.threatbook_words = config['Key_Word']['ThreatBook_Word']
        self.add_admin_words = config['Key_Word']['Add_Admin_Word']
        self.del_admin_words = config['Key_Word']['Del_Admin_Word']
        self.add_BlackRoom_words = config['Key_Word']['Add_BlackRoom_Word']
        self.del_BlackRoom_words = config['Key_Word']['Del_BlackRoom_Word']
        self.add_WhiteRoom_words = config['Key_Word']['Add_WhiteRoom_Word']
        self.del_WhiteRoom_words = config['Key_Word']['Del_WhiteRoom_Word']
        self.add_point_words = config['Point_Function']['Add_Point_Word']
        self.del_point_words = config['Point_Function']['Del_Point_Word']
        self.threatbook_point = config['Point_Function']['Function']['ThreatBook_Point']
        self.md5_point = config['Point_Function']['Function']['Md5_Point']
        self.sign_keyword = config['Point_Function']['Sign_Keyword']

        self.query_point_words = config['Point_Function']['Query_Point']
        self.give_point_words = config['Point_Function']['Give_Point_Word']
        self.morning_page_words = config['Key_Word']['Morning_Page']
        self.evening_page_words = config['Key_Word']['Evening_Page']
        self.help_menu_words = config['System_Config']['Help_Menu']
        self.system_copyright = config['System_Config']['System_Copyright']

    # 获取接收信息
    def get_information(self, msgJson, roomid, senderid, nickname, ws):
        self.msgJson = msgJson
        # 获取群聊ID
        self.roomid = roomid
        # 获取发送者微信ID
        self.senderid = senderid
        # 获取发送者名字
        self.nickname = nickname

        # 获取被@人的微信ID
        id3 = self.msgJson['id3']
        self.at_wxid = 'wxid_' + re.search(r'wxid_(?P<id>.*?)[]|<]', id3).group('id') if 'wxid' in id3 else None
        if not self.at_wxid:
            self.at_wxid = re.search(r'<!\[CDATA\[(?P<id>.*?)]]>', id3).group('id') if 'CDATA' in id3 else None
            if not self.at_wxid:
                self.at_wxid = re.search(r'<atuserlist>(?P<id>.*?)</atuserlist>', id3).group('id') if 'atuserlist' in id3 else None

        # 获取被@人的昵称
        self.at_nickname = self.Ss.get_member_nick(roomid=self.roomid, wxid=self.at_wxid) if self.at_wxid else None

        # 获取接收到的内容，进行处理
        self.keyword = msgJson['content'].replace('\u2005', '')

        # 获取微信群聊名字
        self.room_name = self.Ss.get_member_nick(wxid=self.roomid, roomid=self.roomid)

        # 获取机器人的微信id，和名字
        self.bot_wxid = self.Ss.get_bot_info()
        self.bot_name = self.Ss.get_member_nick(roomid=self.roomid, wxid=self.bot_wxid)

        # 处理接收消息
        self.process_information(ws)

    # 处理接收到的信息
    def process_information(self, ws):
        # print(self.at_wxid, self.at_nickname, self.room_name)
        # print(self.at_wxid)
        # 超级管理员功能
        if self.senderid in self.administrators:
            self.Administrator_Function(ws=ws)
            self.Admin_Function(ws=ws)
            self.Integral_Function(ws=ws)
            self.Happy_Function(ws=ws)

        # 管理员功能
        elif self.judge_admin(wxid=self.senderid, roomid=self.roomid) or self.senderid in self.administrators:
            self.Admin_Function(ws=ws)
            self.Integral_Function(ws=ws)
            self.Happy_Function(ws=ws)
        # 黑名单群聊功能
        elif self.judge_black_room(roomid=self.roomid):
            self.Integral_Function(ws=ws)
        # 正常用户,正常群聊功能
        else:
            self.Integral_Function(ws=ws)
            self.Happy_Function(ws=ws)

    # 超级管理员功能
    def Administrator_Function(self, ws):
        # 新增管理员
        if '\u2005' in self.msgJson['content'] and \
                self.judge_keyword(keyword=self.keyword.replace('@', '').replace(self.at_nickname, ''),
                                   custom_keyword=self.add_admin_words):
            self.pool.submit(self.Tf.add_admin, ws, self.at_wxid, self.at_nickname, self.roomid, self.room_name,
                             self.senderid, self.nickname)
        # 删除管理员
        elif '\u2005' in self.msgJson['content'] and \
                self.judge_keyword(keyword=self.keyword.replace('@', '').replace(self.at_nickname, ''),
                                   custom_keyword=self.del_admin_words):
            self.pool.submit(self.Tf.del_admin, ws, self.at_wxid, self.at_nickname, self.roomid, self.senderid,
                             self.nickname)

    # 管理员功能
    def Admin_Function(self, ws):
        # 新增黑名单群聊
        if self.judge_keyword(keyword=self.keyword, custom_keyword=self.add_BlackRoom_words):
            self.pool.submit(self.Tf.add_black_room, ws, self.roomid, self.room_name, self.senderid, self.nickname)
        # 删除黑名单群聊
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.del_BlackRoom_words):
            self.pool.submit(self.Tf.del_black_room, ws, self.roomid, self.room_name, self.senderid, self.nickname)

        # 新增白名单群聊
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.add_WhiteRoom_words):
            self.pool.submit(self.Tf.add_white_room, ws, self.roomid, self.room_name, self.senderid, self.nickname)
        # 删除白名单群聊
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.del_WhiteRoom_words):
            self.pool.submit(self.Tf.del_white_room, ws, self.roomid, self.room_name, self.senderid, self.nickname)
        # 早报推送
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.morning_page_words):
            self.pool.submit(self.Tf.send_morning_page, ws, self.roomid)
        # 晚报推送
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.evening_page_words):
            self.pool.submit(self.Tf.send_evening_page, ws, self.roomid)

    # 积分功能
    def Integral_Function(self, ws):
        # AI对话
        if self.at_wxid == self.bot_wxid and 'gh_' not in self.roomid:
            if '所有人' not in self.keyword and '@' in self.keyword:
                keyword = self.keyword.replace('@', '').replace(self.bot_name, '').strip().replace(' ', '')
                self.pool.submit(self.Tf.send_ai, ws, keyword, self.senderid, self.roomid, self.nickname)
        # 微步查询
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.threatbook_words, split_bool=True):
            self.pool.submit(self.Tf.find_threatbook_ip, ws, self.keyword, self.nickname, self.roomid, self.senderid)
        # 签到口令提醒
        elif self.judge_keyword(keyword=self.keyword, custom_keyword='签到', one_bool=True):
            self.pool.submit(self.Tf.sign_remind, ws, self.senderid, self.roomid, self.nickname)
        # 签到功能
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.sign_keyword, one_bool=True):
            self.pool.submit(self.Tf.sign, ws, self.senderid, self.roomid, self.nickname)
        # 查询积分
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.query_point_words):
            self.pool.submit(self.Tf.query_point, ws, self.senderid, self.roomid, self.nickname)
        # MD5解密
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.md5_keyword, split_bool=True):
            self.pool.submit(self.Tf.decrypt_md5, ws, self.keyword, self.senderid, self.roomid, self.nickname)
        # 积分加减操作
        self.pool.submit(self.Tf.judge_operation, ws, self.keyword, self.senderid, self.at_wxid, self.at_nickname,
                         self.roomid, self.nickname)

    # 娱乐功能
    def Happy_Function(self, ws):
        # 美女图片
        if self.judge_keyword(keyword=self.keyword, custom_keyword=self.pic_words):
            self.pool.submit(self.Tf.send_pic, ws, self.roomid)
        # 美女视频
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.video_words):
            self.pool.submit(self.Tf.send_video, ws, self.roomid)
        # icp查询
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.icp_words, split_bool=True):
            self.pool.submit(self.Tf.query_icp, ws, self.keyword, self.senderid, self.roomid, self.nickname)
        # 后缀名查询
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.suffix_words, split_bool=True):
            self.pool.submit(self.Tf.query_suffix, ws, self.keyword, self.senderid, self.roomid, self.nickname)
        # 归属查询
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.attribution_words, split_bool=True):
            self.pool.submit(self.Tf.query_attribution, ws, self.keyword, self.senderid, self.roomid, self.nickname)
        # whois查询
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.whois_words, split_bool=True):
            self.pool.submit(self.Tf.query_whois, ws, self.keyword, self.senderid, self.roomid, self.nickname)
        # 摸鱼日历
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.fish_words):
            self.pool.submit(self.Tf.get_fish, self.roomid)
        # 天气查询
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.wether_words, split_bool=True):
            self.pool.submit(self.Tf.query_wether, ws, self.keyword, self.senderid, self.roomid, self.nickname)
        # 舔狗日记
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.dog_words):
            self.pool.submit(self.Tf.get_dog, ws, self.senderid, self.roomid, self.nickname)
        # 星座查询
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.constellation_words, split_bool=True):
            self.pool.submit(self.Tf.query_constellation, ws, self.keyword, self.senderid, self.roomid, self.nickname)
        # 早安寄语
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.morning_words):
            self.pool.submit(self.Tf.get_morning, ws, self.senderid, self.roomid, self.nickname)
        # 帮助菜单
        self.pool.submit(self.Tf.help_menu, ws, self.keyword, self.roomid)

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
            # print(keyword, custom_keyword)
            return True if [ckw for ckw in custom_keyword if ckw == keyword] else False

    # 判断管理员
    def judge_admin(self, wxid, roomid):
        admin_list = self.Dus.show_admin()
        for data in admin_list:
            if wxid == data['wx_id'] and roomid == data['wx_roomid']:
                return True
        else:
            return False

    # 判断黑名单
    def judge_black_room(self, roomid):
        black_rooms = self.Dus.show_black_room()
        for data in black_rooms:
            if roomid == data['wx_roomid']:
                return True
        else:
            return False

    # 判断积分余额
    def judge_point(self, ws, wxid, roomid, function_point):
        user_point = self.Dps.query_point(wx_id=wxid, wx_name=self.nickname)
        if user_point < function_point:
            if not self.judge_admin(wxid=self.senderid, roomid=self.roomid):
                if not self.senderid in self.administrators:
                    ws.send(
                        self.Ss.send_msg(msg=f'\n积分不足，当前可用积分：{user_point}\n功能积分：{function_point}', wxid=self.senderid,
                                         roomid=roomid, nickname=self.nickname))
        return True if user_point >= function_point else False
