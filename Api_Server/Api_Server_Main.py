from Output.output import output
import feedparser
import requests
import urllib3
import random
import time
import yaml
import os
import re


class Api_Server_Main:
    def __init__(self):
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

        # 配置文章变量
        self.news_list = ''

        # 读取配置文件
        config = yaml.load(open(current_path + '/../Config/config.yaml', encoding='UTF-8'), yaml.Loader)
        self.appid = config['Api_Server']['Api_Config']['Appid']
        self.appsecret = config['Api_Server']['Api_Config']['Appsecret']
        self.key = config['Api_Server']['Api_Config']['Key']
        self.threatbook_key = config['Api_Server']['Api_Config']['ThreatBook_Key']

        self.pic_apis = config['Api_Server']['Pic_Api']
        self.video_apis = config['Api_Server']['Video_Api']
        self.icp_api = config['Api_Server']['Icp_Api']
        self.extensions_api = config['Api_Server']['Extensions_Api']
        self.attribution_api = config['Api_Server']['Attribution_Api']
        self.whois_api = config['Api_Server']['Whois_Api']
        self.fish_api = config['Api_Server']['Fish_Api']
        self.wether_api = config['Api_Server']['Wether_Api']
        self.dog_api = config['Api_Server']['Dog_Api']
        self.constellation_api = config['Api_Server']['Constellation_Api']
        self.morning_api = config['Api_Server']['Morning_Api']
        self.threatbook_url = config['Api_Server']['ThreatBook_Api']

    # AI对话接口
    def get_ai(self, keyword):
        url = 'https://v.api.aa1.cn/api/api-xiaoai/talk.php?msg={keyword}&type=text'.format(keyword=keyword)
        try:
            msg = requests.get(url=url, headers=self.headers).text.strip()
        except Exception as e:
            msg = f'[ERROR]:AI对话接口错误，错误信息：{e}'
        return msg

    # 美女图片接口
    def get_pic(self):
        output('[-]:正在调用美女图片API接口... ...')
        url = random.choice(self.pic_apis)
        try:
            pic_data = requests.get(url=url, headers=self.headers, timeout=30).content
            save_path = self.Cache_path + '/Pic_Cache/' + str(int(time.time() * 1000)) + '.jpg'
            with open(file=save_path, mode='wb') as pd:
                pd.write(pic_data)
        except Exception as e:
            msg = f'[ERROR]:美女图片API接口出现错误，错误信息：{e}'
            output(msg)
            return msg
        return save_path

    # 美女视频接口
    def get_video(self):
        output('[-]:正在调用美女视频API接口... ...')
        url = random.choice(self.video_apis)
        try:
            try:
                src = requests.get(url=url, headers=self.headers).json()['mp4']
            except requests.exceptions.JSONDecodeError:
                src = re.findall('src="(.*?)"', requests.get(url=url, headers=self.headers, timeout=20).text)[0]
            mp4_url = 'http:' + src
            video_data = requests.get(url=mp4_url, headers=self.headers).content
            save_path = self.Cache_path + '/Video_Cache/' + str(int(time.time() * 1000)) + '.mp4'
            with open(file=save_path, mode='wb') as vd:
                vd.write(video_data)
        except Exception as e:
            msg = f'[ERROR]:美女视频API接口出现错误，错误信息：{e}'
            output(msg)
            return msg
        return save_path

    # 备案查询接口
    def get_icp(self, keyword):
        try:
            domain = re.findall(r' (\w+.\w+)', keyword)[0]
        except Exception as e:
            msg = '语法格式:\nICP查询 qq.com'
            output(f'[ERROR]:备案查询接口出现错误，错误信息：{e}')
            return msg
        url = self.icp_api.format(domain)
        try:
            data = requests.get(url=url, headers=self.headers, timeout=10).json()
        except Exception as e:
            msg = f'[ERROR]:备案查询接口超时，错误信息：{e}'
            output(msg)
            return msg
        if data['icp'] == '未备案':
            return '该域名未备案!'
        msg = f'======== 查询信息 ========\nICP备案号:{data["icp"]}\n备案主体:{data["name"]}\n备案类型:{data["tyle"]}\n{"By: #" + self.system_copyright if self.system_copyright else ""}\n========================'
        return msg.strip()

    # 后缀名查询接口
    def get_suffix(self, keyword):
        try:
            word = re.findall(r' (\w+)', keyword)[0]
        except Exception as e:
            msg = '语法格式:\n后缀名查询 EXE'
            output(f'\n[ERROR]:后缀名查询接口出现错误，错误信息：{e}')
            return msg
        url = self.extensions_api.format(self.key, word)
        try:
            data = requests.get(url=url, headers=self.headers).json()
        except TimeoutError as e:
            msg = f'\n[ERROR]:后缀名查询接口超时，错误信息：{e}'
            output(msg)
            return msg
        if data['code'] != 200:
            msg = '查询结果为空!'
        else:
            msg = f'\n======== 查询后缀:{word} ========\n查询结果:{data["result"]["notes"]}\n{"By: #" + self.system_copyright if self.system_copyright else ""}\n============================'
        return msg

    # 归属地查询
    def get_attribution(self, keyword):
        try:
            phone = re.findall(r' (\d+)', keyword)[0]
        except Exception as e:
            msg = '语法格式:\n归属查询 110'
            output(f'\n[ERROR]:归属查询接口出现错误，错误信息：{e}')
            return msg
        url = self.attribution_api.format(phone)
        try:
            data = requests.get(url=url, headers=self.headers).json()
        except TimeoutError as e:
            msg = f'\n[ERROR]:归属查询接口超时，错误信息：{e}'
            output(msg)
            return msg
        if not data['data']['province']:
            msg = '查询结果为空!'
        else:
            msg = f'\n===== 查询信息 =====\n手机号码:{phone}\n省份:{data["data"]["province"]}\n城市:{data["data"]["city"]}\n运营商:{data["data"]["sp"]}\n{"By: #" + self.system_copyright if self.system_copyright else ""}\n================='
        return msg

    # Whois查询接口
    def get_whois(self, keyword):
        try:
            domain = re.findall(r' (\w+.\w+)', keyword)[0]
        except Exception as e:
            msg = '语法格式:\nWHOIS查询 qq.com'
            output(f'[ERROR]:WHOIS查询接口出现错误，错误信息：{e}')
            return msg
        url = self.whois_api.format(domain)
        try:
            source_data = requests.get(url=url, headers=self.headers).text
        except TimeoutError as e:
            msg = f'\n[ERROR]:WHOIS查询接口超时，错误信息：{e}'
            output(msg)
            return msg
        msg = '\n' + source_data.strip().split('For more information')[0].strip('<pre>').strip() + f"\n{'By: #' + self.system_copyright if self.system_copyright else ''}"
        return msg

    # 微步ip查询接口
    def get_threatbook_ip(self, keyword):
        try:
            keyword = keyword.split(' ')[-1]
        except Exception as e:
            output(f'[ERROR]:微步ip查询接口出现错误，错误信息：{e}')
        reg = r"((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}"
        ip_result = re.match(reg, keyword.replace(' ', '').strip())
        if ip_result is None:
            msg = "语法格式: \nIP查询 xx.xx.xx.xx"
            return msg
        elif len(keyword) > 0 and ip_result.group():
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
                    msg = f"\n===================\n[+]ip：{search_ip}\n[+]风险等级：{sec_level}\n[+]是否为恶意ip：{is_malicious_msg}\n[+]可信度：{confidence_level}\n[+]威胁类型：{str(judgments)}\n[+]ip归属地：{location}\n更新时间：{resp.json()['data']['{}'.format(search_ip)]['update_time']}\n{'By: #' + self.system_copyright if self.system_copyright else ''}\n==================="
                else:
                    msg = f"[ERROR]:查询失败，返回信息：{resp.json()['verbose_msg']}"
                    output(msg)
            except Exception as e:
                output(f"[ERROR]:微步IP查询出错，错误信息：{e}")
                msg = f"[ERROR]:查询出错请稍后重试，错误信息：{e}"
            return msg

    # 摸鱼日记接口
    def get_fish(self):
        output('[-]:正在调用摸鱼日记API接口... ...')
        try:
            pic_data = requests.get(url=self.fish_api, headers=self.headers, timeout=10).content
            save_path = self.Cache_path + '/Fish_Cache/' + str(int(time.time() * 1000)) + '.jpg'
            with open(file=save_path, mode='wb') as pd:
                pd.write(pic_data)
        except Exception as e:
            msg = f'[ERROR]:摸鱼日记API接口出现错误，错误信息：{e}'
            output(msg)
            return msg
        return save_path

    # 天气查询接口
    def get_wether(self, keyword):
        try:
            city = re.findall(r' (\w+)', keyword)[0]
        except Exception as e:
            msg = '语法格式:\n天气查询 北京'
            output(f'\n[ERROR]:天气查询接口出现错误，错误信息：{e}')
            return msg
        url = self.wether_api.format(self.appid, self.appsecret, city)
        try:
            data = requests.get(url=url, headers=self.headers).json()
        except TimeoutError as e:
            msg = f'\n[ERROR]:天气查询接口超时，错误信息：{e}'
            output(msg)
            return msg
        try:
            if city != data['city']:
                msg = f'城市中不存在：{data["city"]}'
                return msg
            else:
                msg = f'\n今日{data["city"]}天气：{data["wea"]}\n日期：{data["date"]}\n当前温度：{data["tem"]}\n最低温度：{data["tem_day"]}\n风向：{data["win"] + data["win_speed"]}\n风速：{data["win_meter"]}\n湿度：{data["humidity"]}\n{"By: #" + self.system_copyright if self.system_copyright else ""}'
                return msg
        except Exception as e:
            output(f'[ERROR]:天气查询接口出现错误出现错误，错误信息：{e}')
            msg = f'城市中不存在：{city}'
            return msg

    # 舔狗日记
    def get_dog(self):
        url = self.dog_api.format(self.key)
        try:
            data = requests.get(url=url, headers=self.headers).json()
        except TimeoutError as e:
            msg = f'\n[ERROR]:舔狗日记接口超时，错误信息：{e}'
            output(msg)
            return msg
        try:
            msg = data['newslist'][0]['content'].strip()
        except Exception as e:
            msg = f'[ERROR]:舔狗日记接口出现错误出现错误，错误信息：{e}'
            output(msg)
        return msg

    # 星座查询接口
    def get_constellation(self, keyword):
        msg = ''
        try:
            constellation = re.findall(r' (\w+)', keyword)[0]
            if '座' not in constellation:
                constellation += '座'
        except Exception as e:
            msg = '语法格式:\n星座查询 白羊座'
            output(f'\n[ERROR]:星座查询接口出现错误，错误信息：{e}')
            return msg
        url = self.constellation_api.format(self.key, constellation)
        try:
            data = requests.get(url=url, headers=self.headers).json()
        except TimeoutError as e:
            msg = f'\n[ERROR]:星座查询接口超时，错误信息：{e}'
            output(msg)
            return msg
        for news in data['newslist']:
            msg += news['type'] + '：' + news['content'] + '\n'
        msg = f'\n星座：{constellation}\n' + msg.strip() + f"\n{'By: #' + self.system_copyright if self.system_copyright else ''}"
        return msg

    # 早安寄语
    def get_morning(self):
        url = self.morning_api.format(self.key)
        try:
            data = requests.get(url=url, headers=self.headers).json()
        except TimeoutError as e:
            msg = f'\n[ERROR]:早安寄语接口超时，错误信息：{e}'
            output(msg)
            return msg
        msg = f'{data["result"]["content"]}'
        return msg

    # 早报推送
    def get_freebuf_news(self, ):
        str_list = "#FreeBuf早报\n"
        try:
            rs1 = feedparser.parse('https://www.freebuf.com/feed')
            length = len(rs1.entries)
            for buf in range(length):
                try:
                    if (
                            f'tm_year={time.strftime("%Y")}'
                            in str(rs1.entries[buf]["published_parsed"])
                            and f'tm_mon={time.strftime("%m")}'
                            in str(rs1.entries[buf]["published_parsed"])
                            and f'tm_mday={str(int(time.strftime("%d")) - 1)}'
                            in str(rs1.entries[buf]["published_parsed"])
                    ):
                        url_f = rs1.entries[buf]["link"]
                        title_f = (
                            rs1.entries[buf]["title_detail"]["value"]
                            .replace("FreeBuf早报 |", "")
                            .replace(" ", "")
                        )
                        link4 = "\n" + title_f + "\n" + url_f + "\n"
                        str_list += link4
                    else:
                        pass
                except Exception as e:
                    output("[ERROR]:获取FreeBuf早报出错，错误信息：{}".format(e))
                    break
            if len(str_list) == 0:
                link6 = "\n今日暂无文章"
                str_list += link6
            else:
                pass
        except Exception as e:
            link6 = "\n今日暂无文章"
            str_list += link6
            output("ERROR：freebuf {}".format(e))
        str_list += f"\n{self.system_copyright + '整理分享，更多内容请戳:#' + self.system_copyright if self.system_copyright else ''}\n{time.strftime('%Y-%m-%d %X')}"
        return str_list

    # 获取先知社区文章
    def get_xz_news(self, ):
        str_list = ""
        str_list += "#先知社区"
        try:
            rs1 = feedparser.parse('https://xz.aliyun.com/feed')
            length = len(rs1.entries)
            for buf in range(length):
                try:
                    if str(time.strftime("%Y-%m-%d")) in str(rs1.entries[buf]["published"]):
                        url_f = rs1.entries[buf]["link"]
                        title_f = rs1.entries[buf]["title_detail"]["value"]
                        link4 = "\n" + title_f + "\n" + url_f + "\n"
                        str_list += link4
                    else:
                        pass
                except Exception as e:
                    output("[ERROR]:获取先知社区文章出现错误，错误信息：{}".format(e))
                    break
            if len(str_list) > 10:
                self.news_list += str_list
            else:
                link6 = "#先知社区\n今日暂无文章"
                self.news_list += link6
        except Exception as e:
            link6 = "#先知社区\n今日暂无文章"
            self.news_list += link6
            output("ERROR：先知社区 {}".format(e))
            return f'[-]:爬取先知社区文章出错，错误信息：{e}'

    # 获取奇安信攻防社区文章
    def get_qax_news(self, ):
        str_list = ""
        str_list += "\n#奇安信攻防社区"
        try:
            rs1 = feedparser.parse('https://forum.butian.net/Rss')
            length = len(rs1.entries)
            for buf in range(length):
                try:
                    if str(time.strftime("%Y-%m-%d")) in str(rs1.entries[buf]["published"]):
                        url_f = rs1.entries[buf]["link"]
                        title_f = rs1.entries[buf]["title_detail"]["value"]
                        link4 = "\n" + title_f + "\n" + url_f + "\n"
                        str_list += link4
                    else:
                        pass
                except Exception as e:
                    output("[ERROR]:爬取奇安信攻防社区文章出错，错误信息：{}".format(e))
                    break
            if len(str_list) > 10:
                self.news_list += str_list
            else:
                link6 = "\n#奇安信攻防社区\n今日暂无文章"
                self.news_list += link6
        except Exception as e:
            link6 = "\n#奇安信攻防社区\n今日暂无文章"
            self.news_list += link6
            output("[ERROR]:奇安信攻防社区 {}".format(e))
            return f"[-]:爬取奇安信攻防社区文章出错，错误信息：{e}"

    # 获取安全客文章
    def get_anquanke_news(self, ):
        str_list = ""
        str_list += "\n#安全客"
        try:
            rs1 = requests.get('https://www.anquanke.com/knowledge', timeout=5, verify=False)
            rs1.encoding = "utf-8"
            resp_text = (
                rs1.text.replace("\xa9", "")
                .replace("\n", "")
                .replace("&gt;", "")
                .replace(" ", "")
                .replace("                        ", "")
                .replace("                               ", "")
            )
            newlist = re.findall(
                '<divclass="info-content"><divclass="title"><atarget="_blank"rel="noopenernoreferrer"href="(.*?)">(.*?)</a></div><divclass="tagshide-in-mobile-device">',
                resp_text,
                re.S,
            )
            timelist = re.findall(
                '<istyle="margin-right:4px;"class="fafa-clock-o"></i>(.*?)</span></span>',
                resp_text,
                re.S,
            )
            for a in range(len(timelist)):
                try:
                    if time.strftime("%Y-%m-%d") in timelist[a]:
                        link1 = str(newlist[a][1])
                        link2 = "https://www.anquanke.com" + str(newlist[a][0])
                        link3 = "\n" + str(link1) + "\n" + str(link2) + "\n"
                        str_list += link3
                    else:
                        pass
                except Exception as e:
                    output("爬取安全客文章出错，错误信息：{}".format(e))
                    break
            if len(str_list) > 6:
                self.news_list += str_list
            else:
                link6 = "\n#安全客\n今日暂无文章"
                self.news_list += link6
        except Exception as e:
            link6 = "\n#安全客\n今日暂无文章"
            self.news_list += link6
            output("[ERROR]:爬取安全客文章出错，错误信息：{}".format(e))
            return f"[-]:爬取安全客文章出错，错误信息：{e}"

    # 获取各平台安全文章
    def get_safety_news(self, ):
        output("[+]:正在爬取安全新闻... ...")
        self.get_xz_news()
        self.get_qax_news()
        self.get_anquanke_news()
        output("[+]:获取成功")
        self.news_list += f"\n{self.system_copyright + '整理分享，更多内容请戳:#' + self.system_copyright if self.system_copyright else ''}\n{time.strftime('%Y-%m-%d %X')}"
        return self.news_list

    # 测试专用
    def demo(self):
        # url = 'https://tucdn.wpon.cn/api-girl/'
        # data = requests.get(url=url, headers=self.headers).json()
        # print(data)
        domain = 'qq.com'
        text = 'https://v.api.aa1.cn/api/icp/index.php?url={domain}'.format(domain=domain)
        print(text)


if __name__ == '__main__':
    Asm = Api_Server_Main()
    # Asm.get_pic()
    # Asm.demo()
    # Asm.get_video()
    # Asm.icp_query(keyword='ICP查询 qq.com')
    # Asm.get_suffix(keyword='icp查询 apk')
    # Asm.get_attribution(keyword='归属查询 17371963534')
    # Asm.get_whois(keyword='whois查询 qq.com')
    # Asm.get_wether(keyword='天气查询 123')
    # Asm.get_dog()
    # Asm.get_constellation('星座查询 白羊座')
    Asm.get_morning()
