# 简单计时器 (Simple Timer)

一个Windows本地运行的计时器应用，支持多个独立闹钟、自定义提醒音乐、系统托盘运行。

## 功能特点

- ⏰ **多个独立闹钟**：设置多个绝对时间点（24小时制）
- 🔄 **重复闹钟**：支持每天重复的闹钟
- 🎵 **自定义音乐**：内置默认音乐 + 支持自定义音乐文件
- 🪟 **弹出提醒**：到点时弹出独立窗口提醒（需手动确认关闭）
- ⏸️ **暂停功能**：一键暂停所有闹钟检查
- 📌 **系统托盘**：支持最小化到系统托盘后台运行
- 💾 **配置保存**：自动保存闹钟设置和配置

## 系统要求

- Windows 7/8/10/11
- Python 3.7+

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python main.py
```

### 3. 打包为可执行文件（可选）

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=assets/icon.ico --add-data "assets;assets" main.py
```

## 使用说明

### 添加闹钟
1. 点击"添加闹钟"按钮创建新的时间输入行
2. 输入时间（HH:MM格式，24小时制）
3. 选择是否"每天重复"和"启用"
4. 点击"选择音乐"为闹钟设置自定义音乐（可选）

### 控制闹钟
- **开始**：启动所有闹钟的时间检查
- **暂停**：暂停所有闹钟的时间检查（再次点击恢复）
- **删除**：点击每行闹钟的"删除"按钮移除闹钟

### 音乐设置
- **全局默认音乐**：在"音乐设置"区域选择默认音乐文件
- **单个闹钟音乐**：为每个闹钟单独选择音乐文件
- 支持格式：MP3, WAV, OGG, FLAC等

### 系统托盘
- 关闭窗口时，程序会最小化到系统托盘
- 右键点击托盘图标：
  - "显示主窗口"：恢复显示主界面
  - "退出"：完全退出应用

## 文件结构

```
simple_timer/
├── main.py              # 应用主入口
├── gui.py               # Tkinter GUI界面
├── alarm_manager.py     # 闹钟管理核心逻辑
├── audio_player.py      # 音频播放管理
├── tray_icon.py         # 系统托盘集成
├── alarm_dialog.py      # 提醒窗口
├── config.py            # 配置管理
├── utils.py             # 工具函数
├── assets/              # 资源文件
│   ├── default_alarm.mp3  # 默认提醒音乐（需用户提供）
│   └── icon.ico         # 应用图标（需用户提供）
├── config/              # 配置文件目录
│   ├── alarms.json      # 闹钟配置
│   └── app_config.json  # 应用配置
└── requirements.txt     # 依赖列表
```

## 注意事项

1. **音频文件**：程序需要音频文件作为提醒音
   - 将自定义音频文件放入 `assets/` 目录
   - 或通过程序界面选择本地音频文件
   - 如果没有音频文件，程序会使用系统蜂鸣声

2. **图标文件**：程序需要ICO格式图标
   - 将 `icon.ico` 放入 `assets/` 目录
   - 如果没有图标文件，程序会使用自动生成的蓝色钟表图标

3. **时间格式**：必须使用24小时制，格式为 HH:MM（如 14:30）

## 开发说明

### 模块说明
- **AlarmManager**：管理闹钟列表，后台时间检查线程
- **AudioPlayer**：使用pygame.mixer播放音频，支持错误回退
- **TimerGUI**：Tkinter主界面，动态输入框管理
- **AlarmDialog**：弹出提醒窗口
- **TrayIcon**：系统托盘图标管理

### 测试
运行集成测试：
```bash
python test_integration.py
```

## 已知问题

1. 首次运行如果没有音频文件，会使用系统蜂鸣声
2. 系统托盘图标在某些Windows版本上可能显示异常
3. pygame的pkg_resources弃用警告（不影响功能）

## 许可证

MIT License