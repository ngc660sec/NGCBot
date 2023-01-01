from Monitor_Server.Monitor_Server_Main import Monitor_Server_Main
from Api_Server.Api_Server_Main import Api_Server_Main
from Db_Server.Db_Point_Server import Db_Point_Server
from Db_Server.Db_User_Server import Db_User_Server
from BotServer.SendServer import SendServer
from Output.output import output
import schedule
import yaml
import os


class Push_Main_Server:
    def __init__(self, ws):
        current_path = os.path.dirname(__file__)
        config = yaml.load(open(current_path + '/../Config/config.yaml', encoding='UTF-8'), yaml.Loader)
        self.db_file = current_path + '/../Config/Point_db.db'

        # 实例化用户类
        self.Dus = Db_User_Server()

        # 实例化积分类
        self.Dps = Db_Point_Server()

        # 实例化发送消息服务
        self.Ss = SendServer()

        # 实例化API类
        self.Asm = Api_Server_Main()

        # 实例化ws
        self.ws = ws

        self.MSm = Monitor_Server_Main(ws=self.ws)
        self.morning_page_time = config['Timed_Push']['Morning_Page_Time']
        self.evening_page_time = config['Timed_Push']['Evening_Page_Time']
        self.fish_time = config['Timed_Push']['Fish_Time']

    # 早报推送
    def push_morning_page(self, ):
        output('[+]:定时早报推送')
        roomid_list = self.Dus.show_white_room()
        msg = self.Asm.get_freebuf_news()
        for roomid in roomid_list:
            self.ws.send(self.Ss.send_msg(msg=msg, wxid=roomid))

    # 晚报推送
    def push_evening_page(self, ):
        output('[+]:定时晚间新闻推送')
        roomid_list = self.Dus.show_white_room()
        msg = self.Asm.get_safety_news()
        for roomid in roomid_list:
            self.ws.send(self.Ss.send_msg(msg=msg, wxid=roomid))

    # 摸鱼日记推送
    def push_fish(self, ):
        output('[+]:定时摸鱼日记推送')
        roomid_list = self.Dus.show_white_room()
        msg = self.Asm.get_fish()
        for roomid in roomid_list:
            self.Ss.send_msg(msg=msg, wxid=roomid)

    def push_clear_sign(self):
        output('[+]:定时签到表清空')
        self.Dps.clear_sign()

    def run(self):
        schedule.every().day.at(self.morning_page_time).do(self.push_morning_page)
        schedule.every().day.at(self.evening_page_time).do(self.push_evening_page)
        schedule.every().day.at(self.fish_time).do(self.push_fish)
        schedule.every().day.at('00:00').do(self.push_clear_sign)
        # schedule.every(1).seconds.do(self.MSm.main)
        schedule.every(30).minutes.do(self.MSm.main)
        output('[*]:已开启定时推送服务!')
        while True:
            # output('[*]:已开启定时推送服务!')
            schedule.run_pending()
