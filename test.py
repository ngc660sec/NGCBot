import datetime
import time

import openai
import os

import requests


class ChatGpt:
    def __init__(self):
        openai.api_key = 'sk-'
        # self.message = [
        #     {"role": "system", "content": '你叫NGCBot,现在你的主人是云山'},
        # ]

        self.messages = [
            {"role": "system", "content": "你现在叫NGCBot,是一名网络安全专家,精通各种代码!"}
        ]

    def get_text(self, msg):
        self.message.append({"role": "user", "content": f'{msg}'})
        rsp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.message,
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

    def get_text2(self, text):
        data = {
            "model": "gpt-3.5-turbo",
            "messages": self.messages
        }
        url = 'https://api.openai-proxy.com/v1/chat/completions'
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-",
        }
        self.messages.append({"role": 'user', "content": text})
        resp = requests.post(url=url, headers=headers, json=data)
        json_data = resp.json()
        print(json_data)
        assistant_content = json_data['choices'][0]['message']['content']
        # print(json_data)
        self.messages.append({"role": "assistant", "content": f"{assistant_content}"})
        if len(self.messages) == 13:
            self.messages = self.messages[0]
        print(self.messages)
        print(assistant_content)

    def somd5(self, md5):
        url = f'https://www.somd5.com/ss.php?api=4bc2161f&hash={md5}'
        resp = requests.get(url=url)
        print(resp.text)


if __name__ == '__main__':
    Cgt = ChatGpt()
    Cgt.somd5('08bdbbeed946fc96')
    # while 1:
    #     Cgt.get_text2(input('请输入 >> '))
        # Cgt.get_text(input('请输入 >> '))
    # Cgt.get_text('你好')
    # Cgt.get_img('宇宙全景图')
