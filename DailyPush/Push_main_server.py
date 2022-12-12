from DailyPush.Daily_push_server import Daily_push_server
from Db_server.Db_points_server import Db_points_server
from Output.output import output
import schedule
import yaml
import os


class Push_main_server:

    def __init__(self, ws):
        # 实例化推送服务
        self.Dps = Daily_push_server(ws=ws, )
        # 实例化积分数据库服务
        self.Dis = Db_points_server()

        # 读取配置文件信息
        current_path = os.path.dirname(__file__)
        config = yaml.load(open(current_path + '/../config/config.yaml', encoding='UTF-8'), yaml.Loader)
        self.time_morning = config['TIME_MORNING']
        self.time_evening = config['TIME_EVENING']
        self.time_fish = config['TIME_FISH']
        self.time_after = config['TIME_AFTER']

    def auto_push(self):
        output("AUTO PUSH ....")
        schedule.every().day.at(self.time_evening).do(self.Dps.evening_paper_push)
        schedule.every().day.at(self.time_morning).do(self.Dps.morning_paper_push)
        schedule.every().day.at(self.time_morning).do(self.Dps.every_morning_message_push)
        schedule.every().day.at(self.time_fish).do(self.Dps.every_fish_push)
        schedule.every().day.at(self.time_after).do(self.Dps.everyday_after_work_push)
        schedule.every().day.at('00:00').do(self.Dis.clear_sign)
        schedule.every(30).minutes.do(self.Dps.get_privilege_rooms)
        # schedule.every(10).seconds.do(self.Dps.evening_paper_push)
        while True:
            # output('[*] >> 定时任务监控中...')
            schedule.run_pending()
