from Output.output import output
import feedparser
import requests
import yaml
import time
import os
import re


class Api_news_server:
    def __init__(self):
        # 读取配置文件
        current_path = os.path.dirname(__file__)
        config = yaml.load(open(current_path + '/../config/config.yaml', encoding='UTF-8'), yaml.Loader)
        self.xz_url = config['XZ_URL']
        self.freebuf_url = config['FREEBUF_URL']
        self.qax_url = config['QAX_URL']
        self.anquanke_url = config['ANQUANKE_URL']
        # 获取系统消息配置
        self.system_message_configuration = config['MESSAGE_CONFIGURATION']
        # 获取版权信息
        self.copyright_mes = self.system_message_configuration['COPYRIGHT_MESSAGE']

        # 返回信息初始化
        self.news_list = ''

        # 全局HEAD头配置
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            # 'Connection':'keep-alive',#默认时链接一次，多次爬取之后不能产生新的链接就会产生报错Max retries exceeded with url
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Connection": "close",  # 解决Max retries exceeded with url报错
        }

    # 获取先知社区文章
    def get_xz_news(self, ):
        str_list = ""
        self.news_list += "#先知社区"
        try:
            rs1 = feedparser.parse(self.xz_url)
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
                    output("ERROR：{}".format(e))
                    break
            if len(str_list) > 0:
                self.news_list += str_list
            else:
                link6 = "\n今日暂无文章"
                self.news_list += link6
        except Exception as e:
            link6 = "\n今日暂无文章"
            self.news_list += link6
            output("ERROR：先知社区 {}".format(e))
            return 'GET XZ NEWS IS ERROR'

    # 获取freebuf文章
    def get_freebuf_news(self, ):
        str_list = ""
        str_list += "#FreeBuf早报\n"
        try:
            rs1 = feedparser.parse(self.freebuf_url)
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
                    output("ERROR：{}".format(e))
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
        str_list += f"\n{self.copyright_mes}整理分享，更多内容请戳#NGC660安全实验室 \n{time.strftime('%Y-%m-%d %X')}"
        return str_list

    # 获取奇安信攻防社区文章
    def get_qax_news(self, ):
        str_list = ""
        self.news_list += "\n#奇安信攻防社区"
        try:
            rs1 = feedparser.parse(self.qax_url)
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
                    output("ERROR：{}".format(e))
                    break
            if len(str_list) > 0:
                self.news_list += str_list
            else:
                link6 = "\n今日暂无文章"
                self.news_list += link6
        except Exception as e:
            link6 = "\n今日暂无文章"
            self.news_list += link6
            output("ERROR：奇安信攻防社区 {}".format(e))
            return "GET QAX NEWS IS ERROR"

    # 获取安全客文章
    def get_anquanke_news(self, ):
        str_list = ""
        self.news_list += "\n#安全客"
        try:
            rs1 = requests.get(self.anquanke_url, timeout=5, verify=False)
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
                    output("ERROR：{}".format(e))
                    break
            if len(str_list) > 0:
                self.news_list += str_list
            else:
                link6 = "\n今日暂无文章"
                self.news_list += link6
        except Exception as e:
            link6 = "\n今日暂无文章"
            self.news_list += link6
            output("ERROR：安全客 {}".format(e))
            return "GET ANQUANKE NEWS IS ERROR"

    # 获取各平台安全文章
    def get_safety_news(self, ):
        output("[*] >> 正在爬取安全新闻... ...")
        self.news_list = ''
        self.get_xz_news()
        self.get_qax_news()
        self.get_anquanke_news()
        output("[*] >> 获取成功")
        self.news_list += "\n{}整理分享，更多内容请戳#{} \n{}".format(self.copyright_mes, self.copyright_mes, time.strftime("%Y-%m-%d %X"))
        return self.news_list
