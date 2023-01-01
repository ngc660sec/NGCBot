from Output.output import output
import sqlite3
import yaml
import os


class Db_Point_Server:
    def __init__(self):
        current_path = os.path.dirname(__file__)
        # 数据库存放地址
        self.db_file = current_path + '/../Config/Point_db.db'
        self.judge_init()
        config = yaml.load(open(current_path + '/../Config/config.yaml', encoding='UTF-8'), yaml.Loader)

        # 读取积分配置
        self.sign_point = config['Point_Function']['Sign_Point']

    # 打开数据库
    def open_db(self):
        conn = sqlite3.connect(database=self.db_file, )
        cursor = conn.cursor()
        return conn, cursor

    # 关闭数据库
    def close_db(self, conn, cursor):
        cursor.close()
        conn.close()

    # 判断数据库是否初始化
    def judge_init(self, ):
        conn, cursor = self.open_db()
        judge_table_sql = '''SELECT name FROM sqlite_master;'''
        cursor.execute(judge_table_sql)
        data = cursor.fetchall()
        if not data:
            msg = '[+]:检测到积分数据库未初始化，正在初始化数据库'
            self.init_db()
            output(msg)
        self.close_db(conn, cursor)


    # 初始化数据库
    def init_db(self):
        conn, cursor = self.open_db()
        create_point_table_sql = '''CREATE TABLE IF NOT EXISTS points 
                        (wx_id varchar(255),
                        wx_name varchar(255),
                        point int(20));'''
        create_sign_table_sql = '''CREATE TABLE IF NOT EXISTS sign (wx_id varchar(255), wx_name varchar(255));'''
        cursor.execute(create_point_table_sql)
        cursor.execute(create_sign_table_sql)
        self.close_db(conn, cursor)
        output('[*]:积分服务初始化成功!')

    # 初始化新用户
    def init_user(self, wx_id, wx_name):
        conn, cursor = self.open_db()
        add_user_sql = f'''INSERT INTO points VALUES ('{wx_id}', '{wx_name}', 0);'''
        cursor.execute(add_user_sql)
        conn.commit()
        self.close_db(conn, cursor)

    # 判断用户是否存在
    def judge_user(self, wx_id, sign_bool=False):
        conn, cursor = self.open_db()
        judge_user_sql = f'''SELECT wx_id FROM points WHERE wx_id='{wx_id}';'''
        if sign_bool:
            judge_user_sql = f'''SELECT wx_id FROM sign WHERE wx_id='{wx_id}';'''
        cursor.execute(judge_user_sql)
        data = cursor.fetchall()
        if data:
            return True
        else:
            return False

    # 增加积分
    def add_point(self, wx_id, point):
        conn, cursor = self.open_db()
        add_point_sql = f'''UPDATE points SET point=point+{point} WHERE wx_id='{wx_id}';'''
        cursor.execute(add_point_sql)
        conn.commit()
        self.close_db(conn, cursor)
        msg = f'\n基于你的优越表现，+{point}分\n当前未使用积分：{self.query_point(wx_id=wx_id, )}分'
        return msg

    # 扣除积分
    def del_point(self, wx_id, point):
        conn, cursor = self.open_db()
        add_point_sql = f'''UPDATE points SET point=point-{point} WHERE wx_id='{wx_id}';'''
        cursor.execute(add_point_sql)
        conn.commit()
        self.close_db(conn, cursor)
        msg = f'\n介于你的近期表现，-{point}分\n当前未使用积分：{self.query_point(wx_id=wx_id, )}分'
        return msg

    # 查询积分
    def query_point(self, wx_id):
        conn, cursor = self.open_db()
        query_point_sql = f'''SELECT point FROM points WHERE wx_id='{wx_id}';'''
        cursor.execute(query_point_sql)
        data = cursor.fetchone()[0]
        return data

    # 签到功能
    def sign(self, wx_id, wx_name):
        conn, cursor = self.open_db()
        sign_sql = f'''INSERT INTO sign VALUES ('{wx_id}', '{wx_name}');'''
        self.add_point(wx_id=wx_id, point=self.sign_point)
        cursor.execute(sign_sql)
        conn.commit()
        self.close_db(conn, cursor)
        msg = f'签到成功 + {self.sign_point} 分\n当前可用积分：{self.query_point(wx_id=wx_id)}'
        return msg

    # 清空签到表
    def clear_sign(self):
        conn, cursor = self.open_db()
        clear_sign_sql = 'DELETE FROM sign'
        cursor.execute(clear_sign_sql)
        conn.commit()
        self.close_db(conn, cursor)

    # 积分赠送
    def give_point(self, wx_id, wx_name, at_wx_id, at_wx_name, point):
        if self.query_point(wx_id=wx_id) >= self.query_point(wx_id=at_wx_id):
            # 赠送人扣除积分
            self.judge_main(wx_id=wx_id, wx_name=wx_name, point=point, del_bool=True)
            # 被赠送人增加积分
            self.judge_main(wx_id=at_wx_id, wx_name=at_wx_name, point=point, add_bool=True)
            msg = f'\n您已给予 {at_wx_name} {point}分 \n当前可用积分 {self.query_point(wx_id=wx_id)}分'
        else:
            msg = f'\n您当前的余额不足\n当前可用积分：{self.query_point(wx_id=wx_id)} 分'
        give_bool = True
        return msg, give_bool

    # 主判断
    def judge_main(self, wx_id, wx_name, point=None, add_bool=False, del_bool=False, sign_bool=False):
        msg = ''
        if sign_bool:
            if not self.judge_user(wx_id=wx_id, sign_bool=True):
                if self.judge_user(wx_id=wx_id, ):
                    msg = self.sign(wx_id=wx_id, wx_name=wx_name, )
                else:
                    output('[+]:当前用户不存在，正在初始化该用户... ...')
                    self.init_user(wx_id=wx_id, wx_name=wx_name)
                    msg = self.sign(wx_id=wx_id, wx_name=wx_name)
        elif add_bool:
            if self.judge_user(wx_id=wx_id):
                msg = self.add_point(wx_id=wx_id, point=point)
            else:
                output('[+]:当前用户不存在，正在初始化该用户... ...')
                self.init_user(wx_id=wx_id, wx_name=wx_name)
                msg = self.add_point(wx_id=wx_id, point=point)
        elif del_bool:
            if self.judge_user(wx_id=wx_id):
                msg = self.del_point(wx_id=wx_id, point=point)
            else:
                output('[+]:当前用户不存在，正在初始化该用户... ...')
                self.init_user(wx_id=wx_id, wx_name=wx_name)
                msg = self.del_point(wx_id=wx_id, point=point)
        return msg


if __name__ == '__main__':
    Dps = Db_Point_Server()
    # Dps.init_db()
    msg = Dps.judge_main(wx_id='123123123', wx_name='123', sign_bool=True, point=230)
    print(msg)
    # Dps.query_point(wx_id='123')
