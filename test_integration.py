#!/usr/bin/env python
# test_integration.py - 集成测试脚本

import os
import sys
import time
import threading

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alarm_manager import AlarmManager
from audio_player import AudioPlayer
from gui import TimerGUI
from tray_icon import TrayIcon
from config import AppConfig


def test_alarm_manager():
    """测试闹钟管理器"""
    print("1. 测试闹钟管理器...")
    manager = AlarmManager("test_integration_alarms.json")
    manager.load_alarms()

    # 添加测试闹钟
    alarm_id1 = manager.add_alarm("14:30", True, None)
    alarm_id2 = manager.add_alarm("15:00", False, None)
    print(f"   添加了2个闹钟: {alarm_id1[:8]}..., {alarm_id2[:8]}...")

    # 测试闹钟数量
    assert len(manager.alarms) == 2, f"预期2个闹钟，实际{len(manager.alarms)}个"

    # 测试删除闹钟
    manager.remove_alarm(alarm_id1)
    assert len(manager.alarms) == 1, f"删除后预期1个闹钟，实际{len(manager.alarms)}个"

    # 测试保存/加载
    manager.save_alarms()
    manager2 = AlarmManager("test_integration_alarms.json")
    manager2.load_alarms()
    assert len(manager2.alarms) == 1, f"加载后预期1个闹钟，实际{len(manager2.alarms)}个"

    print("   [OK] 闹钟管理器测试通过")
    return manager


def test_audio_player():
    """测试音频播放器"""
    print("2. 测试音频播放器...")
    player = AudioPlayer()

    # 测试初始化
    assert player.initialized, "音频播放器初始化失败"

    # 测试音量设置
    player.set_volume(0.7)
    assert abs(player.get_volume() - 0.7) < 0.01, f"音量设置失败: {player.get_volume()}"

    # 测试播放（系统蜂鸣声，因为默认音频文件不存在）
    print("   播放测试音频（系统蜂鸣声）...")
    player.play_alarm(loop=False)
    time.sleep(0.5)  # 等待播放
    player.stop()

    print("   [OK] 音频播放器测试通过")
    return player


def test_config():
    """测试配置管理器"""
    print("3. 测试配置管理器...")
    config = AppConfig("test_integration_config.json")

    # 测试默认值
    assert config.get_volume() == 0.5, f"默认音量应为0.5，实际{config.get_volume()}"

    # 测试设置/获取
    config.set_volume(0.8)
    assert abs(config.get_volume() - 0.8) < 0.01, f"音量设置失败: {config.get_volume()}"

    config.set_window_geometry("600x700")
    assert config.get_window_geometry() == "600x700", "窗口几何设置失败"

    print("   [OK] 配置管理器测试通过")
    return config


def test_tray_icon():
    """测试系统托盘图标"""
    print("4. 测试系统托盘图标...")
    tray = TrayIcon("测试计时器", "nonexistent.ico")

    # 测试图标创建（使用默认图标）
    tray.create_icon()
    assert tray.icon is not None, "系统托盘图标创建失败"

    # 测试在新线程中运行
    tray_thread = tray.run_in_thread()
    assert tray_thread is not None, "系统托盘线程创建失败"

    # 等待一下让图标初始化
    time.sleep(1)

    # 停止托盘
    tray.stop()

    print("   [OK] 系统托盘图标测试通过")
    return tray


def test_gui_creation():
    """测试GUI创建（不显示窗口）"""
    print("5. 测试GUI创建...")
    manager = AlarmManager("test_gui_alarms.json")
    player = AudioPlayer()

    gui = TimerGUI(manager, player)

    # 创建GUI但不进入主循环
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口

    # 直接调用_create_widgets方法测试
    gui.root = root
    gui._create_widgets()

    # 测试添加闹钟输入框
    gui._add_alarm_input("08:00", True, True)
    assert len(gui.alarm_frames) == 1, f"预期1个闹钟输入框，实际{len(gui.alarm_frames)}个"

    # 测试时间验证
    assert gui._validate_time_format("12:34"), "有效时间验证失败"
    assert not gui._validate_time_format("25:00"), "无效时间验证失败"

    root.destroy()
    print("   [OK] GUI创建测试通过")
    return gui


def main():
    """主测试函数"""
    print("=" * 60)
    print("简单计时器 - 集成测试")
    print("=" * 60)

    try:
        # 运行所有测试
        manager = test_alarm_manager()
        player = test_audio_player()
        config = test_config()
        tray = test_tray_icon()
        gui = test_gui_creation()

        print("\n" + "=" * 60)
        print("所有测试通过！")
        print("=" * 60)

        # 清理测试文件
        import glob
        test_files = glob.glob("test_*.json")
        for file in test_files:
            try:
                os.remove(file)
                print(f"清理测试文件: {file}")
            except:
                pass

        return True

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)