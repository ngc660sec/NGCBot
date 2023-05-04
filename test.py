import datetime
import time

import openai
import os


class ChatGpt:
    def __init__(self):
        os.environ["HTTP_PROXY"] = "192.168.147.1:7890"
        os.environ["HTTPS_PROXY"] = "192.168.147.1:7890"
        openai.api_key = ''
        self.message = [
            {"role": "system", "content": '你叫NGCBot,现在你的主人是云山'},
        ]

    def get_text(self, msg):
        self.message.append({"role": "user", "content": f'{msg}'})
        rsp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.message
        )
        bot_message = rsp.get("choices")[0]["message"]["content"]
        self.message.append({"role": "assistant", "content": f'{bot_message}'})
        print(rsp.get("choices")[0]["message"]["content"])

    def get_img(self, msg):
        response = openai.Image.create(
            prompt=f"{msg}",
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        print(image_url)


if __name__ == '__main__':
    Cgt = ChatGpt()
    while 1:
        Cgt.get_text(input('请输入 >> '))
    # Cgt.get_text('你好')
    # Cgt.get_img('宇宙全景图')
