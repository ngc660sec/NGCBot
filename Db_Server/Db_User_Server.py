from Output.output import output
import sqlite3
import os


class Db_User_Server:
    def __init__(self):
        current_path = os.path.dirname(__file__)
        # 数据库存放地址
        self.db_file = current_path + '/../Config/User_db.db'
        self.judge_init()

    # 打开数据库
    def open_db(self):
        conn = sqlite3.connect(database=self.db_file, )
        cursor = conn.cursor()
        return conn, cursor

    # 关闭数据库
    def close_db(self, conn, cursor):
        cursor.close()
        conn.close()

    # 判断是否初始化
    def judge_init(self, ):
        conn, cursor = self.open_db()
        judge_table_sql = '''SELECT name FROM sqlite_master;'''
        cursor.execute(judge_table_sql)
        data = cursor.fetchall()
        if not data:
            msg = '[-]:检测到用户数据库未初始化，正在初始化数据库'
            output(msg)
            self.init_db()
        self.close_db(conn, cursor)

    # 初始化数据库
    def init_db(self):
        conn, cursor = self.open_db()
        create_admin_table_sql = '''CREATE TABLE IF NOT EXISTS admins 
                (wx_id varchar(255),
                wx_name varchar(255),
                wx_roomid varchar(255),
                wx_room_name varchar(255));'''
        create_white_rooms = '''CREATE TABLE IF NOT EXISTS white_rooms 
                (wx_roomid varchar(255),
                wx_room_name varchar(255));'''
        create_black_rooms = '''CREATE TABLE IF NOT EXISTS black_rooms 
                (wx_roomid varchar(255),
                wx_room_name varchar(255));'''
        cursor.execute(create_admin_table_sql)
        cursor.execute(create_white_rooms)
        cursor.execute(create_black_rooms)
        self.close_db(conn=conn, cursor=cursor)
        output('[*]:用户数据库服务初始化成功!')

    # 添加管理员
    def add_admin(self, wx_id, wx_roomid, wx_name, wx_room_name):
        if not self.judge_data(wx_id=wx_id, wx_roomid=wx_roomid):
            conn, cursor = self.open_db()
            add_admin_sql = f'''INSERT INTO admins VALUES (
            '{wx_id}', '{wx_name}', '{wx_roomid}', '{wx_room_name}');'''
            cursor.execute(add_admin_sql)
            conn.commit()
            self.close_db(conn=conn, cursor=cursor)
            msg = f'添加管理员 {wx_name} 成功!'
        else:
            msg = f'管理员 {wx_name} 已存在!'
        return msg

    # 删除管理员
    def del_admin(self, wx_id, wx_name, wx_roomid):
        if self.judge_data(wx_id=wx_id, wx_roomid=wx_roomid):
            conn, cursor = self.open_db()
            del_admin_sql = f'''DELETE FROM admins WHERE wx_id='{wx_id}' and wx_roomid='{wx_roomid}';'''
            cursor.execute(del_admin_sql)
            conn.commit()
            self.close_db(conn, cursor)
            msg = f'移除管理员 {wx_name} 成功!'
        else:
            msg = f'管理员 {wx_name} 已移出!'
        return msg

    # 查看所有管理员
    def show_admin(self):
        conn, cursor = self.open_db()
        show_admin_sql = '''SELECT wx_id, wx_roomid FROM admins;'''
        cursor.execute(show_admin_sql)
        data = cursor.fetchall()
        self.close_db(conn, cursor)
        msg = []
        for d in data:
            msg.append({'wx_id': d[0], 'wx_roomid': d[1]})
        return msg

    # 添加黑名单群聊
    def add_black_room(self, wx_roomid, wx_room_name):
        if not self.judge_data(black_bool=True, wx_roomid=wx_roomid):
            conn, cursor = self.open_db()
            add_black_room_sql = f'''INSERT INTO black_rooms VALUES ('{wx_roomid}', '{wx_room_name}');'''
            cursor.execute(add_black_room_sql)
            conn.commit()
            self.close_db(conn, cursor)
            msg = f'{wx_room_name} 群聊已拉黑! '
        else:
            msg = '当前群聊已添加至黑名单'
        return msg

    # 删除黑名单群聊
    def del_black_room(self, wx_roomid, wx_room_name):
        if self.judge_data(wx_roomid=wx_roomid, black_bool=True):
            conn, cursor = self.open_db()
            del_black_room_sql = f'''DELETE FROM black_rooms WHERE wx_roomid='{wx_roomid}';'''
            cursor.execute(del_black_room_sql)
            conn.commit()
            self.close_db(conn, cursor)
            msg = f'移除黑名单群聊 {wx_room_name} 成功!'
        else:
            msg = '该群聊未被拉黑!'
        return msg

    # 查看黑名单群聊
    def show_black_room(self):
        conn, cursor = self.open_db()
        show_black_room_sql = '''SELECT wx_roomid FROM black_rooms;'''
        cursor.execute(show_black_room_sql)
        data = cursor.fetchall()
        self.close_db(conn, cursor)
        msg = list()
        for d in data:
            msg.append({'wx_roomid': d[0]})
        return msg

    # 添加白名单群聊
    def add_white_room(self, wx_roomid, wx_room_name):
        if not self.judge_data(wx_roomid=wx_roomid):
            conn, cursor = self.open_db()
            add_white_room_sql = f'''INSERT INTO white_rooms VALUES ('{wx_roomid}', '{wx_room_name}');'''
            cursor.execute(add_white_room_sql)
            conn.commit()
            self.close_db(conn, cursor)
            msg = f'{wx_room_name} 群聊已开启推送服务!'
        else:
            msg = '该群聊已开启推送服务!'
        return msg

    # 删除白名单群聊
    def del_white_room(self, wx_roomid, wx_room_name):
        if self.judge_data(wx_roomid=wx_roomid, ):
            conn, cursor = self.open_db()
            del_white_room_sql = f'''DELETE FROM white_rooms WHERE wx_roomid='{wx_roomid}';'''
            cursor.execute(del_white_room_sql)
            conn.commit()
            self.close_db(conn, cursor)
            msg = f'{wx_room_name} 群聊已关闭推送服务!'
        else:
            msg = '该群聊未开启推送服务!'
        return msg

    # 查看白名单群聊
    def show_white_room(self):
        conn, cursor = self.open_db()
        show_white_room_sql = '''SELECT wx_roomid FROM white_rooms;'''
        cursor.execute(show_white_room_sql)
        data = cursor.fetchall()
        self.close_db(conn, cursor)
        white_rooms = list()
        for d in data:
            white_rooms.append(d[0])
        return white_rooms

    # 判断表中数据是否存在  True False
    def judge_data(self, wx_id=None, wx_roomid=None, black_bool=False):
        conn, cursor = self.open_db()
        if wx_id:
            sql = f'''SELECT wx_id FROM admins WHERE wx_id='{wx_id}' and wx_roomid='{wx_roomid}';'''
        elif black_bool:
            sql = f'''SELECT wx_roomid FROM black_rooms where wx_roomid='{wx_roomid}';'''
        else:
            sql = f'''SELECT wx_roomid FROM white_rooms where wx_roomid='{wx_roomid}';'''
        cursor.execute(sql)
        data = cursor.fetchall()
        if data:
            return True
        else:
            return False


if __name__ == '__main__':
    Dus = Db_User_Server()
    # Dus.init_db()
    # Dus.add_admin(wx_id='yunyun', wx_name='云云', wx_roomid='123123', wx_room_name='测试')
    # Dus.del_admin(wx_id='yunyun', wx_name='云云', wx_roomid='123123')
    Dus.show_admin()
