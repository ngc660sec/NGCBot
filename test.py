import sys
import os
import signal
import threading
import queue
import tkinter as tk
from tkinter import scrolledtext, messagebox
import tkinter.ttk as ttk  # 正确导入ttk模块
import pystray
from PIL import Image
from cprint import cprint
from BotServer.MainServer import MainServer
import socket
import requests
import zipfile
import shutil
import subprocess
import time
import concurrent.futures  # 添加并发库


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

        # 更新配置
        self.update_url = "http://127.0.0.1:8001/main.zip"  # 请替换为您的实际更新地址

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
                    pystray.MenuItem('检查更新', self.check_for_updates),  # 添加更新选项
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem('退出程序', self.quit_app)
                )
                self.tray_icon = pystray.Icon("bot_icon", image, "即推智能客服系统", menu)
                # 删除原来的Windows点击事件处理
                threading.Thread(target=self.tray_icon.run, daemon=True).start()
            except Exception as e:
                print(f"创建托盘图标失败: {str(e)}")

    def check_for_updates(self, icon=None):
        """检查并执行更新"""
        try:
            # 显示主窗口并提示用户
            self.restore_window()
            result = messagebox.askyesno("更新确认", "将从服务器下载最新版本并更新程序，继续吗？")
            if not result:
                return

            # 创建临时目录
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__).replace('_internal', '')), "temp_update")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # 下载更新文件
            cprint.info("正在下载更新文件...")
            zip_path = self.download_update(self.update_url, temp_dir)

            # 准备更新脚本
            update_script = self.prepare_update_script(temp_dir, zip_path)

            # 退出当前程序并执行更新
            cprint.info("准备更新，程序将重启...")
            time.sleep(2)
            self.execute_update(update_script)

        except Exception as e:
            cprint.err(f"更新过程中出错: {str(e)}")
            messagebox.showerror("更新失败", f"更新过程中出错: {str(e)}")

    def download_update(self, url, temp_dir):
        """下载更新文件"""
        try:
            zip_path = os.path.join(temp_dir, "update.zip")

            # 获取文件大小
            response = requests.head(url)
            total_size = int(response.headers.get('content-length', 0))

            # 创建进度条窗口
            progress_window = tk.Toplevel(self)
            progress_window.title("下载进度")
            progress_window.geometry("400x100")
            progress_window.resizable(False, False)
            progress_window.transient(self)  # 设置为主窗口的临时窗口

            # 进度标签
            progress_label = tk.Label(progress_window, text="正在下载更新文件...")
            progress_label.pack(pady=10)

            # 进度条
            progress_bar = ttk.Progressbar(progress_window, length=350, mode="determinate")
            progress_bar.pack(pady=10)

            # 已下载大小和更新锁
            downloaded = [0]
            lock = threading.Lock()
            download_complete = threading.Event()  # 添加事件标志来表示下载完成

            # 更新进度条的函数
            def update_progress():
                percent = int(downloaded[0] / total_size * 100) if total_size > 0 else 0
                progress_bar["value"] = percent
                progress_label.config(
                    text=f"正在下载更新文件... {percent}% ({downloaded[0] / 1024 / 1024:.2f}MB/{total_size / 1024 / 1024:.2f}MB)")
                progress_window.update()

            # 简化下载方法，不使用分块下载
            try:
                with requests.get(url, stream=True) as response:
                    response.raise_for_status()
                    with open(zip_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024 * 1024):  # 使用1MB的块
                            if chunk:
                                f.write(chunk)
                                with lock:
                                    downloaded[0] += len(chunk)
                                    update_progress()
            except Exception as e:
                progress_window.destroy()
                raise Exception(f"下载文件时出错: {str(e)}")

            # 最终更新进度条
            progress_bar["value"] = 100
            progress_label.config(
                text=f"下载完成! 100% ({total_size / 1024 / 1024:.2f}MB/{total_size / 1024 / 1024:.2f}MB)")
            progress_window.update()

            # 确保进度窗口被销毁
            self.after(500, progress_window.destroy)  # 使用after方法确保在主线程中销毁窗口

            return zip_path
        except Exception as e:
            raise Exception(f"下载更新文件失败: {str(e)}")

    def prepare_update_script(self, temp_dir, zip_path):
        """准备更新脚本"""
        current_dir = os.path.dirname(os.path.abspath(__file__).replace('_internal', ''))
        
        # 只使用批处理脚本
        update_script = os.path.join(temp_dir, "update.bat")
        
        # 使用UTF-8编码写入批处理文件，但避免使用中文注释
        with open(update_script, 'w', encoding='utf-8') as f:
            f.write(f"""@echo off
chcp 65001 >nul
echo Waiting for program to exit...
timeout /t 2 /nobreak > nul

echo Extracting update files...
cd /d "{temp_dir}"
if exist extracted rmdir /S /Q extracted
mkdir extracted

echo Using PowerShell to extract files...
powershell -Command "Expand-Archive -Path '{zip_path}' -DestinationPath '{temp_dir}\\extracted' -Force"

echo Checking extraction results...
if not exist "{temp_dir}\\extracted\\*.*" (
    echo Extraction failed, trying alternative method...
    powershell -Command "$shell = New-Object -ComObject Shell.Application; $zip = $shell.NameSpace('{zip_path}'); $dest = $shell.NameSpace('{temp_dir}\\extracted'); $dest.CopyHere($zip.Items())"
    timeout /t 3 /nobreak > nul
)

echo Listing extracted files:
dir "{temp_dir}\\extracted" /b

if not exist "{temp_dir}\\extracted\\*.*" (
    echo Extraction failed, no files found
    echo Creating error message dialog...
    echo MsgBox "Update failed: Could not extract any files from the update package.", 16, "Update Failed" > "{temp_dir}\\error.vbs"
    start "" "{temp_dir}\\error.vbs"
    exit /b 1
)

echo Updating files...
echo Source: {temp_dir}\\extracted
echo Target: {current_dir}

rem 直接复制根目录文件，不使用复杂的脚本，失败时继续
echo Copying root files directly...
for %%f in ({temp_dir}\\extracted\\*.*) do (
    echo Copying root file: %%f to {current_dir}\\%%~nxf
    copy "%%f" "{current_dir}\\%%~nxf" /Y
    if errorlevel 1 (
        echo Warning: Failed to copy %%f, continuing with next file...
    )
)

rem 复制所有子目录，失败时继续
echo Copying all subdirectories...
for /D %%d in ({temp_dir}\\extracted\\*) do (
    echo Copying directory: %%d to {current_dir}\\%%~nxd
    if not exist "{current_dir}\\%%~nxd" mkdir "{current_dir}\\%%~nxd"
    xcopy "%%d" "{current_dir}\\%%~nxd" /E /Y /I /C
    if errorlevel 1 (
        echo Warning: Some files in directory %%d may not have been copied, continuing...
    )
)

echo Cleaning up temporary files...
rmdir /S /Q "{temp_dir}\\extracted"
del "{zip_path}"

echo Update completed! Please restart the program manually.
echo Creating success message dialog...
echo MsgBox "Update completed successfully. Please restart the application manually.", 64, "Update Successful" > "{temp_dir}\\success.vbs"
start "" "{temp_dir}\\success.vbs"
pause
exit
""")
            
        return update_script

    def execute_update(self, update_script):
        """退出当前程序并执行更新脚本"""
        # 启动更新脚本 - 只使用Windows批处理方式
        if os.name == 'nt':  # Windows
            # 直接使用cmd调用批处理文件，不使用特殊标志
            subprocess.Popen(["cmd.exe", "/c", "start", "/wait", update_script])
        else:  # macOS/Linux - 提示不支持
            messagebox.showwarning("更新提示", "自动更新功能仅支持Windows系统，请手动更新。")
            return

        # 退出当前程序
        self.quit_app()

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
