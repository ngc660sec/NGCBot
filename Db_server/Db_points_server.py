from Output.output import output
import sqlite3
import yaml
import os


class Db_points_server:

    def __init__(self):
        # 定义积分数据库
        config_path = 'config/points.db'

        # 建立数据库连接
        self.conn = sqlite3.connect(config_path)

        # 创建数据库指针
        self.cur = self.conn.cursor()

        # 读取配置文件
        current_path = os.path.dirname(__file__)
        config = yaml.load(open(current_path + '/../config/config.yaml', encoding='UTF-8'), yaml.Loader)
        self.sign_point = 10

    def init_database(self):
        # 创建积分表
        create_points_table_sql = '''CREATE TABLE IF NOT EXISTS points 
        (wx_id varchar(255),
        wx_name varchar(255),
        integral int(255));'''
        # 创建签到表
        create_sign_table_sql = '''CREATE TABLE IF NOT EXISTS sign 
        (wx_id varchar(255),
        wx_name varchar(255));'''

        self.cur.execute(create_points_table_sql)
        self.cur.execute(create_sign_table_sql)

        self.conn.commit()
        msg = '[*] >> 积分数据表初始化成功!'
        output(msg)

    # 判断表是否存在
    def judge_table(self, table_name):
        judge_table_sql = f''' SELECT tbl_name FROM sqlite_master WHERE type = 'table';'''
        cursor = self.cur.execute(judge_table_sql)
        query_data = cursor.fetchall()
        if query_data:
            for data in query_data:
                if table_name in data:
                    return True
        else:
            return False

    # 判断数据是否存在
    def judge_data(self, wx_id, sign_bool=False):
        if sign_bool:
            judge_data_sql = f'''SELECT wx_id FROM sign WHERE wx_id = '{wx_id}';'''
        else:
            judge_data_sql = f'''SELECT wx_id FROM points WHERE wx_id = '{wx_id}';'''
        cursor = self.cur.execute(judge_data_sql)
        query_data = cursor.fetchall()
        for data in query_data:
            if data:
                # 存在数据返回True
                return True
            else:
                return False

    # 主判断函数
    def main_judge(self, wx_id, wx_name, integral=0, add_bool=False, del_bool=False, sign_bool=False, query_bool=False):
        msg = ''
        table_bool = (self.judge_table(table_name='points') and self.judge_table(table_name='sign')) if wx_id else False
        if not table_bool:
            msg = '[+] >> 检测到积分数据表未创建，正在初始化... ...'
            output(msg)
            self.init_database()
        # 判断是否为签到操作
        if sign_bool and wx_id:
            # 判断积分表中是否存在该用户
            if not self.judge_data(wx_id=wx_id):
                # 不存在该用户就初始化该用户
                self.insert_points(wx_id=wx_id, wx_name=wx_name)
            # 判断签到数据表是否存在该用户
            if not self.judge_data(wx_id=wx_id, sign_bool=sign_bool):
                # 不存在该用户就执行签到
                msg = self.sign_points(wx_id=wx_id, wx_name=wx_name, sign_integral=self.sign_point)
                return msg
            else:
                return ''
        # 其余积分操作
        else:
            # 判断积分表中是否存在该用户
            if not self.judge_data(wx_id=wx_id):
                # 不存在该用户就初始化该用户
                self.insert_points(wx_id=wx_id, wx_name=wx_name)
            # 增加积分操作
            if add_bool:
                msg = self.add_points(wx_id=wx_id, integral=integral)
            # 扣除积分操作
            if del_bool:
                msg = self.del_points(wx_id=wx_id, integral=integral)
            # 查询积分操作
            if query_bool:
                msg = self.query_points(wx_id=wx_id)
            return msg

    # 插入数据
    def insert_points(self, wx_id, wx_name):
        insert_points_sql = f'''INSERT INTO points VALUES ('{wx_id}', '{wx_name}', 0);'''
        self.cur.execute(insert_points_sql)
        self.conn.commit()
        msg = '[*] >> 插入数据成功'
        output(msg)

    # 签到积分函数
    def sign_points(self, wx_id, wx_name, sign_integral):
        now_integral = 0 if not self.query_points(wx_id=wx_id) else self.query_points(wx_id=wx_id)
        add_integral = now_integral + sign_integral
        add_points_sql = f'''UPDATE points SET integral = {add_integral} WHERE wx_id = '{wx_id}';'''
        sign_points_sql = f'''INSERT INTO sign VALUES ('{wx_id}', '{wx_name}');'''
        self.cur.execute(add_points_sql)
        self.cur.execute(sign_points_sql)
        self.conn.commit()
        msg = f'签到成功 +{sign_integral}分\n当前可用积分：{self.query_points(wx_id=wx_id)}分'
        return msg

    # 查询积分
    def query_points(self, wx_id):
        query_points_sql = f'''SELECT integral FROM points WHERE wx_id='{wx_id}';'''
        cursor = self.cur.execute(query_points_sql)
        query_data = cursor.fetchall()
        for data in list(query_data):
            if data[0]:
                return data[0]

    # 增加积分
    def add_points(self, wx_id, integral):
        now_integral = 0 if not self.query_points(wx_id=wx_id) else self.query_points(wx_id=wx_id)
        add_integral = integral + now_integral
        add_points_sql = f'''UPDATE points SET integral = {add_integral} WHERE wx_id = '{wx_id}';'''
        self.cur.execute(add_points_sql)
        self.conn.commit()
        msg = f'\n基于你的优越表现，+{integral}分\n当前未使用积分：{self.query_points(wx_id=wx_id)}分'
        return msg

    # 扣除积分
    def del_points(self, wx_id, integral, use_bool=False):
        now_integral = self.query_points(wx_id=wx_id)
        del_integral = 0 if integral > now_integral else now_integral - integral
        del_points_sql = f'''UPDATE points SET integral = {del_integral} WHERE wx_id = '{wx_id}';'''
        self.cur.execute(del_points_sql)
        self.conn.commit()
        msg = f'\n介于你的近期表现，-{integral}分\n当前未使用积分：{self.query_points(wx_id=wx_id)}分'
        if use_bool:
            msg = f'\n可用积分 -{integral}，\t当前未使用积分：{self.query_points(wx_id=wx_id)}分'
        return msg

    # 清空签到数据表内容
    def clear_sign(self):
        clear_sign_sql = '''DELETE FROM sign;'''
        self.cur.execute(clear_sign_sql)
        self.conn.commit()
        msg = '[*] >> 签到数据表已清空'
        output(msg)


if __name__ == '__main__':
    Dps = Db_points_server()
    Dps.init_database()
    # Dps.add_points()
    # Dps.reduce_points()
    # point = Dps.query_points()
    # print(point)
    # Dps.add_points(30)
    # Dps.del_points(10)
    Dps.sign_points(wx_id='wx_123')
