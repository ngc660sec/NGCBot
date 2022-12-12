from Output.output import output
import yaml
import os


class File_server:

    def __init__(self):
        # 配置缓存文件存放路径
        self.girl_videos = 'file/girl_pic'
        self.touch_fishes = 'file/girl_video'
        self.girl_pics = 'file/touch_fish'

    def delete_file(self):
        output('[*] >> 缓存清除功能工作中... ...')
        if os.path.exists(self.girl_videos):
            try:
                file_lists = list()
                file_lists += [self.touch_fishes + '/' + file for file in os.listdir(self.touch_fishes)]
                file_lists += [self.girl_videos + '/' + file for file in os.listdir(self.girl_videos)]
                file_lists += [self.girl_pics + '/' + file for file in os.listdir(self.girl_pics)]
                for rm_file in file_lists:
                    os.remove(rm_file)
            except Exception as e:
                msg = "[ERROR] >> 清除缓存时出错，错误信息：{}".format(e)
                output(msg)
                return msg
            msg = "[*] >> 缓存文件已清除!"
            output(msg)
            return msg
        else:
            msg = "[ERROR] >> 缓存文件夹未创建!"
            output(msg)
            return msg

    def create_folder(self):
        if not os.path.exists(self.girl_videos):
            try:
                os.mkdir(self.girl_videos)
                os.mkdir(self.touch_fishes)
                os.mkdir(self.girl_pics)
            except Exception as e:
                msg = '[ERROR] >> 创建文件夹出错，错误信息：{}'.format(e)
                output(msg)
                return msg
            msg = '[*] >> 所有文件已删除!'
            output(msg)
            return msg
        else:
            msg = '[*] >> 缓存文件夹已创建!... ...'
            output(msg)


if __name__ == '__main__':
    Fs = File_server()
    # # Fs.create_folder()
    Fs.delete_file()
    # current_path = os.path.dirname(__file__)
    # lis = os.listdir(current_path)
    # for li in lis:
    #     if os.path.isdir(li):
    #         path = current_path + '/' + li
    #         if os.path.exists(path):
    #             print(path)

