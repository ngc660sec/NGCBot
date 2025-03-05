from urllib.parse import urljoin
import Config.ConfigServer as Cs
from OutPut.outPut import op
from lxml import etree
import feedparser
import datetime
import requests
import urllib3
import time


class NewsApi:
    def __init__(self):
        """
        不要直接调用此文件
        新闻Api接口
        """
        # 忽略HTTPS告警
        urllib3.disable_warnings()
        # 读取配置文件
        configData = Cs.returnConfigData()
        # 读取系统版权设置
        self.systemCopyright = configData['SystemConfig']['SystemCopyright']

    def getMorningNews(self, ):
        """
        早报获取
        :return:
        """
        op(f'[*]: 正在获取FreeBuf早报... ...')
        yesterday = (datetime.date.today() + datetime.timedelta(-1))
        morningTime = yesterday.strftime("%a, %d %b %Y", )
        morningNews = "#FreeBuf早报\n"
        try:
            rs1 = feedparser.parse('https://www.freebuf.com/feed')
            print(rs1)
            for ent in rs1['entries']:
                if morningTime in ent['published']:
                    title = ent['title']
                    link = ent['link']
                    morningNews += '\n' + title + '\n' + link + '\n'
            if 'http' not in morningNews:
                morningNews += '\n今日暂无文章'
        except Exception as e:
            morningNews = "\n今日暂无文章"
            morningNews += morningNews
            op("[-]: 获取FreeBuf早报出错，错误信息： {}".format(e))
        morningNews += f"\n{self.systemCopyright + '整理分享，更多内容请戳 #' + self.systemCopyright if self.systemCopyright else ''}\n{time.strftime('%Y-%m-%d %X')}"
        return morningNews

    def getEveningNews(self, ):
        """
        晚报获取
        :return:
        """
        op(f'[*]: 正在调用晚报接口... ...')
        def getXzNews():
            """
            获取先知文章
            :return:
            """
            yesterday = (datetime.date.today() + datetime.timedelta(-1))
            yesterdayTime = str(yesterday.strftime('%Y-%m-%d'))
            eveningNews = "#先知社区"
            try:
                rs1 = feedparser.parse('https://xz.aliyun.com/feed')
                for ent in rs1['entries']:
                    if yesterdayTime in ent['published']:
                        title = ent['title']
                        link = ent['link']
                        eveningNews += '\n' + title + '\n' + link + '\n'
                if 'http' not in eveningNews:
                    eveningNews += '\n今日暂无文章\n\n'
                else:
                    eveningNews += '\n'
            except Exception as e:
                eveningNews += "\n今日暂无文章\n"
                op("[-]: 获取先知社区文章出错，错误信息: {}".format(e))
            return eveningNews

        def getQaxNews(eveningNews):
            """
            获取奇安信攻防社区文章
            :return:
            """
            eveningNews += '#奇安信攻防社区'
            try:
                yesterday = (datetime.date.today() + datetime.timedelta(-1))
                yesterdayTime = str(yesterday.strftime('%Y-%m-%d'))
                resp = requests.get(url='https://forum.butian.net/community?page=1', verify=True)
                tree = etree.HTML(resp.text)
                sections = tree.xpath('//div[@class="stream-list blog-stream"]/section')
                for section in sections:
                    title = section.xpath('./div/h2/a/text()')[0].strip()
                    href = section.xpath('./div/h2/a/@href')[0]
                    dateTime = section.xpath('./div/ul/li[4]/text()')[0].strip('发布于 ').strip()
                    if yesterdayTime in dateTime:
                        eveningNews += f'\n{title}\n{href}'
                if 'http' not in eveningNews:
                    eveningNews += '\n今日暂无文章\n'
                else:
                    eveningNews += '\n'
            except Exception as e:
                eveningNews += "\n今日暂无文章\n"
                op("[-]: 获取奇安信攻防社区文章出错，错误信息: {}".format(e))
            return eveningNews

        def getAnQuanKe(eveningNews):
            yesterday = (datetime.date.today() + datetime.timedelta(-1))
            yesterdayTime = str(yesterday.strftime('%Y-%m-%d'))
            eveningNews += "\n#安全客"
            try:
                resp = requests.get('https://www.anquanke.com/news', timeout=5, verify=True)
                tree = etree.HTML(resp.text)
                divs = tree.xpath('//div[@id="post-list"]/div')
                for div in divs:
                    title = div.xpath('./div/div[2]/div/div[@class="title"]/a/text()')[0].strip().replace(' ', '')
                    href = urljoin('https://www.anquanke.com/news',
                                   div.xpath('./div/div[2]/div/div[@class="title"]/a/@href')[0])
                    dateTime = div.xpath('./div/div[2]/div/div[@class="info"]/div[1]/span[@class="date"]/span/text()')[
                        1]
                    if yesterdayTime in dateTime:
                        eveningNews += f'\n{title}\n{href}'
                if 'http' not in eveningNews:
                    eveningNews += '\n今日暂无文章\n'
                else:
                    eveningNews += '\n'
            except Exception as e:
                eveningNews += "\n今日暂无文章\n"
                op("[-]: 获取安全客文章出错，错误信息: {}".format(e))
            return eveningNews

        eveningNews = ''
        eveningNews += getXzNews()
        eveningNews += getQaxNews('')
        eveningNews += getAnQuanKe('')
        eveningNews += f"\n{self.systemCopyright + '整理分享，更多内容请戳 #' + self.systemCopyright if self.systemCopyright else ''}\n{time.strftime('%Y-%m-%d %X')}"
        return eveningNews


if __name__ == '__main__':
    Na = NewsApi()
    print(Na.getMorningNews())
    # print(Na.getEveningNews())
