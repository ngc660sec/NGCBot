from BotServer.MainServer import MainServers


class Main:

    def __init__(self):
        self.Ms = MainServers()

    def run(self):
        self.Ms.Bot_start()


if __name__ == '__main__':
    Mn = Main()
    Mn.run()
