from BotServer.MainServer import MainServer
from cprint import cprint
import signal
import time
import sys

Bot_Logo = """
███▄▄▄▄      ▄██████▄   ▄████████ ▀█████████▄   ▄██████▄      ███     
███▀▀▀██▄   ███    ███ ███    ███   ███    ███ ███    ███ ▀█████████▄ 
███   ███   ███    █▀  ███    █▀    ███    ███ ███    ███    ▀███▀▀██ 
███   ███  ▄███        ███         ▄███▄▄▄██▀  ███    ███     ███   ▀ 
███   ███ ▀▀███ ████▄  ███        ▀▀███▀▀▀██▄  ███    ███     ███     
███   ███   ███    ███ ███    █▄    ███    ██▄ ███    ███     ███     
███   ███   ███    ███ ███    ███   ███    ███ ███    ███     ███     
 ▀█   █▀    ████████▀  ████████▀  ▄█████████▀   ▀██████▀     ▄████▀   
     Version: V2.3
     Author: NGC660安全实验室(eXM/云山) 
"""


def shutdown(signum, frame):
    Ms.Pms.stopPushServer()
    Ms.stopWebServer()
    time.sleep(2)
    sys.exit(0)


if __name__ == '__main__':
    cprint.info(Bot_Logo.strip())
    Ms = MainServer()
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    try:
        Ms.processMsg()
    except KeyboardInterrupt:
        shutdown(signal.SIGINT, None)
