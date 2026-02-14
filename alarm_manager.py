# alarm_manager.py - 闹钟管理核心逻辑

import json
import os
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, Optional, Callable


class Alarm:
    """单个闹钟"""

    def __init__(self, alarm_id: str, time_str: str, repeat_daily: bool = True,
                 enabled: bool = True, audio_file: str = None, message: str = ""):
        self.id = alarm_id  # UUID
        self.time_str = time_str  # "HH:MM"格式
        self.repeat_daily = repeat_daily
        self.enabled = enabled
        self.audio_file = audio_file  # None表示使用默认音乐
        self.message = message  # 提醒内容
        # 初始化last_triggered为当前时间的整分钟（避免立即触发）
        now = datetime.now()
        # 设置为当前分钟的起始（秒和微秒归零）
        self.last_triggered = datetime(now.year, now.month, now.day, now.hour, now.minute, 0, 0)
        # 线程锁，保护should_trigger方法的并发访问
        self.lock = threading.RLock()

    @property
    def time(self):
        """解析时间字符串为datetime.time对象"""
        try:
            return datetime.strptime(self.time_str, "%H:%M").time()
        except ValueError:
            # 如果时间格式无效，返回默认时间（午夜）并记录错误
            print(f"警告：无效的时间格式 '{self.time_str}'，使用00:00代替")
            return datetime.strptime("00:00", "%H:%M").time()

    def should_trigger(self, current_time: datetime) -> bool:
        """检查是否应该触发闹钟"""
        with self.lock:
            if not self.enabled:
                return False

            current_time_only = current_time.time()
            alarm_time = self.time

            # 检查时间是否匹配
            time_matches = (current_time_only.hour == alarm_time.hour and
                           current_time_only.minute == alarm_time.minute)

            if not time_matches:
                return False

            # 检查是否已经触发过
            if self.last_triggered:
                # 如果是非重复闹钟，只触发一次
                if not self.repeat_daily:
                    return False

                # 重复闹钟：检查是否在同一天同一分钟已经触发过
                if (self.last_triggered.date() == current_time.date() and
                    self.last_triggered.hour == current_time.hour and
                    self.last_triggered.minute == current_time.minute):
                    return False

            # 记录触发时间
            self.last_triggered = current_time
            return True

    def to_dict(self) -> dict:
        """转换为字典用于序列化"""
        return {
            'id': self.id,
            'time_str': self.time_str,
            'repeat_daily': self.repeat_daily,
            'enabled': self.enabled,
            'audio_file': self.audio_file,
            'message': self.message
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Alarm':
        """从字典创建Alarm实例"""
        return cls(
            alarm_id=data.get('id', str(uuid.uuid4())),
            time_str=data['time_str'],
            repeat_daily=data.get('repeat_daily', True),
            enabled=data.get('enabled', True),
            audio_file=data.get('audio_file'),
            message=data.get('message', '')
        )


class AlarmManager:
    """闹钟管理器"""

    def __init__(self, config_file: str = "config/alarms.json"):
        self.alarms: Dict[str, Alarm] = {}
        self.config_file = config_file
        self.running = False
        self.paused = False
        self.check_thread: Optional[threading.Thread] = None
        self.on_alarm_trigger: Optional[Callable[[Alarm], None]] = None  # 回调函数
        self.lock = threading.RLock()  # 可重入线程锁，保护alarms字典

        # 确保配置文件目录存在
        config_dir = os.path.dirname(config_file)
        if config_dir:  # 只有当目录名非空时才创建
            os.makedirs(config_dir, exist_ok=True)

    def add_alarm(self, time_str: str, repeat_daily: bool = True,
                  audio_file: str = None) -> str:
        """添加新闹钟"""
        alarm_id = str(uuid.uuid4())
        alarm = Alarm(alarm_id, time_str, repeat_daily, True, audio_file)
        with self.lock:
            self.alarms[alarm_id] = alarm
        self.save_alarms()
        return alarm_id

    def remove_alarm(self, alarm_id: str) -> bool:
        """删除闹钟"""
        with self.lock:
            if alarm_id in self.alarms:
                del self.alarms[alarm_id]
                self.save_alarms()
                return True
        return False

    def toggle_alarm(self, alarm_id: str) -> bool:
        """切换闹钟启用状态"""
        with self.lock:
            if alarm_id in self.alarms:
                self.alarms[alarm_id].enabled = not self.alarms[alarm_id].enabled
                self.save_alarms()
                return self.alarms[alarm_id].enabled
        return False

    def update_alarm(self, alarm_id: str, time_str: str = None,
                     repeat_daily: bool = None, enabled: bool = None,
                     audio_file: str = None) -> bool:
        """更新闹钟属性"""
        with self.lock:
            if alarm_id not in self.alarms:
                return False

            alarm = self.alarms[alarm_id]

            if time_str is not None:
                alarm.time_str = time_str
            if repeat_daily is not None:
                alarm.repeat_daily = repeat_daily
            if enabled is not None:
                alarm.enabled = enabled
            if audio_file is not None:
                alarm.audio_file = audio_file

        self.save_alarms()
        return True

    def start(self):
        """启动闹钟检查线程"""
        if self.running:
            return

        self.running = True
        self.paused = False
        self.check_thread = threading.Thread(target=self._check_alarms, daemon=True)
        self.check_thread.start()

    def pause(self):
        """暂停闹钟检查"""
        self.paused = True

    def resume(self):
        """恢复闹钟检查"""
        self.paused = False

    def stop(self):
        """停止闹钟检查"""
        self.running = False
        if self.check_thread:
            self.check_thread.join(timeout=2)

    def _check_alarms(self):
        """闹钟检查线程主循环"""
        while self.running:
            if not self.paused:
                current_time = datetime.now()
                # 复制闹钟列表以避免迭代时字典被修改
                with self.lock:
                    alarms = list(self.alarms.values())
                for alarm in alarms:
                    if alarm.should_trigger(current_time):
                        if self.on_alarm_trigger:
                            self.on_alarm_trigger(alarm)
            time.sleep(1)  # 每秒检查一次

    def save_alarms(self):
        """保存闹钟到配置文件"""
        with self.lock:
            alarms_data = [alarm.to_dict() for alarm in self.alarms.values()]
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(alarms_data, f, indent=2)
        except Exception as e:
            print(f"保存闹钟配置失败: {e}")

    def load_alarms(self):
        """从配置文件加载闹钟"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    alarms_data = json.load(f)
                with self.lock:
                    self.alarms = {
                        alarm_data['id']: Alarm.from_dict(alarm_data)
                        for alarm_data in alarms_data
                    }
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"加载闹钟配置失败，使用空配置: {e}")
            with self.lock:
                self.alarms = {}

    def get_alarm(self, alarm_id: str) -> Optional[Alarm]:
        """获取指定ID的闹钟"""
        with self.lock:
            return self.alarms.get(alarm_id)

    def get_all_alarms(self) -> list:
        """获取所有闹钟列表"""
        with self.lock:
            return list(self.alarms.values())

    def clear_all(self):
        """清除所有闹钟"""
        with self.lock:
            self.alarms.clear()
        self.save_alarms()


if __name__ == "__main__":
    # 测试代码
    manager = AlarmManager("test_alarms.json")

    # 添加测试闹钟
    alarm_id1 = manager.add_alarm("14:30", True)
    alarm_id2 = manager.add_alarm("15:00", False, "custom.mp3")

    print(f"添加了2个闹钟: {alarm_id1}, {alarm_id2}")

    # 设置回调
    def on_alarm(alarm):
        print(f"闹钟触发: {alarm.time_str}")

    manager.on_alarm_trigger = on_alarm

    # 启动管理器
    manager.start()
    print("闹钟管理器已启动")

    try:
        # 运行10秒进行测试
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        manager.stop()
        print("闹钟管理器已停止")