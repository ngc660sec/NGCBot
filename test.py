import re

import requests
import time
import yaml
import os

# msg = os.system('python -m ciphey -t "123"')
# print(msg)

# url = 'https://v.api.aa1.cn/api/phone/guishu-api.php?phone=18079638731'
# phone = '8079638731'
# resp = requests.get(url= url).json()
# print(resp)
# if resp['code'] == 0:
#     msg = f"===== 查询信息 =====\n手机号码: {phone}\n省份: {resp['data']['province']}\n城市: {resp['data']['city']}\n运营商: {resp['data']['sp']}\nBy NGC660安全实验室\n==================="
#     print(msg)

# domain = 'qq.com'
# url = 'https://v.api.aa1.cn/api/whois/index.php?domain={}'.format(domain)
#
# resp = requests.get(url=url)
# # print(resp.text)
# print(resp.text.split('For more information on Whois status codes')[0].replace('<pre>', '').strip())

# url = 'https://api.vvhan.com/api/moyu'
# resp = requests.get(url=url)
# print(resp.text)
# ip_list = ['1', '1', '1', '1']
# ips = True if [i for i in ip_list if '1' != i] else False
# print(ips)

# key = 'e8409cd6401b93d170297440ace30f27'
# word = 'apk'
# extensions_url = 'https://apis.tianapi.com/targa/index?key={}&word={}'
# url = extensions_url.format(key, word)
# resp = requests.get(url=url).json()
# print(resp)

current_path = os.path.dirname(__file__)
config = yaml.load(open(current_path + '/config/config.yaml', encoding='UTF-8'), yaml.Loader)
# custom_keyword_reply = config['CUSTOM_KEYWORD_REPLY']
# print(list(custom_keyword_reply.keys()))
# 获取积分管理关键词
integral_key_response = config['INTEGRAL_CONFIG']
# 归属地积分查询配置
attribution_integral = integral_key_response['ATTRIBUTION_POINT']
# print(type(attribution_integral))
# mes = re.findall(f'[查看|查询|查找]')

