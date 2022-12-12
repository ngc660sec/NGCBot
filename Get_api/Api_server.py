from Output.output import output
import requests
import urllib3
import random
import yaml
import time
import os
import re


class Api_server:
    def __init__(self):
        # 忽略HTTPS告警
        urllib3.disable_warnings()

        # 读取配置文件
        current_path = os.path.dirname(__file__)
        config = yaml.load(open(current_path + '/../config/config.yaml', encoding='UTF-8'), yaml.Loader)
        self.appid = config['APPID']
        self.appsecret = config['APPSECRET']
        self.key = config['KEY']
        self.girl_video_urls = config['GIRL_VIDEO_URLS']
        self.girl_pic_urls = config['GIRL_PIC_URLS']
        self.attribution_url = config['ATTRIBUTION_URL']
        self.whois_url = config['WHOIS_URL']
        self.weather_url = config['WEATHER_URL']
        self.lick_dog_url = config['LICK_DOG_URL']
        self.horoscope_url = config['HOROSCOPE_URL']
        self.good_morning_url = config['GOOD_MORNING_MESSAGE_URL']
        self.icp_url = config['ICP_URL']
        self.touch_fish_calendar_url = config['TOUCH_FISH_CALENDAR']
        self.threatbook_url = config['THREATBOOK_URL']
        self.threatbook_key = config['THREATBOOK_KEY']
        self.extensions_url = config['EXTENSIONS_URL']
        self.xiaoai_url = config['XIAOAI_URL']
        self.Key_Response = config['KEY_RESPONSE']

        # 获取系统消息配置
        self.system_message_configuration = config['MESSAGE_CONFIGURATION']
        # 获取版权信息
        self.copyright_mes = self.system_message_configuration['COPYRIGHT_MESSAGE']

    # 获取美女图片接口
    def get_girl_pic(self):
        output("[*] >> 正在调用美女图片API接口... ...")
        girl_pic_url = random.choice(self.girl_pic_urls)
        # print(girl_url)
        try:
            resp = requests.get(
                url=girl_pic_url,
                timeout=5,
                verify=False,
            )
            if resp.status_code == 200:
                path = os.path.abspath("./File/girl_pic/")
                img_name = int(time.time() * 1000)
                # 以时间轴的形式给图片命名
                with open(f"{path}\\{img_name}.jpg", "wb+") as f:
                    # 写入文件夹
                    f.write(resp.content)
                    # 关闭文件夹
                    f.close()
                video_path = os.path.abspath(f"{path}\\{img_name}.jpg")
                msg = video_path.replace("\\", "\\\\")
            else:
                msg = "[ERROR] >> 美女图片接口调用超时..."
        except Exception as e:
            msg = "[ERROR] >> 美女图片接口调用出错，错误信息：{}".format(e)
        return msg

    # 美女视频调用
    def get_girl_vedio(self):
        output("[*] >> 正在调用美女视频API接口... ...")
        girl_video_url = random.choice(self.girl_video_urls)
        # print(girl_video_url)
        try:
            resp = requests.get(girl_video_url, timeout=5, verify=False)
            if resp.status_code == 200:
                videos_url = re.findall(
                    '<video src="(.*?)" muted controls preload="auto"', resp.text, re.S
                )
                if len(videos_url) > 0:
                    url = "http:" + str(videos_url[0])
                    resp1 = requests.get(url, timeout=5, verify=False)
                    path = os.path.abspath("./file/girl_video/")
                    videos_name = int(time.time() * 1000)
                    # 以时间轴的形式给图片命名
                    with open(f"{path}\\{videos_name}.mp4", "wb+") as f:
                        # 写入文件夹
                        f.write(resp1.content)
                        # 关闭文件夹
                        f.close()
                    video_path = os.path.abspath(f"{path}\\{videos_name}.mp4")
                    msg = video_path.replace("\\", "\\\\")

                elif 'cysir.cn' not in girl_video_url:
                    resp = requests.get(url=girl_video_url).json()
                    url = ('http:' + resp['mp4']).replace(' ', '%20')
                    resp1 = requests.get(url, timeout=5, verify=False)
                    path = os.path.abspath("./file/girl_video/")
                    videos_name = int(time.time() * 1000)
                    # 以时间轴的形式给图片命名
                    with open(f"{path}\\{videos_name}.mp4", "wb+") as f:
                        # 写入文件夹
                        f.write(resp1.content)
                        # 关闭文件夹
                        f.close()
                    video_path = os.path.abspath(f"{path}\\{videos_name}.mp4")
                    msg = video_path.replace("\\", "\\\\")
                else:
                    msg = "[ERROR] >> 调用图片API出错，错误信息：未识别到URL连接"
                    output(msg)
            else:
                msg = "[ERROR] >> 站点状态异常，访问请求：{}".format(resp.status_code)
        except Exception as e:
            msg = "[ERROR] >> 视频接口调用出错，错误信息：{}".format(e)
        return msg

    # 归属地查询调用
    def get_attribution(self, keyword):
        output("[*] >> 正在调用归属地查询API接口......")
        try:
            phone = keyword.split(' ')[1]
            try:
                resp = requests.get(self.attribution_url.format(phone), verify=False).json()
                # print(resp)
                if resp['data']['sp']:
                    msg = f"\n===== 查询信息 =====\n手机号码: {phone}\n省份: {resp['data']['province']}\n城市: {resp['data']['city']}\n运营商: {resp['data']['sp']}\nBy #NGC660安全实验室\n================="
                    return msg
                else:
                    msg = '手机号码错输入错误!'
                    return msg
            except Exception as e:
                output("[ERROR] >> 归属地查询接口访问异常，异常信息：{}".format(e))
                msg = "归属地查询接口访问异常，异常信息： {}".format(e)
                return msg
        except Exception as e:
            output("[ERROR] >> 归属地查询接口调用出错，错误信息：{}".format(e))
            msg = "语法格式: \n [*]>> 归属查询 手机号"
            return msg

    # WHOIS查询调用
    def get_whois(self, keyword):
        output("[*] >> 正在调用WHOIS查询接口... ...")
        try:
            domain = keyword.split(' ')[1]
            try:
                resp = requests.get(url=self.whois_url.format(domain))
                domain_text = resp.text.split('For more information on Whois status codes')[0].replace('<pre>',
                                                                                                       '').replace(
                    '</pre>', '').strip()
                msg = "\n" + domain_text + f"\n>>> By #{self.copyright_mes}"
                return msg
            except Exception as e:
                output("[ERROR] >> WHOIS查询接口调用异常，错误信息：{}".format(e))
                msg = "WHOIS查询接口调用异常!"
                return msg
        except Exception as e:
            output("[ERROR] >> WHOIS查询接口调用异常，错误信息：{}".format(e))
            msg = "语法格式: \n [+] >> whois查询 domain"
            return msg

    # 天气查询调用
    def get_wether(self, keyword):
        output("[*] 正在调用天气查询接口... ...")
        try:
            city = keyword
            keys = [key for key in self.Key_Response['WETHER']['KEY1']] + [key for key in
                                                                           self.Key_Response['WETHER']['KEY2']]
            for key in keys:
                word = city.replace(key, '')
                city = word
            if not city:
                msg = "语法格式: \n[+] >> 查询XX天气"
                return msg
            resp = requests.get(self.weather_url.format(self.appid, self.appsecret, city), timeout=5, verify=False)
            if resp.status_code == 200 and "errcode" not in resp.text:
                msg = f'\n今日{city}的天气\n日期：{resp.json()["date"]}\n当前温度：{resp.json()["tem"]}\n最高气温：{resp.json()["tem_day"]}\n最低气温：{resp.json()["tem_night"]}\n风向：{resp.json()["win"]}\n风速：{resp.json()["win_meter"]}\n天气：{resp.json()["wea"]}\n湿度：{resp.json()["humidity"]}\n\nBy #NGC660安全实验室\n[+]更新时间：{resp.json()["update_time"]}'
            elif "errcode" in resp.text and resp.json()["errcode"] == 100:
                output(f'天气查询接口出错，请稍后重试,接口状态{resp.json()["errmsg"]}')
                msg = resp.json()["errmsg"].replace("city", "城市中")
            else:
                msg = f"天气查询接口出错，请稍后重试,接口状态{resp.status_code}"

        except Exception as e:
            output(f"[ERROR] >> 天气查询接口调用出错，错误信息：{e}")
            msg = "天气查询接口出错，ERROR:{}".format(e)
        return msg

    # 舔狗日记调用
    def get_licking_dog_Diary(self):
        output("[*] >> 正在调用舔狗日记接口... ...")
        try:
            resp = requests.get(
                self.lick_dog_url.format(self.key),
                timeout=5,
                verify=False,
            )
            if resp.status_code == 200 and resp.json()["code"] == 200:
                msg = resp.json()["newslist"][0]["content"]
            else:
                msg = "[+] >> 舔狗日记接口调用超时!"
        except Exception as e:
            msg = "[ERROR] >> 舔狗日记接口调用出错，错误信息：{}".format(e)
            output(msg)
        return msg

    # 星座运势调用
    def get_horoscope(self, keyword):
        output("[*] >> 正在调用星座运势查询接口... ...")
        try:
            constellation = keyword
            keys = [key for key in self.Key_Response['HOROSCOPE']['KEY1']] + [key for key in
                                                                              self.Key_Response['HOROSCOPE']['KEY2']]
            for key in keys:
                word = constellation.replace(key, '')
                constellation = word
            if '座' not in constellation:
                constellation += '座'
            if len(constellation) < 2:
                msg = "语法格式: \n[+] >> 查询XX运势"
                return msg
            resp = requests.get(
                self.horoscope_url.format(self.key, constellation),
                timeout=5,
                verify=False,
            )
            if resp.status_code == 200 and resp.json()["code"] == 200:
                msg = f"\n星座：{constellation}"
                for i in range(0, len(resp.json()["newslist"])):
                    msg += f"\n{resp.json()['newslist'][i]['type']}：{resp.json()['newslist'][i]['content']}"
            else:
                msg = f"[ERROR] >> 接口请求请求异常，错误信息：{resp.json()['msg']}"
                output(msg)

        except Exception as e:
            output(f"[ERROR] >> 星座运势接口调用出错，错误信息：{e}")
            msg = f"星座运势接口调用出错，错误信息：{e}"
        return msg

    # 早安寄语调用
    def get_good_morning_message(self):
        try:
            resp = requests.get(url=self.good_morning_url.format(self.key)).json()
            if resp['code'] == 200 and resp['msg'] == 'success':
                msg = f"{resp['result']['content']}"
                return msg
        except Exception as e:
            msg = "[ERROR] >> 接口请求异常，错误信息：{}".format(e)
            output(msg)

    # ICP调用
    def get_icp(self, keyword):
        try:
            domain = keyword.split(' ')[1]
            try:
                resp = requests.get(url=self.icp_url.format(domain)).json()
                if resp['icp'] == '未备案':
                    msg = '该域名未备案!'
                elif '频率过高' in resp['icp']:
                    msg = resp['icp']
                else:
                    msg = f'\n===== 查询信息 =====\nICP备案号: {resp["icp"]}\n备案主体: {resp["name"]}\n备案类型: {resp["tyle"]}\nBy #{self.copyright_mes}\n================='
                return msg
            except Exception as e:
                msg = '[ERROR] >> 接口请求异常，错误信息：{}'.format(e)
                output(msg)
                return msg
        except Exception as e:
            msg = f"语法格式: \n [+] >>> icp查询 domain"
            output('[ERROR] >> 接口调用出错，错误信息：{}'.format(e))
            return msg

    # 摸鱼日历调用
    def get_touch_fish_calendar(self, ):
        output("[*] >> 正在调用摸鱼日历接口... ...")
        try:
            resp = requests.get(url=self.touch_fish_calendar_url, timeout=10)
            path = os.path.abspath("./file/touch_fish/")
            touch_fish_name = int(time.time() * 1000)
            # 以时间轴的形式给图片命名
            with open(f"{path}\\{touch_fish_name}.png", "wb+") as f:
                # 写入文件夹
                f.write(resp.content)
                # 关闭文件夹
                f.close()
            video_path = os.path.abspath(f"{path}\\{touch_fish_name}.png")
            msg = video_path.replace("\\", "\\\\")
        except Exception as e:
            msg = "[ERROR] >> 摸鱼日历接口调用超时，错误信息：{}".format(e)
            output(msg)
        return msg

    # 微步查询调用
    def get_threatbook_ip(self, keyword):
        ip_list = keyword
        keys = [key for key in self.Key_Response['THREAT_BOOK']['KEY1']] + [key for key in
                                                                            self.Key_Response['THREAT_BOOK']['KEY2']]
        for key in keys:
            word = ip_list.replace(key, '')
            ip_list = word
        reg = "((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}"
        ip_result = re.match(reg, ip_list.replace(' ', '').strip())
        if ip_result is None:
            msg = "语法格式: \n [+] >>> ip查询 ip"
            return msg
        elif len(ip_list) > 0 and ip_result.group():
            search_ip = ip_result.group()
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
                    "apikey": self.threatbook_key,
                    "resource": search_ip,
                }

                resp = requests.post(
                    self.threatbook_url,
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
                    msg = f"\n===================\n[+]ip：{search_ip}\n[+]风险等级：{sec_level}\n[+]是否为恶意ip：{is_malicious_msg}\n[+]可信度：{confidence_level}\n[+]威胁类型：{str(judgments)}\n[+]ip归属地：{location}\n更新时间：{resp.json()['data']['{}'.format(search_ip)]['update_time']}\n==================="
                else:
                    msg = f"查询失败，返回信息：{resp.json()['verbose_msg']}"
                    output(f"[ERROR] >> 查询失败，返回信息：{msg}")
            except Exception as e:
                output(f"[ERROR] >> 微步IP查询出错，错误信息：{e}")
                msg = f"查询出错请稍后重试，错误信息：{e}"
            return msg

    # 扩展名查询调用
    def get_extensions(self, keyword):
        output("[*] >> 正在调用扩展名查询接口... ...")
        msg = ''
        try:
            word = keyword.split(' ')[1]
            url = self.extensions_url.format(self.key, word)
            try:
                resp = requests.get(url=url).json()
                if resp['code'] == 250:
                    msg = f"查询失败，{resp['msg']}"
                    return msg
                if resp['code'] == 200 and resp['msg'] == 'success':
                    msg = f'\n=== 查询后缀 {resp["result"]["targa"].upper()} ===\n {resp["result"]["notes"]}'
            except Exception as e:
                msg = "[ERROR] >> 接口调用超时，错误信息：{}".format(e)
                output(msg)
        except Exception as e:
            msg = "语法格式: \n [+] >>> 后缀查询 后缀名"
            output("[ERROR] >> 扩展名接口调用出错，错误信息：{}".format(e))
        return msg

    # 小爱AI对话调用
    def get_xiaoai_msg(self, keyword):
        try:
            resp = requests.get(self.xiaoai_url.format(keyword)).text
            if not resp.strip():
                msg = '[Doge]小爱听不懂你在说什么'
                return msg
            msg = resp.strip()
            return msg
        except Exception as e:
            msg = '[ERROR] >> 接口调用错误，错误信息 {}'.format(e)
            output(msg)

