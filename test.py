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
        self.title("即推智能客服系统")
        self.geometry("800x600")

        # 设置程序图标
        icon_path = os.path.abspath("./_internal/FileCache/icon.ico")
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

        # 服务控制
        self.ms = MainServer()
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()

        # 退出控制
        self.exiting = False
        signal.signal(signal.SIGINT, self.signal_handler)  # 注册Ctrl+C处理

        # 启动输出监控
        self.after(100, self.update_output)

        # 显示 Logo
        self.show_logo()

    def show_logo(self):
        Bot_Logo = """
        Author: 泉州大圣网络科技有限公司         
        """
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, Bot_Logo.strip() + "\n")
        self.text_area.configure(state='disabled')

    def run_server(self):
        try:
            self.ms.processMsg()
        except Exception as e:
            cprint.err(f"服务异常: {str(e)}")
            self.quit_app()

    def update_output(self):
        while not self.redirector.queue.empty():
            string = self.redirector.queue.get()
            self.text_area.configure(state='normal')
            self.text_area.insert(tk.END, string)
            self.text_area.see(tk.END)
            self.text_area.configure(state='disabled')
        self.after(100, self.update_output)

    def on_minimize(self, event):
        if self.state() == 'iconic':
            self.minimize_to_tray()

    def minimize_to_tray(self):
        self.withdraw()

    def create_tray_icon(self):
        if not self.tray_icon:
            try:
                # 确保使用绝对路径
                icon_path = os.path.abspath("./_internal/FileCache/icon.ico")
                image = Image.open(icon_path)
                menu = pystray.Menu(
                    # 修改此处菜单项，添加default参数作为默认点击事件
                    pystray.MenuItem('显示主界面', self.restore_window, default=True),  # 默认单击事件
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem('退出程序', self.quit_app)
                )
                self.tray_icon = pystray.Icon("bot_icon", image, "即推智能客服系统", menu)
                # 删除原来的Windows点击事件处理
                threading.Thread(target=self.tray_icon.run, daemon=True).start()
            except Exception as e:
                print(f"创建托盘图标失败: {str(e)}")

    # 删除原有的on_tray_click方法
    def restore_window(self, icon=None):
        try:
            self.deiconify()
            self.state('normal')
            self.focus_force()
            # Windows下额外处理
            if os.name == 'nt':
                self.lift()  # 将窗口提升到最前
                self.attributes('-topmost', True)  # 设置为顶层窗口
                self.attributes('-topmost', False)  # 取消顶层窗口
        except Exception as e:
            print(f"恢复窗口失败: {str(e)}")

    def on_tray_click(self, icon, button):
        # 左键单击或双击都显示主界面
        if button == pystray.mouse.Button.left:
            self.restore_window()

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
        ico = Image.open("./_internal/FileCache/icon.ico")
    except Exception as e:
        print(f"图标转换失败: {str(e)}")


if __name__ == '__main__':
    # 单实例检测（新增代码）
    try:
        lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lock_socket.bind(('127.0.0.1', 65432))  # 使用固定端口检测
    except socket.error:
        cprint.err("程序已在运行，请勿重复启动！")
        sys.exit(1)

    convert_ico_to_png()
    app = BotGUI()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.quit_app()
    finally:  # 新增finally块
        lock_socket.close()  # 程序退出时释放端口
