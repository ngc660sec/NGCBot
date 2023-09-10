from Api_Server.Api_Server_Main import Api_Server_Main
from Db_Server.Db_Point_Server import Db_Point_Server
from Db_Server.Db_User_Server import Db_User_Server
from BotServer.SendServer import SendServer
from concurrent.futures import ThreadPoolExecutor
from Cache.Cache_Server import Cache_Server
import yaml
import os
import re


class Thread_function:
    def __init__(self):
        # 实例化消息服务
        self.Ss = SendServer()

        # 实例化接口服务类
        self.Asm = Api_Server_Main()

        # 实例化用户数据操作类
        self.Dus = Db_User_Server()

        # 实例化积分数据类
        self.Dps = Db_Point_Server()

        # 实例化缓存操作类
        self.Cs = Cache_Server()

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
        self.md5_point = config['Point_Function']['Function']['Md5_Point']
        self.ai_point = config['Point_Function']['Function']['Ai_point']
        self.sign_keyword = config['Point_Function']['Sign_Keyword']
        self.query_point_words = config['Point_Function']['Query_Point']
        self.give_point_words = config['Point_Function']['Give_Point_Word']
        self.morning_page_words = config['Key_Word']['Morning_Page']
        self.evening_page_words = config['Key_Word']['Evening_Page']
        self.help_menu_words = config['System_Config']['Help_Menu']
        self.system_copyright = config['System_Config']['System_Copyright']

        self.pool = ThreadPoolExecutor(100)

    # 超级管理员-新增管理员
    def add_admin(self, ws, at_wxid, at_nickname, roomid, room_name, senderid, nickname):
        msg = self.Dus.add_admin(wx_id=at_wxid, wx_name=at_nickname, wx_roomid=roomid,
                                 wx_room_name=room_name)
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, nickname=nickname, roomid=roomid))

    # 管理员功能-新增黑名单群聊
    def add_black_room(self, ws, roomid, room_name, senderid, nickname):
        msg = self.Dus.add_black_room(wx_roomid=roomid, wx_room_name=room_name)
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, nickname=nickname, roomid=roomid))

    # 管理员功能-删除黑名单群聊
    def del_black_room(self, ws, roomid, room_name, senderid, nickname):
        msg = self.Dus.del_black_room(wx_roomid=roomid, wx_room_name=room_name)
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, nickname=nickname, roomid=roomid))

    # 管理员功能-新增白名单群聊
    def add_white_room(self, ws, roomid, room_name, senderid, nickname):
        msg = self.Dus.add_white_room(wx_roomid=roomid, wx_room_name=room_name)
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, nickname=nickname, roomid=roomid))

    # 管理员功能-删除白名单群聊
    def del_white_room(self, ws, roomid, room_name, senderid, nickname):
        msg = self.Dus.del_white_room(wx_roomid=roomid, wx_room_name=room_name)
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, nickname=nickname, roomid=roomid))

    # 超级管理员-删除管理员
    def del_admin(self, ws, at_wxid, at_nickname, roomid, senderid, nickname):
        msg = self.Dus.del_admin(wx_id=at_wxid, wx_name=at_nickname, wx_roomid=roomid, )
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, nickname=nickname, roomid=roomid))

    # 管理员功能-早报推送
    def send_morning_page(self, ws, roomid):
        msg = self.Asm.get_freebuf_news()
        ws.send(self.Ss.send_msg(msg=msg, wxid=roomid))

    # 管理员功能-晚报推送
    def send_evening_page(self, ws, roomid):
        msg = self.Asm.get_safety_news()
        ws.send(self.Ss.send_msg(msg=msg, wxid=roomid))

    # 积分功能-微步ip查询
    def find_threatbook_ip(self, ws, keyword, nickname, roomid,  senderid):
        if self.judge_point(ws=ws, roomid=roomid, function_point=self.threatbook_point, nickname=nickname, senderid=senderid):
            msg = self.Asm.get_threatbook_ip(keyword=keyword)
            if len(msg) > 20:
                if not self.judge_admin(wxid=senderid, roomid=roomid):
                    if not senderid in self.administrators:
                        self.Dps.del_point(wx_id=senderid, point=self.threatbook_point)
                        point_msg = f'\n您使用了IP查询功能，扣除对应积分 {self.threatbook_point}分\n当前可用积分：{self.Dps.query_point(wx_id=senderid)}'
                        ws.send(
                            self.Ss.send_msg(msg=point_msg, wxid=senderid, roomid=roomid,
                                             nickname=nickname))
            ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, roomid=roomid, nickname=nickname))

    # 积分功能-签到口令提醒
    def sign_remind(self, ws, senderid, roomid, nickname):
        msg = f'签到口令已改为：{self.sign_keyword}'
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, nickname=nickname, roomid=roomid))

    # 积分功能-签到功能
    def sign(self, ws, senderid, roomid, nickname):
        msg = self.Dps.judge_main(wx_id=senderid, wx_name=nickname, sign_bool=True)
        if msg:
            ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, nickname=nickname, roomid=roomid))

    # 积分功能-积分查询功能
    def query_point(self, ws, senderid, roomid, nickname):
        msg = f'\n当前可用积分：{0 if not self.Dps.query_point(wx_id=senderid, wx_name=senderid) else self.Dps.query_point(wx_id=senderid, wx_name=nickname)}'
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, nickname=nickname, roomid=roomid))

    # 积分功能-积分加减操作
    def judge_operation(self, ws, keyword, senderid, at_wxid, at_nickname, roomid, nickname):
        list_bool = False
        at_wx_nickname_list = list()
        at_wxid_list = list()
        if at_wxid:
            operations = re.search(
                f'@{at_nickname.strip() if at_nickname.strip() else "xx"}(?P<operation>\w|\+|-)(?P<point>\d+)',
                keyword)
            if ',' in at_wxid:
                list_bool = True
                at_wxid_list = at_wxid.split(',')
                for at_wxid in at_wxid_list:
                    at_wx_nickname_list.append(self.Ss.get_member_nick(roomid=roomid, wxid=at_wxid))
                operations = re.search(
                    f'{"".join(at_wx_nickname_list) if "".join(at_wx_nickname_list) else "xx"}(?P<operation>\w|\+|-)(?P<point>\d+)',
                    keyword.replace('@', ''))
            try:
                operation = operations.group('operation')
                point = int(operations.group('point'))
            except Exception as e:
                # output(f'[+]:小报错，问题不大：{e}')
                return

            msg = ''
            give_bool = False
            # 增加积分
            if self.judge_keyword(keyword=operation, custom_keyword=self.add_point_words, ):
                if self.judge_admin(wxid=senderid, roomid=roomid) or senderid in self.administrators:
                    if list_bool:
                        for wxid, wx_name in zip(at_wxid_list, at_wx_nickname_list):
                            msg = self.Dps.judge_main(wx_id=wxid, wx_name=wx_name, point=point,
                                                      add_bool=True)
                            ws.send(
                                self.Ss.send_msg(msg=msg, wxid=wxid, nickname=wx_name, roomid=roomid))
                    else:
                        msg = self.Dps.judge_main(wx_id=at_wxid, wx_name=at_nickname, point=point, add_bool=True)

            # 扣除积分
            if self.judge_keyword(keyword=operation, custom_keyword=self.del_point_words):
                if self.judge_admin(wxid=senderid, roomid=roomid) or senderid in self.administrators:
                    if list_bool:
                        for wxid, wx_name in zip(at_wxid_list, at_wx_nickname_list):
                            msg = self.Dps.judge_main(wx_id=wxid, wx_name=wx_name, point=point,
                                                      del_bool=True)
                            ws.send(
                                self.Ss.send_msg(msg=msg, wxid=wxid, nickname=wx_name, roomid=roomid))
                    else:
                        msg = self.Dps.judge_main(wx_id=at_wxid, wx_name=at_nickname, point=point, del_bool=True)
            # 赠送积分
            if self.judge_keyword(keyword=operation, custom_keyword=self.give_point_words):
                if list_bool:
                    for wxid, wx_name in zip(at_wxid_list, at_wx_nickname_list):
                        msg, give_bool = self.Dps.give_point(wx_id=senderid, wx_name=nickname,
                                                             at_wx_id=at_wxid, at_wx_name=wx_name,
                                                             point=point)
                        ws.send(
                            self.Ss.send_msg(msg=msg, wxid=senderid, nickname=nickname, roomid=roomid))
                else:
                    msg, give_bool = self.Dps.give_point(wx_id=senderid, wx_name=nickname,
                                                         at_wx_id=at_wxid, at_wx_name=at_nickname,
                                                         point=point)

            # 赠送积分
            if msg and not list_bool and ',' not in at_wxid:
                if give_bool:
                    at_wxid = senderid
                    at_nickname = nickname
                ws.send(self.Ss.send_msg(msg=msg, wxid=at_wxid, nickname=at_nickname, roomid=roomid))

    # 积分功能-AI对话
    def send_ai(self, ws, keyword, senderid, roomid, nickname):
        if self.judge_point(ws=ws, roomid=roomid, function_point=self.ai_point, nickname=nickname,
                            senderid=senderid) and keyword:
            if not self.judge_admin(wxid=senderid, roomid=roomid):
                if not senderid in self.administrators:
                    self.Dps.del_point(wx_id=senderid, point=self.ai_point)
                    point_msg = f'\n您使用了AI对话查询功能，扣除对应积分 {self.ai_point}分\n当前可用积分：{self.Dps.query_point(wx_id=senderid)}'
                    ws.send(
                        self.Ss.send_msg(msg=point_msg, wxid=senderid, roomid=roomid,
                                         nickname=nickname))
            msg = self.Asm.get_ai(keyword=keyword)
            ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, nickname=nickname, roomid=roomid, ))

    # 积分功能-MD5解密
    def decrypt_md5(self, ws, keyword, senderid, roomid, nickname):
        if not self.judge_admin(wxid=senderid, roomid=roomid):
            if not senderid in self.administrators:
                self.Dps.del_point(wx_id=senderid, point=self.md5_point)
                point_msg = f'\n您使用了MD5解密功能，扣除对应积分 {self.md5_point}分\n当前可用积分：{self.Dps.query_point(wx_id=senderid)}'
                ws.send(
                    self.Ss.send_msg(msg=point_msg, wxid=senderid, roomid=roomid,
                                     nickname=nickname))
            msg = self.Asm.get_md5(keyword)
            ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, nickname=nickname, roomid=roomid, ))

    # 娱乐功能-美女图片
    def send_pic(self, ws, roomid):
        msg = self.Asm.get_pic()
        if '/' in msg:
            self.Ss.send_img_room(msg=msg, roomid=roomid)
        else:
            ws.send(self.Ss.send_msg(msg=msg, wxid=roomid))

    # 娱乐功能-美女视频
    def send_video(self, ws, roomid):
        msg = self.Asm.get_video()
        if '/' in msg:
            self.Ss.send_file_room(file=msg, roomid=roomid)
        else:
            ws.send(self.Ss.send_msg(msg=msg, wxid=roomid))

    # 娱乐功能-ICP查询
    def query_icp(self, ws, keyword, senderid, roomid, nickname):
        msg = self.Asm.get_icp(keyword=keyword)
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, roomid=roomid, nickname=nickname))

    # 娱乐功能-后缀名查询
    def query_suffix(self, ws, keyword, senderid, roomid, nickname):
        msg = self.Asm.get_suffix(keyword=keyword)
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, roomid=roomid, nickname=nickname))

    # 娱乐功能-手机归属查询
    def query_attribution(self, ws, keyword, senderid, roomid, nickname):
        msg = self.Asm.get_attribution(keyword=keyword)
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, roomid=roomid, nickname=nickname))

    # 娱乐功能-WHOIS查询
    def query_whois(self, ws, keyword, senderid, roomid, nickname):
        msg = self.Asm.get_whois(keyword=keyword)
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, roomid=roomid, nickname=nickname))

    # 娱乐功能-摸鱼日记
    def get_fish(self, roomid):
        msg = self.Asm.get_fish()
        self.Ss.send_img_room(msg=msg, roomid=roomid)

    # 娱乐功能-天气查询
    def query_wether(self, ws, keyword, senderid, roomid, nickname):
        msg = self.Asm.get_wether(keyword=keyword)
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, roomid=roomid, nickname=nickname))

    # 娱乐功能-舔狗日记
    def get_dog(self, ws, senderid, roomid, nickname):
        msg = self.Asm.get_dog()
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, roomid=roomid, nickname=nickname))

    # 娱乐功能-星座查询
    def query_constellation(self, ws, keyword, senderid, roomid, nickname):
        msg = self.Asm.get_constellation(keyword=keyword)
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, roomid=roomid, nickname=nickname))

    # 娱乐功能-早安寄语
    def get_morning(self, ws, senderid, roomid, nickname):
        msg = self.Asm.get_morning()
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid, roomid=roomid, nickname=nickname))

    # 好友消息-转发消息给好友
    def retransmission_msg(self, ws, keyword):
        try:
            patten = re.search(r'给(?P<nickname>.*?)发消息 (?P<msg>.*)', keyword)
            msg = patten.group('msg')
            nickname = patten.group('nickname')
            recv_user = self.Dus.show_userid(wx_name=nickname.strip())
            if recv_user:
                msg = f'—— 来自主人的消息 ——[庆祝]\n\n{msg}\n\n—— 来自主人的消息 ——[庆祝]'
                ws.send(self.Ss.send_msg(msg=msg, wxid=recv_user))
                return
        except AttributeError:
            pass

    # 好友消息-好友消息转发给主人
    def retransmission_boos(self, ws, keyword, nickname):
        for administrator in self.administrators:
            msg = f'[太阳]收到来自【{nickname}】的消息\n\n{keyword}\n\n———— NGC BOT ————[爱心]'
            ws.send(self.Ss.send_msg(msg=msg, wxid=administrator))

    # 好友消息-清除缓存
    def clear_temps(self, ws, senderid):
        msg = self.Cs.delete_file()
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid))
        return

    # 好友消息-查看白名单群聊
    def show_white_rooms(self, ws, senderid):
        white_room_id, white_room_name = self.Dus.show_white_room()
        msg = '[爱心]【已开启推送服务群聊列表】[爱心]\n'
        for room_name in white_room_name:
            msg += f'[庆祝]【{room_name}】\n'
        ws.send(self.Ss.send_msg(msg=msg.strip(), wxid=senderid))

    # 好友消息-AI对话
    def friend_ai(self, ws, keyword, senderid, nickname):
        self.Dus.add_user(wx_id=senderid, wx_name=nickname)
        recv_msg = self.Asm.get_ai(keyword=keyword.strip().replace(' ', ''))
        if not recv_msg:
            recv_msg = '[嘿哈]本Bot听不懂你在说什么啦，不过我已经将消息通知给主人啦[转圈]'
        msg = f'———— NGC BOT ————[爱心]\n\n{recv_msg}\n\n———— NGC BOT ————[爱心]\n更多功能回复【help】查看'
        ws.send(self.Ss.send_msg(msg=msg, wxid=senderid))

    # 帮助菜单功能
    def help_menu(self, ws, keyword, roomid):
        if self.judge_keyword(keyword=keyword, custom_keyword=self.help_menu_words):
            msg = f"[爱心] ———— NGCBot功能菜单 ———— [爱心]\n[庆祝]【一、积分功能】\n[庆祝]【1.1】、微步威胁IP查询\n\n您可在群内发送信息【WHOIS查询 qq.com】不需要@本Bot哦\n\n[烟花]【二、娱乐功能】\n" \
                  f"[烟花]【2.1】、美女图片\n[烟花]【2.2】、美女视频\n[烟花]【2.3】、舔狗日记\n[烟花]【2.4】、摸鱼日历\n[烟花]【2.5】、星座查询\n[烟花]【2.6】、AI对话\n[烟花]【2.7】、手机号归属地查询\n[烟花]【2.8】、WHOIS信息查询\n" \
                  f"[烟花]【2.9】、备案查询\n[烟花]【2.10】、后缀名查询\n[烟花]【2.11】、MD5解密\n\n您可以在群内发送消息【查询运势 白羊座】进行查询【其它功能类似】，或@本Bot进行AI对话哦\n\n需要调出帮助菜单，回复【帮助菜单】即可\n" \
                  f"回复【help 2.1】可获取相应功能帮助[跳跳]，其它功能帮助以此类推[爱心]\n" \
                  f"{'By #' + self.system_copyright if self.system_copyright else ''}"
            ws.send(self.Ss.send_msg(msg=msg, wxid=roomid))
        elif 'help' in keyword.lower():
            child_help = keyword.strip().split(' ')[1]
            msg = ''
            if child_help == '1.1':
                msg = '[庆祝]【1.1】、微步威胁IP查询功能帮助\n\n[爱心]命令：【ip查询 x.x.x.x】'
            elif child_help == '2.1':
                msg = '[烟花]【2.1】、美女图片功能帮助\n\n[爱心]命令：【图片】【美女图片】'
            elif child_help == '2.2':
                msg = '[烟花]【2.2】、美女视频功能帮助\n\n[爱心]命令：【视频】【美女视频】'
            elif child_help == '2.3':
                msg = '[烟花]【2.3】、舔狗日记功能帮助\n\n[爱心]命令：【舔狗日记】'
            elif child_help == '2.4':
                msg = '[烟花]【2.4】、摸鱼日历功能帮助\n\n[爱心]命令：【摸鱼日历】\n\n[爱心]联系主人可开启定时发送哦[跳跳]'
            elif child_help == '2.5':
                msg = '[烟花]【2.5】、星座查询功能帮助\n\n[爱心]命令：【星座查询 白羊】'
            elif child_help == '2.6':
                msg = '[烟花]【2.6】、AI对话功能帮助\n\n[爱心]命令：【@机器人】直接提问即可哦[跳跳]'
            elif child_help == '2.7':
                msg = '[烟花]【2.7】、手机号归属地查询功能帮助\n\n[爱心]命令：【归属查询 110】'
            elif child_help == '2.8':
                msg = '[烟花]【2.8】、WHOIS信息查询功能帮助\n\n[爱心]命令：【whois查询 qq.com】'
            elif child_help == '2.9':
                msg = '[烟花]【2.9】、备案查询功能帮助\n\n[爱心]命令：【icp查询 qq.com】'
            elif child_help == '2.10':
                msg = '[烟花]【2.10】、后缀名查询功能帮助\n\n[爱心]命令：【后缀查询 apk】'
            elif child_help == '2.11':
                msg = '[烟花]【2.11】、MD5解密功能帮助\n\n[爱心]命令：【MD5解密 xxxxx】'
            ws.send(self.Ss.send_msg(msg=msg, wxid=roomid))

    # 判断积分余额
    def judge_point(self, ws, nickname, roomid,  senderid, function_point):
        user_point = self.Dps.query_point(wx_id=senderid, wx_name=nickname)
        if user_point < function_point:
            if not self.judge_admin(wxid=senderid, roomid=roomid):
                if not senderid in self.administrators:
                    ws.send(
                        self.Ss.send_msg(msg=f'\n积分不足，当前可用积分：{user_point}\n功能积分：{function_point}',
                                         wxid=senderid,
                                         roomid=roomid, nickname=nickname))
        return True if user_point >= function_point else False

    # 判断管理员
    def judge_admin(self, wxid, roomid):
        admin_list = self.Dus.show_admin()
        for data in admin_list:
            if wxid == data['wx_id'] and roomid == data['wx_roomid']:
                return True
        else:
            return False

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

