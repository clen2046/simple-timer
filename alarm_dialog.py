# alarm_dialog.py - 提醒窗口

import tkinter as tk
from tkinter import ttk
from alarm_manager import Alarm
from audio_player import AudioPlayer


class AlarmDialog:
    """闹钟提醒对话框"""

    def __init__(self, parent, alarm: Alarm, audio_player: AudioPlayer):
        self.parent = parent
        self.alarm = alarm
        self.audio_player = audio_player

        # 创建独立窗口
        self.window = tk.Toplevel(parent)
        self.window.title("闹钟提醒")
        self.window.geometry("400x250")
        self.window.resizable(False, False)

        # 设置窗口置顶
        self.window.attributes('-topmost', True)

        # 绑定关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # 阻止用户通过Alt+F4等关闭窗口
        self.window.bind("<Alt-F4>", lambda e: "break")

        self._create_widgets()

        # 将窗口居中显示
        self._center_window()

        # 开始播放闹钟音乐
        self.audio_player.play_alarm(self.alarm.audio_file)

    def _create_widgets(self):
        """创建对话框控件"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="⏰ 闹钟提醒",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))

        # 时间信息
        time_label = ttk.Label(
            main_frame,
            text=f"时间: {self.alarm.time_str}",
            font=("Arial", 14)
        )
        time_label.pack(pady=5)

        # 提醒内容（如果有）
        if self.alarm.message:
            message_label = ttk.Label(
                main_frame,
                text=self.alarm.message,
                font=("Arial", 14),
                wraplength=350
            )
            message_label.pack(pady=10)

        # 分隔线
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)

        # 停止按钮
        stop_btn = ttk.Button(
            main_frame,
            text="停止闹钟",
            command=self._on_close,
            width=15
        )
        stop_btn.pack()

        # 设置焦点到停止按钮
        stop_btn.focus_set()

        # 绑定回车键到停止按钮
        self.window.bind('<Return>', lambda e: self._on_close())

    def _center_window(self):
        """将窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def _on_close(self):
        """关闭对话框"""
        # 停止播放音乐
        self.audio_player.stop()

        # 关闭窗口
        self.window.destroy()

    def wait_for_close(self):
        """等待窗口关闭"""
        self.window.grab_set()  # 模态窗口
        self.parent.wait_window(self.window)


if __name__ == "__main__":
    # 测试代码
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 创建测试闹钟
    test_alarm = Alarm(
        alarm_id="test_id",
        time_str="14:30",
        repeat_daily=True,
        enabled=True,
        audio_file=None,
        message="测试提醒内容"
    )

    # 创建音频播放器
    from audio_player import AudioPlayer
    player = AudioPlayer()

    # 创建提醒对话框
    dialog = AlarmDialog(root, test_alarm, player)

    print("显示提醒窗口...")
    print("请关闭窗口以继续")

    # 等待窗口关闭
    dialog.wait_for_close()

    print("窗口已关闭")
    root.destroy()