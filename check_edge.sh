#!/bin/bash
# 检查 Edge 是否以远程调试模式运行

echo "检查 Edge 浏览器状态..."
echo ""

# 检查是否有 Edge 进程
if pgrep -f "Microsoft Edge" > /dev/null; then
    echo "✅ 发现 Edge 进程正在运行"
    
    # 检查是否监听 9222 端口
    if lsof -i :9222 > /dev/null 2>&1; then
        echo "✅ Edge 正在监听远程调试端口 9222"
        echo ""
        echo "可以运行脚本了："
        echo "  python tennis_booking.py"
    else
        echo "❌ Edge 未启用远程调试模式"
        echo ""
        echo "请关闭所有 Edge 窗口，然后运行："
        echo "  ./start_edge.sh"
        echo ""
        echo "或者手动启动："
        echo '  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" --remote-debugging-port=9222 --user-data-dir="/tmp/edge-debug"'
    fi
else
    echo "❌ Edge 未运行"
    echo ""
    echo "请运行启动脚本："
    echo "  ./start_edge.sh"
fi

