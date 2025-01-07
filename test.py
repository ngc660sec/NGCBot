from ApiServer.ApiMainServer import ApiMainServer

Ams = ApiMainServer()
text = """
群聊名称: NGCBot 2群
123456,test,123456内容
222222,test2,123456内容
123456,test,123456内容2
222222,test2,123456内容2
33333,test3,33333内容
44444,test4,淘宝真的便宜
"""

aiMessages = [{
                    "role": "system",
                    "content": "你叫NGCBot, 是一个微信群聊消息总结小助手, 你会总结我给你的聊天数据集, 它的格式是群聊名称: TEST\n微信ID,微信名称,聊天内容\n.....你会将每一个人的聊天进行分析, 并根据聊天内容总结出这一天都聊了什么内容, 并且以人性化的口吻回答!",
                }]

content, message = Ams.getDeepSeek(text, aiMessages)
print(content)