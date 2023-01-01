from termcolor import cprint
import time


def output(msg):
    if "error" in msg or "ERROR" in msg:
        color = "red"
    elif '[*]' in msg:
        color = "cyan"
    elif '[+]' in msg:
        color = 'yellow'
    else:
        color = "magenta"
    time_now = time.strftime("%Y-%m-%d %X")
    cprint(f"[{time_now}]:{msg}", color)


output('')
