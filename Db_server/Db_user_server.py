from Output.output import output
import sqlite3


class Db_user_server:

    def __init__(self):
        # 定义特权数据库
        db_path = 'config/privilege.db'

        # 建立数据库连接
        self.conn = sqlite3.connect(db_path)

        # 建立数据库指针
        self.cur = self.conn.cursor()

    # 初始化数据库
    def init_database(self):
        # 新建数据表
        create_admin_table_sql = '''CREATE TABLE IF NOT EXISTS admins 
        (wx_id varchar(255),
        wx_name varchar(255),
        wx_roomid varchar(255),
        wx_room_name varchar(255));'''

        create_privilege_room_sql = '''CREATE TABLE IF NOT EXISTS privilege_rooms
        (wx_roomid varchar(255),
        wx_room_name varchar(255));'''

        create_black_rooms_sql = '''CREATE TABLE IF NOT EXISTS black_rooms
        (wx_roomid varchar(255),
        wx_room_name varchar(255));'''

        self.cur.execute(create_admin_table_sql)
        self.cur.execute(create_privilege_room_sql)
        self.cur.execute(create_black_rooms_sql)
        self.conn.commit()
        msg = '[*] >> 管理数据表初始化成功!'
        output(msg)

    # 判断表是否存在
    def judge_table(self, table_name):
        judge_table_sql = f''' SELECT tbl_name FROM sqlite_master WHERE type = 'table';'''
        cursor = self.cur.execute(judge_table_sql)
        query_data = cursor.fetchall()
        # print(query_data)
        if query_data:
            for data in query_data:
                if table_name in data:
                    return True
        else:
            return False

    # 判断数据是否存在
    def judge_data(self, wx_id=None, wx_roomid=None, black_bool=False):
        if wx_id:
            judge_data_sql = f'''SELECT wx_id from admins WHERE wx_roomid = '{wx_roomid}' and wx_id = '{wx_id}';'''
        elif wx_roomid and black_bool:
            judge_data_sql = f'''SELECT wx_roomid FROM black_rooms WHERE wx_roomid = '{wx_roomid}';'''
        else:
            judge_data_sql = f'''SELECT wx_roomid FROM privilege_rooms WHERE wx_roomid = '{wx_roomid}';'''
        cursor = self.cur.execute(judge_data_sql)
        query_data = cursor.fetchall()
        if query_data:
            for data in query_data:
                if wx_id or wx_roomid in data:
                    return True

        else:
            # 没查到数据返回False
            return False

    # 主判断函数
    def main_judge(self, wx_id=None, wx_name=None, wx_roomid=None, wx_room_name=None, delete_bool=False,
                   black_bool=False, add_admin_bool=False):
        table_bool = self.judge_table('admins') if (wx_id and wx_name) else (
                self.judge_table('privilege_rooms') and self.judge_table('black_rooms')) if wx_roomid else False
        if not table_bool:
            msg = '[+] >> 检测到管理数据表未创建，正在初始化... ...'
            output(msg)
            self.init_database()

        # 新增管理员操作
        if wx_id and wx_name and not self.judge_data(wx_id=wx_id, wx_roomid=wx_roomid) and not delete_bool \
                and add_admin_bool and not black_bool:
            msg = self.add_admin(wx_id=wx_id, wx_name=wx_name, wx_roomid=wx_roomid, wx_room_name=wx_room_name)
        # 删除管理员操作
        elif wx_id and wx_name and delete_bool and self.judge_data(wx_id=wx_id, wx_roomid=wx_roomid)\
                and not add_admin_bool and not black_bool:
            msg = self.del_admin(wx_id=wx_id, wx_name=wx_name, wx_roomid=wx_roomid)
        # 添加特权群聊操作
        elif wx_roomid and not self.judge_data(wx_roomid=wx_roomid) and not delete_bool\
                and not add_admin_bool and not black_bool:
            msg = self.add_privilege_room(wx_roomid=wx_roomid, wx_room_name=wx_room_name)
        # 删除特权群聊
        elif wx_roomid and self.judge_data(wx_roomid=wx_roomid) and delete_bool and not black_bool:
            msg = self.del_privilege_room(wx_roomid=wx_roomid)
        # 添加黑名单群聊
        elif wx_roomid and not self.judge_data(wx_roomid=wx_roomid,
                                               black_bool=black_bool) and black_bool and not delete_bool:
            msg = self.add_black_room(wx_roomid=wx_roomid, wx_room_name=wx_room_name)
        # 删除黑名单群聊
        elif wx_roomid and delete_bool and self.judge_data(wx_roomid=wx_roomid,
                                                           black_bool=black_bool) and delete_bool and black_bool:
            msg = self.del_black_room(wx_roomid=wx_roomid)
        # 数据存在操作
        elif delete_bool:
            msg = f'[+] >> 当前数据已移除!'
            output(msg)
        else:
            msg = f'[+] >> 当前数据已存在!'
            output(msg)
        return msg

    # 查询管理员返回列表
    def query_admins(self, wx_roomid=None):
        admin_list = list()
        if wx_roomid:
            query_admins_sql = f'''SELECT wx_id FROM admins where wx_roomid ='{wx_roomid}';'''
        else:
            query_admins_sql = f'''SELECT wx_id FROM admins'''
        cursor = self.cur.execute(query_admins_sql)
        query_data = cursor.fetchall()
        for data in query_data:
            admin_list += data
        return admin_list

    # 查询特权群聊返回列表
    def query_privilege_rooms(self):
        privilege_rooms_list = list()
        query_privilege_sql = '''SELECT wx_roomid FROM privilege_rooms;'''
        try:
            cursor = self.cur.execute(query_privilege_sql)
            query_data = cursor.fetchall()
            for data in query_data:
                privilege_rooms_list += data
            return privilege_rooms_list
        except Exception as e:
            msg = '[ERROR] >> 出现错误，错误信息：{}'.format(e)
            output(msg)
            self.init_database()

    # 查询黑名单群聊返回列表
    def query_black_rooms(self):
        black_rooms_list = list()
        query_black_rooms_sql = '''SELECT wx_roomid FROM black_rooms;'''
        cursor = self.cur.execute(query_black_rooms_sql)
        query_data = cursor.fetchall()
        for data in query_data:
            black_rooms_list += data
        return black_rooms_list

    # 新增黑名单群聊
    def add_black_room(self, wx_roomid, wx_room_name):
        add_black_room_sql = f'''INSERT INTO black_rooms VALUES ('{wx_roomid}', '{wx_room_name}');'''
        self.cur.execute(add_black_room_sql)
        self.conn.commit()
        msg = '已添加至黑名单群聊!'
        return msg

    # 删除黑名单群聊
    def del_black_room(self, wx_roomid):
        del_black_room_sql = f'''DELETE FROM black_rooms WHERE wx_roomid = '{wx_roomid}';'''
        self.cur.execute(del_black_room_sql)
        self.conn.commit()
        msg = '已移出黑名单群聊!'
        return msg

    # 新增特权群聊
    def add_privilege_room(self, wx_roomid, wx_room_name):
        add_privilege_room_sql = f'''INSERT INTO privilege_rooms VALUES ('{wx_roomid}', '{wx_room_name}');'''
        self.cur.execute(add_privilege_room_sql)
        self.conn.commit()
        msg = f'已添加至特权群聊'
        return msg

    # 删除特权群聊
    def del_privilege_room(self, wx_roomid):
        del_privilege_room_sql = f'''DELETE FROM privilege_rooms WHERE wx_roomid = '{wx_roomid}';'''
        self.cur.execute(del_privilege_room_sql)
        self.conn.commit()
        msg = f'已移出特权群聊!'
        return msg

    # 新增管理员
    def add_admin(self, wx_id, wx_name, wx_roomid, wx_room_name):
        add_admin_sql = f'''INSERT INTO admins VALUES ('{wx_id}','{wx_name}', '{wx_roomid}', '{wx_room_name}');'''
        self.cur.execute(add_admin_sql)
        self.conn.commit()
        msg = f'管理员{wx_name}添加成功!'
        return msg

    # 删除管理员
    def del_admin(self, wx_id, wx_roomid, wx_name):
        del_admin_sql = f'''DELETE FROM admins WHERE wx_id = '{wx_id}' and wx_roomid = '{wx_roomid}';'''
        self.cur.execute(del_admin_sql)
        self.conn.commit()
        msg = f'管理员{wx_name}删除成功!'
        return msg

    # 查看所有管理员
    def show_all_admins(self):
        msg = ''
        show_all_admins_sql = '''SELECT wx_id, wx_name, wx_roomid, wx_room_name FROM admins;'''
        cursor = self.cur.execute(show_all_admins_sql)
        query_data = cursor.fetchall()
        for data in list(query_data):
            msg += f'【{data[0]}】【{data[1]}】\n【{data[2]}】【{data[3]}】 \n\n'
        msg = '\t\t\t\t\t【当前所有管理员】\t\t\t\t\t\n' + msg.strip()
        return msg

    # 查看所有特权群聊
    def show_all_privilege_rooms(self):
        msg = ''
        show_all_privilege_rooms_sql = '''SELECT wx_roomid, wx_room_name FROM privilege_rooms;'''
        cursor = self.cur.execute(show_all_privilege_rooms_sql)
        query_data = cursor.fetchall()
        for data in list(query_data):
            msg += f'【{data[0]}】   【{data[1]}】\n'
        msg = '\t\t\t\t\t【当前所有特权群聊】\t\t\t\t\t\n' + msg
        return msg

    # 查看所有黑名单群聊
    def show_all_black_rooms(self):
        msg = ''
        show_all_black_rooms_sql = '''SELECT wx_roomid, wx_room_name FROM black_rooms;'''
        cursor = self.cur.execute(show_all_black_rooms_sql)
        query_data = cursor.fetchall()
        for data in list(query_data):
            msg += f'【{data[0]}】   【{data[1]}】\n'
        msg = '\t\t\t\t\t【当前所有黑名单群聊】\t\t\t\t\t\n' + msg
        return msg


if __name__ == '__main__':
    Dus = Db_user_server()
    Dus.init_database()
