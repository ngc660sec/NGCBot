import Api_Server.SparkApi as SparkApi
from urllib.parse import urljoin
from OutPut import OutPut
from lxml import etree
import feedparser
import requests
import datetime
import urllib3
import qianfan
import random
import yaml
import time
import os


class Api_Main_Server:
    def __init__(self, wcf):
        self.wcf = wcf
        # 全局header头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            # 'Connection':'keep-alive' ,#默认时链接一次，多次爬取之后不能产生新的链接就会产生报错Max retries exceeded with url
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Connection": "close",  # 解决Max retries exceeded with url报错
        }
        # 忽略HTTPS告警
        urllib3.disable_warnings()
        # 获取当前文件路径
        current_path = os.path.dirname(__file__)

        # 配置缓存文件夹路径
        current_list_path = current_path.split('\\')
        current_list_path.pop()
        self.Cache_path = '/'.join(current_list_path) + '/Cache'
        # 初始化读取配置文件
        config = yaml.load(open(current_path + '/../Config/config.yaml', encoding='UTF-8'), yaml.Loader)
        self.system_copyright = config['System_Config']['System_Copyright']

        # 读取配置文件
        config = yaml.load(open(current_path + '/../Config/config.yaml', encoding='UTF-8'), yaml.Loader)
        self.Key = config['Api_Server']['Api_Config']['Key']
        self.ThreatBook_Key = config['Api_Server']['Api_Config']['ThreatBook_Key']
        self.Pic_Apis = config['Api_Server']['Pic_Api']
        self.Video_Apis = config['Api_Server']['Video_Api']
        self.Icp_Api = config['Api_Server']['Icp_Api']
        self.Attribution_Api = config['Api_Server']['Attribution_Api']
        self.Whois_Api = config['Api_Server']['Whois_Api']
        self.Fish_Api = config['Api_Server']['Fish_Api']
        self.Kfc_Api = config['Api_Server']['Kfc_Api']
        self.Weather_Api = config['Api_Server']['Weather_Api']
        self.Dog_Api = config['Api_Server']['Dog_Api']
        self.Morning_Api = config['Api_Server']['Morning_Api']
        self.Constellation_Api = config['Api_Server']['Constellation_Api']
        self.ThreatBook_Api = config['Api_Server']['ThreatBook_Api']
        self.Somd5_Md5_url = config['Api_Server']['Somd5_Md5_Api']
        self.Somd5_Key = config['Api_Server']['Api_Config']['Somd5_Key']
        self.Dream_Api = config['Api_Server']['Dream_Api']
        self.Port_Scan_Api = config['Api_Server']['Port_Scan_Api']
        # 星火配置
        self.Spark_url = config['Api_Server']['Ai_Config']['SparkApi']['Spark_url']
        self.Spark_ApiSecret = config['Api_Server']['Ai_Config']['SparkApi']['ApiSecret']
        self.Spark_Domain = config['Api_Server']['Ai_Config']['SparkApi']['Domain']
        self.Spark_ApiKey = config['Api_Server']['Ai_Config']['SparkApi']['ApiKey']
        self.Spark_Appid = config['Api_Server']['Ai_Config']['SparkApi']['Appid']
        # OpenAi配置
        self.OpenAi_Api = config['Api_Server']['Ai_Config']['Open_Ai']['OpenAi_Api']
        self.OpenAi_Key = config['Api_Server']['Ai_Config']['Open_Ai']['OpenAi_Key']
        self.OpenAi_Initiating_Message = config['Api_Server']['Ai_Config']['Open_Ai']['OpenAi_Role']
        self.messages = [{"role": "system", "content": f"{self.OpenAi_Initiating_Message}"}]
        self.system_copyright = config['System_Config']['System_Copyright']
        # 千帆配置
        self.qf_ak = config['Api_Server']['Ai_Config']['QianFan']['Qf_Access_Key']
        self.qf_sk = config['Api_Server']['Ai_Config']['QianFan']['Qf_Secret_Key']
        if self.qf_ak and self.qf_sk:
            self.chat_comp = qianfan.ChatCompletion(ak=self.qf_ak,
                                                    sk=self.qf_sk)
            self.chat_mess = qianfan.Messages()
        else:
            OutPut.outPut(f'[-]: 千帆模型未配置，请修改配置文件已启用模型！！！')

    # Ai功能
    def get_ai(self, question):
        OutPut.outPut("[*]: 正在调用Ai对话接口... ...")
        send_msgs = []

        def getText(role, content):
            jsonData = dict()
            jsonData["role"] = role
            jsonData["content"] = content
            send_msgs.append(jsonData)
            return send_msgs

        def getLength(text):
            length = 0
            for content in text:
                temp = content["content"]
                line = len(temp)
                length += line
            return length

        def checkLen(text):
            while getLength(text) > 8000:
                del text[0]
            return text

        # Gpt模型
        def getGpt(content):
            self.messages.append({"role": "user", "content": f'{content}'})
            data = {
                "model": "gpt-3.5-turbo",
                "messages": self.messages
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"{self.OpenAi_Key}",
            }
            try:
                resp = requests.post(url=self.OpenAi_Api, headers=headers, json=data, timeout=15)
                json_data = resp.json()
                assistant_content = json_data['choices'][0]['message']['content']
                self.messages.append({"role": "assistant", "content": f"{assistant_content}"})
                if len(self.messages) == 15:
                    self.messages = [{"role": "system", "content": f"{self.OpenAi_Initiating_Message}"}]
                return assistant_content
            except Exception as e:
                OutPut.outPut(f'[-]: AI对话接口出现错误，错误信息： {e}')
                self.messages = [{"role": "system", "content": f"{self.OpenAi_Initiating_Message}"}]
                return None

        # 星火大模型
        def get_xh(question):
            try:
                OutPut.outPut(f'[+]: 正在调用星火大模型... ...')
                question = checkLen(getText("user", question))
                SparkApi.answer = ""
                SparkApi.main(self.Spark_Appid, self.Spark_ApiKey, self.Spark_ApiSecret, self.Spark_url,
                              self.Spark_Domain,
                              question)
                getText("assistant", SparkApi.answer)
                Xh_Msg = SparkApi.get_content()
                return Xh_Msg
            except Exception as e:
                OutPut.outPut(f'[-]: 星火大模型出现错误，错误信息: {e}')
                return None

        # 千帆大模型
        def get_qf(quest):
            try:
                OutPut.outPut(f'[*]: 正在调用千帆大模型... ...')
                self.chat_mess.append(quest)
                resp = self.chat_comp.do(messages=self.chat_mess)
                self.chat_mess.append(resp)
                accept_msg = resp['body']['result']
                OutPut.outPut('[+]: Ai对话接口调用成功！！！')
                return accept_msg
            except Exception as e:
                OutPut.outPut(f'[-]: 千帆大模型出现错误，错误信息: {e}')
                return None

        gpt_msg = getGpt(content=question)
        if gpt_msg:
            OutPut.outPut('[+]: Ai对话接口调用成功！！！')
            return gpt_msg
        else:
            try:
                Xh_Msg = get_xh(question=question)
            except Exception as e:
                OutPut.outPut(f'[-]: 星火大模型出现错误，错误信息: {e}')
                return None
            if not Xh_Msg:
                if not self.qf_ak:
                    OutPut.outPut(f'[-]: 千帆模型接口未配置，其它模型出现错误，请查看日志！')
                    return '千帆模型接口未配置，其它模型出现错误，请查看日志！'
                return get_qf(quest=question)
            else:
                OutPut.outPut('[+]: Ai对话接口调用成功！！！')
                return Xh_Msg

    # 美女图片
    def get_girl_pic(self):
        OutPut.outPut(f'[*]: 正在调用美女图片接口... ...')
        url = random.choice(self.Pic_Apis)
        save_path = self.Cache_path + '/Pic_Cache/' + str(int(time.time() * 1000)) + '.jpg'
        try:
            pic_data = requests.get(url=url, headers=self.headers, timeout=30, verify=False).content
            with open(file=save_path, mode='wb') as pd:
                pd.write(pic_data)
        except Exception as e:
            msg = f'[-]: 美女图片API接口出现错误，错误信息：{e}\n正在回调中... ...'
            OutPut.outPut(msg)
            save_path = self.get_girl_pic()
        OutPut.outPut(f'[+]: 美女图片API接口调用成功！！！')
        return save_path

    # 美女视频
    def get_girl_video(self):
        OutPut.outPut('[*]: 正在调用美女视频API接口... ...')
        url = random.choice(self.Video_Apis)
        save_path = self.Cache_path + '/Video_Cache/' + str(int(time.time() * 1000)) + '.mp4'
        try:
            video_data = requests.get(url=url, headers=self.headers, timeout=90, verify=False).content
            with open(file=save_path, mode='wb') as vd:
                vd.write(video_data)
        except Exception as e:
            msg = f'[-]: 美女视频API接口出现错误，错误信息：{e}\n正在回调中... ...'
            OutPut.outPut(msg)
            save_path = self.get_girl_pic()
        OutPut.outPut(f'[+]: 美女视频API接口调用成功！！！')
        return save_path

    # 天气查询接口
    def query_weather(self, content):
        OutPut.outPut(f'[*]: 正在调用天气查询接口... ...')
        city = content.split(' ')[-1]
        try:
            json_data = requests.get(url=self.Weather_Api.format(self.Key, city), verify=False).json()
            alarm_msg = ''
            if json_data['code'] == 200:
                data = json_data['result']
                if data['alarmlist']:
                    alarm_lists = data['alarmlist']
                    for alarm in alarm_lists:
                        alarm_msg += f'{alarm["content"]}\n'
                msg = f'\n今日{data["weather"]}天：{data["week"]}\n日期：{data["date"]}\n当前温度：{data["real"]}\n最低温度：{data["lowest"]}\n风向：{data["wind"] + data["windsc"]}\n风速：{data["windspeed"]}\n日出：{data["sunrise"]}\n日落：{data["sunset"]}\n降水量：{data["pcpn"]}\n空气质量：{data["quality"]}\n天气预警：{alarm_msg if alarm_msg else "无"}\n{"By: #" + self.system_copyright if self.system_copyright else ""}'
                return msg
            OutPut.outPut(f'[+]: 天气查询API接口调用成功！！！')
            if json_data['code'] != 200:
                return '查询失败, 请重试 ~~~~~~'
        except Exception as e:
            msg = f'[-]: 天气查询API接口出现错误，错误信息：{e}'
            OutPut.outPut(msg)
            return msg

    # 舔狗日记
    def get_dog(self):
        OutPut.outPut('[*]: 正在调用舔狗日记API接口... ...')
        url = self.Dog_Api.format(self.Key)
        try:
            json_data = requests.get(url=url, headers=self.headers, timeout=20, verify=False).json()
            if json_data['code'] == 200 and json_data['msg'] == 'success':
                msg = json_data['result']['content'].strip()
            else:
                OutPut.outPut(f'[~]: 舔狗日记接口出了点小问题... ...')
                msg = self.get_dog()
        except Exception as e:
            msg = f'[-]: 舔狗日记API接口出现错误，错误信息：{e}'
            OutPut.outPut(msg)
            return msg
        OutPut.outPut(f'[+]: 舔狗日记API接口调用成功！！！')
        return msg

    # 星座查询
    def get_constellation(self, content):
        OutPut.outPut('[*]: 正在调用星座查询API接口... ...')
        constellation = content.split(' ')[-1]
        msg = ''
        if '座' not in constellation:
            constellation += '座'
        url = self.Constellation_Api.format(self.Key, constellation)
        try:
            json_data = requests.get(url=url, timeout=20, verify=False).json()
            if json_data['code'] != 200 and json_data['msg'] != 'success':
                msg = '星座查询错误, 请确保输入正确！'
                return msg
            for news in json_data['result']['list']:
                msg += news['type'] + '：' + news['content'] + '\n'
            msg = f'\n星座：{constellation}\n' + msg.strip() + f"\n{'By: #' + self.system_copyright if self.system_copyright else ''}"
            OutPut.outPut(f'[+]: 星座查询API接口调用成功！！！')
        except Exception as e:
            msg = f'[-]: 星座查询接口出现错误, 错误信息：{e}'
            OutPut.outPut(msg)
        return msg

    # 早安寄语
    def get_morning(self):
        OutPut.outPut('[*]: 正在调用早安寄语API接口... ...')
        url = self.Morning_Api.format(self.Key)
        try:
            json_data = requests.get(url=url, timeout=30, verify=False).json()
            if json_data['code'] != 200 and json_data['msg'] != 'success':
                msg = f'[~]: 早安寄语接口出现错误, 错误信息请查看日志 ~~~~~~'
                return msg
            content = json_data['result']['content']
            OutPut.outPut(f'[+]: 早安寄语API接口调用成功！！！')
            return content
        except Exception as e:
            msg = f'[-]: 早安寄语接口出现错误, 错误信息：{e}'
            OutPut.outPut(msg)

    # 摸鱼日记
    def get_fish(self):
        OutPut.outPut(f'[*]: 正在调用摸鱼日记接口... ...')
        save_path = self.Cache_path + '/Fish_Cache/' + str(int(time.time() * 1000)) + '.jpg'
        try:
            pic_data = requests.get(url=self.Fish_Api, headers=self.headers, timeout=30, verify=False).content
            with open(file=save_path, mode='wb') as pd:
                pd.write(pic_data)
        except Exception as e:
            msg = f'[-]: 摸鱼日记API接口出现错误，错误信息：{e}\n正在回调中... ...'
            OutPut.outPut(msg)
            save_path = self.get_fish()
        OutPut.outPut(f'[+]: 摸鱼日记API接口调用成功！！！')
        return save_path

    # Whois查询
    def get_whois(self, content):
        OutPut.outPut('[*]: 正在调用Whois查询API接口... ...')
        domain = content.split(' ')[-1]
        url = self.Whois_Api.format(domain)
        try:
            data = requests.get(url=url, timeout=30, verify=False).text
            if not data:
                msg = f'[~]: Whois查询接口出现错误, 错误信息请查看日志 ~~~~~~'
                return msg
            content = data.replace('<pre>', '').replace('</pre>',
                                                        '').strip() + f"\n{'By: #' + self.system_copyright if self.system_copyright else ''}"
            OutPut.outPut(f'[+]: Whois查询API接口调用成功！！！')
            return content
        except Exception as e:
            msg = f'[-]: Whois查询接口出现错误, 错误信息：{e}'
            OutPut.outPut(msg)

    # 归属地查询
    def get_attribution(self, content):
        OutPut.outPut('[*]: 正在调用归属地查询API接口... ...')
        phone = content.split(' ')[-1]
        url = self.Attribution_Api.format(phone)
        try:
            json_data = requests.get(url=url, timeout=30, verify=False).json()
            if not json_data["data"]["province"]:
                msg = f'[~]: 归属地查询接口出现错误, 错误信息请查看日志 ~~~~~~'
                return msg
            msg = f'\n===== 查询信息 =====\n手机号码: {phone}\n省份: {json_data["data"]["province"]}\n城市: {json_data["data"]["city"]}\n运营商: {json_data["data"]["sp"]}\n{"By: #" + self.system_copyright if self.system_copyright else ""}\n================='
            OutPut.outPut(f'[+]: 归属地查询API接口调用成功！！！')
            return msg
        except Exception as e:
            msg = f'[-]: 归属地查询接口出现错误, 错误信息：{e}'
            OutPut.outPut(msg)

    # 备案查询
    def get_icp(self, content):
        OutPut.outPut('[*]: 正在调用备案查询API接口... ...')
        domain = content.split(' ')[-1]
        url = self.Icp_Api.format(domain)
        try:
            json_data = requests.get(url=url, timeout=30, verify=False).json()
            if 'error' in json_data.keys():
                msg = f'此域名未备案！！！'
                return msg
            msg = f'======== 查询信息 ========\nICP备案号: {json_data["icp"]}\n备案主体: {json_data["unitName"]}\n备案类型: {json_data["natureName"]}\n{"By: #" + self.system_copyright if self.system_copyright else ""}\n========================'
            OutPut.outPut(f'[+]: 备案查询API接口调用成功！！！')
            return msg
        except Exception as e:
            msg = f'[-]: 备案查询接口出现错误, 错误信息：{e}'
            OutPut.outPut(msg)

    # 疯狂星期四文案
    def get_kfc(self):
        OutPut.outPut('[*]: 正在调用疯狂星期四文案API接口... ...')
        try:
            json_data = requests.get(url=self.Kfc_Api, timeout=30, verify=False).json()
            if json_data['code'] != 200:
                msg = '[~]: 疯狂星期四文案接口出现错误，具体原因请看日志 ~~~~~~'
                return msg
            msg = json_data['text']
            OutPut.outPut(f'[+]: 疯狂星期四文案API接口调用成功！！！')
            return msg
        except Exception as e:
            msg = f'[-]: 疯狂星期四文案接口出现错误, 错误信息：{e}'
            OutPut.outPut(msg)

    # 周公解梦
    def get_dream(self, content):
        OutPut.outPut('[*]: 正在调用周公解梦API接口... ...')
        dream = content.split(' ')[-1]
        url = self.Dream_Api.format(self.Key, dream)
        msg = ''
        try:
            json_data = requests.get(url=url, timeout=30, verify=False).json()
            if json_data['code'] != 200:
                msg = '你这梦太牛逼了, 解不了一点 ~~~~~~'
                return msg
            results = json_data['result']
            for result in results['list']:
                msg += f'类型: {result["type"]}\n解释: {result["result"].replace("<br>", ";")}\n'
            msg += "By: #" + self.system_copyright if self.system_copyright else ""
            OutPut.outPut(f'[+]: 周公解梦API接口调用成功！！！')
            return msg
        except Exception as e:
            msg = f'[-]: 周公解梦接口出现错误, 错误信息：{e}'
            OutPut.outPut(msg)

    # Md5查询
    def get_md5(self, content):
        ciphertext = content.strip().split(' ')[-1]
        OutPut.outPut('[*]: 正在调用MD5解密对话API接口... ...')
        try:
            resp = requests.get(url=self.Somd5_Md5_url.format(self.Somd5_Key, ciphertext), verify=False, timeout=10)
        except Exception as e:
            OutPut.outPut(f'[-]: MD5解密接口错误，错误信息：{e}')
            return f'[-]: MD5解密接口错误，错误信息：{e}'
        msg = f'\n======== MD5查询信息 =======\n密文: {ciphertext}\n明文: {resp.text}\n数据来源: #SOMD5\nBy: #{self.system_copyright if self.system_copyright else ""}\n========================'
        return msg

    # 微步IP查询
    def get_threatbook_ip(self, content):
        ip = content.split(' ')[-1]
        OutPut.outPut(f'[*]: 正在调用微步IP查询API接口... ...')
        if len(content) > 0 and ip:
            search_ip = ip
            ips = str(search_ip).split('.')
            continuous_bool = True if [i for i in ips if ips[0] != i] else False
            if ips[0] in ['127', '192', '0', '224', '240', '255'] or \
                    search_ip in ['1.1.1.1', '2.2.2.2', '3.3.3.3', '4.4.4.4', '5.5.5.5', '6.6.6.6', '7.7.7.7',
                                  '8.8.8.8', '9.9.9.9', '10.10.10.10'] or \
                    '.'.join(ips[0:2]) in ['169.254', '100.64', '198.51', '198.18', '172.16'] or \
                    '.'.join(ips[0:3]) in ['203.0.113'] or \
                    ips[-1] in ['255', '254']:
                msg = "[微笑]暂不支持查询该地址!"
                return msg
            if not continuous_bool:
                msg = "[微笑]暂不支持查询该地址!"
                return msg
            try:
                data = {
                    "apikey": self.ThreatBook_Key,
                    "resource": search_ip,
                }

                resp = requests.post(
                    self.ThreatBook_Api,
                    data=data,
                    timeout=10,
                    verify=False,
                )
                if resp.status_code == 200 and resp.json()["response_code"] == 0:
                    # 查风险等级
                    sec_level = resp.json()["data"]["{}".format(search_ip)]["severity"]
                    # 查是否恶意IP
                    is_malicious = resp.json()["data"]["{}".format(search_ip)]["is_malicious"]
                    # 查可信度
                    confidence_level = resp.json()["data"]["{}".format(search_ip)]["confidence_level"]
                    # 查IP归属国家
                    country = resp.json()["data"]["{}".format(search_ip)]["basic"]["location"][
                        "country"
                    ]
                    # 查IP归属省份
                    province = resp.json()["data"]["{}".format(search_ip)]["basic"]["location"][
                        "province"
                    ]
                    # 查IP归属城市
                    city = resp.json()["data"]["{}".format(search_ip)]["basic"]["location"]["city"]
                    # 将IP归属的国家、省份、城市合并成一个字符串
                    location = country + "-" + province + "-" + city
                    # 查威胁类型
                    judgments = ""
                    for j in resp.json()["data"]["{}".format(search_ip)]["judgments"]:
                        judgments += j + " "
                    if is_malicious:
                        is_malicious_msg = "是"
                    else:
                        is_malicious_msg = "否"
                    msg = f"\n===================\n[+]ip：{search_ip}\n[+]风险等级：{sec_level}\n[+]是否为恶意ip：{is_malicious_msg}\n[+]可信度：{confidence_level}\n[+]威胁类型：{str(judgments)}\n[+]ip归属地：{location}\n更新时间：{resp.json()['data']['{}'.format(search_ip)]['update_time']}\n{'By: #' + self.system_copyright if self.system_copyright else ''}\n==================="
                else:
                    msg = f"[-]: 查询失败，返回信息：{resp.json()['verbose_msg']}"
                    OutPut.outPut(msg)
            except Exception as e:
                OutPut.outPut(f"[-]: 微步IP查询出错，错误信息：{e}")
                msg = f"[-]: 查询出错请稍后重试，错误信息：{e}"
            return msg

    # 端口查询
    def get_portScan(self, content):
        ip = content.split(' ')[-1]
        OutPut.outPut(f'[*]: 正在调用端口查询API接口... ...')
        ports_info = ""
        msg = ''
        try:
            json_data = requests.get(url=self.Port_Scan_Api.format(ip)).json()
            for port in json_data['ports']:
                port_info = '{}-{}-{}'.format(port['port'], port['base_protocol'], port['protocol'])
                ports_info += port_info + "\n"
            msg = f'\n=====端口开放情况=====\nIP地址: {json_data["ip"]}\n{ports_info}{"By: #" + self.system_copyright if self.system_copyright else ""}\n================'
        except Exception as e:
            OutPut.outPut(f'[-]: 端口查询API接口出现错误，错误信息: {e}')
        if msg:
            return msg
        else:
            return '端口查询失败, 具体原因请看日志... ...'

    # 早报
    def get_freebuf_news(self, ):
        yesterday = (datetime.date.today() + datetime.timedelta(-1))
        morning_time = yesterday.strftime("%a, %d %b %Y", )
        str_list = "#FreeBuf早报\n"
        try:
            rs1 = feedparser.parse('https://www.freebuf.com/feed')
            for ent in rs1['entries']:
                if morning_time in ent['published']:
                    title = ent['title']
                    link = ent['link']
                    str_list += '\n' + title + '\n' + link + '\n'
            if 'http' not in str_list:
                str_list += '\n今日暂无文章'
        except Exception as e:
            link6 = "\n今日暂无文章"
            str_list += link6
            OutPut.outPut("[-]: 获取FreeBuf早报出错，错误信息： {}".format(e))
        str_list += f"\n{self.system_copyright + '整理分享，更多内容请戳 #' + self.system_copyright if self.system_copyright else ''}\n{time.strftime('%Y-%m-%d %X')}"
        return str_list

    # 获取先知社区文章
    def get_xz_news(self, news_list):
        news_list = "#先知社区"
        try:
            rs1 = feedparser.parse('https://xz.aliyun.com/feed')
            for ent in rs1['entries']:
                if str(time.strftime('%Y-%m-%d')) in ent['published']:
                    title = ent['title']
                    link = ent['link']
                    news_list += '\n' + title + '\n' + link + '\n'
            if 'http' not in news_list:
                news_list += '\n今日暂无文章\n'
        except Exception as e:
            link6 = "\n今日暂无文章\n"
            news_list += link6
            OutPut.outPut("[-]: 获取先知社区文章出错，错误信息: {}".format(e))
        return news_list

    # 获取奇安信攻防社区文章
    def get_qax_news(self, news_list):
        news_list += "\n#奇安信攻防社区"
        try:
            rs1 = feedparser.parse('https://forum.butian.net/Rss')
            for ent in rs1['entries']:
                if str(time.strftime('%Y-%m-%d')) in ent['published']:
                    title = ent['title']
                    link = ent['link']
                    news_list += '\n' + title + '\n' + link + '\n'
            if 'http' not in news_list:
                news_list += '\n今日暂无文章\n'
        except Exception as e:
            link6 = "\n今日暂无文章\n"
            news_list += link6
            OutPut.outPut("[-]: 获取奇安信攻防社区文章出错，错误信息: {}".format(e))
        return news_list

    # 获取安全客文章
    def get_anquanke_news(self, news_list):
        news_list += "\n#安全客"
        try:
            resp = requests.get('https://www.anquanke.com/knowledge', timeout=5, verify=False)
            tree = etree.HTML(resp.text)
            divs = tree.xpath('//div[@class="article-item common-item"]/div')
            for div in divs:
                href = urljoin('https://www.anquanke.com/knowledge', div.xpath('.//div[@class="title"]/a/@href')[0])
                title = div.xpath('.//div[@class="title"]/a/text()')[0].strip()
                publish_time = div.xpath('.//span[@style="vertical-align: middle;"]/text()')[1]
                if str(time.strftime('%Y-%m-%d')) in publish_time:
                    news_list += '\n' + title + '\n' + href + '\n'
            if 'http' not in news_list:
                news_list += '\n今日暂无文章\n'
        except Exception as e:
            link6 = "\n今日暂无文章\n"
            news_list += link6
            OutPut.outPut("[-]: 获取安全客文章出错，错误信息: {}".format(e))
        return news_list

    # 获取各平台安全文章
    def get_safety_news(self, ):
        news_list = ''
        OutPut.outPut("[+]:正在爬取安全新闻... ...")
        news_list = self.get_xz_news(news_list)
        news_list = self.get_qax_news(news_list)
        news_list = self.get_anquanke_news(news_list)
        OutPut.outPut("[+]:获取各平台安全文章成功！！！")
        news_list += f"\n{self.system_copyright + '整理分享，更多内容请戳 #' + self.system_copyright if self.system_copyright else ''}\n{time.strftime('%Y-%m-%d %X')}"
        return news_list.strip()


if __name__ == '__main__':
    Ams = Api_Main_Server(1)
    # Ams.query_weather('天气查询 南昌')
    # print(Ams.get_dog())
    # Ams.get_constellation('运势查询 白羊')
    # print(Ams.get_morning())
    # print(Ams.get_whois('whois查询 qq.com'))
    # print(Ams.get_attribution('归属查询 121264'))
    # print(Ams.get_icp('备案查询 qzzz2131231q.com'))
    print(Ams.get_dream('解梦 淹死'))
