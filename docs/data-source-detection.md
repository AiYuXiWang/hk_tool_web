# 能源驾驶舱数据来源检测功能

## 功能说明

能源驾驶舱现已支持实时显示数据来源，帮助用户直观判断当前显示的数据是真实数据还是模拟数据。

## 数据来源类型

数据来源指示器会显示以下三种状态：

### 1. 🟢 真实数据 (Real Data)
- **显示**：绿色指示灯 + "真实数据"文字
- **含义**：所有数据都是从平台API（9898端口）成功获取的真实运行数据
- **适用场景**：生产环境，站点配置正确且API可访问

### 2. 🟡 混合数据 (Mixed Data)
- **显示**：黄色指示灯 + "混合数据"文字
- **含义**：部分站点获取到真实数据，部分站点使用模拟数据
- **适用场景**：多站点场景下，部分站点API不可达或配置缺失

### 3. 🔴 模拟数据 (Simulated Data)
- **显示**：红色指示灯 + "模拟数据"文字
- **含义**：所有数据都是通过算法生成的模拟数据
- **适用场景**：
  - 开发/测试环境
  - 站点API不可访问
  - 站点配置缺失（缺少IP、object_codes或data_codes）
  - 网络连接异常

## 工作原理

### 后端实现

1. **数据获取层** (`realtime_energy_service.py`)
   - 尝试从平台API获取真实功率数据
   - 如果失败，返回 `None`
   - 新增 `check_data_availability()` 方法检查配置完整性

2. **服务层** (`energy_service.py`)
   - 在 `_get_station_realtime_data()` 中标记每个站点的数据来源
   - 在 `_generate_realtime_response()` 中汇总所有站点的数据来源：
     - 所有站点都是真实数据 → `"real"`
     - 至少一个站点是真实数据 → `"mixed"`
     - 所有站点都是模拟数据 → `"simulated"`

3. **API层** (`energy_dashboard.py`)
   - 在API响应中添加 `data_source` 字段
   - 传递给前端用于显示

### 前端实现

1. **数据接收** (`EnergyCockpit.vue`)
   - 从API响应中提取 `data_source` 字段
   - 使用 `updateDataSource()` 更新全局数据来源状态

2. **优先级机制**
   ```typescript
   const DATA_SOURCE_PRIORITY = {
     real: 3,      // 最高优先级
     mixed: 2,
     simulated: 1  // 最低优先级
   }
   ```
   - 当收到多个数据源时，显示优先级最高的（最真实的）

3. **视觉呈现**
   - 位于控制栏右侧
   - 带有发光效果的圆点指示器
   - 根据数据来源类型显示不同颜色
   - 响应式动画效果

## 使用场景

### 开发阶段
在开发阶段，由于可能没有真实的站点API或配置，系统会显示"模拟数据"。这是正常的，开发者可以专注于功能开发。

### 联调阶段
在与平台API联调时，可以通过数据来源指示器快速判断：
- ✅ 绿色"真实数据"：联调成功，数据正常
- ⚠️ 黄色"混合数据"：部分站点配置有问题，需要检查
- ❌ 红色"模拟数据"：联调失败，需要检查网络、配置或API

### 生产运维
在生产环境中：
- 应当始终显示"真实数据"（绿色）
- 如果出现"混合数据"或"模拟数据"，说明存在异常，需要排查

## 故障排查

### 显示"模拟数据"时的检查清单

1. **网络连接**
   - 确认能够访问站点的9898端口
   - 检查防火墙规则

2. **站点配置**
   - 检查 `config_electricity.py` 中的站点配置
   - 确保包含正确的 `ip`、`object_codes`、`data_codes`

3. **API状态**
   - 尝试直接访问 `http://{station_ip}:9898/data/selectHisData`
   - 检查API是否返回有效数据

4. **日志检查**
   - 查看后端日志中的警告信息
   - 关注以下日志：
     ```
     站点 XXX 实时功率获取失败，使用模拟数据
     站点 XXX 没有IP配置
     站点 XXX 没有节能数据配置
     ```

### 显示"混合数据"时的处理

1. **识别问题站点**
   - 检查每个站点的配置完整性
   - 逐个测试站点API可访问性

2. **分步修复**
   - 优先修复关键站点
   - 修复后刷新页面查看变化

## 代码示例

### 后端：添加数据来源标识
```python
# 在获取实时数据时
current_power = await self.realtime_service.get_station_realtime_power(station)
is_real_data = current_power is not None

return {
    "station_name": station["name"],
    "current_power": current_power,
    "data_source": "real" if is_real_data else "simulated",
}
```

### 前端：显示数据来源
```vue
<div class="data-source-indicator" :class="dataSourceClass">
  <span class="indicator-dot"></span>
  <span class="indicator-text">{{ dataSourceText }}</span>
</div>
```

## 技术细节

### 数据来源判断逻辑

```python
# 判断整体数据来源
has_real_data = any(item.get("data_source") == "real" for item in station_data_list)
all_real_data = all(item.get("data_source") == "real" for item in station_data_list)

if all_real_data:
    data_source = "real"
elif has_real_data:
    data_source = "mixed"
else:
    data_source = "simulated"
```

### CSS动画效果

```css
.data-source-indicator {
  box-shadow: 0 0 16px rgba(34, 197, 94, 0.35);
  transition: background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.data-source-indicator .indicator-dot {
  box-shadow: 0 0 8px currentColor;
}
```

## 未来改进

1. **详细信息弹窗**
   - 点击指示器显示各站点的数据来源详情
   - 显示API响应时间和状态

2. **历史记录**
   - 记录数据来源的变化历史
   - 生成可用性报告

3. **告警通知**
   - 当数据来源从真实切换到模拟时发送告警
   - 配置告警阈值和接收人

4. **更细粒度的分类**
   - 区分"实时真实数据"和"缓存真实数据"
   - 显示数据延迟时间

## 相关文件

- **后端**
  - `backend/app/services/realtime_energy_service.py` - 真实数据服务
  - `backend/app/services/energy_service.py` - 能源业务服务
  - `backend/app/api/energy_dashboard.py` - API接口

- **前端**
  - `frontend/src/views/EnergyCockpit.vue` - 能源驾驶舱主界面
  - `frontend/src/api/energy.ts` - API封装

- **文档**
  - `docs/data-source-detection.md` - 本文档
