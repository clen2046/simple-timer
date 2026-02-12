# audio_player.py - 音频播放管理

import os
import sys
import pygame
import warnings
from typing import Optional


class AudioPlayer:
    """音频播放器"""

    def __init__(self, default_audio_path: str = "assets/default_alarm.mp3"):
        self.default_audio_path = default_audio_path
        self.current_audio: Optional[pygame.mixer.Sound] = None
        self.volume = 0.5  # 默认音量50%
        self.initialized = False
        self._init_pygame()

    def _init_pygame(self):
        """初始化pygame mixer"""
        try:
            # 抑制pygame初始化消息
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.initialized = True
        except Exception as e:
            print(f"初始化pygame.mixer失败: {e}")
            self.initialized = False

    def play_alarm(self, audio_file: str = None, loop: bool = True):
        """播放闹钟音乐"""
        try:
            # 停止当前播放
            self.stop()

            # 确定音频文件路径
            audio_path = audio_file if audio_file else self.default_audio_path

            # 检查文件是否存在
            if not os.path.exists(audio_path):
                print(f"音频文件不存在: {audio_path}")
                # 回退到默认音频文件
                if audio_file and os.path.exists(self.default_audio_path):
                    audio_path = self.default_audio_path
                else:
                    # 使用系统蜂鸣声作为最后的后备
                    self._play_system_beep()
                    return

            if not self.initialized:
                self._play_system_beep()
                return

            # 加载并播放音频
            try:
                self.current_audio = pygame.mixer.Sound(audio_path)
                self.current_audio.set_volume(self.volume)

                if loop:
                    self.current_audio.play(loops=-1)  # -1表示无限循环
                else:
                    self.current_audio.play()

            except pygame.error as e:
                print(f"加载音频文件失败 {audio_path}: {e}")
                self._play_system_beep()

        except Exception as e:
            print(f"播放音频失败: {e}")
            self._play_system_beep()

    def _play_system_beep(self):
        """播放系统蜂鸣声（后备方案）"""
        try:
            if sys.platform == "win32":
                import winsound
                winsound.Beep(1000, 500)  # 频率1000Hz，持续时间500ms
            else:
                # Linux/Mac的简单后备
                print("\a")  # ASCII bell字符
        except Exception as e:
            print(f"播放系统蜂鸣声也失败: {e}")

    def stop(self):
        """停止播放"""
        if self.current_audio:
            try:
                self.current_audio.stop()
            except Exception as e:
                print(f"停止音频播放失败: {e}")
        elif self.initialized:
            # 停止所有pygame音频
            pygame.mixer.stop()

    def set_volume(self, volume: float):
        """设置音量 (0.0 - 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if self.current_audio:
            try:
                self.current_audio.set_volume(self.volume)
            except Exception as e:
                print(f"设置音量失败: {e}")

    def get_volume(self) -> float:
        """获取当前音量"""
        return self.volume

    def is_playing(self) -> bool:
        """检查是否正在播放"""
        if not self.initialized:
            return False
        return pygame.mixer.get_busy()

    def fadeout(self, duration: int = 1000):
        """淡出停止播放"""
        if self.current_audio:
            try:
                self.current_audio.fadeout(duration)
            except Exception as e:
                print(f"淡出音频失败: {e}")
        elif self.initialized:
            pygame.mixer.fadeout(duration)

    def cleanup(self):
        """清理资源"""
        self.stop()
        if self.initialized:
            try:
                pygame.mixer.quit()
            except Exception as e:
                print(f"清理pygame.mixer失败: {e}")
            self.initialized = False


if __name__ == "__main__":
    # 测试代码
    player = AudioPlayer()

    print("测试音频播放器...")
    print("1. 测试系统蜂鸣声（文件不存在时）")
    player.play_alarm("nonexistent.mp3", loop=False)

    import time
    time.sleep(1)

    print("2. 测试停止播放")
    player.stop()

    print("3. 测试音量控制")
    player.set_volume(0.7)
    print(f"当前音量: {player.get_volume()}")

    print("4. 测试是否正在播放")
    print(f"正在播放: {player.is_playing()}")

    print("测试完成")
    player.cleanup()