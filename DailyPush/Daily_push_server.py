from Db_server.Db_user_server import Db_user_server
from Get_api.Api_news_server import Api_news_server
from Get_api.Api_server import Api_server
from BotServer.SendServer import SendServer
from Output.output import output
import datetime
import yaml
import os


class Daily_push_server:

    def __init__(self, ws):
        # 初始化读取配置文件
        current_path = os.path.dirname(__file__)
        config = yaml.load(open(current_path + '/../config/config.yaml', encoding='UTF-8'), yaml.Loader)
        # 获取系统消息配置
        self.system_message_configuration = config['MESSAGE_CONFIGURATION']
        # 获取下班消息配置
        self.off_work_mes = self.system_message_configuration['OFF_WORK_MESSAGE']

        # 获取Robot-WS服务
        self.ws = ws

        # 实例化发送服务
        self.Ss = SendServer()

        # 实例化新闻获取服务
        self.Ans = Api_news_server()

        # 实例化各类API服务
        self.As = Api_server()

        # 实例化用户操作类
        self.Dus = Db_user_server()

        # 获取特权群聊列表
        self.rooms_id = self.Dus.query_privilege_rooms()

    # 每日早报推送
    def morning_paper_push(self, ):
        output("[*] >> 每日早报推送中... ...")
        msg = self.Ans.get_freebuf_news()
        for room_id in self.rooms_id:
            self.ws.send(self.Ss.send_msg(msg=msg, wxid=room_id))

    # 每日晚间新闻推送
    def evening_paper_push(self, ):
        output("[*] >> 每日晚间安全资讯推送中... ...")
        msg = self.Ans.get_safety_news()
        for room_id in self.rooms_id:
            self.ws.send(self.Ss.send_msg(msg=msg, wxid=room_id))

    # 早安寄语推送
    def every_morning_message_push(self, ):
        output("[*] >> 今日早安寄语推送中... ...")
        msg = self.As.get_good_morning_message()
        for room_id in self.rooms_id:
            self.ws.send(self.Ss.send_msg(msg=msg, wxid=room_id))

    # 摸鱼日历推送
    def every_fish_push(self):
        output("[*] >> 今日摸鱼日历推送中... ...")
        if (
                int(datetime.date.today().isoweekday()) == 6
                or int(datetime.date.today().isoweekday()) == 7
        ):
            pass
        else:
            msg = self.As.get_touch_fish_calendar()
            for room_id in self.rooms_id:
                self.Ss.send_img_room(msg=msg, roomid=room_id)

    # 下班推送通知
    def everyday_after_work_push(self, ):
        output("[*] >> 下班通知推送中... ...")
        if (
                int(datetime.date.today().isoweekday()) == 6
                or int(datetime.date.today().isoweekday()) == 7
        ):
            msg = ""
        else:
            msg = ''
            split_list = self.off_work_mes.splt('\n')
            for s in split_list:
                msg += s + '\n'
            msg = msg.strip()
            print(msg)
        split_list = str(self.off_work_mes).split('\\n')
        for s in split_list:
            msg += s + '\n'
        msg = msg.strip()
        for room_id in self.rooms_id:
            self.ws.send(self.Ss.send_msg(msg=msg, wxid=room_id))

    def get_privilege_rooms(self):
        self.rooms_id = self.Dus.query_privilege_rooms()

