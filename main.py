from BotServer.MainServer import MainServers


class Main:
    def __init__(self):
        # 实例化主服务类
        self.Mser = MainServers()

    def main(self, ):
        self.Mser.Robot_start()


if __name__ == '__main__':
    Mn = Main()
    Mn.main()
