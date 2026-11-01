# Auto Clicker

## English Version

### Overview
Auto Clicker is a desktop automation tool written in Python that allows you to automate mouse clicks with various modes and configurations. Built with PyQt6 for the graphical interface and pynput for input control.

### Features
- Auto Click Mode: Fixed CPS (clicks per second) or random CPS within a range
- Mouse Button Selection: Left click or right click
- Hotkey Configuration: Set custom hotkeys to start/stop clicking
- CPS Booster: Additional clicking functionality with configurable rules
- Key Management: Manage and configure multiple click hotkeys
- WASD Boost Detection: Automatically boost CPS when WASD keys are pressed
- Configuration Persistence: Save and load settings via `option.txt`

### Requirements
- Python 3.8 or higher
- PyQt6
- pynput

### Installation
1. Clone or copy the project to your local machine
2. Install dependencies: `pip install PyQt6 pynput`
3. Run the application: `python main.py`

### Usage
1. Launch the application
2. Select your preferred clicking mode (Fixed CPS or Random CPS)
3. Choose the mouse button (Left or Right)
4. Set your desired click speed
5. Configure your hotkey for starting/stopping the clicks
6. Click "启动" (Start) to begin automation
7. Click "停止" (Stop) to halt the clicking

### Configuration
The application saves its configuration to `option.txt` in the project directory. Settings include:
- Hotkey keys
- Clicking mode and speed
- Mouse button selection
- CPS booster settings
- Key management configurations

## 中文版

### 概述
Auto Clicker 是一个用 Python 编写的桌面自动化工具，允许您自动化鼠标点击，具有各种模式和配置选项。使用 PyQt6 构建图形界面，使用 pynput 进行输入控制。

### 功能
- **自动点击模式**：固定 CPS（每秒点击次数）或随机 CPS 在范围内
- **鼠标按键选择**：左键或右键
- **热键配置**：设置自定义热键启动/停止点击
- **CPS Booster**：具有可配置规则的额外点击功能
- **键管理**：管理和配置多个点击热键
- **WASD 检测**：在按下 WASD 键时自动提升 CPS
- **配置持久化**：通过 `option.txt` 保存和加载设置

### 要求
- Python 3.8 或更高版本
- PyQt6
- pynput

### 安装
1. 将项目克隆或复制到您的本地机器
2. 安装依赖：`pip install PyQt6 pynput`
3. 运行应用程序：`python main.py`

### 使用方法
1. 启动应用程序
2. 选择首选的点击模式（固定 CPS 或随机 CPS)
3. 选择鼠标按键（左键或右键）
4. 设置期望的点击速度
5. 配置启动/停止的热键
6. 点击 "启动" (Start) 开始自动化
7. 点击 "停止" (Stop) 停止点击

### 配置
应用程序将其配置保存到项目目录中的 `option.txt`。设置包括：
- 快捷键键
- 点击模式和速度
- 鼠标按钮选择
- CPS Booster 设置
- 键管理配置
