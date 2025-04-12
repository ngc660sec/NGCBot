from BotServer.MsgHandleServer.FriendMsgHandle import FriendMsgHandle
from BotServer.MsgHandleServer.RoomMsgHandle import RoomMsgHandle
from PushServer.PushMainServer import PushMainServer
from DbServer.DbInitServer import DbInitServer
from WebServer.WebServer import WebServer
import FileCache.FileCacheServer as Fcs
import Config.ConfigServer as Cs
from threading import Thread
from OutPut.outPut import op
from cprint import cprint
from queue import Empty
from wcferry import Wcf
import requests



class MainServer:
    def __init__(self):
        # HTTP接口服务配置
        configData = Cs.returnConfigData()
        WebServerConfig = configData['WebServerConfig']
        self.cbApi = WebServerConfig['cbApi']
        webServerHost = WebServerConfig['WebServerHost']
        webServerPort = WebServerConfig['WebServerPort']


        self.wcf = Wcf()
        self.Dis = DbInitServer()
        # 开启全局接收
        self.wcf.enable_receiving_msg(pyq=True)
        self.Rmh = RoomMsgHandle(self.wcf)
        self.Fmh = FriendMsgHandle(self.wcf)
        self.Pms = PushMainServer(self.wcf)
        self.Ws = WebServer(self.wcf, webServerHost, webServerPort)
        # 初始化服务以及配置
        Thread(target=self.initConfig, name='初始化服务以及配置').start()

    def isLogin(self, ):
        """
        判断是否登录
        :return:
        """
        ret = self.wcf.is_login()
        if ret:
            userInfo = self.wcf.get_user_info()
            # 用户信息打印
            cprint.info(f"""
            \t========== NGCBot V2.3 ==========
            \t微信名：{userInfo.get('name')}
            \t微信ID：{userInfo.get('wxid')}
            \t手机号：{userInfo.get('mobile')}
            \t========== NGCBot V2.3 ==========       
            """.replace(' ', ''))

    def processMsg(self, ):
        # 判断是否登录
        self.isLogin()
        # self.wcf.query_sql('', '')
        while self.wcf.is_receiving_msg():
            try:
                msg = self.wcf.get_msg()
                # 调试专用
                # op(f'[*]: 接收到消息: {msg}')
                op(f'[*]: 接收到消息\n[*]: 群聊ID: {msg.roomid}\n[*]: 发送人ID: {msg.sender}\n[*]: 发送内容: {msg.content}\n--------------------')
                # 群聊消息处理
                if '@chatroom' in msg.roomid:
                    Thread(target=self.Rmh.mainHandle, args=(msg,)).start()
                # 好友消息处理
                elif '@chatroom' not in msg.roomid and 'gh_' not in msg.sender:
                    Thread(target=self.Fmh.mainHandle, args=(msg,)).start()
                else:
                    pass
                # 回调消息转发
                if self.cbApi:
                    Thread(target=self._forwardMsg, args=(msg, ), daemon=True).start()
            except Empty:
                continue

    def initConfig(self, ):
        """
        初始化数据库 缓存文件夹 开启定时推送服务
        :return:
        """
        self.Dis.initDb()
        Fcs.initCacheFolder()
        Thread(target=self.Pms.run, name='定时推送服务').start()
        Thread(target=self.Ws.run, name='WebServer服务').start()

    def _forwardMsg(self, msg):
        """
        回调消息转发
        :param msg:
        :return:
        """
        data = {}
        data["id"] = msg.id
        data["ts"] = msg.ts
        data["sign"] = msg.sign
        data["type"] = msg.type
        data["xml"] = msg.xml
        data["sender"] = msg.sender
        data["roomid"] = msg.roomid
        data["content"] = msg.content
        data["thumb"] = msg.thumb
        data["extra"] = msg.extra
        data["is_at"] = msg.is_at(self.wcf.self_wxid)
        data["is_self"] = msg.from_self()
        data["is_group"] = msg.from_group()
        try:
            resp = requests.post(self.cbApi, json=data, timeout=30)
            if resp.status_code != 200:
                op(f'[-]: 回调消息转发失败, HTTP状态码为: {resp.status_code}')
        except Exception as e:
            op(f'[-]: 回调消息转发出现错误, 错误信息: {e}')

    def stopWebServer(self):
        """
        停止WebServer服务
        :return:
        """
        self.Ws.stopWebServer()

if __name__ == '__main__':
    Ms = MainServer()
    Ms.processMsg()
