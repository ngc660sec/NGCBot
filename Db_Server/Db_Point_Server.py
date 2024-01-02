from OutPut import OutPut
import sqlite3
import yaml
import os


class Db_Point_Server:
    def __init__(self):
        current_path = os.path.dirname(__file__)
        # 数据库存放地址
        self.db_file = current_path + '/../Config/Point_db.db'
        config = yaml.load(open(current_path + '/../Config/config.yaml', encoding='UTF-8'), yaml.Loader)

        # 读取积分配置
        self.sign_point = config['Point_Config']['Sign']['Point']
        self.Administrator = config['Administrators']

    # 打开数据库
    def open_db(self):
        conn = sqlite3.connect(database=self.db_file, )
        cursor = conn.cursor()
        return conn, cursor

    # 关闭数据库
    def close_db(self, conn, cursor):
        cursor.close()
        conn.close()

    # 初始化积分数据库
    def db_init(self):
        OutPut.outPut('[*]: 积分数据库正在初始化... ...')
        conn, curser = self.open_db()
        create_point_table_sql = '''CREATE TABLE IF NOT EXISTS points 
                                (wx_id varchar(255),
                                wx_name varchar(255),
                                room_id varchar(255),
                                room_name varchar(255),
                                point int(20));'''
        create_sign_table_sql = '''CREATE TABLE IF NOT EXISTS sign (wx_id varchar(255), wx_name varchar(255), room_id varchar(255), room_name varchar(255));'''
        curser.execute(create_point_table_sql)
        curser.execute(create_sign_table_sql)
        conn.commit()
        self.close_db(conn, curser)
        OutPut.outPut('[+]: 积分数据库初始化成功！！！')

    # 添加新用户
    def add_user(self, wx_id, wx_name, room_id, room_name):
        if not self.judge_user(wx_id=wx_id, room_id=room_id):
            conn, curser = self.open_db()
            add_user_sql = '''INSERT INTO points VALUES (?, ?, ?, ?, ?)'''
            curser.execute(add_user_sql, (wx_id, wx_name, room_id, room_name, 0))
            conn.commit()
            self.close_db(conn, curser)

    # 判断用户是否存在
    def judge_user(self, wx_id, room_id):
        conn, curser = self.open_db()
        judge_user_sql = f'''SELECT wx_id FROM points WHERE wx_id = '{wx_id}' and room_id = '{room_id}';'''
        curser.execute(judge_user_sql)
        data = curser.fetchone()
        self.close_db(conn, curser)
        if data:
            return True
        else:
            return False

    # 查询当前用户积分
    def query_point(self, wx_id, wx_name, room_id, room_name):
        if self.judge_user(wx_id=wx_id, room_id=room_id):
            conn, curser = self.open_db()
            query_point_sql = f'''SELECT point FROM points WHERE wx_id = '{wx_id}' and room_id = '{room_id}';'''
            curser.execute(query_point_sql)
            data = curser.fetchone()
            point = data[0]
        else:
            self.add_user(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name)
            point = self.query_point(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name)
        return point

    # 增加积分
    def add_point(self, wx_id, wx_name, room_id, room_name, point):
        if self.judge_user(wx_id=wx_id, room_id=room_id):
            conn, curser = self.open_db()
            add_point_sql = f'''UPDATE points SET point=point+{int(point)} WHERE wx_id = '{wx_id}' AND room_id = '{room_id}';'''
            curser.execute(add_point_sql)
            conn.commit()
            msg = f'基于您的表现，尊贵的管理员给您施舍了 {point}分，请您好好珍惜\n当前可用积分: {self.query_point(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name)}'
        else:
            self.add_user(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name)
            msg = self.add_point(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name, point=point)
        return msg

    # 扣除积分
    def del_point(self, wx_id, wx_name, room_id, room_name, point):
        """

        :rtype: object
        """
        if self.judge_user(wx_id=wx_id, room_id=room_id):
            conn, curser = self.open_db()
            add_point_sql = f'''UPDATE points SET point=point-{int(point)} WHERE wx_id = '{wx_id}' AND room_id = '{room_id}';'''
            curser.execute(add_point_sql)
            conn.commit()
            msg = f'基于您的表现，尊贵的管理员给你小子扣除了 {point}分，请你好好表现\n当前可用积分: {self.query_point(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name)}'
        else:
            self.add_user(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name)
            msg = self.del_point(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name, point=point)
        return msg

    # 判断签到表是否存在此用户
    def judge_sign_user(self, wx_id, room_id):
        conn, curser = self.open_db()
        judge_sign_user_sql = f'''SELECT wx_id FROM sign WHERE wx_id = '{wx_id}' AND room_id = '{room_id}';'''
        curser.execute(judge_sign_user_sql)
        data = curser.fetchone()
        self.close_db(conn, curser)
        if data:
            return True
        else:
            return False

    # 签到功能
    def sign(self, wx_id, wx_name, room_id, room_name):
        if self.judge_user(wx_id=wx_id, room_id=room_id):
            if self.judge_sign_user(wx_id=wx_id, room_id=room_id):
                msg = f'你干嘛~ 哎呦~ 你已经签到过了~'
            else:
                conn, curser = self.open_db()
                sign_sql = f'''INSERT INTO sign VALUES (?, ?, ?, ?);'''
                self.add_point(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name,
                               point=self.sign_point)
                curser.execute(sign_sql, (wx_id, wx_name, room_id, room_name,))
                conn.commit()
                self.close_db(conn, curser)
                msg = f'恭喜你签到成功, 当前可用群聊可用积分: {self.query_point(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name)}'
        else:
            self.add_user(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name)
            msg = self.sign(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name)
        return msg

    # 清除签到表中数据
    def clear_sign(self):
        conn, cursor = self.open_db()
        clear_sign_sql = 'DELETE FROM sign'
        cursor.execute(clear_sign_sql)
        conn.commit()
        self.close_db(conn, cursor)

    # 赠送积分
    def send_point(self, wx_id, wx_name, room_id, room_name, give_sender, give_name, point):
        if self.judge_user(wx_id=wx_id, room_id=room_id):
            if self.judge_user(wx_id=give_sender, room_id=room_id):
                if int(point) > 0:
                    if int(self.query_point(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name)) >= int(point) and wx_id not in self.Administrator:
                        # 积分足够
                        self.add_point(wx_id=give_sender, wx_name=give_name, room_id=room_id, room_name=room_name,
                                       point=int(point))
                        self.del_point(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name, point=int(point))
                        msg = f'赠送积分成功, 您当前剩余积分: {self.query_point(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name)}'
                    elif wx_id in self.Administrator:
                        # 如果是超级管理员
                        self.add_point(wx_id=give_sender, wx_name=give_name, room_id=room_id, room_name=room_name,
                                      point=int(point))
                        msg = f'您是尊贵的超级管理员, 本次赠送不扣除您积分[爱心]'
                    else:
                        # 积分不足
                        msg = '自己的积分都不够还给别人送, 你牙西啊雷 ~~~~~~'
                else:
                    msg = '你小子想卡Bug是吧'
            else:
                self.add_user(wx_id=give_sender, wx_name=wx_name, room_id=room_id, room_name=room_name)
                msg = self.send_point(wx_id, wx_name, room_id, room_name, give_sender, give_name, point)
        else:
            self.add_user(wx_id=wx_id, wx_name=wx_name, room_id=room_id, room_name=room_name)
            msg = self.send_point(wx_id, wx_name, room_id, room_name, give_sender, give_name, point)
        return msg
