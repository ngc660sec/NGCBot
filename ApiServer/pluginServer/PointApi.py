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
        self.gaoDeApi = configData['FunctionConfig']['PointFunctionConfig']['AiWenIpConfig']['gaoDeApi']
        self.gaoDeKey = configData['KeyConfig']['GaoDeConfig']['GaoDeKey']
        # 埃文配置
        self.aiWenApi = configData['FunctionConfig']['PointFunctionConfig']['AiWenIpConfig']['AiWenApi']
        self.aiWenKey = configData['KeyConfig']['AiWenConfig']['AiWenKey']
        # Cmd5配置
        self.cmd5Api = configData['FunctionConfig']['PointFunctionConfig']['Cmd5Config']['Cmd5Api']
        self.cmd5Email = configData['KeyConfig']['Cmd5Config']['Cmd5Email']
        self.cmd5Key = configData['KeyConfig']['Cmd5Config']['Cmd5Key']


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


if __name__ == '__main__':
    Pa = PointApi()
    print(Pa.getAiWenIpv4('117.167.255.42'))
    # print(Pa.getCmd5('827ccb0eea8a706c4c34a16891f84e7b'))
    # print(Pa.getFeishuVuln('admin'))
