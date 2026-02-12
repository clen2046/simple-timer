#!/usr/bin/env python
# quick_test.py - 快速验证应用可以启动

import sys
import os

print("快速验证简单计时器应用...")
print("=" * 50)

# 检查所有必要文件是否存在
required_files = [
    "main.py",
    "gui.py",
    "alarm_manager.py",
    "audio_player.py",
    "tray_icon.py",
    "alarm_dialog.py",
    "config.py",
    "utils.py",
    "requirements.txt"
]

print("1. 检查文件...")
all_files_exist = True
for file in required_files:
    if os.path.exists(file):
        print(f"   [OK] {file}")
    else:
        print(f"   [FAIL] {file} (缺失)")
        all_files_exist = False

if not all_files_exist:
    print("\n错误：缺少必要文件！")
    sys.exit(1)

print("\n2. 导入模块...")
try:
    from alarm_manager import AlarmManager
    print("   [OK] alarm_manager")
except Exception as e:
    print(f"   [FAIL] alarm_manager: {e}")
    sys.exit(1)

try:
    from audio_player import AudioPlayer
    print("   [OK] audio_player")
except Exception as e:
    print(f"   [FAIL] audio_player: {e}")
    sys.exit(1)

try:
    from gui import TimerGUI
    print("   [OK] gui")
except Exception as e:
    print(f"   [FAIL] gui: {e}")
    sys.exit(1)

try:
    from tray_icon import TrayIcon
    print("   [OK] tray_icon")
except Exception as e:
    print(f"   [FAIL] tray_icon: {e}")
    sys.exit(1)

try:
    from alarm_dialog import AlarmDialog
    print("   [OK] alarm_dialog")
except Exception as e:
    print(f"   [FAIL] alarm_dialog: {e}")
    sys.exit(1)

try:
    from config import AppConfig
    print("   [OK] config")
except Exception as e:
    print(f"   [FAIL] config: {e}")
    sys.exit(1)

try:
    from utils import validate_time_format
    print("   [OK] utils")
except Exception as e:
    print(f"   [FAIL] utils: {e}")
    sys.exit(1)

print("\n3. 创建组件实例...")
try:
    manager = AlarmManager("quick_test_alarms.json")
    print("   [OK] 创建AlarmManager")
except Exception as e:
    print(f"   [FAIL] 创建AlarmManager失败: {e}")
    sys.exit(1)

try:
    player = AudioPlayer()
    print("   [OK] 创建AudioPlayer")
except Exception as e:
    print(f"   [FAIL] 创建AudioPlayer失败: {e}")
    sys.exit(1)

try:
    # 创建隐藏的Tkinter根窗口进行测试
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()

    gui = TimerGUI(manager, player)
    gui.root = root
    print("   [OK] 创建TimerGUI")

    root.destroy()
except Exception as e:
    print(f"   [FAIL] 创建TimerGUI失败: {e}")
    sys.exit(1)

print("\n4. 清理测试文件...")
import glob
for file in glob.glob("quick_test_*.json"):
    try:
        os.remove(file)
        print(f"   清理: {file}")
    except:
        pass

print("\n" + "=" * 50)
print("验证成功！")
print("应用可以正常启动。")
print("\n运行应用: python main.py")
print("=" * 50)