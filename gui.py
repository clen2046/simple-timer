# gui.py - Tkinter GUI界面

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict, Optional
from alarm_manager import Alarm, AlarmManager
from audio_player import AudioPlayer
from alarm_dialog import AlarmDialog


class TimerGUI:
    """计时器GUI主界面"""

    def __init__(self, alarm_manager: AlarmManager, audio_player: AudioPlayer):
        self.alarm_manager = alarm_manager
        self.audio_player = audio_player
        self.root: Optional[tk.Tk] = None
        self.alarm_frames: List[Dict] = []  # 存储闹钟输入框信息
        self.active_dialogs: List[AlarmDialog] = []  # 存储活动的提醒对话框

        # 设置闹钟触发回调
        self.alarm_manager.on_alarm_trigger = self._on_alarm_trigger

    def create_gui(self):
        """创建主GUI窗口"""
        self.root = tk.Tk()
        self.root.title("简单计时器")
        self.root.geometry("600x450")
        self.root.minsize(500, 350)  # 设置最小尺寸
        self.root.resizable(True, True)  # 允许调整大小

        # 设置图标
        try:
            icon_path = "assets/icon.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass  # 图标设置失败不影响功能

        # 创建GUI组件
        self._create_widgets()

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # 加载现有闹钟
        self._load_existing_alarms()

        return self.root

    def _create_widgets(self):
        """创建所有GUI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="⏰ 简单计时器",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 15))

        # 添加闹钟按钮（放在最上面）
        add_frame = ttk.Frame(main_frame)
        add_frame.pack(fill=tk.X, pady=(0, 10))

        add_btn = ttk.Button(
            add_frame,
            text="+ 添加闹钟",
            command=self._add_alarm_input,
            width=15
        )
        add_btn.pack()

        # === 先pack底部元素，确保它们始终可见 ===

        # 状态栏框架（包含状态文本和控制按钮）
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        # 状态栏
        self.status_var = tk.StringVar(value="状态: 已停止")
        status_bar = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 控制按钮（放在状态栏右侧）
        self.is_running = False  # 跟踪运行状态
        self.toggle_btn = ttk.Button(
            status_frame,
            text="点击启动",
            command=self._on_toggle,
            width=12
        )
        self.toggle_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # 默认音乐设置框架
        music_frame = ttk.LabelFrame(main_frame, text="默认音乐设置", padding="10")
        music_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        self.music_var = tk.StringVar(value="使用默认音乐")
        music_label = ttk.Label(
            music_frame,
            textvariable=self.music_var,
            font=("Arial", 10)
        )
        music_label.pack(side=tk.LEFT, padx=(0, 10))

        select_music_btn = ttk.Button(
            music_frame,
            text="选择音乐文件",
            command=self._select_music_file,
            width=15
        )
        select_music_btn.pack(side=tk.RIGHT)

        # === 最后pack闹钟列表，填充剩余空间 ===

        # 闹钟列表框架
        alarms_frame = ttk.LabelFrame(main_frame, text="闹钟列表", padding="10")
        alarms_frame.pack(fill=tk.BOTH, expand=True)

        # 创建滚动区域
        self._create_scrollable_alarms_frame(alarms_frame)

    def _create_scrollable_alarms_frame(self, parent):
        """创建闹钟列表区域（支持鼠标滚轮）"""
        # 创建Canvas和Scrollbar
        self.alarms_canvas = tk.Canvas(parent)
        self.scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.alarms_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.alarms_canvas)

        # 配置滚动区域
        def update_scrollregion(e=None):
            self.alarms_canvas.configure(scrollregion=self.alarms_canvas.bbox("all"))
            self._check_scroll_needed()

        self.scrollable_frame.bind("<Configure>", update_scrollregion)

        self.alarms_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.alarms_canvas.configure(yscrollcommand=self.scrollbar.set)

        # 绑定鼠标滚轮事件
        def on_mousewheel(event):
            # 只在需要滚动时响应滚轮
            if self._is_scroll_needed():
                self.alarms_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # 绑定到Canvas和scrollable_frame
        self.alarms_canvas.bind("<MouseWheel>", on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", on_mousewheel)

        # 布局
        self.alarms_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 初始检查滚动需求
        self.root.after(100, self._check_scroll_needed)

    def _is_scroll_needed(self) -> bool:
        """检查是否需要滚动条"""
        if not hasattr(self, 'alarms_canvas') or not hasattr(self, 'scrollable_frame'):
            return False

        try:
            # 获取Canvas和scrollable_frame的高度
            self.root.update_idletasks()  # 确保布局已更新
            canvas_height = self.alarms_canvas.winfo_height()
            frame_height = self.scrollable_frame.winfo_height()

            # 如果Canvas高度为0（尚未渲染），返回False
            if canvas_height <= 0:
                return False

            return frame_height > canvas_height
        except Exception:
            # 如果发生任何异常（如widget被销毁），返回False
            return False

    def _check_scroll_needed(self):
        """根据内容高度显示或隐藏滚动条"""
        try:
            if not hasattr(self, 'scrollbar'):
                return

            if self._is_scroll_needed():
                self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                self.scrollbar.pack_forget()
        except Exception:
            # 忽略滚动条更新时的异常
            pass

    def _add_alarm_input(self, time_str: str = "", repeat_daily: bool = True,
                         enabled: bool = True, alarm_id: str = None,
                         audio_file: str = "", message: str = ""):
        """添加闹钟输入行"""
        # 如果没有提供参数且已有闹钟，复制上一个闹钟的设置
        if not time_str and not alarm_id and self.alarm_frames:
            last_alarm = self.alarm_frames[-1]
            time_str = last_alarm['time_var'].get()
            repeat_daily = last_alarm['repeat_var'].get()
            enabled = last_alarm['enabled_var'].get()
            message = last_alarm['message_var'].get()

        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill=tk.X, pady=5, padx=5)

        # 单行布局
        row = ttk.Frame(frame)
        row.pack(fill=tk.X)

        # 解析时间字符串
        if time_str:
            parts = time_str.split(":")
            hour = parts[0] if len(parts) > 0 else "00"
            minute = parts[1] if len(parts) > 1 else "00"
        else:
            hour, minute = "00", "00"

        # 时间选择框架
        time_frame = ttk.Frame(row)
        time_frame.pack(side=tk.LEFT, padx=(0, 8))

        # 阻止Combobox滚轮事件冒泡的函数
        def block_scroll(event):
            return "break"

        # 小时下拉框
        hour_var = tk.StringVar(value=hour)
        hour_combo = ttk.Combobox(
            time_frame,
            textvariable=hour_var,
            values=[f"{i:02d}" for i in range(24)],
            width=3,
            state="readonly"
        )
        hour_combo.pack(side=tk.LEFT)
        hour_combo.bind("<MouseWheel>", block_scroll)

        # 冒号分隔符
        ttk.Label(time_frame, text=":", font=("Arial", 12)).pack(side=tk.LEFT)

        # 分钟下拉框
        minute_var = tk.StringVar(value=minute)
        minute_combo = ttk.Combobox(
            time_frame,
            textvariable=minute_var,
            values=[f"{i:02d}" for i in range(60)],
            width=3,
            state="readonly"
        )
        minute_combo.pack(side=tk.LEFT)
        minute_combo.bind("<MouseWheel>", block_scroll)

        # 创建组合时间变量
        time_var = tk.StringVar(value=f"{hour}:{minute}")

        def update_time_var(*args):
            time_var.set(f"{hour_var.get()}:{minute_var.get()}")

        hour_var.trace_add("write", update_time_var)
        minute_var.trace_add("write", update_time_var)

        # 重复复选框
        repeat_var = tk.BooleanVar(value=repeat_daily)
        repeat_check = ttk.Checkbutton(row, text="重复", variable=repeat_var)
        repeat_check.pack(side=tk.LEFT, padx=(0, 5))

        # 启用复选框
        enabled_var = tk.BooleanVar(value=enabled)
        enabled_check = ttk.Checkbutton(row, text="启用", variable=enabled_var)
        enabled_check.pack(side=tk.LEFT, padx=(0, 8))

        # 提醒内容（放在右侧，占据剩余空间）
        message_var = tk.StringVar(value=message)
        message_entry = ttk.Entry(row, textvariable=message_var)
        message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        # 添加占位符效果
        placeholder_text = "请输入提醒内容"

        def on_focus_in(event):
            if message_entry.get() == placeholder_text:
                message_entry.delete(0, tk.END)
                message_entry.configure(style="TEntry")

        def on_focus_out(event):
            if not message_entry.get():
                message_entry.insert(0, placeholder_text)
                message_entry.configure(style="Placeholder.TEntry")

        # 创建占位符样式（灰色文字）
        style = ttk.Style()
        style.configure("Placeholder.TEntry", foreground="gray")

        # 初始化占位符
        if not message:
            message_entry.insert(0, placeholder_text)
            message_entry.configure(style="Placeholder.TEntry")

        message_entry.bind("<FocusIn>", on_focus_in)
        message_entry.bind("<FocusOut>", on_focus_out)

        # 删除按钮
        delete_btn = ttk.Button(
            row,
            text="删除",
            command=lambda f=frame: self._remove_alarm_input(f),
            width=5
        )
        delete_btn.pack(side=tk.RIGHT)

        # 分隔线
        separator = ttk.Separator(frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(5, 0))

        # 音频变量（保留但不显示，统一使用默认音乐）
        audio_var = tk.StringVar(value="")

        # 保存闹钟信息
        frame.alarm_data = {
            'frame': frame,
            'time_var': time_var,
            'repeat_var': repeat_var,
            'enabled_var': enabled_var,
            'audio_var': audio_var,
            'message_var': message_var,
            'alarm_id': alarm_id
        }

        self.alarm_frames.append(frame.alarm_data)

        # 如果是新增闹钟（不是加载现有闹钟），立即保存
        if alarm_id is None:
            self._save_all_alarms()

        # 更新滚动条状态
        self.root.after(100, self._check_scroll_needed)

    def _select_music_file(self):
        """选择全局默认音乐文件"""
        file_path = filedialog.askopenfilename(
            title="选择默认闹钟音乐",
            filetypes=[
                ("音频文件", "*.mp3 *.wav *.ogg *.flac"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.audio_player.default_audio_path = file_path
            self.music_var.set(f"音乐: {os.path.basename(file_path)}")

    def _remove_alarm_input(self, frame):
        """删除闹钟输入行"""
        # 从alarm_frames列表中删除
        alarm_id = None
        for i, alarm_data in enumerate(self.alarm_frames):
            if alarm_data['frame'] == frame:
                alarm_id = alarm_data.get('alarm_id')
                del self.alarm_frames[i]
                break

        frame.destroy()

        # 如果有关联的闹钟ID，从管理器删除
        if alarm_id:
            self.alarm_manager.remove_alarm(alarm_id)

        # 更新滚动条状态
        self.root.after(100, self._check_scroll_needed)

    def _load_existing_alarms(self):
        """加载现有闹钟到GUI"""
        for alarm in self.alarm_manager.alarms.values():
            self._add_alarm_input(
                time_str=alarm.time_str,
                repeat_daily=alarm.repeat_daily,
                enabled=alarm.enabled,
                alarm_id=alarm.id,
                audio_file=alarm.audio_file or "",
                message=alarm.message or ""
            )

    def _validate_time_format(self, time_str: str) -> bool:
        """验证时间格式（HH:MM）"""
        try:
            from datetime import datetime
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False

    def _save_all_alarms(self):
        """保存所有闹钟设置"""
        # 占位符文本（不应保存）
        placeholder_text = "请输入提醒内容"

        # 在锁内更新闹钟管理器中的闹钟
        with self.alarm_manager.lock:
            # 清除所有现有闹钟
            self.alarm_manager.alarms.clear()

            # 重新添加所有GUI中的闹钟
            for alarm_data in self.alarm_frames:
                time_str = alarm_data['time_var'].get()
                repeat_daily = alarm_data['repeat_var'].get()
                enabled = alarm_data['enabled_var'].get()
                audio_file = alarm_data['audio_var'].get() or None
                message = alarm_data['message_var'].get() or ""

                # 如果是占位符文本，清空
                if message == placeholder_text:
                    message = ""

                # 验证时间格式
                if not self._validate_time_format(time_str):
                    continue  # 跳过无效的时间

                # 使用现有ID或生成新ID
                alarm_id = alarm_data['alarm_id']
                if not alarm_id:
                    import uuid
                    alarm_id = str(uuid.uuid4())
                    alarm_data['alarm_id'] = alarm_id

                # 创建闹钟对象
                alarm = Alarm(
                    alarm_id=alarm_id,
                    time_str=time_str,
                    repeat_daily=repeat_daily,
                    enabled=enabled,
                    audio_file=audio_file,
                    message=message
                )
                self.alarm_manager.alarms[alarm_id] = alarm

        self.alarm_manager.save_alarms()

    def _on_toggle(self):
        """启动/关闭按钮点击事件"""
        if self.is_running:
            # 关闭
            self.alarm_manager.stop()
            self.is_running = False
            self.toggle_btn.config(text="点击启动")
            self.status_var.set("状态: 已停止")
        else:
            # 启动
            # 保存所有闹钟设置
            self._save_all_alarms()

            # 检查是否至少有一个闹钟
            if not self.alarm_frames:
                messagebox.showwarning("警告", "请先添加至少一个闹钟")
                return

            # 启动闹钟管理器
            self.alarm_manager.start()
            self.is_running = True
            self.toggle_btn.config(text="点击关闭")
            self.status_var.set("状态: 运行中")

    def _on_alarm_trigger(self, alarm: Alarm):
        """闹钟触发回调"""
        # 在主线程中创建提醒对话框
        self.root.after(0, self._show_alarm_dialog, alarm)

    def _show_alarm_dialog(self, alarm: Alarm):
        """显示闹钟提醒对话框"""
        dialog = AlarmDialog(self.root, alarm, self.audio_player)
        self.active_dialogs.append(dialog)

        # 对话框关闭时从列表中移除
        def on_dialog_close():
            if dialog in self.active_dialogs:
                self.active_dialogs.remove(dialog)

        dialog.window.protocol("WM_DELETE_WINDOW", lambda: [dialog._on_close(), on_dialog_close()])

    def _on_window_close(self):
        """窗口关闭事件"""
        # 保存设置
        self._save_all_alarms()

        # 注意：不停止闹钟管理器和音频播放器，保持后台运行
        # 关闭所有提醒对话框
        for dialog in self.active_dialogs[:]:
            try:
                dialog.window.destroy()
            except:
                pass

        # 隐藏窗口（不退出，进入系统托盘）
        self.root.withdraw()

    def show_window(self):
        """显示主窗口"""
        if self.root:
            self.root.deiconify()  # 显示窗口
            self.root.lift()       # 置顶
            self.root.focus_force()  # 获取焦点


if __name__ == "__main__":
    # 测试代码
    from alarm_manager import AlarmManager
    from audio_player import AudioPlayer

    print("测试GUI界面...")

    # 初始化管理器
    alarm_manager = AlarmManager("test_gui_alarms.json")
    alarm_manager.load_alarms()

    # 初始化音频播放器
    audio_player = AudioPlayer()

    # 创建GUI
    gui = TimerGUI(alarm_manager, audio_player)
    root = gui.create_gui()

    print("GUI已创建，显示窗口...")
    print("请测试添加闹钟、开始、暂停等功能")

    root.mainloop()

    print("GUI测试完成")
    alarm_manager.stop()
    audio_player.cleanup()