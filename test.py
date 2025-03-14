import sys
import os
import signal
import threading
import queue
import tkinter as tk
from tkinter import scrolledtext
import pystray
from PIL import Image
from cprint import cprint
from BotServer.MainServer import MainServer


class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.queue = queue.Queue()
        self.running = True

    def write(self, string):
        self.queue.put(string)

    def flush(self):
        pass


class BotGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("泉州大圣网络科技有限公司 智能客服系统")
        self.geometry("800x600")

        # 设置程序图标
        icon_path = os.path.abspath("icon.ico")
        try:
            # 为 Windows 设置任务栏图标
            if os.name == 'nt':
                import ctypes
                myappid = 'mycompany.myproduct.subproduct.version'  # 可以自定义
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                self.iconbitmap(default=icon_path)
            else:
                # 为其他系统设置图标
                img = Image.open(icon_path)
                photo = tk.PhotoImage(file=icon_path)
                self.iconphoto(True, photo)
        except Exception as e:
            print(f"设置图标失败: {str(e)}")

        # 初始化界面组件
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill=tk.BOTH)
        # 设置黑色背景和白色字体
        self.text_area.configure(
            state='disabled',
            bg='black',
            fg='white',
            insertbackground='white'  # 光标颜色
        )

        # 重定向标准输出
        sys.stdout = self.redirector = RedirectText(self.text_area)
        sys.stderr = self.redirector

        # 系统托盘相关
        self.tray_icon = None
        self.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)
        self.bind("<Unmap>", self.on_minimize)
        
        # 创建托盘图标
        self.create_tray_icon()

    def create_tray_icon(self):
        if not self.tray_icon:
            image = Image.open("icon.ico")
            menu = pystray.Menu(
                pystray.MenuItem('显示主界面', self.restore_window),
                pystray.MenuItem('退出程序', self.quit_app)
            )
            self.tray_icon = pystray.Icon("bot_icon", image, "Bot Server", menu)
            self.tray_icon.on_double_click = lambda: self.restore_window(None)  # 修改双击事件处理
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_window(self, icon=None):  # 保留这个版本的restore_window
        if self.tray_icon:
            self.deiconify()
            self.state('normal')
            self.focus_force()  # 强制获取焦点

    def minimize_to_tray(self):
        self.withdraw()

    # 删除重复的 restore_window 方法

    def restore_window(self):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.deiconify()
        self.state('normal')

    def signal_handler(self, signum, frame):
        """处理Ctrl+C信号"""
        cprint.warn("\n检测到Ctrl+C，正在关闭程序...")
        self.quit_app()

    def quit_app(self):
        if self.exiting:
            return
        self.exiting = True

        cprint.warn("正在关闭服务...")

        # 停止服务
        try:
            self.ms.Pms.stopPushServer()
        except Exception as e:
            cprint.err(f"停止服务时出错: {str(e)}")

        # 停止托盘图标
        if self.tray_icon:
            self.tray_icon.stop()

        # 关闭窗口
        try:
            self.destroy()
            self.quit()
        except tk.TclError:
            pass

        # 强制退出保证所有线程终止
        os._exit(0)


def convert_ico_to_png():
    try:
        ico = Image.open("icon.ico")
        ico.save("icon.png", "PNG")
    except Exception as e:
        print(f"图标转换失败: {str(e)}")

if __name__ == '__main__':
    convert_ico_to_png()
    app = BotGUI()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.quit_app()