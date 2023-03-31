from Output.output import output
import os


class Cache_Server:

    def __init__(self):
        # 配置缓存文件存放路径
        current_path = os.path.dirname(__file__)
        self.video_cache = current_path + '/Video_Cache'
        self.fish_cache = current_path + '/Fish_Cache'
        self.pic_cache = current_path + '/Pic_Cache'
        self.create_folder()

    def delete_file(self):
        output('[+]:缓存清除功能工作中... ...')
        if os.path.exists(self.video_cache):
            try:
                file_lists = list()
                file_lists += [self.video_cache + '/' + file for file in os.listdir(self.video_cache)]
                file_lists += [self.fish_cache + '/' + file for file in os.listdir(self.fish_cache)]
                file_lists += [self.pic_cache + '/' + file for file in os.listdir(self.pic_cache)]
                for rm_file in file_lists:
                    os.remove(rm_file)
            except Exception as e:
                msg = "[ERROR]:清除缓存时出错，错误信息：{}".format(e)
                output(msg)
                return msg
            msg = "缓存文件已清除!"
            return msg
        else:
            msg = "[-]:缓存文件夹未创建,正在创建缓存文件夹... ..."
            output(msg)
            self.create_folder()

    def create_folder(self):
        if not os.path.exists(self.video_cache):
            try:
                os.mkdir(self.video_cache)
                os.mkdir(self.pic_cache)
                os.mkdir(self.fish_cache)
            except Exception as e:
                msg = '[ERROR]:创建文件夹出错，错误信息：{}'.format(e)
                output(msg)


if __name__ == '__main__':
    Fs = Cache_Server()
    # # Fs.create_folder()
    Fs.delete_file()

