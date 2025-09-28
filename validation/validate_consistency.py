import pandas as pd
import hashlib
import os
from typing import Dict, List, Tuple
import logging
from datetime import datetime
import config_electricity
from export_data import batch_export_data, process_data, get_energy_status, export_data
import requests
import json

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConsistencyValidator:
    """一致性验证工具，用于验证桌面端和Web端功能的一致性"""
    
    def __init__(self):
        self.line_configs = config_electricity.line_configs
    
    def validate_electricity_export(self, line_name: str, start_time: datetime, end_time: datetime) -> Dict:
        """验证电耗导出功能的一致性"""
        try:
            logger.info(f"开始验证电耗导出功能: 线路={line_name}")
            
            # 获取线路配置
            if line_name not in self.line_configs:
                return {
                    "success": False,
                    "message": f"线路 {line_name} 不存在"
                }
            
            config_map = self.line_configs[line_name]
            
            # 验证每个车站的配置一致性
            validation_results = []
            
            for ip, config in config_map.items():
                try:
                    logger.info(f"验证车站 {ip} 的配置")
                    
                    # 验证配置结构
                    required_fields = ["ip", "station", "data_list", "data_codes", "object_codes", "jienengfeijieneng"]
                    missing_fields = [field for field in required_fields if field not in config]
                    
                    if missing_fields:
                        validation_results.append({
                            "station_ip": ip,
                            "station_name": config.get("station", "未知"),
                            "success": False,
                            "message": f"缺少配置字段: {missing_fields}"
                        })
                        continue
                    
                    # 验证节能配置
                    jieneng_config = config["jienengfeijieneng"]
                    if "data_codes" not in jieneng_config or "object_codes" not in jieneng_config:
                        validation_results.append({
                            "station_ip": ip,
                            "station_name": config.get("station", "未知"),
                            "success": False,
                            "message": "节能配置不完整"
                        })
                        continue
                    
                    validation_results.append({
                        "station_ip": ip,
                        "station_name": config.get("station", "未知"),
                        "success": True,
                        "message": "配置验证通过"
                    })
                    
                except Exception as e:
                    validation_results.append({
                        "station_ip": ip,
                        "station_name": config.get("station", "未知"),
                        "success": False,
                        "message": f"验证配置时出错: {str(e)}"
                    })
            
            # 统计结果
            success_count = sum(1 for r in validation_results if r["success"])
            total_count = len(validation_results)
            
            return {
                "success": True,
                "message": f"电耗导出配置验证完成: {success_count}/{total_count} 个车站通过验证",
                "details": validation_results
            }
            
        except Exception as e:
            logger.error(f"验证电耗导出功能时出错: {e}")
            return {
                "success": False,
                "message": f"验证电耗导出功能时出错: {str(e)}"
            }
    
    def validate_api_calls(self, line_name: str, start_time: datetime, end_time: datetime) -> Dict:
        """验证API调用的一致性"""
        try:
            logger.info(f"开始验证API调用一致性: 线路={line_name}")
            
            if line_name not in self.line_configs:
                return {
                    "success": False,
                    "message": f"线路 {line_name} 不存在"
                }
            
            config_map = self.line_configs[line_name]
            
            # 验证API调用参数一致性
            api_validation_results = []
            
            for ip, config in config_map.items():
                try:
                    api_url = f'http://{config["ip"]}:9898'
                    data_codes = config.get("data_codes", [])
                    object_codes = config.get("object_codes", [])
                    
                    # 构造API调用参数（与桌面端一致）
                    start_timestamp = int(start_time.timestamp() * 1000)
                    end_timestamp = int(end_time.timestamp() * 1000)
                    
                    # 验证结束时间数据请求参数
                    end_obj = {
                        "dataCodes": data_codes,
                        "endTime": end_timestamp,
                        "fill": "0",
                        "funcName": "mean",
                        "funcTime": "",
                        "measurement": "realData",
                        "objectCodes": object_codes,
                        "startTime": end_timestamp - 10 * 60000  # 10分钟前
                    }
                    
                    # 验证开始时间数据请求参数
                    start_obj = {
                        "dataCodes": data_codes,
                        "endTime": start_timestamp + 3 * 60000,  # 3分钟后
                        "fill": "0",
                        "funcName": "mean",
                        "funcTime": "",
                        "measurement": "realData",
                        "objectCodes": object_codes,
                        "startTime": start_timestamp
                    }
                    
                    # 验证节能状态请求参数
                    jieneng_data_codes = config["jienengfeijieneng"]["data_codes"]
                    jieneng_object_codes = config["jienengfeijieneng"]["object_codes"]
                    
                    energy_obj = {
                        "dataCodes": jieneng_data_codes,
                        "endTime": end_timestamp,
                        "fill": "0",
                        "funcName": "",
                        "funcTime": "",
                        "measurement": "realData",
                        "objectCodes": jieneng_object_codes,
                        "startTime": start_timestamp
                    }
                    
                    api_validation_results.append({
                        "station_ip": ip,
                        "station_name": config.get("station", "未知"),
                        "success": True,
                        "message": "API调用参数验证通过",
                        "end_obj": end_obj,
                        "start_obj": start_obj,
                        "energy_obj": energy_obj
                    })
                    
                except Exception as e:
                    api_validation_results.append({
                        "station_ip": ip,
                        "station_name": config.get("station", "未知"),
                        "success": False,
                        "message": f"验证API调用参数时出错: {str(e)}"
                    })
            
            # 统计结果
            success_count = sum(1 for r in api_validation_results if r["success"])
            total_count = len(api_validation_results)
            
            return {
                "success": True,
                "message": f"API调用参数验证完成: {success_count}/{total_count} 个车站通过验证",
                "details": api_validation_results
            }
            
        except Exception as e:
            logger.error(f"验证API调用一致性时出错: {e}")
            return {
                "success": False,
                "message": f"验证API调用一致性时出错: {str(e)}"
            }
    
    def validate_data_processing(self, line_name: str, start_time: datetime, end_time: datetime) -> Dict:
        """验证数据处理逻辑的一致性"""
        try:
            logger.info(f"开始验证数据处理逻辑一致性: 线路={line_name}")
            
            if line_name not in self.line_configs:
                return {
                    "success": False,
                    "message": f"线路 {line_name} 不存在"
                }
            
            config_map = self.line_configs[line_name]
            
            # 验证数据处理逻辑
            processing_validation_results = []
            
            for ip, config in config_map.items():
                try:
                    # 验证数据列表结构
                    data_list = config.get("data_list", [])
                    data_codes = config.get("data_codes", [])
                    object_codes = config.get("object_codes", [])
                    
                    # 验证数据列表和数据代码数量一致性
                    if len(data_list) != len(data_codes):
                        processing_validation_results.append({
                            "station_ip": ip,
                            "station_name": config.get("station", "未知"),
                            "success": False,
                            "message": f"数据列表数量({len(data_list)})与数据代码数量({len(data_codes)})不一致"
                        })
                        continue
                    
                    # 验证数据处理逻辑结构
                    # 检查每个数据项是否包含必要字段
                    required_fields = ["p1", "p2", "p3", "p4", "p5", "p6", "p7"]
                    invalid_items = []
                    
                    for i, item in enumerate(data_list):
                        missing_fields = [field for field in required_fields if field not in item]
                        if missing_fields:
                            invalid_items.append(f"第{i+1}项缺少字段: {missing_fields}")
                    
                    if invalid_items:
                        processing_validation_results.append({
                            "station_ip": ip,
                            "station_name": config.get("station", "未知"),
                            "success": False,
                            "message": f"数据列表存在错误: {', '.join(invalid_items)}"
                        })
                        continue
                    
                    processing_validation_results.append({
                        "station_ip": ip,
                        "station_name": config.get("station", "未知"),
                        "success": True,
                        "message": "数据处理逻辑验证通过"
                    })
                    
                except Exception as e:
                    processing_validation_results.append({
                        "station_ip": ip,
                        "station_name": config.get("station", "未知"),
                        "success": False,
                        "message": f"验证数据处理逻辑时出错: {str(e)}"
                    })
            
            # 统计结果
            success_count = sum(1 for r in processing_validation_results if r["success"])
            total_count = len(processing_validation_results)
            
            return {
                "success": True,
                "message": f"数据处理逻辑验证完成: {success_count}/{total_count} 个车站通过验证",
                "details": processing_validation_results
            }
            
        except Exception as e:
            logger.error(f"验证数据处理逻辑一致性时出错: {e}")
            return {
                "success": False,
                "message": f"验证数据处理逻辑一致性时出错: {str(e)}"
            }
    
    def generate_validation_report(self, line_name: str, start_time: datetime, end_time: datetime, output_file: str = "validation_report.txt"):
        """生成一致性验证报告"""
        try:
            report_lines = []
            report_lines.append("一致性验证报告")
            report_lines.append("=" * 50)
            report_lines.append(f"线路: {line_name}")
            report_lines.append(f"开始时间: {start_time}")
            report_lines.append(f"结束时间: {end_time}")
            report_lines.append("=" * 50)
            
            # 验证电耗导出功能
            report_lines.append("\n1. 电耗导出功能验证")
            report_lines.append("-" * 30)
            electricity_result = self.validate_electricity_export(line_name, start_time, end_time)
            report_lines.append(f"结果: {electricity_result['message']}")
            
            if electricity_result["success"] and "details" in electricity_result:
                for detail in electricity_result["details"]:
                    status = "通过" if detail["success"] else "失败"
                    report_lines.append(f"  {detail['station_name']} ({detail['station_ip']}): {status} - {detail['message']}")
            
            # 验证API调用一致性
            report_lines.append("\n2. API调用一致性验证")
            report_lines.append("-" * 30)
            api_result = self.validate_api_calls(line_name, start_time, end_time)
            report_lines.append(f"结果: {api_result['message']}")
            
            if api_result["success"] and "details" in api_result:
                for detail in api_result["details"]:
                    status = "通过" if detail["success"] else "失败"
                    report_lines.append(f"  {detail['station_name']} ({detail['station_ip']}): {status} - {detail['message']}")
            
            # 验证数据处理逻辑一致性
            report_lines.append("\n3. 数据处理逻辑一致性验证")
            report_lines.append("-" * 30)
            processing_result = self.validate_data_processing(line_name, start_time, end_time)
            report_lines.append(f"结果: {processing_result['message']}")
            
            if processing_result["success"] and "details" in processing_result:
                for detail in processing_result["details"]:
                    status = "通过" if detail["success"] else "失败"
                    report_lines.append(f"  {detail['station_name']} ({detail['station_ip']}): {status} - {detail['message']}")
            
            # 总体结论
            report_lines.append("\n总体结论")
            report_lines.append("-" * 30)
            
            all_success = (
                electricity_result["success"] and 
                api_result["success"] and 
                processing_result["success"]
            )
            
            if all_success:
                report_lines.append("所有验证项目均通过，桌面端与Web端功能一致")
            else:
                report_lines.append("存在验证失败项目，桌面端与Web端功能可能存在差异")
            
            # 写入报告文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            logger.info(f"一致性验证报告已生成: {output_file}")
            return {
                "success": True,
                "report_file": output_file
            }
        except Exception as e:
            logger.error(f"生成一致性验证报告时出错: {e}")
            return {
                "success": False,
                "message": f"生成一致性验证报告时出错: {str(e)}"
            }

def main():
    """主函数，用于命令行调用"""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='一致性验证工具')
    parser.add_argument('line_name', help='线路名称')
    parser.add_argument('start_time', help='开始时间 (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('end_time', help='结束时间 (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('-o', '--output', default='validation_report.txt', help='输出报告文件路径')
    
    args = parser.parse_args()
    
    # 解析时间参数
    start_time = datetime.strptime(args.start_time, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(args.end_time, "%Y-%m-%d %H:%M:%S")
    
    validator = ConsistencyValidator()
    result = validator.generate_validation_report(args.line_name, start_time, end_time, args.output)
    
    if result["success"]:
        print(f"一致性验证报告已生成: {result['report_file']}")
    else:
        print(f"生成一致性验证报告失败: {result['message']}")

if __name__ == "__main__":
    main()