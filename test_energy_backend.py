#!/usr/bin/env python3
"""
能源驾驶舱后端API测试脚本

此脚本用于测试后端是否能正常通过环控API获取真实数据。
测试内容包括：
1. 配置完整性检查
2. 站点API连通性测试
3. 实时功率数据获取测试
4. 能耗数据获取测试
5. 能源驾驶舱各个接口测试
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests  # type: ignore

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.config.electricity_config import ElectricityConfig  # noqa: E402
from backend.app.services.energy_service import EnergyService  # noqa: E402
from backend.app.services.realtime_energy_service import (  # noqa: E402
    RealtimeEnergyService,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class EnergyBackendTester:
    """能源后端测试器"""

    def __init__(self):
        self.electricity_config = ElectricityConfig()
        self.realtime_service = RealtimeEnergyService()
        self.energy_service = EnergyService()
        self.test_results = []

    def print_header(self, title: str):
        """打印测试标题"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)

    def print_success(self, message: str):
        """打印成功消息"""
        print(f"✅ {message}")

    def print_error(self, message: str):
        """打印错误消息"""
        print(f"❌ {message}")

    def print_warning(self, message: str):
        """打印警告消息"""
        print(f"⚠️  {message}")

    def print_info(self, message: str):
        """打印信息消息"""
        print(f"ℹ️  {message}")

    def record_test_result(
        self, test_name: str, passed: bool, message: str, data: Optional[Dict] = None
    ):
        """记录测试结果"""
        self.test_results.append(
            {
                "test_name": test_name,
                "passed": passed,
                "message": message,
                "data": data,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def test_config_integrity(self):
        """测试配置完整性"""
        self.print_header("1. 配置完整性检查")

        try:
            # 获取所有站点
            all_stations = self.electricity_config.get_all_stations()
            self.print_info(f"配置文件中总共有 {len(all_stations)} 个站点")

            if not all_stations:
                self.print_error("未找到任何站点配置")
                self.record_test_result("配置完整性", False, "未找到任何站点配置")
                return False

            # 获取所有线路
            line_summary = self.electricity_config.get_line_summary()
            all_lines = [line["line_code"] for line in line_summary]
            self.print_info(f"配置文件中总共有 {len(all_lines)} 条线路: {', '.join(all_lines)}")

            # 检查站点配置完整性
            valid_stations = []
            invalid_stations = []

            for station in all_stations:
                station_name_raw = station.get("name")
                station_ip = station.get("ip")
                line = station.get("line")

                station_name = station_name_raw or "未知"

                if not station_ip:
                    self.print_warning(f"站点 '{station_name}' 缺少IP配置")
                    invalid_stations.append(station_name)
                    continue

                if not line or not station_name_raw:
                    self.print_warning(f"站点 '{station_name}' 缺少线路或名称配置")
                    invalid_stations.append(station_name)
                    continue

                # 检查节能配置
                jieneng_config = self._get_jieneng_config(line, station_name_raw)
                if not jieneng_config:
                    self.print_warning(
                        f"站点 '{station_name}' (线路: {line}) 缺少节能数据配置 (jienengfeijieneng)"
                    )
                    invalid_stations.append(station_name)
                    continue

                object_codes = jieneng_config.get("object_codes", [])
                data_codes = jieneng_config.get("data_codes", [])

                if not object_codes or not data_codes:
                    self.print_warning(
                        f"站点 '{station_name}' 节能配置不完整 "
                        f"(object_codes: {len(object_codes)}, data_codes: {len(data_codes)})"
                    )
                    invalid_stations.append(station_name)
                    continue

                valid_stations.append(station)

            self.print_info(f"配置完整的站点数: {len(valid_stations)}")
            self.print_info(f"配置不完整的站点数: {len(invalid_stations)}")

            if valid_stations:
                self.print_success("配置完整性检查通过")
                self.record_test_result(
                    "配置完整性",
                    True,
                    f"找到 {len(valid_stations)} 个配置完整的站点",
                    {
                        "total_stations": len(all_stations),
                        "valid_stations": len(valid_stations),
                        "invalid_stations": len(invalid_stations),
                    },
                )
                return True
            else:
                self.print_error("没有找到配置完整的站点，无法进行后续测试")
                self.record_test_result("配置完整性", False, "没有找到配置完整的站点")
                return False

        except Exception as e:
            self.print_error(f"配置检查失败: {e}")
            self.record_test_result("配置完整性", False, str(e))
            return False

    def test_api_connectivity(self, max_stations: int = 3):
        """测试API连通性"""
        self.print_header("2. 站点API连通性测试")

        all_stations = self.electricity_config.get_all_stations()
        test_stations = all_stations[:max_stations]

        reachable = []
        unreachable = []

        for station in test_stations:
            station_name = station.get("name", "未知")
            station_ip = station.get("ip")

            if not station_ip:
                self.print_warning(f"站点 '{station_name}' 没有IP配置，跳过")
                continue

            api_url = f"http://{station_ip}:9898"
            self.print_info(f"测试站点 '{station_name}' ({api_url})...")

            try:
                # 尝试访问API
                response = requests.get(f"{api_url}/", timeout=5)
                if response.status_code in [200, 404, 405]:
                    self.print_success(
                        f"站点 '{station_name}' API可访问 (状态码: {response.status_code})"
                    )
                    reachable.append(station_name)
                else:
                    self.print_warning(
                        f"站点 '{station_name}' API响应异常 (状态码: {response.status_code})"
                    )
                    unreachable.append(station_name)

            except requests.Timeout:
                self.print_error(f"站点 '{station_name}' 连接超时 (>5s)")
                unreachable.append(station_name)

            except requests.ConnectionError:
                self.print_error(f"站点 '{station_name}' 无法连接")
                unreachable.append(station_name)

            except Exception as e:
                self.print_error(f"站点 '{station_name}' 测试失败: {e}")
                unreachable.append(station_name)

        self.print_info(f"\n可访问站点数: {len(reachable)}")
        self.print_info(f"不可访问站点数: {len(unreachable)}")

        passed = len(reachable) > 0
        self.record_test_result(
            "API连通性",
            passed,
            f"可访问: {len(reachable)}, 不可访问: {len(unreachable)}",
            {"reachable": reachable, "unreachable": unreachable},
        )

        return passed

    async def test_realtime_power(self, max_stations: int = 3):
        """测试实时功率获取"""
        self.print_header("3. 实时功率数据获取测试")

        all_stations = self.electricity_config.get_all_stations()

        # 只测试配置完整的站点
        valid_stations = []
        for station in all_stations:
            line = station.get("line")
            station_name = station.get("name")
            if not line or not station_name:
                continue
            jieneng_config = self._get_jieneng_config(line, station_name)
            if jieneng_config:
                object_codes = jieneng_config.get("object_codes", [])
                data_codes = jieneng_config.get("data_codes", [])
                if object_codes and data_codes:
                    valid_stations.append(station)

        test_stations = valid_stations[:max_stations]

        success_count = 0
        failed_count = 0
        results = []

        for station in test_stations:
            station_name = station.get("name", "未知")
            self.print_info(f"获取站点 '{station_name}' 实时功率...")

            try:
                power = await self.realtime_service.get_station_realtime_power(station)

                if power is not None:
                    self.print_success(f"站点 '{station_name}' 实时功率: {power:.2f} kW")
                    success_count += 1
                    results.append(
                        {"station": station_name, "power": power, "success": True}
                    )
                else:
                    self.print_error(f"站点 '{station_name}' 未能获取实时功率")
                    failed_count += 1
                    results.append(
                        {"station": station_name, "power": None, "success": False}
                    )

            except Exception as e:
                self.print_error(f"站点 '{station_name}' 测试失败: {e}")
                failed_count += 1
                results.append(
                    {
                        "station": station_name,
                        "power": None,
                        "success": False,
                        "error": str(e),
                    }
                )

        self.print_info(f"\n成功获取: {success_count}")
        self.print_info(f"获取失败: {failed_count}")

        passed = success_count > 0
        self.record_test_result(
            "实时功率获取",
            passed,
            f"成功: {success_count}, 失败: {failed_count}",
            {"results": results},
        )

        return passed

    async def test_energy_consumption(self, max_stations: int = 3):
        """测试能耗数据获取"""
        self.print_header("4. 能耗数据获取测试")

        all_stations = self.electricity_config.get_all_stations()

        # 只测试配置完整的站点
        valid_stations = []
        for station in all_stations:
            line = station.get("line")
            station_name = station.get("name")
            if not line or not station_name:
                continue
            jieneng_config = self._get_jieneng_config(line, station_name)
            if jieneng_config:
                object_codes = jieneng_config.get("object_codes", [])
                data_codes = jieneng_config.get("data_codes", [])
                if object_codes and data_codes:
                    valid_stations.append(station)

        test_stations = valid_stations[:max_stations]

        # 获取当天的能耗（从今天00:00到现在）
        now = datetime.now()
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = now

        self.print_info(f"测试时间段: {start_time} 至 {end_time}")

        success_count = 0
        failed_count = 0
        results = []

        for station in test_stations:
            station_name = station.get("name", "未知")
            self.print_info(f"获取站点 '{station_name}' 能耗数据...")

            try:
                consumption = (
                    await self.realtime_service.get_station_energy_consumption(
                        station, start_time, end_time
                    )
                )

                if consumption is not None:
                    self.print_success(f"站点 '{station_name}' 能耗: {consumption:.2f} kWh")
                    success_count += 1
                    results.append(
                        {
                            "station": station_name,
                            "consumption": consumption,
                            "success": True,
                        }
                    )
                else:
                    self.print_error(f"站点 '{station_name}' 未能获取能耗数据")
                    failed_count += 1
                    results.append(
                        {
                            "station": station_name,
                            "consumption": None,
                            "success": False,
                        }
                    )

            except Exception as e:
                self.print_error(f"站点 '{station_name}' 测试失败: {e}")
                failed_count += 1
                results.append(
                    {
                        "station": station_name,
                        "consumption": None,
                        "success": False,
                        "error": str(e),
                    }
                )

        self.print_info(f"\n成功获取: {success_count}")
        self.print_info(f"获取失败: {failed_count}")

        passed = success_count > 0
        self.record_test_result(
            "能耗数据获取",
            passed,
            f"成功: {success_count}, 失败: {failed_count}",
            {"results": results},
        )

        return passed

    async def test_energy_overview(self):
        """测试能源总览接口"""
        self.print_header("5. 能源总览接口测试")

        try:
            self.print_info("调用 energy_service.get_energy_overview()...")
            result = await self.energy_service.get_energy_overview()

            if result.get("success"):
                data = result.get("data", {})
                self.print_success("能源总览接口调用成功")
                self.print_info(f"总能耗: {data.get('total_consumption', 0)} kWh")
                self.print_info(f"当前功率: {data.get('current_power', 0)} kW")
                self.print_info(f"能效比: {data.get('efficiency_ratio', 0)}")
                self.print_info(f"节能收益: {data.get('cost_saving', 0)} 元")
                self.print_info(f"数据来源: {data.get('data_source', 'unknown')}")

                data_source = data.get("data_source", "unknown")
                if data_source == "real":
                    self.print_success("✅ 使用真实数据")
                elif data_source == "partial":
                    self.print_warning("⚠️ 部分真实数据，部分估算数据")
                else:
                    self.print_warning("⚠️ 数据不可用或使用估算数据")

                self.record_test_result(
                    "能源总览接口",
                    True,
                    "接口调用成功",
                    {"overview": data},
                )
                return True
            else:
                self.print_error(f"能源总览接口调用失败: {result.get('message')}")
                self.record_test_result("能源总览接口", False, result.get("message", "未知错误"))
                return False

        except Exception as e:
            self.print_error(f"测试失败: {e}")
            self.record_test_result("能源总览接口", False, str(e))
            return False

    async def test_realtime_api(self):
        """测试实时数据接口"""
        self.print_header("6. 实时数据接口测试")

        try:
            self.print_info("调用 energy_service.get_realtime_data()...")
            result = await self.energy_service.get_realtime_data()

            if result.get("success"):
                data = result.get("data", {})
                station_data = data.get("data", [])
                self.print_success(f"实时数据接口调用成功 (站点数: {len(station_data)})")

                if station_data:
                    for station in station_data[:3]:
                        station_name = station.get("station_name", "未知")
                        current_power = station.get("current_power", 0)
                        data_source = station.get("data_source", "unknown")
                        self.print_info(
                            f"  - {station_name}: {current_power} kW ({data_source})"
                        )

                    self.record_test_result(
                        "实时数据接口",
                        True,
                        f"获取到 {len(station_data)} 个站点数据",
                        {"station_count": len(station_data)},
                    )
                    return True
                else:
                    self.print_warning("实时数据接口返回空数据")
                    self.record_test_result("实时数据接口", False, "返回空数据")
                    return False
            else:
                self.print_error(f"实时数据接口调用失败: {result.get('message')}")
                self.record_test_result("实时数据接口", False, result.get("message", "未知错误"))
                return False

        except Exception as e:
            self.print_error(f"测试失败: {e}")
            self.record_test_result("实时数据接口", False, str(e))
            return False

    async def test_trend_api(self):
        """测试趋势数据接口"""
        self.print_header("7. 趋势数据接口测试")

        try:
            now = datetime.now()
            start_time = now - timedelta(hours=24)

            self.print_info("调用 energy_service.get_trend_series()...")
            self.print_info(f"时间段: {start_time} 至 {now}")

            result = await self.energy_service.get_trend_series(start_time, now)

            if result.get("success"):
                data = result.get("data", {})
                values = data.get("values", [])
                timestamps = data.get("timestamps", [])
                self.print_success(f"趋势数据接口调用成功 (数据点数: {len(values)})")
                self.print_info(f"时间戳数量: {len(timestamps)}")
                self.print_info(f"粒度: {data.get('granularity', 'unknown')}")
                self.print_info(f"站点数: {data.get('station_count', 0)}")
                self.print_info(f"有效数据点: {data.get('valid_points', 0)}")

                if values:
                    avg_value = sum(values) / len(values)
                    max_value = max(values)
                    min_value = min(values)
                    self.print_info(
                        f"数据范围: 最小={min_value:.2f}, 最大={max_value:.2f}, 平均={avg_value:.2f}"
                    )

                self.record_test_result(
                    "趋势数据接口",
                    True,
                    f"获取到 {len(values)} 个数据点",
                    {"data_points": len(values)},
                )
                return True
            else:
                self.print_error(f"趋势数据接口调用失败: {result.get('error')}")
                self.record_test_result("趋势数据接口", False, result.get("error", "未知错误"))
                return False

        except Exception as e:
            self.print_error(f"测试失败: {e}")
            self.record_test_result("趋势数据接口", False, str(e))
            return False

    def _get_jieneng_config(
        self, line_code: str, station_name: str
    ) -> Optional[Dict[str, Any]]:
        """获取站点的节能配置"""
        try:
            from config_electricity import line_configs

            line_config = line_configs.get(line_code)
            if not line_config:
                return None

            station_config = line_config.get(station_name)
            if not station_config:
                return None

            # 使用data_codes和object_codes数组
            data_codes = station_config.get("data_codes", [])
            object_codes = station_config.get("object_codes", [])

            if not data_codes or not object_codes:
                return None

            return {"data_codes": data_codes, "object_codes": object_codes}

        except Exception:
            return None

    def generate_test_report(self):
        """生成测试报告"""
        self.print_header("测试总结报告")

        passed_count = sum(1 for result in self.test_results if result["passed"])
        failed_count = len(self.test_results) - passed_count

        print(f"\n总测试数: {len(self.test_results)}")
        print(f"通过: {passed_count}")
        print(f"失败: {failed_count}")
        print("\n详细结果:")

        for i, result in enumerate(self.test_results, 1):
            status = "✅ 通过" if result["passed"] else "❌ 失败"
            print(f"{i}. {result['test_name']}: {status}")
            print(f"   消息: {result['message']}")

        # 保存报告到文件
        report_file = "energy_backend_test_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "summary": {
                        "total": len(self.test_results),
                        "passed": passed_count,
                        "failed": failed_count,
                    },
                    "results": self.test_results,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        self.print_success(f"\n测试报告已保存至: {report_file}")

        return passed_count == len(self.test_results)

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("  能源驾驶舱后端API测试")
        print("=" * 80)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Python版本: {sys.version}")

        # 1. 配置完整性检查
        if not self.test_config_integrity():
            self.print_error("\n配置检查失败，无法继续后续测试")
            self.generate_test_report()
            return False

        # 2. API连通性测试
        self.test_api_connectivity(max_stations=3)

        # 3. 实时功率测试
        await self.test_realtime_power(max_stations=3)

        # 4. 能耗数据测试
        await self.test_energy_consumption(max_stations=3)

        # 5. 能源总览接口测试
        await self.test_energy_overview()

        # 6. 实时数据接口测试
        await self.test_realtime_api()

        # 7. 趋势数据接口测试
        await self.test_trend_api()

        # 生成测试报告
        all_passed = self.generate_test_report()

        if all_passed:
            self.print_success("\n🎉 所有测试通过！")
        else:
            self.print_warning("\n⚠️  部分测试失败，请查看上述详细日志")

        return all_passed


async def main():
    """主函数"""
    tester = EnergyBackendTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
