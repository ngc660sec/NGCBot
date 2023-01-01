from Db_Server.Db_User_Server import Db_User_Server
from BotServer.SendServer import SendServer
from collections import OrderedDict
from Output.output import output
from lxml import etree
import requests
import datetime
import hashlib
import sqlite3
import json
import yaml
import time
import re
import os


class Monitor_Server_Main:
    def __init__(self, ws):

        self.ws = ws
        self.Ss = SendServer()
        self.Dus = Db_User_Server()

        current_path = os.path.dirname(__file__)
        config = yaml.load(open(current_path + '/../Config/config.yaml', encoding='UTF-8'), yaml.Loader)
        self.db_file = current_path + '/../Config/Monitor_db.db'

        self.github_headers = {
            'Authorization': f"token {config['Monitor_Server']['Github_Token']}"
        }

        self.tools_list = config['Monitor_Server']['tools_list']
        self.keyword_list = config['Monitor_Server']['keyword_list']
        self.user_list = config['Monitor_Server']['user_list']

        self.judge_init()

    # 打开数据库
    def open_db(self):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        return conn, cur

    # 关闭数据库
    def close_db(self, conn, cur):
        cur.close()
        conn.close()

    # 判断数据库是否初始化
    def judge_init(self, ):
        conn, cursor = self.open_db()
        judge_table_sql = '''SELECT name FROM sqlite_master;'''
        cursor.execute(judge_table_sql)
        data = cursor.fetchall()
        if not data:
            msg = '[+]:检测到积分数据库未初始化，正在初始化数据库'
            self.create_database()
            output(msg)
        self.close_db(conn, cursor)

    # 初始化创建数据库
    def create_database(self, ):
        conn, cur = self.open_db()
        try:
            cur.execute('''CREATE TABLE IF NOT EXISTS cve_monitor
                       (cve_name varchar(255),
                        pushed_at varchar(255),
                        cve_url varchar(255));''')
            output("[+]:成功创建CVE监控表")
            cur.execute('''CREATE TABLE IF NOT EXISTS keyword_monitor
                       (keyword_name varchar(255),
                        pushed_at varchar(255),
                        keyword_url varchar(255));''')
            output("[+]:成功创建关键字监控表")
            cur.execute('''CREATE TABLE IF NOT EXISTS redteam_tools_monitor
                       (tools_name varchar(255),
                        pushed_at varchar(255),
                        tag_name varchar(255));''')
            output("[+]:成功创建红队工具监控表")
            cur.execute('''CREATE TABLE IF NOT EXISTS user_monitor
                       (repo_name varchar(255));''')
            output("[+]:成功创建大佬仓库监控表")
        except Exception as e:
            output("[ERROR]:创建监控表错误，错误信息：{}".format(e))
        conn.commit()  # 数据库存储在硬盘上需要commit  存储在内存中的数据库不需要
        self.close_db(conn, cur)
        self.wx_send(text='Github实时推送连接成功!', body='')

    # 根据排序获取本年前20条CVE
    def getNews(self, ):
        today_cve_info_tmp = []
        try:
            # 抓取本年的
            year = datetime.datetime.now().year
            api = "https://api.github.com/search/repositories?q=CVE-{}&sort=updated".format(year)
            json_str = requests.get(api, headers=self.github_headers, timeout=10).json()
            today_date = datetime.date.today()
            n = len(json_str['items'])
            if n > 20:
                n = 20
            for i in range(0, n):
                cve_url = json_str['items'][i]['html_url']
                try:
                    cve_name_tmp = json_str['items'][i]['name'].upper()
                    cve_name = re.findall('(CVE\-\d+\-\d+)', cve_name_tmp)[0].upper()
                    pushed_at_tmp = json_str['items'][i]['created_at']
                    pushed_at = re.findall('\d{4}-\d{2}-\d{2}', pushed_at_tmp)[0]
                    if pushed_at == str(today_date):
                        today_cve_info_tmp.append(
                            {"cve_name": cve_name, "cve_url": cve_url, "pushed_at": pushed_at})
                except Exception as e:
                    pass
            today_cve_info = OrderedDict()
            for item in today_cve_info_tmp:
                today_cve_info.setdefault(item['cve_name'], {**item, })
            today_cve_info = list(today_cve_info.values())
            return today_cve_info
        except Exception as e:
            output(f'[ERROR]:连接Github出错，错误信息：{e}')
            return '', '', ''

    def getKeywordNews(self, keyword):
        today_keyword_info_tmp = []
        try:
            # 抓取本年的
            api = "https://api.github.com/search/repositories?q={}&sort=updated".format(keyword)
            json_str = requests.get(api, headers=self.github_headers, timeout=10).json()
            today_date = datetime.date.today()
            n = len(json_str['items'])
            if n > 20:
                n = 20
            for i in range(0, n):
                keyword_url = json_str['items'][i]['html_url']
                try:
                    keyword_name = json_str['items'][i]['name']
                    pushed_at_tmp = json_str['items'][i]['created_at']
                    pushed_at = re.findall('\d{4}-\d{2}-\d{2}', pushed_at_tmp)[0]
                    if pushed_at == str(today_date):
                        today_keyword_info_tmp.append(
                            {"keyword_name": keyword_name, "keyword_url": keyword_url, "pushed_at": pushed_at})
                except Exception as e:
                    output(f'[ERROR]:出现错误，错误信息：{e}')
            today_keyword_info = OrderedDict()
            for item in today_keyword_info_tmp:
                today_keyword_info.setdefault(item['keyword_name'], {**item, })
            today_keyword_info = list(today_keyword_info.values())
            return today_keyword_info

        except Exception as e:
            output(f'[ERROR]:连接Github出错，错误信息：{e}')
        return today_keyword_info_tmp

    # 获取到的关键字仓库信息插入到数据库
    def keyword_insert_into_sqlite3(self, data):
        conn, cur = self.open_db()
        for i in range(len(data)):
            try:
                keyword_name = data[i]['keyword_name']
                cur.execute(
                    "INSERT INTO keyword_monitor (keyword_name,pushed_at,keyword_url) VALUES ('{}', '{}', '{}')".format(
                        keyword_name, data[i]['pushed_at'], data[i]['keyword_url']))
            except Exception as e:
                output(f'[ERROR]:关键字仓库信息插入到数据库出错，错误信息：{e}')
        self.close_db(conn, cur)

    # 查询数据库里是否存在该关键字仓库的方法
    def query_keyword_info_database(self, keyword_name):
        conn, cur = self.open_db()
        sql_grammar = "SELECT keyword_name FROM keyword_monitor WHERE keyword_name = '{}';".format(keyword_name)
        cursor = cur.execute(sql_grammar)
        self.close_db(conn, cur)
        return len(list(cursor))

    # 获取不存在数据库里的关键字信息
    def get_today_keyword_info(self, today_keyword_info_data):
        today_all_keyword_info = []
        for i in range(len(today_keyword_info_data)):
            try:
                today_keyword_name = today_keyword_info_data[i]['keyword_name']
                today_cve_name = re.findall(r'(CVE\-\d+\-\d+)', today_keyword_info_data[i]['keyword_name'].upper())
                if len(today_cve_name) > 0 and self.query_cve_info_database(today_cve_name.upper()) == 1:
                    pass
                Verify = self.query_keyword_info_database(today_keyword_name)
                if Verify == 0:
                    today_all_keyword_info.append(today_keyword_info_data[i])
            except Exception as e:
                output(f'[ERROR]:获取不存在数据库里的关键字信息出错，错误信息：{e}')
        return today_all_keyword_info

    # 获取到的CVE信息插入到数据库
    def cve_insert_into_sqlite3(self, data):
        conn, cur = self.open_db()
        for i in range(len(data)):
            try:
                cve_name = re.findall('(CVE\-\d+\-\d+)', data[i]['cve_name'])[0].upper()
                cur.execute(
                    "INSERT INTO cve_monitor (cve_name,pushed_at,cve_url) VALUES ('{}', '{}', '{}')".format(cve_name,
                                                                                                            data[i][
                                                                                                                'pushed_at'],
                                                                                                            data[i][
                                                                                                                'cve_url']))
            except Exception as e:
                output(f'[ERROR]:CVE信息插入到数据库出错，错误信息：{e}')
        self.close_db(conn, cur)

    # 查询数据库里是否存在该CVE的方法
    def query_cve_info_database(self, cve_name):
        conn, cur = self.open_db()
        sql_grammar = "SELECT cve_name FROM cve_monitor WHERE cve_name = '{}';".format(cve_name)
        cursor = cur.execute(sql_grammar)
        self.close_db(conn, cur)
        return len(list(cursor))

    # 查询数据库里是否存在该tools工具名字的方法
    def query_tools_info_database(self, tools_name):
        conn, cur = self.open_db()
        sql_grammar = "SELECT tools_name FROM redteam_tools_monitor WHERE tools_name = '{}';".format(tools_name)
        cursor = cur.execute(sql_grammar)
        return len(list(cursor))

    # 获取不存在数据库里的CVE信息
    def get_today_cve_info(self, today_cve_info_data):
        today_all_cve_info = []
        for i in range(len(today_cve_info_data)):
            try:
                today_cve_name = re.findall('(CVE\-\d+\-\d+)', today_cve_info_data[i]['cve_name'])[0].upper()
                if self.exist_cve(today_cve_name) == 1:
                    Verify = self.query_cve_info_database(today_cve_name.upper())
                    if Verify == 0:
                        today_all_cve_info.append(today_cve_info_data[i])
            except Exception as e:
                output(f'[ERROR]:获取不存在数据库里的CVE信息出错，错误信息：{e}')
        return today_all_cve_info

    # 获取红队工具信息插入到数据库
    def tools_insert_into_sqlite3(self, data):
        conn, cur = self.open_db()
        for i in range(len(data)):
            Verify = self.query_tools_info_database(data[i]['tools_name'])
            if Verify == 0:
                cur.execute(
                    "INSERT INTO redteam_tools_monitor (tools_name,pushed_at,tag_name) VALUES ('{}', '{}','{}')".format(
                        data[i]['tools_name'], data[i]['pushed_at'], data[i]['tag_name']))
                conn.commit()
        self.close_db(conn, cur)

    # 获取红队工具的名称，更新时间，版本名称信息
    def get_pushed_at_time(self, tools_list):
        tools_info_list = []
        for url in tools_list:
            try:
                tools_json = requests.get(url, headers=self.github_headers, timeout=10).json()
                pushed_at_tmp = tools_json['pushed_at']
                pushed_at = re.findall('\d{4}-\d{2}-\d{2}', pushed_at_tmp)[0]  # 获取的是API上的时间
                tools_name = tools_json['name']
                api_url = tools_json['url']
                try:
                    releases_json = requests.get(url + "/releases", headers=self.github_headers, timeout=10).json()
                    tag_name = releases_json[0]['tag_name']
                except Exception as e:
                    tag_name = "no releases"
                tools_info_list.append(
                    {"tools_name": tools_name, "pushed_at": pushed_at, "api_url": api_url, "tag_name": tag_name})
            except Exception as e:
                output(f'[ERROR]: 获取红队工具的名称，更新时间，版本名称信息出错，错误信息：{e}')
        return tools_info_list

    # 根据红队名名称查询数据库红队工具的更新时间以及版本名称并返回
    def tools_query_sqlite3(self, tools_name):
        conn, cur = self.open_db()
        result_list = []
        sql_grammar = "SELECT pushed_at,tag_name FROM redteam_tools_monitor WHERE tools_name = '{}';".format(tools_name)
        cursor = cur.execute(sql_grammar)
        for result in cursor:
            result_list.append({"pushed_at": result[0], "tag_name": result[1]})
        self.close_db(conn, cur)
        return result_list

    # 获取更新了的红队工具在数据库里面的时间和版本
    def get_tools_update_list(self, data):
        tools_update_list = []
        for dist in data:
            query_result = self.tools_query_sqlite3(dist['tools_name'])
            if len(query_result) > 0:
                today_tools_pushed_at = query_result[0]['pushed_at']
                if dist['pushed_at'] != today_tools_pushed_at:
                    # 返回数据库里面的时间和版本
                    tools_update_list.append({"api_url": dist['api_url'], "pushed_at": today_tools_pushed_at,
                                              "tag_name": query_result[0]['tag_name']})
        return tools_update_list

    # 监控用户是否新增仓库，不是 fork 的
    def getUserRepos(self, user):
        try:
            api = "https://api.github.com/users/{}/repos".format(user)
            json_str = requests.get(api, headers=self.github_headers, timeout=10).json()
            today_date = datetime.date.today()

            for i in range(0, len(json_str)):
                created_at = re.findall('\d{4}-\d{2}-\d{2}', json_str[i]['created_at'])[0]
                if not json_str[i]['fork'] and created_at == str(today_date):
                    Verify = self.user_insert_into_sqlite3(json_str[i]['full_name'])
                    if Verify == 0:
                        name = json_str[i]['name']
                        try:
                            description = json_str[i]['description']
                        except Exception as e:
                            description = "作者未写描述"
                        download_url = json_str[i]['html_url']
                        text = r'大佬' + r'** ' + user + r' ** ' + r'又分享了一款工具! '
                        body = "工具名称: " + name + " \r\n" + "工具地址: " + download_url + " \r\n" + "工具描述: " + "" + description
                        self.wx_send(text=text, body=body)
        except Exception as e:
            output(f'[ERROR]:连接Github出错，错误信息：{e}')

    # 获取用户或者组织信息插入到数据库
    def user_insert_into_sqlite3(self, repo_name):
        conn, cur = self.open_db()
        sql_grammar = "SELECT repo_name FROM user_monitor WHERE repo_name = '{}';".format(repo_name)
        Verify = len(list(cur.execute(sql_grammar)))
        if Verify == 0:
            cur.execute("INSERT INTO user_monitor (repo_name) VALUES ('{}')".format(repo_name))
        self.close_db(conn, cur)
        return Verify

    # 获取更新信息并发送到对应社交软件
    def send_body(self, url, query_pushed_at, query_tag_name):
        conn, cur = self.open_db()
        json_str = requests.get(url + '/releases', headers=self.github_headers, timeout=10).json()
        new_pushed_at = \
            re.findall('\d{4}-\d{2}-\d{2}',
                       requests.get(url, headers=self.github_headers, timeout=10).json()['pushed_at'])[
                0]
        if len(json_str) != 0:
            tag_name = json_str[0]['tag_name']
            if query_pushed_at < new_pushed_at:
                if tag_name != query_tag_name:
                    try:
                        update_log = json_str[0]['body']
                    except Exception as e:
                        update_log = "作者未写更新内容"
                    download_url = json_str[0]['html_url']
                    tools_name = url.split('/')[-1]
                    text = r'** ' + tools_name + r' ** 工具,版本更新啦!'
                    body = "工具名称：" + tools_name + "\r\n" + "工具地址：" + download_url + "\r\n" + "工具更新日志：" + "\r\n" + update_log
                    self.wx_send(text=text, body=body)
                    sql_grammar = "UPDATE redteam_tools_monitor SET tag_name = '{}' WHERE tools_name='{}'".format(
                        tag_name,
                        tools_name)
                    sql_grammar1 = "UPDATE redteam_tools_monitor SET pushed_at = '{}' WHERE tools_name='{}'".format(
                        new_pushed_at, tools_name)
                    cur.execute(sql_grammar)
                    cur.execute(sql_grammar1)
                elif tag_name == query_tag_name:
                    commits_url = url + "/commits"
                    commits_url_response_json = requests.get(commits_url).text
                    commits_json = json.loads(commits_url_response_json)
                    tools_name = url.split('/')[-1]
                    download_url = commits_json[0]['html_url']
                    try:
                        update_log = commits_json[0]['commit']['message']
                    except Exception as e:
                        update_log = "作者未写更新内容，具体点击更新详情地址的URL进行查看"
                    text = r'** ' + tools_name + r' ** 工具小更新了一波!'
                    body = "工具名称：" + tools_name + "\r\n" + "更新详情地址：" + download_url + "\r\n" + "commit更新日志：" + "\r\n" + update_log
                    self.wx_send(text=text, body=body)
                    sql_grammar = "UPDATE redteam_tools_monitor SET pushed_at = '{}' WHERE tools_name='{}'".format(
                        new_pushed_at, tools_name)
                    cur.execute(sql_grammar)
        else:
            if query_pushed_at != new_pushed_at:
                json_str = requests.get(url + '/commits', headers=self.github_headers, timeout=10).json()
                update_log = json_str[0]['commit']['message']
                download_url = json_str[0]['html_url']
                tools_name = url.split('/')[-1]
                text = r'** ' + tools_name + r' ** 工具更新啦!'
                body = "工具名称：" + tools_name + "\r\n" + "工具地址：" + download_url + "\r\n" + "commit更新日志：" + "\r\n" + update_log
                self.wx_send(text=text, body=body)
                sql_grammar = "UPDATE redteam_tools_monitor SET pushed_at = '{}' WHERE tools_name='{}'".format(
                    new_pushed_at, tools_name)
                cur.execute(sql_grammar)
                # return update_log, download_url
        self.close_db(conn, cur)

    # 创建md5对象
    def nmd5(self, str):
        m = hashlib.md5()
        b = str.encode(encoding='utf-8')
        m.update(b)
        str_md5 = m.hexdigest()
        return str_md5

    # 有道翻译
    def translate(self, word):
        headerstr = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        bv = self.nmd5(headerstr)
        lts = str(round(time.time() * 1000))
        salt = lts + '90'
        strexample = 'fanyideskweb' + word + salt + 'Y2FYu%TNSbMCxc3t2u^XT'
        sign = self.nmd5(strexample)
        data = {
            'i': word,
            'from': 'AUTO',
            'to': 'AUTO',
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': salt,
            'sign': sign,
            'lts': lts,
            'bv': bv,
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_CLICKBUTTION',
        }
        url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Referer': 'http://fanyi.youdao.com/',
            'Origin': 'http://fanyi.youdao.com',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'fanyi.youdao.com',
            'cookie': '_ntes_nnid=937f1c788f1e087cf91d616319dc536a,1564395185984; OUTFOX_SEARCH_USER_ID_NCOO=; OUTFOX_SEARCH_USER_ID=-10218418@11.136.67.24; JSESSIONID=; ___rl__test__cookies=1'
        }
        res = requests.post(url=url, data=data, headers=header)
        result_dict = res.json()
        result = ""
        for json_str in result_dict['translateResult'][0]:
            tgt = json_str['tgt']
            result += tgt
        return result

    # 判断是否存在该CVE
    def exist_cve(self, cve):
        try:
            query_cve_url = "https://cve.mitre.org/cgi-bin/cvename.cgi?name=" + cve
            response = requests.get(query_cve_url, timeout=10)
            html = etree.HTML(response.text)
            return 1
        except Exception as e:
            return 0

    # 根据cve 名字，获取描述，并翻译
    def get_cve_des_zh(self, cve):
        time.sleep(3)
        try:
            query_cve_url = "https://cve.mitre.org/cgi-bin/cvename.cgi?name=" + cve
            response = requests.get(query_cve_url, timeout=10)
            html = etree.HTML(response.text)
            des = html.xpath('//*[@id="GeneratedTable"]/table//tr[4]/td/text()')[0].strip()
            cve_time = html.xpath('//*[@id="GeneratedTable"]/table//tr[11]/td[1]/b/text()')[0].strip()
            return des, cve_time
        except Exception as e:
            pass

    # 发送CVE信息到社交工具
    def sendNews(self, data):
        try:
            text = '有新的CVE送达! \r\n** 请自行分辨是否为红队钓鱼!!! **'
            # 获取 cve 名字 ，根据cve 名字，获取描述，并翻译
            for i in range(len(data)):
                try:
                    cve_name = re.findall(r'(CVE\-\d+\-\d+)', data[i]['cve_name'])[0].upper()
                    cve_zh, cve_time = self.get_cve_des_zh(cve_name)
                    body = "CVE编号: " + cve_name + "  --- " + cve_time + " \r\n" + "Github地址: " + str(
                        data[i]['cve_url']) + "\r\n" + "CVE描述: " + "\r\n" + cve_zh
                    self.wx_send(text=text, body=body)
                except IndexError:
                    pass
        except Exception as e:
            output(f'[ERROR]:发送CVE信息到社交工具出现错误，错误信息：{e}')

    # 发送信息到社交工具
    def sendKeywordNews(self, keyword, data):
        try:
            text = '有新的关键字监控 - {} - 送达! \r\n** 请自行分辨是否为红队钓鱼!!! **'.format(keyword)
            # 获取 cve 名字 ，根据cve 名字，获取描述，并翻译
            for i in range(len(data)):
                try:
                    keyword_name = data[i]['keyword_name']
                    body = "项目名称: " + keyword_name + "\r\n" + "Github地址: " + str(data[i]['keyword_url']) + "\r\n"
                    self.wx_send(text, body)
                except IndexError:
                    pass
        except Exception as e:
            output(f'[ERROR]:发送信息到社交工具出现错误，错误信息：{e}')

    # 发送微信消息
    def wx_send(self, text, body):
        roomid_list = self.Dus.show_white_room()
        msg = text + '\n\n' + body
        for roomid in roomid_list:
            self.ws.send(self.Ss.send_msg(msg=msg.strip(), wxid=roomid))

    # main函数
    def main(self, ):
        while True:
            output("[*]:Cve 、Github 工具 和 大佬仓库 监控中... ...")
            tools_data = self.get_pushed_at_time(self.tools_list)
            self.tools_insert_into_sqlite3(tools_data)  # 获取文件中的工具列表，并从 github 获取相关信息，存储下来

            for user in self.user_list:
                self.getUserRepos(user)
            # CVE部分
            cve_data = self.getNews()
            if len(cve_data) > 0:
                today_cve_data = self.get_today_cve_info(cve_data)
                self.sendNews(today_cve_data)
                self.cve_insert_into_sqlite3(today_cve_data)
            # 关键字监控 , 最好不要太多关键字，防止 github 次要速率限制  https://docs.github.com/en/rest/overview/resources-in-the-rest-api#secondary-rate-limits=
            for keyword in self.keyword_list:
                time.sleep(1)  # 每个关键字停 1s ，防止关键字过多导致速率限制
                keyword_data = self.getKeywordNews(keyword)

                if len(keyword_data) > 0:
                    today_keyword_data = self.get_today_keyword_info(keyword_data)
                    if len(today_keyword_data) > 0:
                        self.sendKeywordNews(keyword, today_keyword_data)
                        self.keyword_insert_into_sqlite3(today_keyword_data)
            time.sleep(1)
            data2 = self.get_pushed_at_time(self.tools_list)  # 再次从文件中获取工具列表，并从 github 获取相关信息,
            data3 = self.get_tools_update_list(data2)  # 与 3 分钟前数据进行对比，如果在三分钟内有新增工具清单或者工具有更新则通知一下用户
            for i in range(len(data3)):
                try:
                    self.send_body(data3[i]['api_url'], data3[i]['pushed_at'], data3[i]['tag_name'])
                except Exception as e:
                    output(f"[ERROR]:main函数 try循环 遇到错误-->{e}")
            output('OK')
