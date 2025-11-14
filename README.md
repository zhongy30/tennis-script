# 网球场快速预订脚本

一个简洁的 Python 脚本，用于在已登录的预订页面上快速选择时间段并点击预订按钮。

## 功能

- 快速选择指定数量的时间段
- 支持指定首选时间段
- 自动点击预订按钮
- 连接到已打开的 Edge 浏览器（保持登录状态）

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 方法 1：使用已打开的浏览器（推荐）

这样可以保持你的登录状态，不需要每次都登录。

#### 步骤 1：启动 Edge（远程调试模式）

**macOS:**
```bash
chmod +x start_edge.sh
./start_edge.sh
```

或者手动运行：
```bash
"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" --remote-debugging-port=9222
```

**Windows:**
```cmd
msedge.exe --remote-debugging-port=9222
```

**Linux:**
```bash
microsoft-edge --remote-debugging-port=9222
```

#### 步骤 2：登录并打开预订页面

1. 在启动的 Edge 浏览器中登录你的账户
2. 导航到预订页面
3. 选择好要预订的日期

#### 步骤 3：配置并运行脚本

编辑 `tennis_booking.py` 文件：

```python
NUM_SLOTS = 2  # 要预订的时间段数量
PREFERRED_TIMES = ["3:00pm", "4:00pm", "5:00pm"]  # 首选时间段
USE_EXISTING_BROWSER = True  # 使用已打开的浏览器
```

运行脚本：
```bash
python tennis_booking.py
```

### 方法 2：打开新浏览器窗口

如果你想打开新的浏览器窗口：

1. 编辑 `tennis_booking.py`，设置 `USE_EXISTING_BROWSER = False`
2. 运行脚本，然后在新窗口中手动登录

## 测试按钮点击成功率

使用 `test_buttons.py` 脚本可以测试 book 和 confirm 按钮的点击成功率：

```bash
python test_buttons.py
```

### 测试脚本功能

- 自动运行多次测试（默认 10 次）
- 测试 Book 按钮的点击成功率
- 测试 Confirm 按钮的点击成功率
- 显示详细的统计信息，包括：
  - Book 按钮成功率
  - Confirm 按钮成功率
  - 整体成功率
  - 最成功的选择器
  - 每次测试的详细结果

### 配置测试参数

编辑 `test_buttons.py` 文件：

```python
NUM_TESTS = 10  # 测试次数
TEST_INTERVAL = 2  # 每次测试间隔（秒）
```

### 测试前准备

1. 使用远程调试模式启动 Edge（见上方说明）
2. 在浏览器中登录并打开预订页面
3. 选择好要预订的日期
4. （可选）手动选择一些时间段，这样 Book 按钮会出现

## 注意事项

- 使用已打开浏览器模式时，必须先用远程调试模式启动 Edge
- 如果连接失败，检查 Edge 是否以远程调试模式启动
- 如果选择器无法找到元素，可能需要根据实际网站结构调整选择器
- 测试脚本会保持浏览器打开，方便查看结果

