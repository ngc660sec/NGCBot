from Api_Server.Api_Server_Main import Api_Server_Main
from Db_Server.Db_Point_Server import Db_Point_Server
from Db_Server.Db_User_Server import Db_User_Server
from BotServer.SendServer import SendServer
from Output.output import output
from chinese_calendar import is_workday
import datetime
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

        self.morning_page_time = config['Timed_Push']['Morning_Page_Time']
        self.evening_page_time = config['Timed_Push']['Evening_Page_Time']
        self.off_work_time = config['Timed_Push']['Off_Work_Time']
        self.fish_time = config['Timed_Push']['Fish_Time']

    # 早报推送
    def push_morning_page(self, ):
        if is_workday(datetime.date.today()):
            output('[+]:定时早报推送')
            roomid_list, room_name_list = self.Dus.show_white_room()
            msg = self.Asm.get_freebuf_news()
            for roomid in roomid_list:
                self.ws.send(self.Ss.send_msg(msg=msg, wxid=roomid))

    # 晚报推送
    def push_evening_page(self, ):
        if is_workday(datetime.date.today()):
            output('[+]:定时晚间新闻推送')
            roomid_list, room_name_list = self.Dus.show_white_room()
            msg = self.Asm.get_safety_news()
            for roomid in roomid_list:
                self.ws.send(self.Ss.send_msg(msg=msg, wxid=roomid))

    # 摸鱼日历推送
    def push_fish(self, ):
        if is_workday(datetime.date.today()):
            output('[+]:定时摸鱼日记推送')
            roomid_list, room_name_list = self.Dus.show_white_room()
            msg = self.Asm.get_fish()
            for roomid in roomid_list:
                self.Ss.send_img_room(msg=msg, roomid=roomid)

    # 下班信息推送
    def off_work_msg_push(self, ):
        if is_workday(datetime.date.today()):
            output('[+]:下班消息推送')
            roomid_list, room_name_list = self.Dus.show_white_room()
            msg = '各部门请注意，下班时间已到！！！请使用你最快的速度火速离开，\n不要浪费电费，记得打卡发日报！\n[旺财]over'
            for roomid in roomid_list:
                self.Ss.send_img_room(msg=msg, roomid=roomid)

    # 签到表清空
    def push_clear_sign(self):
        output('[+]:定时签到表清空')
        self.Dps.clear_sign()

    def run(self):
        schedule.every().day.at(self.morning_page_time).do(self.push_morning_page)
        schedule.every().day.at(self.evening_page_time).do(self.push_evening_page)
        schedule.every().day.at(self.off_work_time).do(self.off_work_msg_push)
        schedule.every().day.at(self.fish_time).do(self.push_fish)
        schedule.every().day.at('00:00').do(self.push_clear_sign)
        # schedule.every(1).seconds.do(self.push_morning_page)
        output('[*]:已开启定时推送服务!')
        while True:
            # output('[*]:已开启定时推送服务!')
            schedule.run_pending()


if __name__ == '__main__':
    Psm = Push_Main_Server('1')
    # Psm.push_fish()
    Psm.push_morning_page()
