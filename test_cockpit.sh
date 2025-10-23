#!/bin/bash

echo "======================================"
echo "能源驾驶舱功能测试报告"
echo "======================================"
echo ""
echo "测试时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查服务状态
echo "1. 服务状态检查"
echo "--------------------------------------"

# 检查后端
backend_pid=$(ps aux | grep "python main.py" | grep -v grep | awk '{print $2}')
if [ -n "$backend_pid" ]; then
    echo "✓ 后端服务运行中 (PID: $backend_pid)"
    echo "  地址: http://localhost:8000"
else
    echo "✗ 后端服务未运行"
    exit 1
fi

# 检查前端
frontend_pid=$(ps aux | grep "vite" | grep -v grep | awk '{print $2}')
if [ -n "$frontend_pid" ]; then
    echo "✓ 前端服务运行中 (PID: $frontend_pid)"
    echo "  地址: http://localhost:5173"
else
    echo "✗ 前端服务未运行"
    exit 1
fi

echo ""
echo "2. API 接口测试"
echo "--------------------------------------"

# 测试根路径
echo -n "测试根路径: "
root_response=$(curl -s http://localhost:8000/)
if echo "$root_response" | grep -q "环控平台维护工具Web版 API"; then
    echo "✓ 成功"
else
    echo "✗ 失败"
fi

# 测试线路列表
echo -n "测试线路列表: "
lines_response=$(curl -s http://localhost:8000/api/lines)
if echo "$lines_response" | grep -q "lines"; then
    echo "✓ 成功"
    lines_count=$(echo "$lines_response" | python -m json.tool 2>/dev/null | grep -c "M[0-9]")
    echo "  线路数量: $lines_count"
else
    echo "✗ 失败"
fi

# 测试能源KPI接口
echo -n "测试能源KPI接口 (M3线): "
kpi_response=$(curl -s "http://localhost:8000/api/energy/kpi?line=M3")
if echo "$kpi_response" | grep -q "total_kwh_today"; then
    echo "✓ 成功"
    total_kwh=$(echo "$kpi_response" | python -m json.tool 2>/dev/null | grep "total_kwh_today" | awk '{print $2}' | sed 's/,//')
    current_kw=$(echo "$kpi_response" | python -m json.tool 2>/dev/null | grep "current_kw" | awk '{print $2}' | sed 's/,//')
    echo "  今日总能耗: ${total_kwh} kWh"
    echo "  当前功率: ${current_kw} kW"
else
    echo "✗ 失败"
fi

# 测试实时监测接口
echo -n "测试实时监测接口 (M3线): "
realtime_response=$(curl -s "http://localhost:8000/api/energy/realtime?line=M3")
if echo "$realtime_response" | grep -q "timestamps"; then
    echo "✓ 成功"
    data_points=$(echo "$realtime_response" | python -m json.tool 2>/dev/null | grep -c "\"[0-9][0-9]:[0-9][0-9]\"")
    echo "  数据点数量: $data_points"
else
    echo "✗ 失败"
fi

# 测试历史趋势接口
echo -n "测试历史趋势接口 (M3线, 24h): "
trend_response=$(curl -s "http://localhost:8000/api/energy/trend?line=M3&period=24h")
if echo "$trend_response" | grep -q "timestamps"; then
    echo "✓ 成功"
    trend_points=$(echo "$trend_response" | python -m json.tool 2>/dev/null | grep "timestamps" -A 30 | grep -c "\"[0-9]")
    echo "  趋势数据点: $trend_points"
else
    echo "✗ 失败"
fi

# 测试节能建议接口
echo -n "测试节能建议接口 (M3线): "
suggestions_response=$(curl -s "http://localhost:8000/api/energy/suggestions?line=M3")
if echo "$suggestions_response" | grep -q "items"; then
    echo "✓ 成功"
    suggestions_count=$(echo "$suggestions_response" | python -m json.tool 2>/dev/null | grep "\"title\"" | wc -l)
    echo "  建议数量: $suggestions_count"
else
    echo "✗ 失败"
fi

# 测试能耗对比接口
echo -n "测试能耗对比接口 (M3线, 24h): "
compare_response=$(curl -s "http://localhost:8000/api/energy/compare?line=M3&period=24h")
if echo "$compare_response" | grep -q "mom_percent"; then
    echo "✓ 成功"
    mom=$(echo "$compare_response" | python -m json.tool 2>/dev/null | grep "mom_percent" | awk '{print $2}' | sed 's/,//')
    yoy=$(echo "$compare_response" | python -m json.tool 2>/dev/null | grep "yoy_percent" | awk '{print $2}')
    echo "  环比变化: ${mom}%"
    echo "  同比变化: ${yoy}%"
else
    echo "✗ 失败"
fi

# 测试分类分项接口
echo -n "测试分类分项接口 (M3线, 24h): "
classification_response=$(curl -s "http://localhost:8000/api/energy/classification?line=M3&period=24h")
if echo "$classification_response" | grep -q "categories"; then
    echo "✓ 成功"
    categories_count=$(echo "$classification_response" | python -m json.tool 2>/dev/null | grep "\"name\"" | wc -l)
    total_kwh=$(echo "$classification_response" | python -m json.tool 2>/dev/null | grep "total_kwh" | awk '{print $2}' | sed 's/,//')
    echo "  设备分类: $categories_count 类"
    echo "  总能耗: ${total_kwh} kWh"
else
    echo "✗ 失败"
fi

echo ""
echo "3. 前端访问测试"
echo "--------------------------------------"

# 测试前端主页
echo -n "测试前端主页: "
frontend_response=$(curl -s http://localhost:5173/)
if echo "$frontend_response" | grep -q "<!DOCTYPE html>"; then
    echo "✓ 成功"
else
    echo "✗ 失败"
fi

echo ""
echo "4. 日志检查"
echo "--------------------------------------"
echo "后端日志 (最近5行):"
tail -5 backend.log | sed 's/^/  /'

echo ""
echo "前端日志 (最近5行):"
tail -5 frontend.log | sed 's/^/  /'

echo ""
echo "======================================"
echo "测试完成！"
echo "======================================"
echo ""
echo "访问地址："
echo "  前端界面: http://localhost:5173"
echo "  后端API: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo ""
echo "驾驶舱页面路径："
echo "  /energy - 能源驾驶舱"
echo "  /dashboard - 能源管理驾驶舱"
echo ""
