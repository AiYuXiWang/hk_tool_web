# 真实数据校准方案

## 概述
当前系统使用模拟数据进行开发和测试。本文档列出需要根据真实数据调整的计算参数，以确保系统在生产环境中能够准确反映实际能耗情况。

## 1. 功率计算参数

### 1.1 基础功率计算
**位置**: `backend/app/services/energy_service.py:193-194`

```python
# 当前模拟代码
base_power = device_count * 25 + random.uniform(-10, 10)
current_power = max(0, base_power + random.uniform(-15, 15))
```

**需要调整的参数**:
- `device_count * 25`: 每个设备的平均功率（当前假设25kW）
  - **建议**: 根据真实设备功率规格表设置
  - **数据来源**: 设备铭牌、历史监测数据
  - **预期范围**: 10-50kW（根据设备类型不同）

- 功率波动范围 `±10` 和 `±15`
  - **建议**: 基于历史数据的标准差
  - **数据来源**: 最近30天的功率监测数据
  - **预期范围**: ±5% ~ ±20%（根据设备负荷稳定性）

### 1.2 时段功率系数
**位置**: `backend/app/services/energy_service.py:226-228`

```python
if 6 <= hour <= 22:  # 白天功率较高
    power = base_power * (0.8 + 0.4 * (1 + 0.1 * (i % 3)))
else:  # 夜间功率较低
    power = base_power * (0.5 + 0.3 * (1 + 0.1 * (i % 2)))
```

**需要调整的参数**:
- 白天时段: `6:00-22:00`
  - **建议**: 根据地铁运营时间调整
  - **数据来源**: 运营时刻表、历史客流数据
  
- 白天功率系数: `0.8-1.2`
  - **建议**: 基于历史白天平均功率 / 基础功率
  - **数据来源**: 最近90天白天时段平均功率
  - **预期范围**: 0.6-1.5
  
- 夜间功率系数: `0.5-0.8`
  - **建议**: 基于历史夜间平均功率 / 基础功率
  - **数据来源**: 最近90天夜间时段平均功率
  - **预期范围**: 0.3-0.7

### 1.3 日能耗计算
**位置**: `backend/app/services/energy_service.py:198`

```python
daily_consumption = current_power * 20 + random.uniform(-50, 50)
```

**需要调整的参数**:
- 时间系数 `* 20`
  - **建议**: 应该是 `* 24`（24小时）或基于实际平均负荷率
  - **数据来源**: 历史日能耗 / 平均功率
  - **预期范围**: 18-24小时等效运行时间
  
- 波动范围 `±50`
  - **建议**: 基于历史日能耗的标准差
  - **数据来源**: 最近30天的日能耗数据
  - **预期范围**: ±3% ~ ±15%

## 2. 能效比计算参数

### 2.1 能效比基准值
**位置**: `backend/app/services/energy_service.py:257`

```python
efficiency_ratio = round(3.5 + (total_consumption / 10000) * 0.1, 1)
```

**需要调整的参数**:
- 基准能效比: `3.5`
  - **建议**: 根据设备COP（制冷系数）或EER（能效比）设定
  - **数据来源**: 冷机设备规格书、历史运行数据
  - **预期范围**: 2.5-5.0（冷机COP通常在此范围）
  
- 能耗影响系数: `/ 10000 * 0.1`
  - **建议**: 基于实际负荷率与能效比的相关性
  - **数据来源**: 历史能效比与能耗的回归分析
  - **预期范围**: 根据设备特性调整

## 3. 节能收益计算参数

### 3.1 基准能耗
**位置**: `backend/app/services/energy_service.py:260-262`

```python
baseline_consumption = total_consumption * 1.15
energy_saved = baseline_consumption - total_consumption
cost_saving = energy_saved * 1.5  # 按1.5元/kWh计算
```

**需要调整的参数**:
- 基准倍数: `1.15` (15%节能)
  - **建议**: 基于节能改造前的历史数据
  - **数据来源**: 改造前同期能耗数据
  - **预期范围**: 1.10-1.30 (10%-30%节能潜力)
  
- 电价: `1.5元/kWh`
  - **建议**: 使用实际电价
  - **数据来源**: 电费账单、分时电价表
  - **预期范围**: 0.5-2.0元/kWh（峰谷平不同）
  - **注意**: 应考虑分时电价：
    - 峰时电价（通常较高）
    - 平时电价（中等）
    - 谷时电价（通常较低）

## 4. 趋势分析参数

### 4.1 同比环比计算
**位置**: `backend/app/services/energy_service.py:253-254`

```python
yesterday_consumption = total_consumption * 0.95
last_hour_power = current_power * 1.02
```

**需要调整的参数**:
- 日对比系数: `0.95` (5%增长)
  - **建议**: 基于实际同比/环比增长率
  - **数据来源**: 去年同期数据、上周期数据
  - **计算方式**: `(当前值 - 对比值) / 对比值 * 100%`
  
- 小时对比系数: `1.02` (2%波动)
  - **建议**: 基于实际小时级功率波动
  - **数据来源**: 最近24小时功率数据
  - **预期范围**: 0.95-1.10

### 4.2 季节性系数
**位置**: `backend/app/services/energy_service.py:371`

```python
seasonal_factor = 1 + 0.2 * (1 + 0.5 * (time_point.month % 12 / 12))
```

**需要调整的参数**:
- 季节波动幅度: `0.2` (20%)
  - **建议**: 基于历史各月份能耗数据
  - **数据来源**: 最近1-3年各月平均能耗
  - **预期范围**: 0.15-0.40（夏季制冷、冬季制热需求差异）
  
- 季节曲线形状: `1 + 0.5 * (month % 12 / 12)`
  - **建议**: 基于历史数据拟合季节曲线
  - **数据来源**: 月度能耗统计
  - **可选方法**: 三角函数拟合、多项式拟合

## 5. 设备状态判断参数

### 5.1 设备状态阈值
**位置**: `backend/app/api/energy_dashboard.py:371-380`

```python
if status_rand > 0.9:
    status = "error"
elif status_rand > 0.7:
    status = "warning"
else:
    status = "normal"
```

**需要调整的参数**:
- 故障率: `10%` (status_rand > 0.9)
  - **建议**: 基于历史设备故障统计
  - **数据来源**: 设备维修记录、报警日志
  - **预期范围**: 0.1%-5%
  
- 预警率: `20%` (status_rand > 0.7)
  - **建议**: 基于设备效率偏低的历史频率
  - **数据来源**: 效率监测记录
  - **预期范围**: 5%-15%

### 5.2 设备效率阈值
**位置**: `backend/app/api/energy_dashboard.py:386`

```python
efficiency = 85 + 15 * random.random()
```

**需要调整的参数**:
- 效率范围: `85%-100%`
  - **建议**: 基于设备实际运行效率
  - **数据来源**: 设备性能测试、历史效率数据
  - **预期范围**: 70%-95%（根据设备类型和运行年限）
  - **判断标准**:
    - 优秀: >90%
    - 良好: 80%-90%
    - 偏低: <80%

## 6. 分类分项能耗比例

### 6.1 能耗分类比例
**位置**: `backend/app/api/energy_dashboard.py:560-571`

```python
categories = {
    "冷机": 0.45,
    "水泵": 0.20,
    "冷却塔": 0.15,
    "照明": 0.12,
    "其他": 0.08
}
```

**需要调整的参数**:
- 各分类占比
  - **建议**: 基于历史分项计量数据
  - **数据来源**: 分项电表数据、负荷分析报告
  - **典型地铁站能耗分布**:
    - 环控系统（冷机+水泵+冷却塔）: 50%-70%
    - 照明系统: 10%-15%
    - 电扶梯: 5%-10%
    - 通信信号: 3%-8%
    - 其他: 5%-15%

## 7. 优化建议参数

### 7.1 节能潜力评估
**位置**: `backend/app/api/energy_dashboard.py:431-433`

```python
"energy_saving": 2500,
"cost_saving": 3750,
```

**需要调整的参数**:
- 各项优化措施的节能量
  - **建议**: 基于节能审计报告、试点项目数据
  - **数据来源**: 
    - 同类项目节能案例
    - 设备厂商节能方案
    - 专业节能审计报告
  - **评估方法**:
    - 理论计算法
    - 对比测试法
    - 模拟仿真法

## 8. 数据校准实施步骤

### 步骤1: 数据收集（1-2周）
1. 收集最近3-12个月的历史数据
2. 整理设备规格参数
3. 收集电费账单和电价信息
4. 统计设备故障和维修记录

### 步骤2: 数据分析（1周）
1. 计算各项统计指标（均值、标准差、分位数）
2. 分析时段特征（白天/夜间、工作日/周末、季节）
3. 识别异常数据并剔除
4. 建立参数范围

### 步骤3: 参数配置（2-3天）
1. 创建配置文件 `backend/app/config/energy_parameters.py`
2. 实现参数动态加载机制
3. 支持环境变量覆盖
4. 添加参数验证

### 步骤4: 测试验证（3-5天）
1. 使用历史数据进行回测
2. 对比预测值与实际值
3. 调整参数以提高准确性
4. 验证边界情况

### 步骤5: 持续优化（长期）
1. 定期（每季度）更新参数
2. 监控预测准确性
3. 收集用户反馈
4. 优化算法模型

## 9. 配置文件示例

建议创建 `backend/app/config/energy_parameters.py`:

```python
"""
能源计算参数配置
根据真实数据校准后的参数
"""
from typing import Dict, Any
import os

class EnergyParameters:
    """能源计算参数配置类"""
    
    # 功率计算参数
    DEVICE_BASE_POWER: float = float(os.getenv("DEVICE_BASE_POWER", "30.0"))  # kW
    POWER_FLUCTUATION_RANGE: float = 0.10  # ±10%
    
    # 时段系数
    DAYTIME_HOURS: tuple = (6, 22)
    DAYTIME_POWER_FACTOR: tuple = (0.7, 1.3)  # 最小、最大系数
    NIGHTTIME_POWER_FACTOR: tuple = (0.4, 0.6)
    
    # 能效比参数
    BASE_EFFICIENCY_RATIO: float = 3.8  # COP
    EFFICIENCY_LOAD_FACTOR: float = 0.08
    
    # 电价参数（元/kWh）
    ELECTRICITY_PRICE: Dict[str, float] = {
        "peak": 1.2,      # 峰时电价
        "flat": 0.8,      # 平时电价
        "valley": 0.4,    # 谷时电价
    }
    
    # 节能基准
    BASELINE_SAVING_RATE: float = 0.15  # 15%节能潜力
    
    # 设备状态阈值
    DEVICE_ERROR_RATE: float = 0.02   # 2%故障率
    DEVICE_WARNING_RATE: float = 0.10  # 10%预警率
    DEVICE_EFFICIENCY_RANGE: tuple = (75, 95)  # 效率范围
    
    # 分类能耗比例
    ENERGY_CLASSIFICATION: Dict[str, float] = {
        "冷机": 0.40,
        "水泵": 0.18,
        "冷却塔": 0.12,
        "照明": 0.15,
        "电扶梯": 0.08,
        "其他": 0.07,
    }
    
    # 季节系数
    SEASONAL_AMPLITUDE: float = 0.25  # 季节波动幅度
    
    @classmethod
    def get_power_factor(cls, hour: int) -> tuple:
        """获取指定小时的功率系数范围"""
        if cls.DAYTIME_HOURS[0] <= hour <= cls.DAYTIME_HOURS[1]:
            return cls.DAYTIME_POWER_FACTOR
        return cls.NIGHTTIME_POWER_FACTOR
    
    @classmethod
    def get_electricity_price(cls, hour: int) -> float:
        """获取指定小时的电价"""
        if 8 <= hour < 11 or 18 <= hour < 21:
            return cls.ELECTRICITY_PRICE["peak"]
        elif 23 <= hour or hour < 7:
            return cls.ELECTRICITY_PRICE["valley"]
        return cls.ELECTRICITY_PRICE["flat"]
```

## 10. 监控和反馈机制

### 10.1 准确性监控
- 预测值与实际值的误差率
- MAPE (Mean Absolute Percentage Error)
- RMSE (Root Mean Square Error)

### 10.2 异常检测
- 参数超出合理范围预警
- 连续多次预测偏差过大预警
- 数据质量问题预警

### 10.3 优化反馈
- 用户反馈收集
- A/B测试不同参数配置
- 机器学习模型自动优化

## 11. 参考标准

- GB/T 51350-2019 《地铁设计规范》
- GB 50157-2013 《地铁设计规范》
- 地铁能耗监测与管理系统技术规范
- 公共建筑能耗监测系统技术导则

## 总结

以上参数调整需要在获取真实数据后逐步实施。建议采用渐进式调整策略，先调整影响最大的核心参数（功率计算、能效比），再优化细节参数（季节系数、设备状态）。所有参数调整都应该有数据支撑，避免主观臆断。
