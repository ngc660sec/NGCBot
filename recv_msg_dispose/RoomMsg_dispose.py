from Db_server.Db_points_server import Db_points_server
from Get_api.Api_news_server import Api_news_server
from Db_server.Db_user_server import Db_user_server
from BotServer.SendServer import SendServer
from Get_api.Api_server import Api_server
import yaml
import os
import re


class RoomMsg_disposes:
    def __init__(self, ):
        # 初始化核心参数
        self.room_name = None
        self.at_nickname = None
        self.at_wxid = None
        self.roomid = 'null'
        self.senderid = 'null'
        self.nickname = 'null'
        self.msgJson = ''
        self.keyword = ''

        # 实例化消息服务
        self.Ss = SendServer()

        # 实例化接口获取服务
        self.As = Api_server()

        # 实例化新闻接口
        self.Ans = Api_news_server()

        # 实例化特权管理类
        self.Dus = Db_user_server()

        # 实例化积分管理类
        self.Dps = Db_points_server()

        # 获取机器人名字，微信ID
        self.Bot_name, self.Bot_wxid = self.Ss.get_personal_info()

        # 读取配置文件
        current_path = os.path.dirname(__file__)
        config = yaml.load(open(current_path + '/../config/config.yaml', encoding='UTF-8'), yaml.Loader)
        # 获取超级管理员列表
        self.Administrators = config['ADMINISTRATOR']

        # 初始化普通管理员列表
        self.admins = list()

        # 初始化特权群聊列表
        self.privilege_rooms = self.Dus.query_privilege_rooms()

        # 初始化黑名单群聊列表
        self.black_rooms = self.Dus.query_black_rooms()

        # 获取关键词
        self.Key_Response = config['KEY_RESPONSE']
        # 获取美女图片触发关键词列表
        self.girl_pic_keys = self.Key_Response['GIRL_PIC']
        # 获取美女视频触发关键词列表
        self.girl_video_keys = self.Key_Response['GIRL_VIDEO']
        # 获取舔狗日记触发关键词列表
        self.lick_dog_keys = self.Key_Response['LICK_DOG']
        # 获取摸鱼日记关键词回复列表
        self.touch_fish_keys = self.Key_Response['TOUCH_FISH']
        # 获取早安寄语关键词回复列表
        self.morning_message_keys = self.Key_Response['MORNING_MESSAGE']
        # 获取星座查询关键词回复字典
        self.horoscope_dicts = self.Key_Response['HOROSCOPE']
        # 获取天气查询关键词回复字典
        self.wether_dicts = self.Key_Response['WETHER']
        # 获取归属查询关键词回复字典
        self.ascription_dicts = self.Key_Response['ASCRIPTION']
        # 获取WHOIS查询关键词回复字典
        self.whois_dicts = self.Key_Response['WHOIS']
        # 获取备案查询关键词回复字典
        self.icp_dicts = self.Key_Response['ICP']
        # 获取后缀查询关键词回复字典
        self.suffix_dicts = self.Key_Response['SUFFIX']
        # 获取微步查询关键词回复字典
        self.threatbook_dicts = self.Key_Response['THREAT_BOOK']
        # 获取早报关键词回复列表
        self.morning_paper_keys = self.Key_Response['MORNING_PAPER']
        # 获取晚报关键词回复列表
        self.evening_paper_keys = self.Key_Response['EVENING_PAGE']
        # 获取帮助菜单关键词回复列表
        self.help_keys = self.Key_Response['HELP']

        # 获取管理关键词
        self.admin_key_response = config['ADMIN_KEY_RESPONSE']
        # 获取添加管理关键词列表
        self.add_admin_keys = self.admin_key_response['ADD_ADMIN']
        # 获取删除管理关键词列表
        self.del_admin_keys = self.admin_key_response['DEL_ADMIN']
        # 获取拉黑群聊关键词列表
        self.add_black_group_keys = self.admin_key_response['ADD_BLACK_GROUP']
        # 获取解除拉黑群聊关键词
        self.del_black_group_keys = self.admin_key_response['DEL_BLACK_GROUP']
        # 获取新增特权群聊关键词
        self.add_privilege_group_keys = self.admin_key_response['ADD_PRIVILEGE_GROUP']
        # 获取删除特权群聊关键词
        self.del_privilege_group_keys = self.admin_key_response['DEL_PRIVILEGE_GROUP']

        # 获取自定义关键词
        self.custom_keyword_reply = config['CUSTOM_KEYWORD_REPLY']
        # 获取自定义问题列表
        self.custom_problem_list = list(self.custom_keyword_reply.keys())

        # 获取系统消息配置
        self.system_messages = config['MESSAGE_CONFIGURATION']
        # 获取帮助菜单信息
        self.help_messages = self.system_messages['FUNCTION_MENUS']

        # 获取积分管理关键词
        self.integral_key_response = config['INTEGRAL_CONFIG']
        # 增加积分关键词配置
        self.add_integral_keys = self.integral_key_response['ADD_INTEGRAL']
        # 扣除积分关键词配置
        self.del_integral_keys = self.integral_key_response['DEL_INTEGRAL']
        # 获取签到口令
        self.sign_key = self.integral_key_response['SIGN_KEY']
        # 获取积分查询关键词配置
        self.query_integral_keys = self.integral_key_response['QUERY_INTEGRAL']
        # 归属地积分查询配置
        self.attribution_integral = self.integral_key_response['ATTRIBUTION_POINT']
        # WHOIS积分查询配置
        self.whois_integral = self.integral_key_response['WHOIS_POINT']
        # 备案查询积分配置
        self.icp_integral = self.integral_key_response['ICP_POINT']
        # 后缀名查询积分配置
        self.extensions_integral = self.integral_key_response['EXTENSIONS_POINT']
        # 微步情报查询积分配置
        self.threatbook_integral = self.integral_key_response['THREATBOOK_POINT']

    # 获取接收信息
    def get_information(self, msgJson, roomid, senderid, nickname, ws):
        self.msgJson = msgJson
        # 获取群聊ID
        self.roomid = roomid
        # 获取发送者微信ID
        self.senderid = senderid
        # 获取发送者名字
        self.nickname = nickname
        # 获取接收到的内容，进行处理
        self.keyword = msgJson['content'].replace('\u2005', '')
        # 获取被@人的微信ID
        try:
            self.at_wxid = re.findall("<!\[CDATA\[,(.*?)]]", str(self.msgJson['id3']))[0] if 'CDATA' in str(
                msgJson) else None
        except:
            self.at_wxid = re.findall("><!\[CDATA\[(.*?)]]>", str(self.msgJson['id3']))[0] if 'CDATA' in str(
                msgJson) else None
        # 获取被@人的昵称
        self.at_nickname = self.Ss.get_member_nick(roomid=self.roomid, wxid=self.at_wxid) if self.at_wxid else None
        # 获取微信群聊名字
        self.room_name = self.Ss.get_member_nick(wxid=self.roomid, roomid=self.roomid)
        # 获取普通管理员列表
        self.admins = self.Dus.query_admins(wx_roomid=self.roomid)
        # 获取特权群聊列表
        self.privilege_rooms = self.Dus.query_privilege_rooms()
        # 获取黑名单群聊劫镖
        self.black_rooms = self.Dus.query_black_rooms()
        # 处理接收消息
        self.process_information(ws)

    # 处理接收到的信息
    def process_information(self, ws):
        # 测试专用
        # if 'OK' == self.keyword:
        #    msg = 'OOOk'
        #    ws.send(self.Ss.send_msg(msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # if 'ok' == self.keyword:
        #    msg = 'OOK'
        #    ws.send(self.Ss.send_msg(msg, wxid=self.roomid))
        # print(self.at_wxid, self.at_nickname, self.room_name)
        # 超级管理员功能
        if self.senderid in self.Administrators:
            self.supertube_function(ws, )
            self.administrator_function(ws, )
            self.entertainment_function(ws, )
            self.integral_function(ws, )
            self.custom_keyword_function(ws, )
        # 管理员功能
        elif self.senderid in self.admins:
            self.administrator_function(ws, )
            self.entertainment_function(ws, )
            self.integral_function(ws, )
            self.custom_keyword_function(ws, )
        # 黑名单群聊功能
        elif self.roomid in self.black_rooms:
            self.judge_integral(ws, )
            self.custom_keyword_function(ws, )
        # 普通用户功能
        else:
            self.entertainment_function(ws, )
            self.judge_integral(ws, )
            self.custom_keyword_function(ws, )

    # 超管功能
    def supertube_function(self, ws):
        # 添加管理员
        if self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.add_admin_keys,
                                  in_bool=True) and self.at_nickname:
            msg = self.Dus.main_judge(wx_id=self.at_wxid, wx_name=self.at_nickname, wx_roomid=self.roomid,
                                      wx_room_name=self.room_name, add_admin_bool=True)
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # 删除管理员
        if self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.del_admin_keys,
                                  in_bool=True) and self.at_nickname:
            msg = self.Dus.main_judge(wx_id=self.at_wxid, wx_name=self.at_nickname, wx_roomid=self.roomid,
                                      delete_bool=True)
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))

    # 娱乐功能
    def entertainment_function(self, ws):
        # 美女图片
        if self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.girl_pic_keys):
            msg = self.As.get_girl_pic()
            self.Ss.send_img_room(msg=msg, roomid=self.roomid)
        # 美女视频
        if self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.girl_video_keys):
            msg = self.As.get_girl_vedio()
            self.Ss.send_file_room(file=msg, roomid=self.roomid)
        # 舔狗日记
        if self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.lick_dog_keys):
            msg = self.As.get_licking_dog_Diary()
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # 摸鱼日历
        if self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.touch_fish_keys):
            msg = self.As.get_touch_fish_calendar()
            self.Ss.send_img_room(msg=msg, roomid=self.roomid)
        # 早安寄语
        if self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.morning_message_keys):
            msg = self.As.get_good_morning_message()
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # 星座运势
        if self.Ss.judge_key_word(receive_keyword=self.keyword, key1=self.horoscope_dicts['KEY1'],
                                  key2=self.horoscope_dicts['KEY2'], and_bool=True, in_bool=True):
            msg = self.As.get_horoscope(self.keyword)
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # 天气查询
        if self.Ss.judge_key_word(receive_keyword=self.keyword, key1=self.wether_dicts['KEY1'],
                                  key2=self.wether_dicts['KEY2'], and_bool=True, in_bool=True):
            msg = self.As.get_wether(keyword=self.keyword)
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # AI对话
        if self.Ss.judge_key_word(receive_keyword=self.msgJson['content'], keyword=f"@{self.Bot_name}\u2005",
                                  ai_bool=True, in_bool=True):
            keyword = self.keyword.replace(f'@{self.Bot_name}', '').strip()
            msg = self.As.get_xiaoai_msg(keyword=keyword) if keyword else False
            if msg:
                ws.send(self.Ss.send_msg(msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # 帮助菜单
        elif self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.help_keys, and_bool=True):
            messages = self.help_messages.split('\\n')
            msg = ''
            for s in messages:
                msg += s + '\n'
            ws.send(self.Ss.send_msg(msg=msg.strip(), wxid=self.roomid))

    # 管理员功能
    def administrator_function(self, ws):
        # 拉黑群聊
        if self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.add_black_group_keys, and_bool=True):
            msg = self.Dus.main_judge(wx_roomid=self.roomid, wx_room_name=self.room_name, black_bool=True)
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # 解除拉黑
        elif self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.del_black_group_keys, and_bool=True):
            msg = self.Dus.main_judge(wx_roomid=self.roomid, black_bool=True, delete_bool=True)
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # 添加特权群聊
        elif self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.add_privilege_group_keys, and_bool=True):
            msg = self.Dus.main_judge(wx_roomid=self.roomid, wx_room_name=self.room_name)
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # 解除特权群聊
        elif self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.del_privilege_group_keys, and_bool=True):
            msg = self.Dus.main_judge(wx_roomid=self.roomid, delete_bool=True)
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # 添加积分
        elif self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.add_integral_keys, in_bool=True):
            try:
                integral = int(re.findall(f'\d+', self.keyword.replace(self.at_nickname, ''))[0])
                # 优化多人增加积分
                for wxid in self.at_wxid.split(','):
                    nickname = self.Ss.get_member_nick(wxid=wxid, roomid=self.roomid)
                    msg = self.Dps.main_judge(integral=integral, wx_id=wxid, wx_name=nickname, add_bool=True)
                    ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=wxid, nickname=nickname))
            except IndexError as e:
                pass

        # 扣除积分
        elif self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.del_integral_keys, in_bool=True):
            try:
                integral = int(re.findall(f'\d+', self.keyword.replace(self.at_nickname, ''))[0])
                for wxid in self.at_wxid.split(','):
                    nickname = self.Ss.get_member_nick(wxid=wxid, roomid=self.roomid)
                    msg = self.Dps.main_judge(integral=integral, wx_id=wxid, wx_name=nickname,
                                              del_bool=True)
                    ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=wxid, nickname=nickname))
            except IndexError as e:
                pass
        # 获取早报功能
        elif self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.morning_paper_keys, and_bool=True):
            msg = self.Ans.get_freebuf_news()
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.roomid))
        # 获取晚间新闻
        elif self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.evening_paper_keys, and_bool=True):
            msg = self.Ans.get_safety_news()
            ws.send(self.Ss.send_msg(msg=msg, wxid=self.roomid))

    # 积分功能
    def integral_function(self, ws):
        # 手机号归属查询
        if self.Ss.judge_key_word(receive_keyword=self.keyword, key1=self.ascription_dicts['KEY1'],
                                  key2=self.ascription_dicts['KEY2'], and_bool=True, in_bool=True):
            msg = self.As.get_attribution(keyword=self.keyword)
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # whois查询
        if self.Ss.judge_key_word(receive_keyword=self.keyword, key1=self.whois_dicts['KEY1'],
                                  key2=self.whois_dicts['KEY2'], and_bool=True, in_bool=True):
            msg = self.As.get_whois(self.keyword)
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # 备案查询
        if self.Ss.judge_key_word(receive_keyword=self.keyword, key1=self.icp_dicts['KEY1'],
                                  key2=self.icp_dicts['KEY2'], and_bool=True, in_bool=True):
            msg = self.As.get_icp(keyword=self.keyword)
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # 后缀名查询
        if self.Ss.judge_key_word(receive_keyword=self.keyword, key1=self.suffix_dicts['KEY1'],
                                  key2=self.suffix_dicts['KEY2'], and_bool=True, in_bool=True):
            msg = self.As.get_extensions(keyword=self.keyword)
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # 微步情报查询
        if self.Ss.judge_key_word(receive_keyword=self.keyword, key1=self.threatbook_dicts['KEY1'],
                                  key2=self.threatbook_dicts['KEY2'], and_bool=True, in_bool=True):
            msg = self.As.get_threatbook_ip(self.keyword)
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # 签到功能
        if self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.sign_key, and_bool=True):
            msg = self.Dps.main_judge(wx_id=self.senderid, wx_name=self.nickname, sign_bool=True)
            if msg != '':
                ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        elif self.keyword == '签到':
            msg = f'签到口令已改为：{self.sign_key[0]}'
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
        # 积分查询功能
        if self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.query_integral_keys, and_bool=True):
            msg = f'\n本群未使用积分：{self.Dps.query_points(wx_id=self.senderid)}分'
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))

    # 用户自定义关键词回复
    def custom_keyword_function(self, ws):
        for problem in self.custom_problem_list:
            if problem == self.keyword.strip():
                msg = self.custom_keyword_reply[f'{problem}']
                ws.send(self.Ss.send_msg(msg=msg, wxid=self.senderid, roomid=self.roomid, nickname=self.nickname))

    # 是否能够调用积分功能
    def judge_integral(self, ws, ):
        msg = ''
        user_integral = self.Dps.query_points(wx_id=self.senderid)
        # 手机号归属查询
        if self.Ss.judge_key_word(receive_keyword=self.keyword, key1=self.ascription_dicts['KEY1'],
                                  key2=self.ascription_dicts['KEY2'], and_bool=True, in_bool=True):
            if user_integral > self.attribution_integral or user_integral == self.attribution_integral:
                msg = self.Dps.del_points(wx_id=self.senderid, integral=self.attribution_integral, use_bool=True)
                self.integral_function(ws, )
            else:
                msg = f'您的积分余额不足，需要积分:{self.attribution_integral}'
                return msg
        # whois查询
        elif self.Ss.judge_key_word(receive_keyword=self.keyword, key1=self.whois_dicts['KEY1'],
                                    key2=self.whois_dicts['KEY2'], and_bool=True, in_bool=True):
            if user_integral > self.whois_integral or user_integral == self.whois_integral:
                msg = self.Dps.del_points(wx_id=self.senderid, integral=self.whois_integral, use_bool=True)
                self.integral_function(ws, )
            else:
                msg = f'您的积分余额不足，需要积分:{self.whois_integral}'
                return msg
        # 备案查询
        elif self.Ss.judge_key_word(receive_keyword=self.keyword, key1=self.icp_dicts['KEY1'],
                                    key2=self.icp_dicts['KEY2'], and_bool=True, in_bool=True):
            if user_integral > self.icp_integral or user_integral == self.icp_integral:
                msg = self.Dps.del_points(wx_id=self.senderid, integral=self.icp_integral, use_bool=True)
                self.integral_function(ws, )
            else:
                msg = f'您的积分余额不足，需要积分:{self.icp_integral}'
                return msg
        # 后缀名查询
        elif self.Ss.judge_key_word(receive_keyword=self.keyword, key1=self.suffix_dicts['KEY1'],
                                    key2=self.suffix_dicts['KEY2'], and_bool=True, in_bool=True):
            if user_integral > self.extensions_integral or user_integral == self.extensions_integral:
                msg = self.Dps.del_points(wx_id=self.senderid, integral=self.extensions_integral, use_bool=True)
                self.integral_function(ws, )
            else:
                msg = f'您的积分余额不足，需要积分:{self.extensions_integral}'
                return msg
        # 微步情报查询
        elif self.Ss.judge_key_word(receive_keyword=self.keyword, key1=self.threatbook_dicts['KEY1'],
                                    key2=self.threatbook_dicts['KEY2'], and_bool=True, in_bool=True):
            if user_integral > self.threatbook_integral or user_integral == self.threatbook_integral:
                msg = self.Dps.del_points(wx_id=self.senderid, integral=self.threatbook_integral, use_bool=True)
                self.integral_function(ws, )
            else:
                msg = f'您的积分余额不足，需要积分:{self.threatbook_integral}'
                return msg
        # 签到功能
        elif self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.sign_key, and_bool=True):
            self.integral_function(ws, )
        # 积分查询功能
        elif self.Ss.judge_key_word(receive_keyword=self.keyword, keyword=self.query_integral_keys, and_bool=True):
            self.integral_function(ws, )
        # 签到功能
        elif self.keyword == '签到':
            self.integral_function(ws, )
        # 帮助菜单功能
        if msg:
            ws.send(self.Ss.send_msg(msg=msg, roomid=self.roomid, wxid=self.senderid, nickname=self.nickname))
