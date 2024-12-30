import FileCache.FileCacheServer as Fcs
import Config.ConfigServer as Cs
from OutPut.outPut import op
import requests
import time


class PointApi:
    def __init__(self):
        """
        不要直接调用此类
        积分功能Api文件
        """
        configData = Cs.returnConfigData()
        # 高德配置
        self.gaoDeApi = configData['apiServer']['gaoDeApi']
        self.gaoDeKey = configData['apiServer']['apiConfig']['gaoDeKey']
        # 埃文配置
        self.aiWenApi = configData['apiServer']['aiWenApi']
        self.aiWenKey = configData['apiServer']['apiConfig']['aiWenKey']
        # 微步配置
        self.threatBookApi = configData['apiServer']['threatBookApi']
        self.threatBookKey = configData['apiServer']['apiConfig']['threatBookKey']
        # Cmd5配置
        self.cmd5Api = configData['apiServer']['cmd5Api']
        self.cmd5Email = configData['apiServer']['apiConfig']['cmd5Email']
        self.cmd5Key = configData['apiServer']['apiConfig']['cmd5Key']
        # 飞书Wiki配置
        self.feishuApi = configData['apiServer']['feishuWiki']
        # 飞书Token配置
        self.feishuConfigData = Cs.returnFeishuConfigData()

    def getGaoDeMap(self, lat, lng):
        op(f'[*]: 正在调用高德地图Api接口... ...')
        params = {
            'location': f'{lat},{lng}',
            'zoom': 13,
            'size': '1024*1024',
            'markers': f'mid,,A:{lat},{lng}',
            'key': self.gaoDeKey
        }
        try:
            file_name = Fcs.returnGaoDeCacheFolder() + '/' + str(int(time.time() * 1000)) + '.png'
            resp = requests.get(url=self.gaoDeApi, params=params)
            with open(file_name, mode='wb') as f:
                f.write(resp.content)
            return file_name
        except Exception as e:
            op(f'[-]: 高德地图Api接口查询错误, 错误信息: {e}')
            return None

    def getAiWenIpv4(self, ip):
        dictData = {'maps': [], 'message': ''}
        """
        埃文科技IPV4地址查询
        :param ip:
        :return:
        """
        ips = str(ip).split('.')
        op(f'[*]: 正在调用埃文IPV4查询接口... ...')
        if ips[0] in ['127', '192', '0', '224', '240', '255'] or \
                ip in ['1.1.1.1', '2.2.2.2', '3.3.3.3', '4.4.4.4', '5.5.5.5', '6.6.6.6', '7.7.7.7',
                       '8.8.8.8', '9.9.9.9', '10.10.10.10'] or \
                '.'.join(ips[0:2]) in ['169.254', '100.64', '198.51', '198.18', '172.16'] or \
                '.'.join(ips[0:3]) in ['203.0.113'] or \
                ips[-1] in ['255', '254']:
            return None

        parameters = {
            'key': self.aiWenKey,
            'ip': ip,
            'lang': '',
            'coordsys': 'WGS84',
            'area': 'multi',
        }
        try:
            resp = requests.get(url=self.aiWenApi, params=parameters, timeout=10)
            json_data = resp.json()
            if json_data['code'] != 'Success':
                return None
            continent = json_data['data']['continent']
            country = json_data['data']['country']
            accuracy = json_data['data']['accuracy']
            isp = json_data['data']['isp']
            multiAreas = json_data['data']['multiAreas']
            dictData['message'] = f'==========\n地区: {continent}\n国家: {country}\n精确度: {accuracy}\n运营商: {isp}\n'
            for areas in multiAreas:
                picPath = self.getGaoDeMap(areas.get('lng'), areas.get('lat'))
                dictData['maps'].append(picPath)
                dictData[
                    'message'] += f'纬度: {areas.get("lat")}\n经度: {areas.get("lng")}\n省份: {areas.get("prov")}\n市区: {areas.get("city")}\n县: {areas.get("district")}\n详细地址: {areas.get("address")}\n==========\n'
            return dictData
        except Exception as e:
            op(f'[-]: 埃文IPV4查询接口错误, 错误信息: {e}')
            return None

    def getThreatBook(self, ip):
        """
        微步威胁Ip查询
        :param ip: IP地址
        :return:
        """
        ips = str(ip).split('.')
        op(f'[*]: 正在调用微步IP查询API接口... ...')
        if ips[0] in ['127', '192', '0', '224', '240', '255'] or \
                ip in ['1.1.1.1', '2.2.2.2', '3.3.3.3', '4.4.4.4', '5.5.5.5', '6.6.6.6', '7.7.7.7',
                       '8.8.8.8', '9.9.9.9', '10.10.10.10'] or \
                '.'.join(ips[0:2]) in ['169.254', '100.64', '198.51', '198.18', '172.16'] or \
                '.'.join(ips[0:3]) in ['203.0.113'] or \
                ips[-1] in ['255', '254']:
            return None
        params = {
            "apikey": self.threatBookKey,
            "resource": ip,
            'lang': 'zh'
        }
        try:
            msg = '==========\n'
            msg += f'查询IP: {ip}\n'
            resp = requests.get(
                self.threatBookApi,
                params=params,
                timeout=10,
                verify=True,
            )
            jsonData = resp.json()['data'][f'{ip}']
            if resp.status_code == 200 and resp.json()["response_code"] == 0:
                # 获取标签
                tags_classes = jsonData['tags_classes']
                for tag_class in tags_classes:
                    tags = tag_class.get('tags')
                    msg += '标签: ' + ','.join(tags) + '\n'
                    msg += '标签类别: ' + tag_class.get('tags_type') + '\n'
                # 获取威胁类型
                judgments = jsonData['judgments']
                msg += '威胁类别: ' + ','.join(judgments) + '\n' + '----------\n'
                # 获取微步在线情报
                threatBook_labs = jsonData['intelligences']['threatbook_lab']
                for threatBook_lab in threatBook_labs:
                    msg += threatBook_lab.get('source') + '\n'
                    msg += '可信度: ' + str(threatBook_lab.get('confidence')) + '\n'
                    msg += '是否有效: '
                    msg += 'YES\n' if not threatBook_lab.get('expired') else 'NO\n'
                    intel_tags = threatBook_lab.get('intel_tags')
                    if intel_tags:
                        msg += '威胁标签: ' + ','.join(threatBook_lab.get('intel_tags')[0].get('tags')) + '\n'
                        msg += '标签类别: ' + threatBook_lab.get('intel_tags')[0].get('tags_type') + '\n'
                    msg += '威胁类型: ' + ','.join(threatBook_lab.get('intel_types')) + '\n'
                    msg += '发现时间: ' + threatBook_lab.get('find_time') + '\n'
                    msg += '更新时间: ' + threatBook_lab.get('update_time') + '\n'
                    msg += '----------\n'
                # 获取运营商
                msg += '服务商: ' + jsonData.get('basic').get('carrier') + '\n'
                # 获取地址
                msg += '所在国家: ' + jsonData.get('basic').get('location').get('country') + '\n'
                msg += '所在省份: ' + jsonData.get('basic').get('location').get('province') + '\n'
                msg += '所在市区: ' + jsonData.get('basic').get('location').get('city') + '\n'
                # 获取最后更新时间
                msg += '最后更新时间: ' + jsonData.get('update_time') + '\n'
                msg += '=========='
                return msg
            else:
                op(f"[-]: 微步威胁IP查询失败, 返回信息：{resp.json()['verbose_msg']}")
                return None
        except Exception as e:
            op(f"[-]: 微步威胁IP查询出现错误, 错误信息：{e}")
            return None

    def getCmd5(self, ciphertext):
        """
        MD5解密接口
        :param ciphertext: 密文
        :return:
        """
        op(f'[*]: 正在调用cMd5解密接口... ...')
        md5Url = self.cmd5Api.format(self.cmd5Email, self.cmd5Key, ciphertext)
        try:
            content = requests.get(url=md5Url).text
            print(content)
            if 'CMD5-ERROR' in content:
                return None
            else:
                return content
        except Exception as e:
            op(f'[-]: 调用CMD5解密接口出现错误, 错误信息: {e}')
            return None

    def getFeishuVuln(self, vulnMsg):
        """
        飞书Wiki Api查询接口
        :param vulnMsg:
        :return:
        """

        def getAccessToken():
            url = 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal'
            data = {
                'app_id': self.feishuConfigData['feishuAppId'],
                'app_secret': self.feishuConfigData['feishuSecret']
            }
            resp = requests.post(url, json=data)
            app_access_token = resp.json()['app_access_token']
            return app_access_token

        def refreshUserToken():
            url = 'https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token'
            headers = {
                'Authorization': 'Bearer ' + getAccessToken()
            }
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.feishuConfigData['feishuRefreshToken'],
            }
            resp = requests.post(url, headers=headers, json=data)
            jsonData = resp.json()
            userToken = jsonData['data']['access_token']
            refreshToken = jsonData['data']['refresh_token']
            newFeishuData = self.feishuConfigData
            newFeishuData['feishuUserToken'] = userToken
            newFeishuData['feishuRefreshToken'] = refreshToken
            Cs.saveFeishuConfigData(newFeishuData)
            return userToken, refreshToken

        def getFinger():
            msg = ''
            vulnName = vulnMsg.strip()
            fingerConfigData = Cs.returnFingerConfigData()
            for fingerName, syntaxData in fingerConfigData.items():
                if vulnName.lower() in fingerName.lower():
                    msg = f'🔏指纹:\n'
                    for engines, syntax in syntaxData.items():
                        msg += f'{engines}: {syntax}\n'
                    msg += '------ ------ ------\n'
                    break
            if not msg:
                msg = '🔏指纹:\n暂无任何指纹, 请补充！！！\n------ ------ ------\n'
            return msg

        data = {
            'query': vulnMsg.strip(),
            'page_size': 50
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.feishuConfigData['feishuUserToken']
        }
        try:
            response = requests.post(self.feishuApi, headers=headers, json=data)
            jsonData = response.json()
            items = jsonData['data']['items']
            returnMsg = f'🔍搜索内容：「{vulnMsg}」\n------ ------ ------\n'
            returnMsg += getFinger()
            for item in items:
                returnMsg += f'{item["title"].strip()}\n{item["url"]}\n\n'
            if not items:
                returnMsg += '🐱‍🐉暂无此漏洞记录！！！'
            return returnMsg.strip()
        except Exception as e:
            op(f'[-]: 调用飞书Wiki Api查询接口出现错误, 错误信息" {e}, 正在尝试重新获取Token... ...')
            refreshUserToken()
            return None


if __name__ == '__main__':
    Pa = PointApi()
    # print(Pa.getAiWenIpv4('117.167.255.42'))
    # print(Pa.getThreatBook('117.167.255.42'))
    # print(Pa.getCmd5('827ccb0eea8a706c4c34a16891f84e7b'))
    # print(Pa.getFeishuVuln('admin'))
