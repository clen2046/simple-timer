# main.py - 简单计时器应用入口

import os
import sys
import threading
from alarm_manager import AlarmManager
from audio_player import AudioPlayer
from gui import TimerGUI
from tray_icon import TrayIcon


def main():
    """应用主入口"""
    print("启动简单计时器...")

    # 创建必要的目录
    os.makedirs("assets", exist_ok=True)
    os.makedirs("config", exist_ok=True)

    # 初始化管理器
    alarm_manager = AlarmManager("config/alarms.json")
    alarm_manager.load_alarms()

    # 初始化音频播放器
    audio_player = AudioPlayer()

    # 初始化GUI
    gui = TimerGUI(alarm_manager, audio_player)
    root = gui.create_gui()

    # 初始化系统托盘
    tray_icon = TrayIcon("简单计时器", "assets/icon.ico")
    tray_icon.on_show = gui.show_window
    tray_icon.on_quit = lambda: _quit_app(root, alarm_manager, audio_player, tray_icon)
    tray_icon.create_icon()

    # 启动系统托盘（在单独线程中）
    tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
    tray_thread.start()

    # 设置窗口关闭事件（最小化到托盘）
    def on_window_close():
        # 保存设置
        gui._save_all_alarms()

        # 注意：不停止闹钟管理器和音频播放器，保持后台运行
        # 隐藏窗口（不退出，进入系统托盘）
        root.withdraw()

        # 显示托盘通知
        tray_icon.notify("简单计时器", "程序已最小化到系统托盘")

    root.protocol("WM_DELETE_WINDOW", on_window_close)

    # 启动GUI主循环
    try:
        print("应用程序已启动")
        root.mainloop()
    except KeyboardInterrupt:
        print("收到中断信号，退出应用...")
        _quit_app(root, alarm_manager, audio_player, tray_icon)
    except Exception as e:
        print(f"应用程序错误: {e}")
        _quit_app(root, alarm_manager, audio_player, tray_icon)


def _quit_app(root, alarm_manager, audio_player, tray_icon):
    """退出应用"""
    print("正在退出应用...")

    # 停止所有组件
    try:
        alarm_manager.stop()
    except Exception as e:
        print(f"停止闹钟管理器失败: {e}")

    try:
        audio_player.stop()
        audio_player.cleanup()
    except Exception as e:
        print(f"停止音频播放器失败: {e}")

    try:
        tray_icon.stop()
    except Exception as e:
        print(f"停止系统托盘失败: {e}")

    # 销毁窗口
    if root:
        try:
            root.quit()
            root.destroy()
        except Exception as e:
            print(f"销毁窗口失败: {e}")

    print("应用已退出")


if __name__ == "__main__":
    main()