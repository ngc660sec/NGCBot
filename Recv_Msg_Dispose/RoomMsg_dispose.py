from Api_Server.Api_Server_Main import Api_Server_Main
from Db_Server.Db_Point_Server import Db_Point_Server
from Db_Server.Db_User_Server import Db_User_Server
from BotServer.SendServer import SendServer
from Output.output import output
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

        try:
            self.at_wxid = re.findall(r"<!\[CDATA\[,(.*?)]]", str(self.msgJson['id3']))[0] if 'CDATA' in str(
                msgJson) else None
        except IndexError:
            self.at_wxid = re.findall(r"<!\[CDATA\[(.*?)]]", str(self.msgJson['id3']))[0] if 'CDATA' in str(
                msgJson) else None

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
            msg = self.Dus.add_admin(wx_id=self.at_wxid, wx_name=self.at_nickname, wx_roomid=self.roomid,
                                     wx_room_name=self.room_name)
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, nickname=self.nickname, roomid=self.roomid))
        # 删除管理员
        elif '\u2005' in self.msgJson['content'] and \
                self.judge_keyword(keyword=self.keyword.replace('@', '').replace(self.at_nickname, ''),
                                   custom_keyword=self.del_admin_words):
            msg = self.Dus.del_admin(wx_id=self.at_wxid, wx_name=self.at_nickname, wx_roomid=self.roomid, )
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, nickname=self.nickname, roomid=self.roomid))

    # 管理员功能
    def Admin_Function(self, ws):
        # 新增黑名单群聊
        if self.judge_keyword(keyword=self.keyword, custom_keyword=self.add_BlackRoom_words):
            msg = self.Dus.add_black_room(wx_roomid=self.roomid, wx_room_name=self.room_name)
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, nickname=self.nickname, roomid=self.roomid))
        # 删除黑名单群聊
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.del_BlackRoom_words):
            msg = self.Dus.del_black_room(wx_roomid=self.roomid, wx_room_name=self.room_name)
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, nickname=self.nickname, roomid=self.roomid))
        # 新增白名单群聊
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.add_WhiteRoom_words):
            msg = self.Dus.add_white_room(wx_roomid=self.roomid, wx_room_name=self.room_name)
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, nickname=self.nickname, roomid=self.roomid))
        # 删除白名单群聊
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.del_WhiteRoom_words):
            msg = self.Dus.del_white_room(wx_roomid=self.roomid, wx_room_name=self.room_name)
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, nickname=self.nickname, roomid=self.roomid))
        # 早报推送
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.morning_page_words):
            msg = self.Asm.get_freebuf_news()
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.roomid))
        # 晚报推送
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.evening_page_words):
            msg = self.Asm.get_safety_news()
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.roomid))
        # 积分加减操作
        self.judge_operation(keyword=self.keyword, ws=ws)

    # 积分功能
    def Integral_Function(self, ws):
        # 微步查询
        if self.judge_keyword(keyword=self.keyword, custom_keyword=self.threatbook_words, split_bool=True):
            if self.judge_point(wxid=self.senderid, point=self.threatbook_point):
                msg = self.Asm.get_threatbook_ip(keyword=self.keyword)
                if len(msg) > 20:
                    point_msg = f'\n您使用了IP查询功能，扣除对应积分 {self.threatbook_point}分\n当前可用积分：{self.Dps.query_point(wx_id=self.senderid)}'
                    self.Dps.del_point(wx_id=self.senderid, point=self.threatbook_point)
                    ws.send(
                        self.Ss.send_msg(msg=point_msg, wxid=self.senderid, roomid=self.roomid, nickname=self.nickname))
                ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, roomid=self.roomid, nickname=self.nickname))
        # 签到口令提醒
        elif self.judge_keyword(keyword=self.keyword, custom_keyword='签到', one_bool=True):
            msg = f'签到口令已改为：{self.sign_keyword}'
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, nickname=self.nickname, roomid=self.roomid))
        # 签到功能
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.sign_keyword, one_bool=True):
            msg = self.Dps.judge_main(wx_id=self.senderid, wx_name=self.nickname, sign_bool=True)
            if msg:
                ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, nickname=self.nickname, roomid=self.roomid))
        # 查询积分
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.query_point_words):
            msg = f'\n当前可用积分：{0 if not self.Dps.query_point(wx_id=self.senderid) else self.Dps.query_point(wx_id=self.senderid)}'
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, nickname=self.nickname, roomid=self.roomid))

    # 娱乐功能
    def Happy_Function(self, ws):
        # AI对话
        if self.at_wxid == self.bot_wxid:
            keyword = self.keyword.replace('@', '').replace(self.bot_name, '').strip()
            if keyword:
                msg = self.Asm.get_ai(keyword=keyword)
                ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, nickname=self.nickname, roomid=self.roomid, ))
            else:
                return
        # 美女图片
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.pic_words):
            msg = self.Asm.get_pic()
            if '/' in msg:
                self.Ss.send_img_room(msg=msg, roomid=self.roomid)
            else:
                ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid))
        # 美女视频
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.video_words):
            msg = self.Asm.get_video()
            if '/' in msg:
                self.Ss.send_file_room(file=msg, roomid=self.roomid)
            else:
                ws.send(self.Ss.send_msg(msg=msg, wxid=self.roomid))
        # icp查询
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.icp_words, split_bool=True):
            msg = self.Asm.get_icp(keyword=self.keyword)
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, roomid=self.roomid, nickname=self.nickname))
        # 后缀名查询
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.suffix_words, split_bool=True):
            msg = self.Asm.get_suffix(keyword=self.keyword)
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, roomid=self.roomid, nickname=self.nickname))
        # 归属查询
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.attribution_words, split_bool=True):
            msg = self.Asm.get_attribution(keyword=self.keyword)
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, roomid=self.roomid, nickname=self.nickname))
        # whois查询
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.whois_words, split_bool=True):
            msg = self.Asm.get_whois(keyword=self.keyword)
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, roomid=self.roomid, nickname=self.nickname))
        # 摸鱼日记
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.fish_words):
            msg = self.Asm.get_fish()
            self.Ss.send_img_room(msg=msg, roomid=self.roomid)
        # 天气查询
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.wether_words, split_bool=True):
            msg = self.Asm.get_wether(keyword=self.keyword)
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, roomid=self.roomid, nickname=self.nickname))
        # 舔狗日记
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.dog_words):
            msg = self.Asm.get_dog()
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, roomid=self.roomid, nickname=self.nickname))
        # 星座查询
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.constellation_words, split_bool=True):
            msg = self.Asm.get_constellation(keyword=self.keyword)
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, roomid=self.roomid, nickname=self.nickname))
        # 早安寄语
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.morning_words):
            msg = self.Asm.get_morning()
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, roomid=self.roomid, nickname=self.nickname))
        # 帮助菜单
        elif self.judge_keyword(keyword=self.keyword, custom_keyword=self.help_menu_words):
            msg = f"NGCBot功能菜单\n【积分功能】\n【1】、微步威胁IP查询\n\n您可在群内发送信息【WHOIS查询 qq.com】不需要@本Bot哦\n\n【娱乐功能】\n" \
                  f"【1】、美女图片\n【2】、美女视频\n【3】、舔狗日记\n【4】、摸鱼日历\n【5】、星座查询\n【6】、AI对话\n【7】、手机号归属地查询\n【8】、WHOIS信息查询\n" \
                  f"【9】、备案查询\n【10】、后缀名查询\n\n您可以在群内发送消息【查询运势 白羊座】进行查询【其它功能类似】，或@本Bot进行AI对话哦\n\n需要调出帮助菜单，回复即可【帮助菜单】\n" \
                  f"{'By: #' + self.system_copyright if self.system_copyright else ''}"
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.roomid))

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
    def judge_point(self, wxid, point):
        user_point = self.Dps.query_point(wx_id=wxid)
        return True if user_point > point else False

    # 判断积分增减赠送
    def judge_operation(self, keyword, ws):
        list_bool = False
        at_wx_nickname_list = list()
        at_wxid_list = list()
        if self.at_wxid:
            operations = re.search(
                f'@{self.at_nickname.strip() if self.at_nickname.strip() else "xx"}(?P<operation>\w)(?P<point>\d+)',
                keyword)
            if ',' in self.at_wxid:
                list_bool = True
                at_wxid_list = self.at_wxid.split(',')
                for at_wxid in at_wxid_list:
                    at_wx_nickname_list.append(self.Ss.get_member_nick(roomid=self.roomid, wxid=at_wxid))
                operations = re.search(
                    f'{"".join(at_wx_nickname_list) if "".join(at_wx_nickname_list) else "xx"}(?P<operation>\w)(?P<point>\d+)',
                    keyword.replace('@', ''))
            try:
                operation = operations.group('operation')
                point = int(operations.group('point'))
            except Exception as e:
                output(f'[+]:小报错，问题不大：{e}')
                return
            msg = ''
            # print(operation, point)
            give_bool = False
            # 赠送积分
            if self.judge_keyword(keyword=operation, custom_keyword=self.add_point_words):
                if list_bool:
                    for wxid, wx_name in zip(at_wxid_list, at_wx_nickname_list):
                        msg = self.Dps.judge_main(wx_id=self.at_wxid, wx_name=self.at_nickname, point=point,
                                                  add_bool=True)
                        ws.send(
                            self.Ss.send_msg(msg=msg, wxid=wxid, nickname=wx_name, roomid=self.roomid))
                else:
                    msg = self.Dps.judge_main(wx_id=self.at_wxid, wx_name=self.at_nickname, point=point, add_bool=True)
            # 扣除积分
            if self.judge_keyword(keyword=operation, custom_keyword=self.del_point_words):
                if list_bool:
                    for wxid, wx_name in zip(at_wxid_list, at_wx_nickname_list):
                        msg = self.Dps.judge_main(wx_id=self.at_wxid, wx_name=self.at_nickname, point=point,
                                                  del_bool=True)
                        ws.send(
                            self.Ss.send_msg(msg=msg, wxid=wxid, nickname=wx_name, roomid=self.roomid))
                else:
                    msg = self.Dps.judge_main(wx_id=self.at_wxid, wx_name=self.at_nickname, point=point, del_bool=True)
            # 赠送积分
            if self.judge_keyword(keyword=operation, custom_keyword=self.give_point_words):
                if list_bool:
                    for wxid, wx_name in zip(at_wxid_list, at_wx_nickname_list):
                        msg, give_bool = self.Dps.give_point(wx_id=self.senderid, wx_name=self.nickname,
                                                             at_wx_id=wxid, at_wx_name=wx_name,
                                                             point=point)
                        ws.send(
                            self.Ss.send_msg(msg=msg, wxid=self.senderid, nickname=self.nickname, roomid=self.roomid))
                else:
                    msg, give_bool = self.Dps.give_point(wx_id=self.senderid, wx_name=self.nickname, at_wx_id=self.at_wxid, at_wx_name=self.at_nickname, point=point)
            if msg and not list_bool and ',' not in self.at_wxid:
                if give_bool:
                    self.at_wxid = self.senderid
                    self.at_nickname = self.nickname
                ws.send(self.Ss.send_msg(msg=msg, wxid=self.at_wxid, nickname=self.at_nickname, roomid=self.roomid))
