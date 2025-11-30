#!/bin/bash
# 启动 Edge 浏览器并启用远程调试
# 这样脚本就可以连接到已打开的浏览器

# macOS 路径
EDGE_PATH="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"

# 检查 Edge 是否存在
if [ ! -f "$EDGE_PATH" ]; then
    echo "❌ 未找到 Edge 浏览器"
    echo "请手动使用以下命令启动："
    echo '"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" --remote-debugging-port=9222 --user-data-dir="/tmp/edge-debug"'
    exit 1
fi

# 检查是否已有远程调试端口在运行
if lsof -i :9222 > /dev/null 2>&1; then
    echo "✅ Edge 远程调试已在运行（端口 9222）"
    echo "正在打开新窗口..."
    # 使用 open 命令打开新窗口，不会关闭现有进程
    open -a "Microsoft Edge" --args --remote-debugging-port=9222 --user-data-dir="/tmp/edge-debug" > /dev/null 2>&1
    sleep 1
    echo "✅ 已打开新窗口"
else
    # 如果没有运行，则启动 Edge（远程调试模式）
    echo "正在启动 Edge 浏览器（远程调试模式）..."
    echo "使用用户数据目录: /tmp/edge-debug"
    "$EDGE_PATH" --remote-debugging-port=9222 --user-data-dir="/tmp/edge-debug" > /dev/null 2>&1 &
    sleep 3
fi

# 等待浏览器启动或新窗口打开
sleep 1

# 检查是否成功启动
if pgrep -f "Microsoft Edge" > /dev/null; then
    echo "✅ Edge 已启动（远程调试端口: 9222）"
    echo ""
    echo "下一步："
    echo "1. 在浏览器中登录你的账户"
    echo "2. 导航到预订页面"
    echo "3. 选择好要预订的日期"
    echo "4. 然后运行: python tennis_booking.py"
else
    echo "❌ Edge 启动失败"
    echo "请手动运行："
    echo '"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" --remote-debugging-port=9222 --user-data-dir="/tmp/edge-debug"'
    exit 1
fi

