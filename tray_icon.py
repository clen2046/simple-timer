# tray_icon.py - 系统托盘集成

import os
import threading
from PIL import Image, ImageDraw
import pystray


class TrayIcon:
    """系统托盘图标管理器"""

    def __init__(self, app_title: str = "简单计时器", icon_path: str = "assets/icon.ico"):
        self.app_title = app_title
        self.icon_path = icon_path
        self.icon: pystray.Icon = None
        self.on_show = None  # 显示主窗口回调
        self.on_quit = None  # 退出应用回调
        self._stop_event = threading.Event()

    def create_icon(self):
        """创建系统托盘图标"""
        try:
            # 加载或创建图标
            image = self._load_or_create_icon()

            # 创建菜单
            menu_items = []

            if self.on_show:
                menu_items.append(
                    pystray.MenuItem("显示主窗口", self._on_show)
                )

            menu_items.append(pystray.Menu.SEPARATOR)

            if self.on_quit:
                menu_items.append(
                    pystray.MenuItem("退出", self._on_quit)
                )

            menu = pystray.Menu(*menu_items)

            # 创建托盘图标
            self.icon = pystray.Icon(self.app_title, image, self.app_title, menu)

        except Exception as e:
            print(f"创建系统托盘图标失败: {e}")
            # 创建备用图标
            self._create_fallback_icon()

    def _load_or_create_icon(self):
        """加载或创建图标图像"""
        try:
            if os.path.exists(self.icon_path):
                # 加载现有图标
                image = Image.open(self.icon_path)
                # 确保图像有alpha通道
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                return image
            else:
                # 创建默认图标（蓝色圆形钟表）
                return self._create_default_icon()
        except Exception as e:
            print(f"加载图标失败 {self.icon_path}: {e}")
            return self._create_default_icon()

    def _create_default_icon(self):
        """创建默认图标（蓝色圆形钟表）"""
        # 创建64x64 RGBA图像
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # 绘制蓝色圆形背景
        bg_color = (70, 130, 180, 255)  # 钢蓝色
        draw.ellipse([(4, 4), (size-4, size-4)], fill=bg_color, outline=(255, 255, 255, 255), width=2)

        # 绘制钟表指针
        center = size // 2
        # 小时指针
        draw.line([(center, center), (center, center - 15)], fill=(255, 255, 255, 255), width=4)
        # 分钟指针
        draw.line([(center, center), (center + 20, center)], fill=(255, 255, 255, 255), width=3)

        # 绘制中心点
        draw.ellipse([(center-3, center-3), (center+3, center+3)], fill=(255, 255, 255, 255))

        return image

    def _create_fallback_icon(self):
        """创建备用图标（简单的红色圆形）"""
        try:
            size = 64
            image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.ellipse([(10, 10), (size-10, size-10)], fill=(255, 0, 0, 255))
            self.icon = pystray.Icon(self.app_title, image, self.app_title)
        except Exception as e:
            print(f"创建备用图标也失败: {e}")

    def run(self):
        """运行系统托盘图标"""
        if self.icon:
            try:
                self.icon.run()
            except Exception as e:
                print(f"运行系统托盘图标失败: {e}")

    def run_in_thread(self):
        """在新线程中运行系统托盘图标"""
        if self.icon:
            thread = threading.Thread(target=self.run, daemon=True)
            thread.start()
            return thread

    def stop(self):
        """停止系统托盘图标"""
        if self.icon:
            try:
                self.icon.stop()
            except Exception as e:
                print(f"停止系统托盘图标失败: {e}")

    def _on_show(self, icon, item):
        """显示主窗口回调"""
        if self.on_show:
            self.on_show()

    def _on_quit(self, icon, item):
        """退出应用回调"""
        if self.on_quit:
            self.on_quit()

    def notify(self, title: str, message: str):
        """显示系统通知"""
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception as e:
                print(f"显示通知失败: {e}")

    def remove_notification(self):
        """移除系统通知"""
        if self.icon:
            try:
                self.icon.remove_notification()
            except Exception as e:
                print(f"移除通知失败: {e}")


if __name__ == "__main__":
    # 测试代码
    import time

    print("测试系统托盘图标...")

    tray = TrayIcon("测试计时器")

    def show_app():
        print("显示主窗口")

    def quit_app():
        print("退出应用")
        tray.stop()

    tray.on_show = show_app
    tray.on_quit = quit_app

    tray.create_icon()

    # 在新线程中运行托盘图标
    tray_thread = tray.run_in_thread()

    print("系统托盘图标已启动，请在系统托盘中查看")
    print("等待10秒...")

    try:
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        tray.stop()
        print("系统托盘图标已停止")