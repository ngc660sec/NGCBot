import os
import qianfan


# 通过AppID设置使用的应用，该参数可选；如果不设置该参数，SDK默认使用最新创建的应用AppID；如果设置，使用如下代码，替换示例中参数，应用AppID替换your_AppID

chat_completion = qianfan.ChatCompletion(ak="", sk="")

resp = chat_completion.do(messages=[{
    "role": "user",
    "content": "hello"
}])

print(resp)
