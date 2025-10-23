"""
能源计算参数配置
根据真实数据校准后的参数

使用说明:
1. 默认参数基于行业标准和经验值
2. 可通过环境变量覆盖默认值
3. 在获取真实数据后，应更新这些参数以提高准确性
"""

import os
from typing import Dict, Tuple


class EnergyParameters:
    """能源计算参数配置类"""

    # ==================== 功率计算参数 ====================

    # 设备基础功率 (kW)
    # 说明: 每个设备的平均额定功率
    # 建议: 根据设备铭牌功率或历史平均功率设定
    DEVICE_BASE_POWER: float = float(os.getenv("DEVICE_BASE_POWER", "30.0"))

    # 功率波动范围 (百分比)
    # 说明: 实际功率相对于基础功率的波动范围
    # 建议: 基于历史数据的标准差计算
    POWER_FLUCTUATION_RANGE: float = float(
        os.getenv("POWER_FLUCTUATION_RANGE", "0.10")
    )  # ±10%

    # ==================== 时段系数 ====================

    # 白天时段 (小时)
    # 说明: 定义白天高负荷时段的起止时间
    # 建议: 根据地铁运营时间和客流高峰期调整
    DAYTIME_START_HOUR: int = int(os.getenv("DAYTIME_START_HOUR", "6"))
    DAYTIME_END_HOUR: int = int(os.getenv("DAYTIME_END_HOUR", "22"))

    # 白天功率系数范围 (最小, 最大)
    # 说明: 白天时段功率相对于基础功率的系数范围
    # 建议: 基于历史白天时段平均功率 / 基础功率
    DAYTIME_POWER_FACTOR_MIN: float = float(
        os.getenv("DAYTIME_POWER_FACTOR_MIN", "0.7")
    )
    DAYTIME_POWER_FACTOR_MAX: float = float(
        os.getenv("DAYTIME_POWER_FACTOR_MAX", "1.3")
    )

    # 夜间功率系数范围 (最小, 最大)
    # 说明: 夜间时段功率相对于基础功率的系数范围
    # 建议: 基于历史夜间时段平均功率 / 基础功率
    NIGHTTIME_POWER_FACTOR_MIN: float = float(
        os.getenv("NIGHTTIME_POWER_FACTOR_MIN", "0.4")
    )
    NIGHTTIME_POWER_FACTOR_MAX: float = float(
        os.getenv("NIGHTTIME_POWER_FACTOR_MAX", "0.6")
    )

    # ==================== 能耗计算参数 ====================

    # 日能耗等效运行时间 (小时)
    # 说明: 用于将平均功率转换为日能耗的等效时间
    # 建议: 基于历史数据: 日能耗 / 平均功率
    DAILY_EQUIVALENT_HOURS: float = float(os.getenv("DAILY_EQUIVALENT_HOURS", "20.0"))

    # 能耗波动范围 (百分比)
    # 说明: 日能耗的随机波动范围
    # 建议: 基于历史日能耗数据的标准差
    ENERGY_FLUCTUATION_RANGE: float = float(
        os.getenv("ENERGY_FLUCTUATION_RANGE", "0.08")
    )  # ±8%

    # ==================== 能效比参数 ====================

    # 基准能效比 (COP)
    # 说明: 制冷系统的制冷系数或能效比
    # 建议: 根据冷机设备规格书或历史运行数据设定
    # 典型值: 风冷冷机 2.5-3.5, 水冷冷机 4.0-6.0
    BASE_EFFICIENCY_RATIO: float = float(os.getenv("BASE_EFFICIENCY_RATIO", "3.8"))

    # 能效比负荷影响系数
    # 说明: 负荷率对能效比的影响系数
    # 建议: 基于设备性能曲线或历史数据回归分析
    EFFICIENCY_LOAD_FACTOR: float = float(os.getenv("EFFICIENCY_LOAD_FACTOR", "0.08"))

    # ==================== 电价参数 ====================

    # 电价 (元/kWh)
    # 说明: 不同时段的电价
    # 建议: 根据实际电费账单和分时电价政策设定
    ELECTRICITY_PRICE_PEAK: float = float(
        os.getenv("ELECTRICITY_PRICE_PEAK", "1.2")
    )  # 峰时
    ELECTRICITY_PRICE_FLAT: float = float(
        os.getenv("ELECTRICITY_PRICE_FLAT", "0.8")
    )  # 平时
    ELECTRICITY_PRICE_VALLEY: float = float(
        os.getenv("ELECTRICITY_PRICE_VALLEY", "0.4")
    )  # 谷时

    # 峰时时段 (小时范围列表)
    # 说明: 定义峰时电价的时段
    # 建议: 根据当地电价政策设定
    PEAK_HOURS: list = [
        (8, 11),  # 8:00-11:00
        (18, 21),  # 18:00-21:00
    ]

    # 谷时时段 (小时范围列表)
    # 说明: 定义谷时电价的时段
    # 建议: 根据当地电价政策设定
    VALLEY_HOURS: list = [
        (23, 24),  # 23:00-24:00
        (0, 7),  # 0:00-7:00
    ]

    # ==================== 节能基准参数 ====================

    # 节能基准倍数
    # 说明: 相对于当前能耗的基准能耗倍数
    # 建议: 基于节能改造前的历史数据或行业标准
    # 计算方式: 基准能耗 = 当前能耗 * 倍数
    BASELINE_MULTIPLIER: float = float(
        os.getenv("BASELINE_MULTIPLIER", "1.15")
    )  # 15%节能潜力

    # 节能率目标
    # 说明: 节能优化的目标节能率
    # 建议: 根据节能审计报告或试点项目数据设定
    ENERGY_SAVING_TARGET: float = float(
        os.getenv("ENERGY_SAVING_TARGET", "0.15")
    )  # 15%

    # ==================== 设备状态参数 ====================

    # 设备故障率
    # 说明: 设备处于故障状态的概率
    # 建议: 基于历史设备故障统计数据
    DEVICE_ERROR_RATE: float = float(os.getenv("DEVICE_ERROR_RATE", "0.02"))  # 2%

    # 设备预警率
    # 说明: 设备处于预警状态（效率偏低）的概率
    # 建议: 基于效率监测记录
    DEVICE_WARNING_RATE: float = float(os.getenv("DEVICE_WARNING_RATE", "0.10"))  # 10%

    # 设备效率范围 (最小%, 最大%)
    # 说明: 设备运行效率的正常范围
    # 建议: 基于设备性能测试和历史效率数据
    DEVICE_EFFICIENCY_MIN: float = float(os.getenv("DEVICE_EFFICIENCY_MIN", "75.0"))
    DEVICE_EFFICIENCY_MAX: float = float(os.getenv("DEVICE_EFFICIENCY_MAX", "95.0"))

    # 设备效率阈值
    # 说明: 用于判断设备状态的效率阈值
    DEVICE_EFFICIENCY_EXCELLENT: float = 90.0  # 优秀
    DEVICE_EFFICIENCY_GOOD: float = 80.0  # 良好
    DEVICE_EFFICIENCY_LOW: float = 70.0  # 偏低

    # ==================== 分类能耗比例 ====================

    # 能耗分类比例
    # 说明: 各分类系统的能耗占比
    # 建议: 基于分项计量数据或负荷分析报告
    # 注意: 所有比例之和应为1.0
    ENERGY_CLASSIFICATION: Dict[str, float] = {
        "冷机": float(os.getenv("ENERGY_CLASS_CHILLER", "0.40")),  # 40%
        "水泵": float(os.getenv("ENERGY_CLASS_PUMP", "0.18")),  # 18%
        "冷却塔": float(os.getenv("ENERGY_CLASS_COOLING_TOWER", "0.12")),  # 12%
        "照明": float(os.getenv("ENERGY_CLASS_LIGHTING", "0.15")),  # 15%
        "电扶梯": float(os.getenv("ENERGY_CLASS_ESCALATOR", "0.08")),  # 8%
        "其他": float(os.getenv("ENERGY_CLASS_OTHER", "0.07")),  # 7%
    }

    # ==================== 季节系数参数 ====================

    # 季节波动幅度
    # 说明: 能耗随季节变化的最大波动幅度
    # 建议: 基于历史各月份能耗数据计算标准差
    SEASONAL_AMPLITUDE: float = float(os.getenv("SEASONAL_AMPLITUDE", "0.25"))  # 25%

    # 夏季峰值月份
    # 说明: 能耗最高的月份（通常是制冷需求最大的月份）
    SUMMER_PEAK_MONTH: int = int(os.getenv("SUMMER_PEAK_MONTH", "7"))  # 7月

    # 冬季谷值月份
    # 说明: 能耗最低的月份
    WINTER_VALLEY_MONTH: int = int(os.getenv("WINTER_VALLEY_MONTH", "11"))  # 11月

    # ==================== 同比环比参数 ====================

    # 同比增长率范围
    # 说明: 模拟数据时使用的同比增长率范围
    # 建议: 基于历史同比增长率数据
    YOY_GROWTH_RATE_MIN: float = float(
        os.getenv("YOY_GROWTH_RATE_MIN", "-0.15")
    )  # -15%
    YOY_GROWTH_RATE_MAX: float = float(os.getenv("YOY_GROWTH_RATE_MAX", "0.25"))  # +25%

    # 环比增长率范围
    # 说明: 模拟数据时使用的环比增长率范围
    # 建议: 基于历史环比增长率数据
    MOM_GROWTH_RATE_MIN: float = float(
        os.getenv("MOM_GROWTH_RATE_MIN", "-0.20")
    )  # -20%
    MOM_GROWTH_RATE_MAX: float = float(os.getenv("MOM_GROWTH_RATE_MAX", "0.20"))  # +20%

    # ==================== 优化建议参数 ====================

    # 各类优化措施的单位节能潜力 (kWh/年/站)
    # 说明: 不同优化措施预期的年节能量
    # 建议: 基于节能审计报告、试点项目数据或同类案例
    OPTIMIZATION_SAVING_POTENTIAL: Dict[str, float] = {
        "冷机优化": float(os.getenv("OPT_CHILLER", "50000")),
        "水泵变频": float(os.getenv("OPT_PUMP_VFD", "25000")),
        "照明控制": float(os.getenv("OPT_LIGHTING", "15000")),
        "预防维护": float(os.getenv("OPT_MAINTENANCE", "10000")),
    }

    # ==================== 工具方法 ====================

    @classmethod
    def get_power_factor_range(cls, hour: int) -> Tuple[float, float]:
        """
        获取指定小时的功率系数范围

        Args:
            hour: 小时 (0-23)

        Returns:
            (最小系数, 最大系数)
        """
        if cls.DAYTIME_START_HOUR <= hour <= cls.DAYTIME_END_HOUR:
            return (cls.DAYTIME_POWER_FACTOR_MIN, cls.DAYTIME_POWER_FACTOR_MAX)
        return (cls.NIGHTTIME_POWER_FACTOR_MIN, cls.NIGHTTIME_POWER_FACTOR_MAX)

    @classmethod
    def get_electricity_price(cls, hour: int) -> float:
        """
        获取指定小时的电价

        Args:
            hour: 小时 (0-23)

        Returns:
            电价 (元/kWh)
        """
        # 检查是否在峰时时段
        for start, end in cls.PEAK_HOURS:
            if start <= hour < end:
                return cls.ELECTRICITY_PRICE_PEAK

        # 检查是否在谷时时段
        for start, end in cls.VALLEY_HOURS:
            if start == 0 and end >= hour:
                return cls.ELECTRICITY_PRICE_VALLEY
            if start <= hour < end or (start > end and (hour >= start or hour < end)):
                return cls.ELECTRICITY_PRICE_VALLEY

        # 否则为平时电价
        return cls.ELECTRICITY_PRICE_FLAT

    @classmethod
    def calculate_average_electricity_price(cls) -> float:
        """
        计算24小时平均电价

        Returns:
            平均电价 (元/kWh)
        """
        total_price = sum(cls.get_electricity_price(hour) for hour in range(24))
        return total_price / 24

    @classmethod
    def get_seasonal_factor(cls, month: int) -> float:
        """
        获取指定月份的季节系数

        Args:
            month: 月份 (1-12)

        Returns:
            季节系数 (1.0为基准)
        """
        # 使用正弦曲线模拟季节变化
        # 峰值在SUMMER_PEAK_MONTH，谷值在WINTER_VALLEY_MONTH
        import math

        # 将月份映射到0-2π的相位
        phase = (month - cls.SUMMER_PEAK_MONTH) * (2 * math.pi / 12)

        # 计算季节系数: 1.0 + amplitude * sin(phase)
        factor = 1.0 + cls.SEASONAL_AMPLITUDE * math.sin(phase)

        return factor

    @classmethod
    def get_device_status(cls, efficiency: float) -> tuple:
        """
        根据设备效率判断设备状态

        Args:
            efficiency: 设备效率 (%)

        Returns:
            (状态码, 状态描述)
        """
        if efficiency >= cls.DEVICE_EFFICIENCY_EXCELLENT:
            return ("normal", "运行优秀")
        elif efficiency >= cls.DEVICE_EFFICIENCY_GOOD:
            return ("normal", "正常运行")
        elif efficiency >= cls.DEVICE_EFFICIENCY_LOW:
            return ("warning", "效率偏低")
        else:
            return ("error", "效率异常")

    @classmethod
    def validate_classification_sum(cls) -> bool:
        """
        验证分类能耗比例总和是否为1.0

        Returns:
            是否有效
        """
        total = sum(cls.ENERGY_CLASSIFICATION.values())
        return abs(total - 1.0) < 0.01  # 允许1%的误差

    @classmethod
    def get_config_summary(cls) -> Dict[str, any]:
        """
        获取配置摘要

        Returns:
            配置参数摘要字典
        """
        return {
            "device_base_power": cls.DEVICE_BASE_POWER,
            "daytime_hours": f"{cls.DAYTIME_START_HOUR}:00-{cls.DAYTIME_END_HOUR}:00",
            "base_efficiency_ratio": cls.BASE_EFFICIENCY_RATIO,
            "avg_electricity_price": round(
                cls.calculate_average_electricity_price(), 3
            ),
            "energy_saving_target": f"{cls.ENERGY_SAVING_TARGET * 100}%",
            "seasonal_amplitude": f"±{cls.SEASONAL_AMPLITUDE * 100}%",
            "classification_valid": cls.validate_classification_sum(),
        }


# 创建全局实例
energy_params = EnergyParameters()


# 验证配置
if not energy_params.validate_classification_sum():
    import logging

    logger = logging.getLogger(__name__)
    logger.warning(
        f"能耗分类比例总和不为1.0: {sum(energy_params.ENERGY_CLASSIFICATION.values())}"
    )


if __name__ == "__main__":
    # 测试和展示配置
    print("=" * 60)
    print("能源计算参数配置")
    print("=" * 60)

    print("\n配置摘要:")
    for key, value in energy_params.get_config_summary().items():
        print(f"  {key}: {value}")

    print("\n分时电价:")
    for hour in [2, 8, 12, 18, 23]:
        price = energy_params.get_electricity_price(hour)
        print(f"  {hour}:00 - {price}元/kWh")

    print("\n季节系数:")
    for month in [1, 4, 7, 10]:
        factor = energy_params.get_seasonal_factor(month)
        print(f"  {month}月 - {factor:.3f}")

    print("\n设备状态判断:")
    for eff in [95, 85, 75, 65]:
        status, desc = energy_params.get_device_status(eff)
        print(f"  效率{eff}% - {status}: {desc}")
