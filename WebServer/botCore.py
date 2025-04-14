from ApiServer.InterFaceServer.InterFaceApi import InterFaceApi
from fastapi import Body, FastAPI, Query, File, UploadFile
from DbServer.DbMainServer import DbMainServer
import FileCache.FileCacheServer as Fcs
import base64
import time
import os

__version__ = "39.4.4"


class botCore(FastAPI):
    def __init__(
            self,
            wcf,
            **extra
    ) -> None:
        super().__init__(**extra)
        self.wcf = wcf
        self.Dms = DbMainServer()
        self.Ifa = InterFaceApi()

    """
    批量给群聊或好友发消息
    查看白名单群聊
    查看黑名单群聊
    查看推送群聊
    批量给白名单，黑名单，推送群聊发消息

    """

    def send_many_text(self, msg: str = Body("你好", description="要发送的消息"),
                       receiver: list = Body(['wxid1', 'roomId1', 'wxid2'], description="成员列表")):
        """给多个群聊或好友发消息

        Args:
            msg (str): 消息内容, 如: 你好
            receiver (LIST): 接收者列表, 可以是群, 也可以是好友。如: ['wxid1','wxid2','roomid1']

        Returns:
            int: 0成功 其它为失败
        """
        ret = 0
        for rec in receiver:
            ret = self.wcf.send_text(msg, receiver=rec.strip())
        return {"status": ret, "message": "成功" if ret == 0 else "失败"}

    def send_image(self, base64ImgData: str = Body("图片Base64数据", description="base64Data"),
                   receiver: str = Body("wxid_123", description="接收者")):
        """发送图片

        Args:
            base64ImgData (str): base64图片数据
            receiver (str): 接收者
        Returns:
            int: 0成功 其它为失败
        """
        imgData = base64.b64decode(base64ImgData)
        imgPath = f'{Fcs.returnWebServerFolder()}/{int(time.time())}.png'
        with open(imgPath, mode='wb') as f:
            f.write(imgData)
        if not os.path.exists(imgPath):
            return {"status": -1, "message": "失败, 图片路径不存在"}
        ret = self.wcf.send_image(path=imgPath, receiver=receiver)
        return {"status": ret, "message": "成功" if ret == 0 else "失败"}

    def upload_file(self, file: UploadFile = File('文件对象', description='要上传的文件')):
        """ 上传文件

        Args:
            file (str): 上传的文件对象

        Returns:
            int: 0成功 其它为失败
        """
        filePath = f'{Fcs.returnWebServerFolder()}/{int(time.time())}-{file.filename}'
        try:
            with open(filePath, mode='wb') as buffer:
                while content := file.file.read(1024 * 1024):
                    buffer.write(content)
            return {'status': 0, "message": '成功', 'filePath': filePath}
        except Exception as e:
            return {"status": -1, "message": str(e)}

    def send_file(self, filePath: str = Body('`c:/123.zip` 或者 `http://baidu.com/robots.txt` ',
                                             description='通过上传文件接口返回的文件路径'),
                  receiver: str = Body("wxid_123", description="接收者")):
        """ 发送文件

        Args:
            filePath (str): 文件路径，通过上传文件接口返回的文件路径
            receiver (str): 接收者

        Returns:
            int: 0成功 其它为失败
        """
        if 'http://' in filePath or 'https://' in filePath:
            savePath = f'{Fcs.returnWebServerFolder()}/{int(time.time())}.{filePath.split(".")[-1]}'
            filePath = self.Ifa.downloadFile(filePath, savePath)
        ret = self.wcf.send_file(path=filePath, receiver=receiver)
        return {"status": ret, "message": "成功" if ret == 0 else "失败"}

    def show_rooms(self, roomType: str = (Query("white, black, push", description="对应白名单, 黑名单, 推送群聊"))):
        """查看白名单, 黑名单, 推送群聊

        Args:
            roomType (str): 群聊类型, white白名单群聊, black黑名单群聊, push推送群聊

        Returns:
            Dict: {'status': 0成功1失败, 'message': '成功', 'data': 群聊数据}
        """
        roomData = {}
        if roomType == 'white':
            roomData = self.Dms.showWhiteRoom()
        elif roomType == 'black':
            roomData = self.Dms.showBlackRoom()
        elif roomType == 'push':
            roomData = self.Dms.showPushRoom()
        if not roomData:
            return {'status': -1, 'message': '失败'}
        return {'status': 0, 'message': '成功', 'data': roomData}

    def send_room_text(self, msg: str = Body("你好", description="要发送的消息"),
                       roomType: str = (Body("white, black, push", description="对应白名单, 黑名单, 推送群聊")),
                       aters: str = Body("", description="要 @ 的 wxid，多个用逗号分隔；@所有人 用 notify@all")):
        """给白名单 黑名单 推送群聊发消息

        Args:
            msg (str): 消息内容, 如: 你好
            roomType (str): 群聊类型, white,black,push
            aters (str): 要 @ 的 wxid，多个用逗号分隔；@所有人 用 notify@all

        Returns:
            int: 0成功 其它为失败
        """
        jsonData = self.show_rooms(roomType)
        status = jsonData.get('status')
        if status == -1:
            return {'status': -1, 'message': '失败'}
        roomData = jsonData.get('data')
        ret = 0
        for roomId, roomName in roomData:
            ret = self.wcf.send_text(msg, receiver=roomId, aters=aters)
        return {"status": ret, "message": "成功" if ret == 0 else "失败"}

    def get_name_wxid(self, wxName: str = Query("张三", description="通过名字拿wxId")):
        """ 通过微信名字拿wxId, 可以是好友名字, 也可以是群聊名字

        Args:
            wxName (str): 好友或群聊名字, 如: 张三

        Returns:
            Dict: {'status': 0, 'message': '成功', 'data': {'wxId': wxId}}
        """
        contacts = self.wcf.get_contacts()
        for contact in contacts:
            name = contact.get('name').strip()
            wxId = contact.get('wxid').strip()
            if name == wxName:
                return {'status': 0, 'message': '成功', 'data': {'wxId': wxId}}
        return {'status': -1, 'message': '失败'}


if __name__ == '__main__':
    bc = botCore(1)
    print(bc.show_rooms('push'))
