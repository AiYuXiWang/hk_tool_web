import requests
import pandas as pd
from datetime import datetime
import concurrent.futures
from functools import partial
import os
import logging
import asyncio
import config_electricity
import db_config
from db_config import select_bus_object_point_data, execute_query, DB_CONFIG
from models import ExportResult, StationExportResult
from logger_config import app_logger

# 使用配置好的logger
logger = app_logger

class ElectricityMeter:
    """电表数据模型"""
    def __init__(self, p1, p2, p3, p4, p5, p6, p7):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.p5 = p5
        self.p6 = p6
        self.p7 = p7
        self.p8 = ""  # 耗电量
        self.p9 = ""  # 电表起码
        self.p10 = ""  # 电表止码

class ElectricityExportService:
    """电耗数据导出服务"""
    
    def __init__(self):
        self.line_configs = config_electricity.line_configs

    def get_historical_data(self, api_url, obj):
        """获取历史数据"""
        try:
            logger.info(f"开始请求历史数据: {api_url}")
            response = requests.post(f"{api_url}/data/selectHisData", json=obj, timeout=5)  # 5秒超时
            if response.status_code == 200:
                data = response.json().get("data", [])
                logger.info(f"成功获取历史数据: {api_url}, 数据条数: {len(data)}")
                return data
            else:
                logger.error(f"获取数据失败: {api_url}, 状态码: {response.status_code}")
                return []
        except requests.Timeout:
            logger.error(f"API请求超时(超过5秒): {api_url}")
            return []
        except requests.ConnectionError:
            logger.error(f"API连接失败: {api_url}")
            return []
        except requests.RequestException as e:
            logger.error(f"API请求异常: {api_url}, 错误: {e}")
            return []

    def get_energy_status(self, api_url, data_code, object_code, start_time, end_time):
        """获取节能状态"""
        obj = {
            "dataCodes": data_code,
            "endTime": int(end_time.timestamp() * 1000),
            "fill": "0",
            "funcName": "",
            "funcTime": "",
            "measurement": "realData",
            "objectCodes": object_code,
            "startTime": int(start_time.timestamp() * 1000)
        }
        
        try:
            logger.info(f"开始请求节能状态数据: {api_url}")
            response = requests.post(f"{api_url}/data/selectHisData", json=obj, timeout=5)  # 5秒超时
            if response.status_code == 200:
                data = response.json().get("data", [])
                logger.info(f"节能状态数据数量: {len(data)}")
                
                if len(data) == 1:
                    values = data[0].get("values", [])
                    status_list = []
                    if values:
                        flag = values[0]["value"]
                        logger.info(f"开始时间: {values[0]['time']}")
                        status_list.append({
                            "开始时间": datetime.strptime(values[0]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S"),
                            "结束时间": "",
                            "节能状态": "节能" if flag == 1 else "非节能",
                            "系统": ""
                        })
                        for i in range(1, len(values)):
                            if values[i]["value"] != flag and values[i]["value"] != '' and values[i]["value"] is not None:
                                logger.info(f"结束时间时间: {values[i]['time']}")
                                status_list[-1]["结束时间"] = datetime.strptime(values[i]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
                                flag = values[i]["value"]
                                status_list.append({
                                    "开始时间": datetime.strptime(values[i]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S"),
                                    "结束时间": "",
                                    "节能状态": "节能" if flag == 1 else "非节能",
                                    "系统": ""
                                })
                        if status_list:
                            logger.info(f"最后时间: {values[-1]['time']}")
                            status_list[-1]["结束时间"] = datetime.strptime(values[-1]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
                    return status_list
                    
                if len(data) == 4:  # 针对8号线风水分开的特殊处理
                    # 水系统
                    values = data[0].get("values", [])
                    status_list = []
                    if values:
                        flag = values[0]["value"]
                        status_list.append({
                            "开始时间": datetime.strptime(values[0]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S"),
                            "结束时间": "",
                            "节能状态": "节能" if flag == 1 else "非节能",
                            "系统": "水系统"
                        })
                        for i in range(1, len(values)):
                            if values[i]["value"] != flag and values[i]["value"] != '' and values[i]["value"] is not None:
                                status_list[-1]["结束时间"] = datetime.strptime(values[i]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
                                flag = values[i]["value"]
                                status_list.append({
                                    "开始时间": datetime.strptime(values[i]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S"),
                                    "结束时间": "",
                                    "节能状态": "节能" if flag == 1 else "非节能",
                                    "系统": "水系统"
                                })
                        if status_list:
                            status_list[-1]["结束时间"] = datetime.strptime(values[-1]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
                            
                    # 风系统
                    values = data[3].get("values", [])
                    if values:
                        flag = values[0]["value"]
                        status_list.append({
                            "开始时间": datetime.strptime(values[0]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S"),
                            "结束时间": "",
                            "节能状态": "节能" if flag == 1 else "非节能",
                            "系统": "风系统"
                        })
                        for i in range(1, len(values)):
                            if values[i]["value"] != flag and values[i]["value"] != '' and values[i]["value"] is not None:
                                status_list[-1]["结束时间"] = datetime.strptime(values[i]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
                                flag = values[i]["value"]
                                status_list.append({
                                    "开始时间": datetime.strptime(values[i]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S"),
                                    "结束时间": "",
                                    "节能状态": "节能" if flag == 1 else "非节能",
                                    "系统": "风系统"
                                })
                        if status_list:
                            status_list[-1]["结束时间"] = datetime.strptime(values[-1]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")

                    return status_list
            else:
                logger.error(f"获取节能状态数据失败: {api_url}, 状态码: {response.status_code}")
        except requests.Timeout:
            logger.error(f"节能状态API请求超时(超过5秒): {api_url}")
            return None
        except requests.ConnectionError:
            logger.error(f"节能状态API连接失败: {api_url}")
            return None
        except requests.RequestException as e:
            logger.error(f"节能状态API请求异常: {api_url}, 错误: {e}")
            return None
        except Exception as e:
            logger.error(f"处理节能状态数据错误: {e}")
            return None
            
        return []

    def process_data(self, api_url, data_list, data_codes, object_codes, start_time, end_time):
        """处理数据"""
        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)

        # 获取结束时间的数据
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
        end_data = self.get_historical_data(api_url, end_obj)
        
        # 如果API超时，直接返回空数据
        if not end_data:
            logger.error(f"获取结束时间数据失败，停止处理: {api_url}")
            return []
        
        # 获取开始时间的数据
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
        start_data = self.get_historical_data(api_url, start_obj)
        
        # 如果API超时，直接返回空数据
        if not start_data:
            logger.error(f"获取开始时间数据失败，停止处理: {api_url}")
            return []
        
        # 计算耗电量
        for i in range(len(data_list)):
            for j in range(len(object_codes)):
                start_entry = next((item for item in start_data if item["tags"]["dataCode"] == data_codes[i] and item["tags"]["objectCode"] == object_codes[j]), None)
                end_entry = next((item for item in end_data if item["tags"]["dataCode"] == data_codes[i] and item["tags"]["objectCode"] == object_codes[j]), None)

                if start_entry and end_entry and start_entry["values"] and end_entry["values"]:
                    data_list[i]["p9"] = round(start_entry["values"][0]["value"], 2)
                    data_list[i]["p10"] = round(end_entry["values"][0]["value"], 2)
                    if end_entry["values"][0]["value"] - start_entry["values"][0]["value"] >= -1:
                        data_list[i]["p8"] = round(end_entry["values"][0]["value"] - start_entry["values"][0]["value"], 2)
                    else:
                        data_list[i]["p8"] = "电表异常"
                    break

        return data_list

    def export_data(self, data_list, energy_status, start_time, end_time, filename="电耗统计.xls"):
        """导出数据到Excel"""
        try:
            #准备查询起止时间
            start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
            end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
            date_time = pd.DataFrame([{"开始时间": start_time_str, "结束时间": end_time_str}])

            # 准备节能状态数据
            energy_status_df = pd.DataFrame(energy_status)

            # 准备电表数据
            data_df = pd.DataFrame([{
                "序号": d["p1"],
                "站端区域": d["p2"],
                "设备名称": d["p3"],
                "抽屉柜编号": d["p4"],
                "设备功率(kw)": d["p5"],
                "电表安装位置": d["p6"],
                "互感器倍率": d["p7"],
                "耗电量(KWh)": d["p8"],
                "电表起码(KWh)": d["p9"],
                "电表止码(KWh)": d["p10"]
            } for d in data_list])

            # 创建 Excel 文件
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                #导出查询时间
                date_time.to_excel(writer, sheet_name='Sheet1', startrow=0, index=False)
                # 导出节能状态
                energy_status_df.to_excel(writer, sheet_name='Sheet1', startrow=2, index=False)

                # 导出电表数据
                data_df.to_excel(writer, sheet_name='Sheet1', startrow=len(energy_status_df) + 4, index=False)
                # 获取工作表对象
                worksheet = writer.sheets['Sheet1']
                # 自动调整列宽
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter  # 获取列字母

                    # 计算列中最大字符长度
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass

                    # 设置列宽（加2作为缓冲）
                    adjusted_width = (max_length + 2)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            logger.info(f"数据已导出到 {filename}")
            return True
        except Exception as e:
            logger.error(f"导出数据时出错: {e}")
            return False

    def export_single_ip(self, ip, config, start_time, end_time):
        """导出单个IP的数据"""
        station_name = config.get('station', '未知站名')
        try:
            logger.info(f"开始处理站点: {station_name} ({ip})")
            api_url = f'http://{config["ip"]}:9898'
            data_list = config["data_list"]
            data_codes = config.get("data_codes", [])
            object_codes = config.get("object_codes", [])
            
            if not data_codes or not object_codes:
                logger.error(f"{station_name} ({ip}) 缺少数据点配置")
                return False, "缺少数据点配置", None
            
            logger.info(f"{station_name} ({ip}) 正在获取节能状态数据...")
            energy_status = self.get_energy_status(
                api_url, 
                config["jienengfeijieneng"]["data_codes"], 
                config["jienengfeijieneng"]["object_codes"], 
                start_time, 
                end_time
            )
            
            # 检查节能状态API是否超时失败
            if energy_status is None:
                error_msg = "API超时，导出失败"
                logger.error(f"{station_name} ({ip}) {error_msg}")
                return False, error_msg, None
            
            logger.info(f"{station_name} ({ip}) 正在处理电耗数据...")
            processed_data = self.process_data(api_url, data_list, data_codes, object_codes, start_time, end_time)
            
            # 检查数据处理是否成功（如果所有API都超时，数据为空）
            if not processed_data or all(d.get("p8") == "" for d in processed_data):
                error_msg = "API超时，数据获取失败"
                logger.error(f"{station_name} ({ip}) {error_msg}")
                return False, error_msg, None
            
            filename = f"电耗统计_{config['ip']}_{ip}_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}.xlsx"
            
            logger.info(f"{station_name} ({ip}) 正在导出文件: {filename}")
            if self.export_data(processed_data, energy_status, start_time, end_time, filename):
                logger.info(f"{station_name} ({ip}) 导出成功: {filename}")
                return True, None, filename
            else:
                logger.error(f"{station_name} ({ip}) 导出文件失败")
                return False, "导出文件失败", None
        except Exception as e:
            error_msg = f"处理异常: {str(e)}"
            logger.error(f"{station_name} ({ip}) {error_msg}")
            return False, error_msg, None

    async def export_data_async(self, selected_line, start_time, end_time):
        """异步导出数据"""
        try:
            config_map = self.line_configs.get(selected_line, {})
            if not config_map:
                logger.error(f"所选线路 {selected_line} 没有配置信息")
                return ExportResult(
                    success=False,
                    message=f"所选线路 {selected_line} 没有配置信息"
                )

            logger.info(f"开始导出 {selected_line} 的电耗数据，共 {len(config_map)} 个站点")
            logger.info(f"导出时间范围: {start_time} 至 {end_time}")
            
            # 打印所有车站信息
            logger.info("车站列表:")
            for ip, config in config_map.items():
                station_name = config.get('station', '未知站名')
                logger.info(f"  - {station_name} ({ip})")
            
            # 使用线程池执行CPU密集型任务
            loop = asyncio.get_event_loop()
            
            results = []
            success_count = 0
            fail_count = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(
                        self.export_single_ip,
                        ip, config, start_time, end_time
                    ): ip for ip, config in config_map.items()
                }

                for future in concurrent.futures.as_completed(futures):
                    ip = futures[future]
                    station_name = config_map[ip].get('station', '未知站名')
                    try:
                        success, error, filename = future.result(timeout=15)  # 15秒超时
                        if success:
                            success_count += 1
                            logger.info(f"✓ {station_name} ({ip}) 导出成功 - 文件: {filename}")
                            results.append(StationExportResult(
                                station_ip=ip,
                                station_name=station_name,
                                success=True,
                                message="导出成功",
                                file_path=filename
                            ))
                        else:
                            fail_count += 1
                            logger.error(f"✗ {station_name} ({ip}) 导出失败: {error}")
                            results.append(StationExportResult(
                                station_ip=ip,
                                station_name=station_name,
                                success=False,
                                message=error or "导出失败",
                                file_path=None
                            ))
                    except concurrent.futures.TimeoutError:
                        fail_count += 1
                        error_msg = "导出超时(15秒)"
                        logger.error(f"✗ {station_name} ({ip}) {error_msg}")
                        results.append(StationExportResult(
                            station_ip=ip,
                            station_name=station_name,
                            success=False,
                            message=error_msg,
                            file_path=None
                        ))
                    except Exception as e:
                        fail_count += 1
                        error_msg = f"未知错误: {str(e)}"
                        logger.error(f"✗ {station_name} ({ip}) {error_msg}")
                        results.append(StationExportResult(
                            station_ip=ip,
                            station_name=station_name,
                            success=False,
                            message=error_msg,
                            file_path=None
                        ))

            # 打印最终统计结果
            logger.info(f"\n=== 导出统计结果 ===")
            logger.info(f"总计: {len(config_map)} 个站点")
            logger.info(f"成功: {success_count} 个")
            logger.info(f"失败: {fail_count} 个")
            
            if fail_count > 0:
                logger.info(f"\n=== 失败站点详情 ===")
                for result in results:
                    if not result.success:
                        logger.info(f"✗ {result.station_name} ({result.station_ip}): {result.message}")
            
            logger.info(f"=== 导出完成 ===")

            return ExportResult(
                success=True,
                message=f"导出完成: 成功 {success_count} 个, 失败 {fail_count} 个",
                details={
                    "total": len(config_map),
                    "success_count": success_count,
                    "fail_count": fail_count,
                    "results": [result.dict() for result in results]
                }
            )
        except Exception as e:
            logger.error(f"异步导出数据时出错: {e}")
            return ExportResult(
                success=False,
                message=f"导出失败: {str(e)}"
            )


class SensorDataExportService:
    """传感器数据导出服务"""
    
    def __init__(self):
        self.line_configs = config_electricity.line_configs

    def process_temperature_humidity_sensor_data(self, point_data, point_pinlv_data, point_mingcheng_data):
        """
        处理温湿度传感器的点位 (将JavaScript逻辑转换为Python)
        """
        object_codes = set()
        data_codes = set()
        point_name_list = []  # 用来存点位名称，方便计算
        fengji_point_name_list = []
        daxt_point_name_list = []
        flag = 0  # 0-18 循环一次（每组风机对应19个温湿度传感器）
        pinlvflag = 0

        for item in point_data:
            if isinstance(item, tuple) and 'fRoomTemp' not in item[0]:
                if flag == 0:
                    # 添加进风机频率的点位名称
                    if len(point_pinlv_data) > pinlvflag:
                        str_val = point_pinlv_data[pinlvflag][1]
                        str1_val = point_pinlv_data[pinlvflag + 1][1] if len(point_pinlv_data) > pinlvflag + 1 else None
                        symbol = "."
                        index = str_val.find(symbol)
                        if index != -1:
                            object_codes.add(str_val[:index])
                            data_codes.add(str_val[index + 1:])
                            fengji_point_name_list.append({
                                "objectCode": str_val[:index],
                                "dataCode": str_val[index + 1:]
                            })

                        if str1_val:
                            index1 = str1_val.find(symbol)
                            if index1 != -1:
                                object_codes.add(str1_val[:index1])
                                data_codes.add(str1_val[index1 + 1:])
                                fengji_point_name_list.append({
                                    "objectCode": str1_val[:index1],
                                    "dataCode": str1_val[index1 + 1:]
                                })

                        pinlvflag = pinlvflag + 2

                if flag == 18:
                    point_name_list.append(fengji_point_name_list)
                    fengji_point_name_list = []
                    flag = 0
                else:
                    str_val = item[1]
                    symbol = "."
                    index = str_val.find(symbol)

                    if index != -1:
                        object_codes.add(str_val[:index])
                        data_codes.add(str_val[index + 1:])
                        fengji_point_name_list.append({
                            "objectCode": str_val[:index],
                            "dataCode": str_val[index + 1:]
                        })
                    flag += 1
            elif isinstance(item, tuple):
                str_val = item[1]
                symbol = "."
                index = str_val.find(symbol)

                if index != -1:
                    object_codes.add(str_val[:index])
                    data_codes.add(str_val[index + 1:])
                    daxt_point_name_list.append({
                        "objectCode": str_val[:index],
                        "dataCode": str_val[index + 1:]
                    })

        point_name_list.append(daxt_point_name_list)
        return point_name_list, list(object_codes), list(data_codes)
        
    def fetch_sensor_data(self, api_url, dataCodes, objectCodes, start_time, end_time):
        """
        获取传感器历史数据
        """
        try:
            logger.info(f"开始请求传感器数据: {api_url}")
            # 构造查询对象
            obj = {
                "dataCodes": dataCodes,
                "endTime": int(end_time.timestamp() * 1000),
                "fill": "0",
                "funcName": "MEAN",
                "funcTime": "1h",
                "measurement": "realData",
                "objectCodes": objectCodes,
                "startTime": int(start_time.timestamp() * 1000)
            }

            # 发送请求获取历史数据
            response = requests.post(f"{api_url}/data/selectHisData", json=obj, timeout=5)  # 5秒超时
            if response.status_code == 200:
                data = response.json().get("data", [])
                logger.info(f"成功获取传感器数据: {api_url}, 数据条数: {len(data)}")
                return data
            else:
                logger.error(f"获取传感器数据失败，状态码: {response.status_code}")
                return None
        except requests.Timeout:
            logger.error(f"传感器API请求超时(超过5秒): {api_url}")
            return None
        except requests.ConnectionError:
            logger.error(f"传感器API连接失败: {api_url}")
            return None
        except requests.RequestException as e:
            logger.error(f"传感器API请求异常: {api_url}, 错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取传感器数据时出错: {str(e)}")
            return None

    def export_temperature_humidity_sensor_data_to_csv(self, res_data, point_name_list, point_mingcheng_data, filename):
        """
        将温湿度传感器数据导出为CSV文件
        """
        try:
            # 构建excelValuesList
            excel_values_list = []
            for name_list in point_name_list:
                for point_name in name_list:
                    node = None
                    for element in res_data:
                        tags = element.get("tags", {})
                        if (tags.get("dataCode") == point_name["dataCode"] and
                                tags.get("objectCode") == point_name["objectCode"]):
                            node = element
                            break

                    if node:
                        excel_values_list.append(node["values"])

            # 构建CSV内容
            csv_content = "时间,"

            # 表头
            daochu_flag = 0
            for i in range(len(point_name_list) - 1):
                fengjimingcheng = point_mingcheng_data[i * 2][1] if i * 2 < len(
                    point_mingcheng_data) else "" if len(point_mingcheng_data) > i * 2 else ""
                fengjimingcheng1 = point_mingcheng_data[i * 2 + 1][1] if i * 2 + 1 < len(
                    point_mingcheng_data) else "" if len(point_mingcheng_data) > i * 2 + 1 else ""

                if fengjimingcheng != "":
                    daochu_flag += 1
                    csv_content += f"{fengjimingcheng}频率,"

                if fengjimingcheng1 != "":
                    daochu_flag += 1
                    csv_content += f"{fengjimingcheng1}频率,"

                for j in range(daochu_flag, len(point_name_list[i])):
                    csv_content += f"温度传感器{point_name_list[i][j]['dataCode']},"

                daochu_flag = 0

            # 处理大系统温度传感器
            dxtwsdcgq_list = point_name_list[-1] if point_name_list else []
            for i in range(len(dxtwsdcgq_list)):
                csv_content += f"大系统温度传感器{dxtwsdcgq_list[i]['dataCode']},"

            csv_content += "\n"

            # 内容
            if excel_values_list and len(excel_values_list) > 0 and len(excel_values_list[0]) > 0:
                for i in range(len(excel_values_list[0])):
                    # 添加时间
                    time_str = excel_values_list[0][i]["time"][:16] if "time" in excel_values_list[0][i] else ""
                    csv_content += f"{time_str}\t,"

                    # 添加数值
                    for j in range(len(excel_values_list)):
                        if i < len(excel_values_list[j]):
                            value = excel_values_list[j][i].get("value", 0)
                            csv_content += f"{value:.2f}\t,"
                        else:
                            csv_content += "0.00\t,"

                    csv_content += "\n"

            # 写入文件
            with open(filename, 'w', encoding='utf-8-sig') as f:
                f.write(csv_content)

            logger.info(f"成功导出温湿度传感器数据到 {filename}")
            return True

        except Exception as e:
            logger.error(f"导出温湿度传感器数据到CSV时出错: {str(e)}")
            return False

    async def export_data_async(self, selected_line, start_time, end_time):
        """异步导出传感器数据"""
        try:
            config_map = self.line_configs.get(selected_line, {})
            if not config_map:
                logger.error(f"所选线路 {selected_line} 没有配置信息")
                return ExportResult(
                    success=False,
                    message=f"所选线路 {selected_line} 没有配置信息"
                )

            logger.info(f"开始导出 {selected_line} 的传感器数据，共 {len(config_map)} 个站点")
            logger.info(f"导出时间范围: {start_time} 至 {end_time}")
            
            # 打印所有车站信息
            logger.info("车站列表:")
            for ip, config in config_map.items():
                station_name = config.get('station', '未知站名')
                logger.info(f"  - {station_name} ({ip})")
            
            # 使用线程池执行CPU密集型任务
            loop = asyncio.get_event_loop()
            
            results = []
            success_count = 0
            fail_count = 0
            
            for ip, config in config_map.items():
                station_name = config.get('station', '未知站名')
                try:
                    logger.info(f"正在处理 {station_name} ({ip}) 的传感器数据...")
                    station_ip = config['ip']
                    api_url = f"http://{config['ip']}:9898"
                    DB_CONFIG['host'] = station_ip
                    
                    logger.info(f"{station_name} ({ip}) 正在查询数据库配置...")
                    data_cgq = execute_query(db_config.SELECT_CGQ_OBJECT_POINT_DATA)
                    data1_fanfre = execute_query(db_config.SELECT_FANFRE_OBJECT_POINT_DATA)
                    data2_fanname = execute_query(db_config.SELECT_FANNAME_OBJECT_POINT_DATA)
                    
                    point_name_list, object_codes, data_codes = self.process_temperature_humidity_sensor_data(data_cgq, data1_fanfre, data2_fanname)
                    
                    # 获取传感器数据
                    logger.info(f"{station_name} ({ip}) 正在获取传感器历史数据...")
                    sensor_data = self.fetch_sensor_data(api_url, data_codes, object_codes, start_time, end_time)
                    
                    if sensor_data:
                        filename = f"传感器历史数据_{config['station']}_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}.csv"
                        logger.info(f"{station_name} ({ip}) 正在导出文件: {filename}")
                        if self.export_temperature_humidity_sensor_data_to_csv(sensor_data, point_name_list, data2_fanname, filename):
                            success_count += 1
                            logger.info(f"✓ {station_name} ({ip}) 传感器数据导出成功 - 文件: {filename}")
                            results.append(StationExportResult(
                                station_ip=ip,
                                station_name=station_name,
                                success=True,
                                message="导出成功",
                                file_path=filename
                            ))
                        else:
                            fail_count += 1
                            error_msg = "导出文件失败"
                            logger.error(f"✗ {station_name} ({ip}) {error_msg}")
                            results.append(StationExportResult(
                                station_ip=ip,
                                station_name=station_name,
                                success=False,
                                message=error_msg,
                                file_path=None
                            ))
                    else:
                        fail_count += 1
                        error_msg = "没有传感器数据"
                        logger.error(f"✗ {station_name} ({ip}) {error_msg}")
                        results.append(StationExportResult(
                            station_ip=ip,
                            station_name=station_name,
                            success=False,
                            message=error_msg,
                            file_path=None
                        ))

                except Exception as e:
                    fail_count += 1
                    error_msg = f"处理时出错: {str(e)}"
                    logger.error(f"✗ {station_name} ({ip}) {error_msg}")
                    results.append(StationExportResult(
                        station_ip=ip,
                        station_name=station_name,
                        success=False,
                        message=error_msg,
                        file_path=None
                    ))

            # 打印最终统计结果
            logger.info(f"\n=== 传感器数据导出统计结果 ===")
            logger.info(f"总计: {len(config_map)} 个站点")
            logger.info(f"成功: {success_count} 个")
            logger.info(f"失败: {fail_count} 个")
            
            if fail_count > 0:
                logger.info(f"\n=== 失败站点详情 ===")
                for result in results:
                    if not result.success:
                        logger.info(f"✗ {result.station_name} ({result.station_ip}): {result.message}")
            
            logger.info(f"=== 传感器数据导出完成 ===")

            return ExportResult(
                success=True,
                message=f"传感器数据导出完成: 成功 {success_count} 个, 失败 {fail_count} 个",
                details={
                    "total": len(config_map),
                    "success_count": success_count,
                    "fail_count": fail_count,
                    "results": [result.dict() for result in results]
                }
            )
        except Exception as e:
            logger.error(f"异步导出传感器数据时出错: {e}")
            return ExportResult(
                success=False,
                message=f"导出失败: {str(e)}"
            )