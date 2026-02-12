# config.py - 配置管理

import json
import os


class AppConfig:
    """应用配置管理器"""

    def __init__(self, config_file: str = "config/app_config.json"):
        self.config_file = config_file
        self.config = self._load_default_config()

        # 确保配置文件目录存在
        config_dir = os.path.dirname(config_file)
        if config_dir:  # 只有当目录名非空时才创建
            os.makedirs(config_dir, exist_ok=True)

        # 加载现有配置
        self.load()

    def _load_default_config(self) -> dict:
        """加载默认配置"""
        return {
            "window_geometry": "500x600",
            "volume": 0.5,
            "start_minimized": False,
            "show_notifications": True,
            "default_audio_path": "assets/default_alarm.mp3"
        }

    def load(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # 合并配置，保留默认值
                self.config.update(loaded_config)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"加载应用配置失败，使用默认配置: {e}")

    def save(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"保存应用配置失败: {e}")

    def get(self, key: str, default=None):
        """获取配置项"""
        return self.config.get(key, default)

    def set(self, key: str, value):
        """设置配置项"""
        self.config[key] = value
        self.save()

    def get_window_geometry(self) -> str:
        """获取窗口几何设置"""
        return self.get("window_geometry", "500x600")

    def set_window_geometry(self, geometry: str):
        """设置窗口几何设置"""
        self.set("window_geometry", geometry)

    def get_volume(self) -> float:
        """获取音量设置"""
        return self.get("volume", 0.5)

    def set_volume(self, volume: float):
        """设置音量设置"""
        self.set("volume", max(0.0, min(1.0, volume)))

    def get_start_minimized(self) -> bool:
        """获取是否启动时最小化"""
        return self.get("start_minimized", False)

    def set_start_minimized(self, minimized: bool):
        """设置是否启动时最小化"""
        self.set("start_minimized", minimized)

    def get_show_notifications(self) -> bool:
        """获取是否显示通知"""
        return self.get("show_notifications", True)

    def set_show_notifications(self, show: bool):
        """设置是否显示通知"""
        self.set("show_notifications", show)


if __name__ == "__main__":
    # 测试代码
    config = AppConfig("test_config.json")

    print("当前配置:")
    for key, value in config.config.items():
        print(f"  {key}: {value}")

    print(f"\n窗口几何: {config.get_window_geometry()}")
    print(f"音量: {config.get_volume()}")

    # 修改配置
    config.set_volume(0.7)
    config.set_window_geometry("600x700")

    print("\n修改后配置:")
    print(f"音量: {config.get_volume()}")
    print(f"窗口几何: {config.get_window_geometry()}")