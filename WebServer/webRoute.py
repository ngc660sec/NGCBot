from fastapi import FastAPI, Depends, APIRouter, HTTPException
from fastapi.security import APIKeyHeader
from Config.ConfigData import getBotKey
from WebServer.wcfCore import wcfCore
from WebServer.botCore import botCore
import Config.ConfigServer as Cs
from pydantic import BaseModel

__version__ = "39.4.4"

BotKeyHeader = APIKeyHeader(name='BotKey')


class Msg(BaseModel):
    id: int
    ts: int
    sign: str
    type: int
    xml: str
    sender: str
    roomid: str
    content: str
    thumb: str
    extra: str
    is_at: bool
    is_self: bool
    is_group: bool


class webRoute(FastAPI):
    def __init__(
            self,
            wcf,
            **extra
    ) -> None:
        super().__init__(**extra)

        self.wcf = wcf
        self.wcfCore = wcfCore(self.wcf)
        self.botCore = botCore(self.wcf)
        self.secureRoute = APIRouter(dependencies=[Depends(verifyKey)])
        self.addSecureRoutes()
        self.include_router(self.secureRoute)

    def addSecureRoutes(self, ):
        self.secureRoute.add_api_route("/login", self.wcfCore.is_login, methods=["GET"], summary="获取登录状态",
                                       tags=["WCF查询类接口"])
        self.secureRoute.add_api_route("/wxid", self.wcfCore.get_self_wxid, methods=["GET"],
                                       summary="获取登录账号 wxid",
                                       tags=["WCF查询类接口"])
        self.secureRoute.add_api_route("/user-info", self.wcfCore.get_user_info, methods=["GET"],
                                       summary="获取登录账号个人信息",
                                       tags=["WCF查询类接口"])
        self.secureRoute.add_api_route("/msg-types", self.wcfCore.get_msg_types, methods=["GET"],
                                       summary="获取消息类型",
                                       tags=["WCF查询类接口"])
        self.secureRoute.add_api_route("/contacts", self.wcfCore.get_contacts, methods=["GET"],
                                       summary="获取完整通讯录",
                                       tags=["WCF查询类接口"])
        self.secureRoute.add_api_route("/friends", self.wcfCore.get_friends, methods=["GET"], summary="获取好友列表",
                                       tags=["WCF查询类接口"])
        self.secureRoute.add_api_route("/dbs", self.wcfCore.get_dbs, methods=["GET"], summary="获取所有数据库",
                                       tags=["WCF查询类接口"])
        self.secureRoute.add_api_route("/{db}/tables", self.wcfCore.get_tables, methods=["GET"],
                                       summary="获取 db 中所有表",
                                       tags=["WCF查询类接口"])
        self.secureRoute.add_api_route("/pyq", self.wcfCore.refresh_pyq, methods=["GET"],
                                       summary="刷新朋友圈（数据从消息回调中查看）", tags=["WCF操作类接口"])
        self.secureRoute.add_api_route("/chatroom-member", self.wcfCore.get_chatroom_members, methods=["GET"],
                                       summary="获取群成员",
                                       tags=["WCF查询类接口"])
        self.secureRoute.add_api_route("/alias-in-chatroom", self.wcfCore.get_alias_in_chatroom, methods=["GET"],
                                       summary="获取群成员名片", tags=["WCF查询类接口"])

        # POST Routes
        self.secureRoute.add_api_route("/text", self.wcfCore.send_text, methods=["POST"], summary="发送文本消息",
                                       tags=["WCF消息发送接口"])
        self.secureRoute.add_api_route("/image", self.wcfCore.send_image, methods=["POST"], summary="发送图片消息",
                                       tags=["WCF消息发送接口"])
        self.secureRoute.add_api_route("/file", self.wcfCore.send_file, methods=["POST"], summary="发送文件消息",
                                       tags=["WCF消息发送接口"])
        self.secureRoute.add_api_route("/rich-text", self.wcfCore.send_rich_text, methods=["POST"],
                                       summary="发送卡片消息",
                                       tags=["WCF消息发送接口"])
        self.secureRoute.add_api_route("/pat", self.wcfCore.send_pat_msg, methods=["POST"], summary="发送拍一拍消息",
                                       tags=["WCF消息发送接口"])
        self.secureRoute.add_api_route("/xml", self.wcfCore.send_xml, methods=["POST"], summary="发送 XML 消息",
                                       tags=["WCF消息发送接口"])
        self.secureRoute.add_api_route("/emotion", self.wcfCore.send_emotion, methods=["POST"], summary="发送表情消息",
                                       tags=["WCF消息发送接口"])
        self.secureRoute.add_api_route("/sql", self.wcfCore.query_sql, methods=["POST"],
                                       summary="执行 SQL，如果数据量大注意分页，以免 OOM", tags=["WCF查询类接口"])
        self.secureRoute.add_api_route("/new-friend", self.wcfCore.accept_new_friend, methods=["POST"],
                                       summary="通过好友申请",
                                       tags=["WCF操作类接口"])
        self.secureRoute.add_api_route("/chatroom-member", self.wcfCore.add_chatroom_members, methods=["POST"],
                                       summary="添加群成员", tags=["WCF操作类接口"])
        self.secureRoute.add_api_route("/cr-members", self.wcfCore.invite_chatroom_members, methods=["POST"],
                                       summary="邀请群成员",
                                       tags=["WCF操作类接口"])
        self.secureRoute.add_api_route("/transfer", self.wcfCore.receive_transfer, methods=["POST"], summary="接收转账",
                                       tags=["WCF操作类接口"])
        self.secureRoute.add_api_route("/attachment", self.wcfCore.download_attachment, methods=["POST"],
                                       summary="（废弃）下载图片、文件和视频", tags=["WCF操作类接口"])
        self.secureRoute.add_api_route("/save-image", self.wcfCore.download_image, methods=["POST"], summary="下载图片",
                                       tags=["WCF操作类接口"])
        self.secureRoute.add_api_route("/save-audio", self.wcfCore.get_audio_msg, methods=["POST"], summary="保存语音",
                                       tags=["WCF操作类接口"])
        self.secureRoute.add_api_route("/chatroom-member", self.wcfCore.del_chatroom_members, methods=["POST"],
                                       summary="删除群成员", tags=["WCF操作类接口"])

        # Bot操作接口
        self.secureRoute.add_api_route("/send-many-text", self.botCore.send_many_text, methods=["POST"],
                                       summary="批量发送消息",
                                       tags=["NGCBot接口"])
        self.secureRoute.add_api_route("/show-rooms", self.botCore.show_rooms, methods=["GET"],
                                       summary="查看白名单|黑名单|推送群聊", tags=["NGCBot接口"])
        self.secureRoute.add_api_route("/send-room-text", self.botCore.send_room_text, methods=["POST"],
                                       summary="给白名单|黑名单|推送群聊发送消息", tags=["NGCBot接口"])
        self.secureRoute.add_api_route('/get-name-wxid', self.botCore.get_name_wxid, methods=["GET"],
                                       summary="通过微信名字拿到 wxId", tags=["NGCBot接口"])
        self.secureRoute.add_api_route('/upload-file', self.botCore.upload_file, methods=["POST"],
                                       summary="上传文件接口", tags=["NGCBot接口"])
        self.secureRoute.add_api_route('/send-image', self.botCore.send_image, methods=["POST"],
                                       summary="图片发送接口", tags=["NGCBot接口"])
        self.secureRoute.add_api_route('/send-file', self.botCore.send_file, methods=["POST"],
                                       summary="文件发送接口", tags=["NGCBot接口"])

async def verifyKey(BotKey: str = Depends(BotKeyHeader)):
    if BotKey.strip() != getBotKey():
        raise HTTPException(status_code=403, detail='Invalid API Key')
    return BotKey
