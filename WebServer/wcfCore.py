from fastapi import Body, FastAPI, Query
import base64

__version__ = "39.4.4"


class wcfCore(FastAPI):
    def __init__(
            self,
            wcf,
            **extra
    ) -> None:
        super().__init__(**extra)
        self.wcf = wcf

    def is_login(self):
        """
        获取登录状态
        :return:
        """
        ret = self.wcf.is_login()
        return {'status': 0, 'message': '成功', 'data': {'ret': ret}}

    def get_self_wxid(self, ):
        """
        获取登录账号的wxid
        :return:
        """
        ret = self.wcf.get_self_wxid()
        if ret:
            return {"status": 0, "message": "成功", "data": {"wxid": ret}}
        return {"status": -1, "message": "失败"}

    def get_msg_types(self):
        """获取消息类型"""
        ret = self.wcf.get_msg_types()
        if ret:
            return {"status": 0, "message": "成功", "data": {"types": ret}}
        return {"status": -1, "message": "失败"}

    def get_contacts(self):
        """获取完整通讯录"""
        ret = self.wcf.get_contacts()
        if ret:
            return {"status": 0, "message": "成功", "data": {"contacts": ret}}
        return {"status": -1, "message": "失败"}

    def get_friends(self):
        """获取好友列表"""
        ret = self.wcf.get_friends()
        if ret:
            return {"status": 0, "message": "成功", "data": {"friends": ret}}
        return {"status": -1, "message": "失败"}

    def get_dbs(self):
        """获取所有数据库"""
        ret = self.wcf.get_dbs()
        if ret:
            return {"status": 0, "message": "成功", "data": {"dbs": ret}}
        return {"status": -1, "message": "失败"}

    def get_tables(self, db: str):
        """获取 db 中所有表

        Args:
            db (str): 数据库名（可通过 `get_dbs` 查询）

        Returns:
            List[dict]: `db` 下的所有表名及对应建表语句
        """
        ret = self.wcf.get_tables(db)
        if ret:
            return {"status": 0, "message": "成功", "data": {"tables": ret}}
        return {"status": -1, "message": "失败"}

    def get_user_info(self):
        """获取登录账号个人信息"""
        ret = self.wcf.get_user_info()
        if ret:
            return {"status": 0, "message": "成功", "data": {"userInfo": ret}}
        return {"status": -1, "message": "失败"}

    def send_text(
            self, msg: str = Body(description="要发送的消息，换行用\\n表示"),
            receiver: str = Body("filehelper", description="消息接收者，roomid 或者 wxid"),
            aters: str = Body("", description="要 @ 的 wxid，多个用逗号分隔；@所有人 用 notify@all")):
        """发送文本消息，可参考：https://github.com/lich0821/WeChatRobot/blob/master/robot.py 里 sendTextMsg

        Args:
            msg (str): 要发送的消息，换行使用 `\\n`；如果 @ 人的话，需要带上跟 `aters` 里数量相同的 @
            receiver (str): 消息接收人，wxid 或者 roomid
            aters (str): 要 @ 的 wxid，多个用逗号分隔；`@所有人` 只需要 `notify@all`

        Returns:
            int: 0 为成功，其他失败
        """
        ret = self.wcf.send_text(msg, receiver, aters)
        return {"status": ret, "message": "成功" if ret == 0 else "失败"}

    def send_image(self,
                   path: str = Body("C:\\Projs\\WeChatRobot\\TEQuant.jpeg", description="图片路径"),
                   receiver: str = Body("filehelper", description="消息接收者，roomid 或者 wxid")):
        """发送图片，非线程安全

        Args:
            path (str): 图片路径，如：`C:/Projs/WeChatRobot/TEQuant.jpeg` 或 `https://raw.githubusercontent.com/lich0821/WeChatRobot/master/TEQuant.jpeg`
            receiver (str): 消息接收人，wxid 或者 roomid

        Returns:
            int: 0 为成功，其他失败
        """
        ret = self.wcf.send_image(path, receiver)
        return {"status": ret, "message": "成功" if ret == 0 else "失败"}

    def send_file(self,
                  path: str = Body("C:\\Projs\\WeChatRobot\\TEQuant.jpeg", description="本地文件路径，不支持网络路径"),
                  receiver: str = Body("filehelper", description="roomid 或者 wxid")):
        """发送文件

        Args:
            path (str): 本地文件路径，如：`C:/Projs/WeChatRobot/README.MD`
            receiver (str): 消息接收人，wxid 或者 roomid

        Returns:
            int: 0 为成功，其他失败
        """
        ret = self.wcf.send_file(path, receiver)
        return {"status": ret, "message": "成功" if ret == 0 else "失败"}

    def send_rich_text(
            self, name: str = Body("碲矿", description="左下显示的名字"),
            account: str = Body("gh_75dea2d6c71f", description="填公众号 id 可以显示对应的头像"),
            title: str = Body("【FAQ】WeChatFerry 机器人常见问题 v39.0.10", description="标题，最多两行"),
            digest: str = Body("先看再问，少走弯路。", description="最多三行，会占位"),
            url:
            str = Body(
                "http://mp.weixin.qq.com/s?__biz=MzI0MjI1OTk0OQ==&amp;mid=2247487601&amp;idx=1&amp;sn=1bf7a0d1c659f8bc78a00cba18d7b204&amp;chksm=e97e52f3de09dbe591fe23f335ce73bc468bd107a8c7bc5a458752a47f9d2d55a5fcdc5dd386&amp;mpshare=1&amp;scene=1&amp;srcid=1209eP4EsXnynxyRQHzCK2bY&amp;sharer_shareinfo=a12096ee76b4e3a9e72c9aedaf51a5ef&amp;sharer_shareinfo_first=a12096ee76b4e3a9e72c9aedaf51a5ef#rd",
                description="点击后跳转的链接"),
            thumburl: str = Body(
                "https://mmbiz.qpic.cn/mmbiz_jpg/XaSOeHibHicMGIiaZsBeYYjcuS2KfBGXfm8ibb9QrKJqk0H0W3JHia9icVica9nlWMiaD0xWmA0pKHpMOWbeBCJaAQc2IQ/0?wx_fmt=jpeg",
                description="缩略图的链接"),
            receiver: str = Body("filehelper", description="接收人, wxid 或者 roomid")):
        """发送卡片消息
        卡片样式（格式乱了，看这里：https://github.com/lich0821/WeChatFerry/blob/master/clients/python/wcferry/client.py#L421）：
            |-------------------------------------|
            |title, 最长两行
            |(长标题, 标题短的话这行没有)
            |digest, 最多三行，会占位    |--------|
            |digest, 最多三行，会占位    |thumburl|
            |digest, 最多三行，会占位    |--------|
            |(account logo) name
            |-------------------------------------|
        Args:
            name (str): 左下显示的名字
            account (str): 填公众号 id 可以显示对应的头像（gh_ 开头的）
            title (str): 标题，最多两行
            digest (str): 摘要，三行
            url (str): 点击后跳转的链接
            thumburl (str): 缩略图的链接
            receiver (str): 接收人, wxid 或者 roomid

        Returns:
            int: 0 为成功，其他失败
        """
        ret = self.wcf.send_rich_text(name, account, title, digest, url, thumburl, receiver)
        return {"status": ret, "message": "成功" if ret == 0 else "失败，原因见日志"}

    def send_pat_msg(
            self, roomid: str = Body(description="要发送的消息，换行用\\n表示"),
            wxid: str = Body("filehelper", description="消息接收者，roomid 或者 wxid")):
        """拍一拍群友

        Args:
            roomid (str): 群友所在群 roomid
            wxid (str): 要拍的群友的 wxid

        Returns:
            int: 1 为成功，其他失败
        """
        ret = self.wcf.send_pat_msg(roomid, wxid)
        return {"status": ret, "message": "成功" if ret == 1 else "失败，原因见日志"}

    def send_xml(
            self, receiver: str = Body("filehelper", description="roomid 或者 wxid"),
            xml:
            str = Body(
                '<?xml version="1.0"?><msg><appmsg appid="" sdkver="0"><title>叮当药房，24小时服务，28分钟送药到家！</title><des>叮当快药首家承诺范围内28分钟送药到家！叮当快药核心区域内7*24小时全天候服务，送药上门！叮当快药官网为您提供快捷便利，正品低价，安全放心的购药、送药服务体验。</des><action>view</action><type>33</type></appmsg><fromusername>wxid_xxxxxxxxxxxxxx</fromusername><scene>0</scene><appinfo><version>1</version><appname /></appinfo><commenturl /></msg>',
                description="xml 内容"),
            type: int = Body(0x21, description="xml 类型，0x21 为小程序"),
            path: str = Body(None, description="封面图片路径")):
        """发送 XML

        Args:
            receiver (str): 消息接收人，wxid 或者 roomid
            xml (str): xml 内容
            type (int): xml 类型，如：0x21 为小程序
            path (str): 封面图片路径

        Returns:
            int: 0 为成功，其他失败
        """
        ret = self.wcf.send_xml(receiver, xml, type, path)
        return {"status": ret, "message": "成功" if ret == 0 else "失败"}

    def send_emotion(self,
                     path: str = Body("C:/Projs/WeChatRobot/emo.gif", description="本地文件路径，不支持网络路径"),
                     receiver: str = Body("filehelper", description="roomid 或者 wxid")):
        """发送表情

        Args:
            path (str): 本地表情路径，如：`C:/Projs/WeChatRobot/emo.gif`
            receiver (str): 消息接收人，wxid 或者 roomid

        Returns:
            int: 0 为成功，其他失败
        """
        ret = self.wcf.send_emotion(path, receiver)
        return {"status": ret, "message": "成功" if ret == 0 else "失败"}

    def query_sql(self,
                  db: str = Body("MicroMsg.db", description="数据库"),
                  sql: str = Body("SELECT * FROM Contact LIMIT 1;", description="SQL 语句")):
        """执行 SQL，如果数据量大注意分页，以免 OOM

        Args:
            db (str): 要查询的数据库
            sql (str): 要执行的 SQL

        Returns:
            List[dict]: 查询结果
        """
        ret = self.wcf.query_sql(db, sql)
        if ret:
            for row in ret:
                for k, v in row.items():
                    print(k, type(v))
                    if type(v) is bytes:
                        row[k] = base64.b64encode(v)
            return {"status": 0, "message": "成功", "data": {"bs64": ret}}
        return {"status": -1, "message": "失败"}

    def accept_new_friend(self,
                          v3: str = Body("v3", description="加密用户名 (好友申请消息里 v3 开头的字符串)"),
                          v4: str = Body("v4", description="Ticket (好友申请消息里 v4 开头的字符串)"),
                          scene: int = Body(30, description="申请方式 (好友申请消息里的 scene)")):
        """通过好友申请

        Args:
            v3 (str): 加密用户名 (好友申请消息里 v3 开头的字符串)
            v4 (str): Ticket (好友申请消息里 v4 开头的字符串)
            scene: 申请方式 (好友申请消息里的 scene)

        Returns:
            int: 1 为成功，其他失败
        """
        ret = self.wcf.accept_new_friend(v3, v4, scene)
        return {"status": ret, "message": "成功" if ret == 1 else "失败"}

    def add_chatroom_members(self,
                             roomid: str = Body("xxxxxxxx@chatroom", description="待加群的 id"),
                             wxids: str = Body("wxid_xxxxxxxxxxxxx",
                                               description="要加到群里的 wxid，多个用逗号分隔")):
        """添加群成员

        Args:
            roomid (str): 待加群的 id
            wxids (str): 要加到群里的 wxid，多个用逗号分隔

        Returns:
            int: 1 为成功，其他失败
        """
        ret = self.wcf.add_chatroom_members(roomid, wxids)
        return {"status": ret, "message": "成功" if ret == 1 else "失败"}

    def invite_chatroom_members(self,
                                roomid: str = Body("xxxxxxxx@chatroom", description="待加群的 id"),
                                wxids: str = Body("wxid_xxxxxxxxxxxxx",
                                                  description="要加到群里的 wxid，多个用逗号分隔")):
        """邀请群成员

        Args:
            roomid (str): 待加群的 id
            wxids (str): 要加到群里的 wxid，多个用逗号分隔

        Returns:
            int: 1 为成功，其他失败
        """
        ret = self.wcf.invite_chatroom_members(roomid, wxids)
        return {"status": ret, "message": "成功" if ret == 1 else "失败"}

    def del_chatroom_members(self,
                             roomid: str = Body("xxxxxxxx@chatroom", description="群的 id"),
                             wxids: str = Body("wxid_xxxxxxxxxxxxx",
                                               description="要删除的 wxid，多个用逗号分隔")):
        """删除群成员

        Args:
            roomid (str): 群的 id
            wxids (str): 要删除的 wxid，多个用逗号分隔

        Returns:
            int: 1 为成功，其他失败
        """
        ret = self.wcf.del_chatroom_members(roomid, wxids)
        return {"status": ret, "message": "成功" if ret == 1 else "失败"}

    def receive_transfer(self,
                         wxid: str = Body("wxid_xxxxxxxxxxxxx", description="转账消息里的发送人 wxid"),
                         transferid: str = Body("transferid", description="转账消息里的 transferid"),
                         transactionid: str = Body("transactionid", description="转账消息里的 transactionid")):
        """接收转账

        Args:
            wxid (str): 转账消息里的发送人 wxid
            transferid (str): 转账消息里的 transferid
            transactionid (str): 转账消息里的 transactionid

        Returns:
            int: 1 为成功，其他失败
        """
        ret = self.wcf.receive_transfer(wxid, transferid, transactionid)
        return {"status": ret, "message": "成功" if ret == 1 else "失败"}

    def refresh_pyq(self, id: int = Query(0, description="开始 id，0 为最新页")):
        """刷新朋友圈

        Args:
            id (int): 开始 id，0 为最新页

        Returns:
            int: 1 为成功，其他失败
        """
        ret = self.wcf.refresh_pyq(id)
        return {"status": ret, "message": "成功" if ret == 1 else "失败"}

    def decrypt_image(self,
                      src: str = Body("C:\\...", description="加密的图片路径，从图片消息中获取"),
                      dst: str = Body("C:\\...", description="解密的图片路径")):
        """解密图片:

        Args:
            src (str): 加密的图片路径
            dst (str): 解密的图片路径

        Returns:
            bool: 是否成功
        """
        ret = self.wcf.decrypt_image(src, dst)
        return {"status": ret, "message": "成功" if ret else "废弃，请使用 save-image"}

    def download_attachment(self,
                            id: int = Body("0", description="消息中的id"),
                            thumb: str = Body("C:/...", description="消息中的 thumb"),
                            extra: str = Body("C:/...", description="消息中的 extra")):
        """下载附件（图片、视频、文件）

        Args:
            id (int): 消息中 id
            thumb (str): 消息中的 thumb
            extra (str): 消息中的 extra

        Returns:
            str: 成功返回存储路径；空字符串为失败，原因见日志。
        """
        ret = self.wcf.download_attach(id, thumb, extra)
        if ret:
            return {"status": 0, "message": "成功", "data": {"path": ret}}

        return {"status": -1, "message": "废弃，请使用 save-image"}

    def download_image(self,
                       id: int = Body("0", description="消息中的id"),
                       extra: str = Body("C:/...", description="消息中的 extra"),
                       dir: str = Body("C:/...", description="保存图片的目录"),
                       timeout: int = Body("30", description="超时时间（秒）")):
        """下载图片

        Args:
            id (int): 消息中 id
            extra (str): 消息中的 extra
            dir (str): 存放图片的目录
            timeout (int): 超时时间（秒）

        Returns:
            str: 成功返回存储路径；空字符串为失败，原因见日志。
        """
        ret = self.wcf.download_image(id, extra, dir, timeout)
        if ret:
            return {"status": 0, "message": "成功", "data": {"path": ret}}

        return {"status": -1, "message": "失败，原因见日志"}

    def get_audio_msg(self,
                      id: int = Body("0", description="消息中的id"),
                      dir: str = Body("C:/...", description="保存语音的目录"),
                      timeout: int = Body("30", description="超时时间（秒）")):
        """保存语音

        Args:
            id (int): 消息中 id
            dir (str): 存放图片的目录
            timeout (int): 超时时间（秒）

        Returns:
            str: 成功返回存储路径；空字符串为失败，原因见日志。
        """
        ret = self.wcf.get_audio_msg(id, dir, timeout)
        if ret:
            return {"status": 0, "message": "成功", "data": {"path": ret}}

        return {"status": -1, "message": "失败，原因见日志"}

    def get_chatroom_members(self, roomid: str = Query("xxxxxxxx@chatroom", description="群的 id")):
        """获取群成员

        Args:
            roomid (str): 群的 id

        Returns:
            List[dict]: 群成员列表
        """
        ret = self.wcf.get_chatroom_members(roomid)
        return {"status": 0, "message": "成功", "data": {"members": ret}}

    def get_alias_in_chatroom(self, wxid: str = Query("wxid_xxxxxxxxxxxxx", description="wxid"),
                              roomid: str = Query("xxxxxxxx@chatroom", description="群的 id")):
        """获取群成员名片

        Args:
            roomid (str): 群的 id
            wxid (str): wxid

        Returns:
            str: 名片
        """
        ret = self.wcf.get_alias_in_chatroom(wxid, roomid)
        return {"status": 0, "message": "成功", "data": {"alias": ret}}


"""
1. 给推送群聊推送消息
2. 给白名单群聊推送消息
3.
"""
