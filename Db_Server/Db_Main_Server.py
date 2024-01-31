import time

from OutPut import OutPut
import sqlite3
import os


class Db_Main_Server:
    def __init__(self, wcf):
        self.wcf = wcf
        current_path = os.path.dirname(__file__)
        # 数据库存放地址
        self.All_Db_file = current_path + '/../Config/All_Db_File.db'

    # 查询所有联系人(公众号，群聊) 添加到自建数据库
    def query_all_users(self, init=False):
        contacts = self.wcf.query_sql("MicroMsg.db", "SELECT UserName, NickName FROM Contact WHERE UserName LIKE '%chatroom%' OR UserName LIKE '%gh\_%';")
        try:
            for contact in contacts:
                UserName = contact.get('UserName')
                NickName = contact.get('NickName')
                if '@chatroom' in UserName:
                    self.add_room(room_id=UserName, room_name=NickName)
                elif 'gh_' in UserName:
                    self.add_gh(gh_id=UserName, gh_name=NickName)
                else:
                    self.add_user(wx_id=UserName, wx_name=NickName)
            if not init:
                OutPut.outPut('[+]: 总数据库初始化成功！！！')
        except Exception as e:
            OutPut.outPut(f'[-]: 查询所有联系人(公众号，群聊) 出现错误，错误信息: {e}')

    # 打开数据库
    def open_db(self):
        conn = sqlite3.connect(database=self.All_Db_file, )
        cursor = conn.cursor()
        return conn, cursor

    # 关闭数据库
    def close_db(self, conn, cursor):
        cursor.close()
        conn.close()

    # 数据库初始化(创建群数据库，好友数据库，公众号数据库)
    def db_init(self):
        OutPut.outPut(f'[*]: 正在初始化总数据库... ...')
        conn, cursor = self.open_db()
        create_rooms_sql = '''CREATE TABLE IF NOT EXISTS rooms 
                (room_id varchar(255),
                room_name varchar(255));'''
        create_users_sql = '''CREATE TABLE IF NOT EXISTS users 
                (wx_id varchar(255),
                wx_name varchar(255));'''
        create_ghs_sql = '''CREATE TABLE IF NOT EXISTS ghs 
                (gh_id varchar(255),
                gh_name varchar(255));'''
        create_admins_sql = '''CREATE TABLE IF NOT EXISTS admins
                (room_id varchar(255),
                room_name varchar(255),
                wx_id varchar(255),
                wx_name varchar(255));'''
        create_white_rooms_sql = '''CREATE TABLE IF NOT EXISTS white_rooms
                (room_id varchar(255),
                room_name varchar(255));'''
        create_black_rooms_sql = '''CREATE TABLE IF NOT EXISTS black_rooms
                (room_id varchar(255),
                room_name varchar(255));'''
        create_white_ghs_sql = '''CREATE TABLE IF NOT EXISTS white_ghs
                (gh_id varchar(255),
                gh_name varchar(255));'''
        create_push_rooms_sql = '''CREATE TABLE IF NOT EXISTS push_rooms
                (room_id varchar(255),
                room_name varchar(255));'''

        cursor.execute(create_rooms_sql)
        cursor.execute(create_users_sql)
        cursor.execute(create_ghs_sql)
        cursor.execute(create_admins_sql)
        cursor.execute(create_white_rooms_sql)
        cursor.execute(create_black_rooms_sql)
        cursor.execute(create_white_ghs_sql)
        cursor.execute(create_push_rooms_sql)
        self.close_db(conn=conn, cursor=cursor)

    # 添加群到群数据表中
    def add_room(self, room_id, room_name):
        if not self.judge_room(room_id=room_id):
            conn, curser = self.open_db()
            add_room_sql = f'''INSERT INTO rooms VALUES (?, ?);'''
            curser.execute(add_room_sql, (room_id, room_name))
            conn.commit()
            self.close_db(conn, curser)

    # 添加公众号到公众号数据库中
    def add_gh(self, gh_id, gh_name):
        if not self.judge_gh(gh_id=gh_id):
            conn, curser = self.open_db()
            add_gh_sql = f'''INSERT INTO ghs VALUES (?, ?);'''
            curser.execute(add_gh_sql, (gh_id, gh_name))
            conn.commit()
            self.close_db(conn, curser)

    # 添加用户到用户数据库中
    def add_user(self, wx_id, wx_name):
        if not self.judge_user(wx_id=wx_id):
            conn, curser = self.open_db()
            add_user_sql = f'''INSERT INTO users VALUES (?, ?);'''
            curser.execute(add_user_sql, (wx_id, wx_name))
            conn.commit()
            self.close_db(conn, curser)

    # 添加管理员
    def add_admin(self, room_id, wx_id, wx_name):
        room_name = self.query_room_name(room_id)
        if not self.judge_admin(room_id=room_id, wx_id=wx_id):
            conn, curser = self.open_db()
            add_admin_sql = f'''INSERT INTO admins VALUES (?, ?, ?, ?);'''
            curser.execute(add_admin_sql, (room_id, room_name, wx_id, wx_name))
            conn.commit()
            self.close_db(conn, curser)
            msg = f'[+]: 群聊【{room_name}】管理员 {wx_name} 已添加！！！'
        else:
            msg = f'[~]: 群聊【{room_name}】管理员 {wx_name} 已存在！！！'
        OutPut.outPut(msg)
        return msg

    # 删除管理员
    def del_admin(self, room_id, wx_id, wx_name):
        room_name = self.query_room_name(room_id)
        if self.judge_admin(wx_id=wx_id, room_id=room_id):
            conn, curser = self.open_db()
            del_admin_sql = f'''DELETE FROM admins WHERE wx_id = '{wx_id}' AND room_id = '{room_id}';'''
            curser.execute(del_admin_sql)
            conn.commit()
            self.close_db(conn, curser)
            msg = f'[+]: 群聊【{room_name}】管理员 {wx_name} 已删除！！！'
        else:
            msg = f'[~]: 群聊【{room_name}】管理员 {wx_name} 不存在！！！'
        OutPut.outPut(msg)
        return msg

    # 添加白名单群聊
    def add_white_room(self, room_id):
        room_name = self.query_room_name(room_id)
        if not self.judge_white_room(room_id=room_id):
            conn, curser = self.open_db()
            add_white_room_sql = f'''INSERT INTO white_rooms VALUES (?, ?);'''
            curser.execute(add_white_room_sql, (room_id, room_name))
            conn.commit()
            self.close_db(conn, curser)
            msg = f'[+]: 群聊【{room_name}】已添加到白名单！！！'
        else:
            msg = f'[~]: 群聊【{room_name}】已在白名单中！！！'
        OutPut.outPut(msg)
        return msg

    # 删除白名单群聊
    def del_white_room(self, room_id):
        room_name = self.query_room_name(room_id)
        if self.judge_white_room(room_id=room_id):
            conn, curser = self.open_db()
            del_white_room_sql = f'''DELETE FROM white_rooms WHERE room_id = '{room_id}';'''
            curser.execute(del_white_room_sql)
            conn.commit()
            self.close_db(conn, curser)
            msg = f'[+]: 群聊【{room_name}】已从白名单从移除！！！'
        else:
            msg = f'[~]: 群聊【{room_name}】已不在白名单中！！！'
        OutPut.outPut(msg)
        return msg

    # 添加黑名单群聊
    def add_black_room(self, room_id):
        room_name = self.query_room_name(room_id)
        if not self.judge_black_room(room_id=room_id):
            conn, curser = self.open_db()
            add_black_room_sql = f'''INSERT INTO black_rooms VALUES (?, ?);'''
            curser.execute(add_black_room_sql, (room_id, room_name))
            conn.commit()
            self.close_db(conn, curser)
            msg = f'[+]: 群聊【{room_name}】拉黑成功！！！'
        else:
            msg = f'[~]: 群聊【{room_name}】已拉黑！！！'
        OutPut.outPut(msg)
        return msg

    # 删除黑名单群聊
    def del_black_room(self, room_id):
        room_name = self.query_room_name(room_id)
        if self.judge_black_room(room_id=room_id):
            conn, curser = self.open_db()
            del_black_room_sql = f'''DELETE from black_rooms WHERE room_id = '{room_id}';'''
            curser.execute(del_black_room_sql)
            conn.commit()
            self.close_db(conn, curser)
            msg = f'[+]: 群聊【{room_name}】解除拉黑成功！！！'
        else:
            msg = f'[~]: 群聊【{room_name}】已解除拉黑！！！'
        OutPut.outPut(msg)
        return msg

    # 添加推送群聊
    def add_push_room(self, room_id):
        room_name = self.query_room_name(room_id)
        if not self.judge_push_room(room_id=room_id):
            conn, curser = self.open_db()
            add_push_room_sql = f'''INSERT INTO push_rooms VALUES (?, ?);'''
            curser.execute(add_push_room_sql, (room_id, room_name,))
            conn.commit()
            self.close_db(conn, curser)
            msg = f'[+]: 群聊【{room_name}】开启推送服务成功！！！'
        else:
            msg = f'[~]: 群聊【{room_name}】已开启推送服务'
        OutPut.outPut(msg)
        return msg

    # 移除推送群聊
    def del_push_room(self, room_id):
        room_name = self.query_room_name(room_id)
        if self.judge_push_room(room_id=room_id):
            conn, curser = self.open_db()
            del_push_room_sql = f'''DELETE FROM push_rooms WHERE room_id= '{room_id}';'''
            curser.execute(del_push_room_sql)
            conn.commit()
            self.close_db(conn, curser)
            msg = f'[+]: 群聊【{room_name}】移除推送服务成功！！！'
        else:
            msg = f'[~]: 群聊【{room_name}】已移除推送服务'
        OutPut.outPut(msg)
        return msg

    # 添加白名单公众号
    def add_white_gh(self, gh_id, gh_name):
        if not self.judge_white_gh(gh_name=gh_name):
            conn, curser = self.open_db()
            add_white_gh_sql = f'''INSERT INTO white_ghs VALUES (?, ?);'''
            curser.execute(add_white_gh_sql, (gh_id, gh_name,))
            conn.commit()
            self.close_db(conn, curser)
            msg = f'[+]: 公众号【{gh_name}】添加白名单成功！！！'
        else:
            msg = f'[~]: 公众号【{gh_name}】已添加到白名单！！！'
        OutPut.outPut(msg)
        return msg

    # 删除白名单公众号
    def del_white_gh(self, gh_name):
        if self.judge_white_gh(gh_name=gh_name):
            conn, curser = self.open_db()
            del_white_gh = f'''DELETE FROM white_ghs WHERE gh_name = '{gh_name}';'''
            curser.execute(del_white_gh)
            conn.commit()
            self.close_db(conn, curser)
            msg = f'[+]: 公众号【{gh_name}】从白名单移除成功！！！'
        else:
            msg = f'[~]: 公众号【{gh_name}】已从白名单移除！！！'
        OutPut.outPut(msg)
        return msg

    # 查找群名(room_name)
    def query_room_name(self, room_id):
        if self.judge_room(room_id=room_id):
            conn, curser = self.open_db()
            query_room_name = f'''SELECT room_name FROM rooms WHERE room_id= '{room_id}';'''
            curser.execute(query_room_name)
            data = curser.fetchone()
            self.close_db(conn, curser)
            if data:
                return data[0]
        else:
            OutPut.outPut('[-]: 不存在此群, 正在尝试添加到库... ...')
            self.query_all_users(init=True)
            self.query_room_name(room_id=room_id)

    # 判断某人是否为管理员
    def judge_admin(self, room_id, wx_id):
        conn, curser = self.open_db()
        judge_admin_sql = f'''SELECT wx_name FROM admins where wx_id='{wx_id}' and room_id='{room_id}';'''
        curser.execute(judge_admin_sql)
        data = curser.fetchone()
        self.close_db(conn, curser)
        if data:
            return True
        else:
            return False

    # 判断群聊是否处于白名单群聊
    def judge_white_room(self, room_id):
        conn, curser = self.open_db()
        judge_white_room_sql = f'''SELECT room_id FROM white_rooms WHERE room_id = '{room_id}';'''
        curser.execute(judge_white_room_sql)
        data = curser.fetchone()
        self.close_db(conn, curser)
        if data:
            return True
        else:
            return False

    # 判断群聊是否为黑名单群聊
    def judge_black_room(self, room_id):
        conn, curser = self.open_db()
        judge_black_room_sql = f'''SELECT room_id FROM black_rooms WHERE room_id = '{room_id}';'''
        curser.execute(judge_black_room_sql)
        data = curser.fetchone()
        self.close_db(conn, curser)
        if data:
            return True
        else:
            return False

    # 判断群聊是否为推送群聊
    def judge_push_room(self, room_id):
        conn, curser = self.open_db()
        judge_push_room_sql = f'''SELECT room_id FROM push_rooms WHERE room_id = '{room_id}';'''
        curser.execute(judge_push_room_sql)
        data = curser.fetchone()
        self.close_db(conn, curser)
        if data:
            return True
        else:
            return False

    # 判断是否为白名单公众号
    def judge_white_gh(self, gh_name):
        conn, curser = self.open_db()
        judge_white_gh_sql = f'''SELECT gh_id FROM white_ghs WHERE gh_name = '{gh_name}';'''
        curser.execute(judge_white_gh_sql)
        data = curser.fetchone()
        self.close_db(conn, curser)
        if data:
            return True
        else:
            return False

    # 判断群聊是否存在
    def judge_room(self, room_id):
        conn, curser = self.open_db()
        judge_room_sql = f'''SELECT room_id FROM rooms WHERE room_id = '{room_id}';'''
        curser.execute(judge_room_sql)
        data = curser.fetchone()
        self.close_db(conn, curser)
        if data:
            return True
        else:
            return False

    # 判断好友是否存在
    def judge_user(self, wx_id):
        conn, curser = self.open_db()
        judge_user_sql = f'''SELECT wx_id FROM users WHERE wx_id = '{wx_id}';'''
        curser.execute(judge_user_sql)
        data = curser.fetchone()
        self.close_db(conn, curser)
        if data:
            return True
        else:
            return False

    # 判断微信公众号是否存在
    def judge_gh(self, gh_id):
        conn, curser = self.open_db()
        judge_gh_sql = f'''SELECT gh_id FROM ghs WHERE gh_id = '{gh_id}';'''
        curser.execute(judge_gh_sql)
        data = curser.fetchone()
        if data:
            return True
        else:
            return False

    # 查看某群所有管理员
    def show_admins(self, wx_id, room_id):
        conn, curser = self.open_db()
        show_admins_sql = f'''SELECT wx_id, wx_name FROM admins WHERE wx_id = '{wx_id}' AND room_id = '{room_id}';'''
        curser.execute(show_admins_sql)
        data = curser.fetchall()
        self.close_db(conn, curser)
        msg = dict()
        for d in data:
            msg[d[0]] = d[1]
        return msg

    # 查看所有白名单群聊
    def show_white_rooms(self, ):
        conn, curser = self.open_db()
        show_white_rooms_sql = f'''SELECT room_id, room_name FROM white_rooms;'''
        curser.execute(show_white_rooms_sql)
        data = curser.fetchall()
        self.close_db(conn, curser)
        msg = dict()
        for d in data:
            msg[d[0]] = d[1]
        return msg

    # 查看所有黑名单群聊
    def show_black_rooms(self, ):
        conn, curser = self.open_db()
        show_white_rooms_sql = f'''SELECT room_id, room_name FROM black_rooms;'''
        curser.execute(show_white_rooms_sql)
        data = curser.fetchall()
        self.close_db(conn, curser)
        msg = dict()
        for d in data:
            msg[d[0]] = d[1]
        return msg

    # 查看所有推送群聊
    def show_push_rooms(self):
        conn, curser = self.open_db()
        show_push_rooms_sql = f'''SELECT room_id, room_name FROM push_rooms;'''
        curser.execute(show_push_rooms_sql)
        data = curser.fetchall()
        self.close_db(conn, curser)
        msg = dict()
        for d in data:
            msg[d[0]] = d[1]
        return msg

    # 查看所有白名单公众号
    def show_white_ghs(self):
        conn, curser = self.open_db()
        show_white_ghs = f'''SELECT gh_id, gh_name FROM white_ghs;'''
        curser.execute(show_white_ghs)
        data = curser.fetchall()
        self.close_db(conn, curser)
        msg = dict()
        for d in data:
            msg[d[0]] = d[1]
        return msg
