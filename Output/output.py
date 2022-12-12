from termcolor import cprint
import time


def output(msg):
    if "error" in msg or "ERROR" in msg:
        color = "red"
    elif '[*]' in msg:
        color = "blue"
    elif '[+]' in msg:
        color = 'yellow'
    else:
        color = "green"
    time_now = time.strftime("%Y-%m-%d %X")
    cprint(f"[{time_now}]:{msg}", color)
