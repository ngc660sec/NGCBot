from cprint import cprint
import time


def op(msg: str):
    """
    消息输出函数
    :param msg:
    :return:
    """
    now_time = time.strftime("%Y-%m-%d %X")
    if '[*]' in msg:
        cprint.info(f'[{now_time}]: {msg}')
    elif '[+]' in msg:
        cprint.ok(f'[{now_time}]: {msg}')
    elif '[-]' in msg:
        cprint.err(f'[{now_time}]: {msg}')
    elif '[~]' in msg:
        cprint.warn(f'[{now_time}]: {msg}')
    else:
        cprint(f'[{now_time}]: {msg}')
