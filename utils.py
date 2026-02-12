# utils.py - 工具函数

import os
import re
from datetime import datetime


def validate_time_format(time_str: str) -> bool:
    """验证时间格式 (HH:MM 24小时制)"""
    pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    if re.match(pattern, time_str):
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False
    return False


def format_time_display(time_str: str) -> str:
    """格式化时间显示"""
    if validate_time_format(time_str):
        return time_str
    return "00:00"


def get_short_filename(filepath: str, max_length: int = 15) -> str:
    """获取缩短的文件名显示"""
    if not filepath:
        return "默认音乐"

    filename = os.path.basename(filepath)
    if len(filename) <= max_length:
        return filename

    name, ext = os.path.splitext(filename)
    if len(name) > max_length - 3:
        name = name[:max_length - 6] + "..."
    return name + ext


def ensure_directory_exists(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def is_audio_file(filename: str) -> bool:
    """检查文件是否为支持的音频文件"""
    audio_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac'}
    _, ext = os.path.splitext(filename.lower())
    return ext in audio_extensions


def get_current_time_str() -> str:
    """获取当前时间字符串 (HH:MM格式)"""
    now = datetime.now()
    return now.strftime("%H:%M")


if __name__ == "__main__":
    # 测试代码
    print("测试工具函数...")

    test_times = ["14:30", "25:00", "09:15", "9:5", "23:59"]
    for time_str in test_times:
        valid = validate_time_format(time_str)
        print(f"{time_str}: {'有效' if valid else '无效'}")

    print(f"\n当前时间: {get_current_time_str()}")

    test_files = ["/path/to/music.mp3", "short.wav", "very_long_audio_filename.ogg", ""]
    for filepath in test_files:
        short = get_short_filename(filepath, 10)
        print(f"{filepath} -> {short}")