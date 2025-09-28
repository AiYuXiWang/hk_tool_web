import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, time
import config_electricity
#from export_data import batch_export_data  # 假设batch_export_data在另一个模块中
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
#import export_data
import requests
import pandas as pd
#import concurrent.futures
#from functools import partial
#import os
import threading
import db_config
from db_config import select_bus_object_point_data, execute_query,DB_CONFIG
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#定义数据模型
class ElectricityMeter:
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

#数据获取
def get_historical_data(api_url, obj):
    try:
        response = requests.post(f"{api_url}/data/selectHisData", json=obj, timeout=30)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            logger.error(f"Failed to fetch data from {api_url}, status code: {response.status_code}")
            return []
    except requests.RequestException as e:
        logger.error(f"Request error when fetching data from {api_url}: {e}")
        return []

#节能状态检测
def get_energy_status(api_url, data_code, object_code, start_time, end_time):
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
        response = requests.post(f"{api_url}/data/selectHisData", json=obj, timeout=30)
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
            logger.error(f"Failed to fetch energy status data, status code: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Request error when fetching energy status data: {e}")
    except Exception as e:
        logger.error(f"Error processing energy status data: {e}")
        
    return []

#数据处理
def process_data(api_url, data_list, data_codes, object_codes, start_time, end_time):
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
    end_data = get_historical_data(api_url, end_obj)
    
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
    start_data = get_historical_data(api_url, start_obj)
    
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

#数据导出
def export_data(data_list, energy_status, start_time, end_time, filename="电耗统计.xls"):
    try:
        #准备查询起止时间
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
        date_time = pd.DataFrame([{"开始时间": start_time_str, "结束时间": end_time_str}], columns=["开始时间", "结束时间"])

        # 准备节能状态数据
        energy_status_df = pd.DataFrame(energy_status, columns=["开始时间", "结束时间", "节能状态", "系统"])

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

# def batch_export_data(ip_config_map, start_time, end_time):
#     success_count = 0
#     fail_count = 0
#
#     for ip, config in ip_config_map.items():
#         try:
#             api_url = f'http://{config["ip"]}:9898'
#             data_list = config["data_list"]
#             data_codes = config["data_codes"]
#             object_codes = config["object_codes"]
#             energy_status = get_energy_status(api_url, config["jienengfeijieneng"]["data_codes"], config["jienengfeijieneng"]["object_codes"], start_time, end_time)
#             processed_data = process_data(api_url, data_list, data_codes, object_codes, start_time, end_time)
#
#             filename = f"电耗统计_{config['ip']}_{ip}_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}.xlsx"
#             if export_data(processed_data, energy_status, start_time, end_time, filename):
#                 success_count += 1
#             else:
#                 fail_count += 1
#         except Exception as e:
#             logger.error(f"处理 {ip} 时发生错误: {e}")
#             fail_count += 1
#
#     return success_count, fail_count

class ElectricityExportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("车站电耗数据导出系统")

        # 线路配置映射
        self.line_configs = config_electricity.line_configs
        self.setup_ui()
        # 添加消息队列用于线程间通信
        self.message_queue = queue.Queue()
        self._cancel_export = False
        self.after_id = None  # 用于定时检查消息队列

    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 线路选择
        ttk.Label(main_frame, text="选择线路:").grid(row=0, column=0, sticky=tk.W)
        self.line_var = tk.StringVar()
        self.line_combobox = ttk.Combobox(main_frame, textvariable=self.line_var,
                                          values=list(self.line_configs.keys()))
        self.line_combobox.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.line_combobox.current(0)

        # 时间范围选择
        ttk.Label(main_frame, text="开始时间:").grid(row=1, column=0, sticky=tk.W)
        self.start_time_entry = ttk.Entry(main_frame)
        self.start_time_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        # 获取当前日期并设置时间为00:00:00
        today_midnight = datetime.combine(datetime.today(), time.min).strftime("%Y-%m-%d %H:%M:%S")
        self.start_time_entry.insert(0, today_midnight)

        ttk.Label(main_frame, text="结束时间:").grid(row=2, column=0, sticky=tk.W)
        self.end_time_entry = ttk.Entry(main_frame)
        self.end_time_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        # 设置结束时间为当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.end_time_entry.insert(0, current_time)

        # 导出按钮
        self.export_btn = ttk.Button(main_frame, text="导出电耗数据", command=self.handle_export_data)
        self.export_btn.grid(row=3, column=0, columnspan=1, pady=1)
        # 导出传感器历史数据按钮
        self.export_sensor_btn = ttk.Button(main_frame, text="导出传感器数据", command=self.handle_export_sensor_data)
        self.export_sensor_btn.grid(row=3, column=1, columnspan=1, pady=1)
        # 取消按钮
        self.cancel_btn = ttk.Button(main_frame, text="取消导出", command=self.cancel_export, state=tk.DISABLED)
        self.cancel_btn.grid(row=4, column=1, columnspan=1, pady=1)

        # 日志输出
        ttk.Label(main_frame, text="操作日志:").grid(row=4, column=0, sticky=tk.W)
        self.log_text = tk.Text(main_frame, height=10, state=tk.DISABLED)
        self.log_text.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW)

        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
    def _start_message_pump(self):
        """启动消息处理循环"""
        if not self.message_queue.empty():
            message = self.message_queue.get_nowait()
            self._update_log_ui(message)
        self.after_id = self.root.after(100, self._start_message_pump)

    def log_message(self, message):
        """线程安全的日志记录方法"""
        self.message_queue.put(message)
        if self.after_id is None:
            self._start_message_pump()
            
    def _update_log_ui(self, message):
        """实际更新UI的日志显示"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def handle_export_data(self):
        """处理导出数据的完整方法（带日期验证）"""
        try:
            # 从UI控件获取时间参数（替换硬编码日期）
            start_time_str = self.start_time_entry.get()
            end_time_str = self.end_time_entry.get()

            # 验证日期格式
            try:
                start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror("错误", "时间格式不正确，请使用YYYY-MM-DD HH:MM:SS格式")
                return

            # 验证日期范围合理性
            if start_time > end_time:
                messagebox.showerror("错误", "开始时间不能晚于结束时间")
                return
                
            selected_line = self.line_var.get()
            if not selected_line:
                messagebox.showerror("错误", "请选择一条线路")
                return
                
            # 启用取消按钮并禁用导出按钮
            self.root.after(0, lambda: [
                self.cancel_btn.config(state=tk.NORMAL),
                self.export_btn.config(state=tk.DISABLED)
            ])

            # 在线程中执行导出操作
            threading.Thread(target=self.parallel_export_data,
                             args=(selected_line, start_time, end_time),
                             daemon=True).start()
            #self.parallel_export_data(selected_line, start_time, end_time)
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")

    def export_single_ip(self, ip, config, start_time, end_time):
        """线程安全的单个IP导出操作"""
        try:
            if self._cancel_export:
                return False, "操作已取消"

            api_url = f'http://{config["ip"]}:9898'
            data_list = config["data_list"]
            data_codes = config.get("data_codes", [])
            object_codes = config.get("object_codes", [])
            
            if not data_codes or not object_codes:
                return False, "缺少数据点配置"
                
            energy_status = get_energy_status(
                api_url, 
                config["jienengfeijieneng"]["data_codes"], 
                config["jienengfeijieneng"]["object_codes"], 
                start_time, 
                end_time
            )
            
            processed_data = process_data(api_url, data_list, data_codes, object_codes, start_time, end_time)
            filename = f"电耗统计_{config['ip']}_{ip}_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}.xlsx"
            
            if export_data(processed_data, energy_status, start_time, end_time, filename):
                return True, None
            else:
                return False, "导出文件失败"
        except Exception as e:
            logger.error(f"导出 {ip} 数据时出错: {e}")
            return False, str(e)

    def parallel_export_data(self, selected_line, start_time, end_time):
        """带资源管理的并行导出方法"""
        config_map = self.line_configs.get(selected_line, {})
        if not config_map:
            messagebox.showerror("错误", "所选线路没有配置信息")
            return

        # 初始化状态
        self._cancel_export = False
        total = len(config_map)
        success_count = 0
        fail_count = 0
        fail_details = []

        try:
            self.log_message(f"开始导出 {selected_line} 的数据（共 {total} 个站点）...")

            with ThreadPoolExecutor(max_workers=3) as executor:  # 减少线程数以避免网络拥塞
                futures = {
                    executor.submit(
                        self.export_single_ip,
                        ip, config, start_time, end_time
                    ): ip for ip, config in config_map.items()
                }

                processed = 0
                for future in as_completed(futures):
                    if self._cancel_export:
                        # 取消未完成的任务
                        for f in futures:
                            if not f.done():
                                f.cancel()
                        self.log_message("导出已被用户取消")
                        break

                    ip = futures[future]
                    processed += 1

                    try:
                        success, error = future.result(timeout=10)  # 10秒超时
                        if success:
                            success_count += 1
                            self.log_message(f"成功导出 {ip} 的数据")
                        else:
                            fail_count += 1
                            fail_details.append(f"{ip}: {error}")
                            self.log_message(f"导出 {ip} 数据失败: {error}")
                    except Exception as e:
                        fail_count += 1
                        error = f"未知错误: {str(e)}"
                        fail_details.append(f"{ip}: {error}")
                        self.log_message(f"{ip} 发生错误: {error}")

                    # 更新进度
                    self.log_message(f"进度: {processed}/{total}")

            # 导出完成处理
            result_msg = f"导出完成: 成功 {success_count}/{total}, 失败 {fail_count}"
            if fail_details:
                result_msg += "\n失败详情:\n" + "\n".join(fail_details[:5])  # 只显示前5个错误

            self.log_message(result_msg)
            messagebox.showinfo("完成", result_msg)

        except Exception as e:
            self.log_message(f"导出过程中发生严重错误: {str(e)}")
            messagebox.showerror("错误", f"导出失败: {str(e)}")
        finally:
            # 清理资源
            self._cancel_export = False
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
            # 恢复按钮状态
            self.root.after(0, lambda: [
                self.cancel_btn.config(state=tk.DISABLED),
                self.export_btn.config(state=tk.NORMAL)
            ])

    def cancel_export(self):
        """取消导出操作"""
        self._cancel_export = True
        self.log_message("正在取消导出操作...")
        
    def handle_export_sensor_data(self):
        """处理导出传感器历史数据"""
        try:
            # 从UI控件获取时间参数
            start_time_str = self.start_time_entry.get()
            end_time_str = self.end_time_entry.get()

            # 验证日期格式
            try:
                start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror("错误", "时间格式不正确，请使用YYYY-MM-DD HH:MM:SS格式")
                return

            # 验证日期范围合理性
            if start_time > end_time:
                messagebox.showerror("错误", "开始时间不能晚于结束时间")
                return

            selected_line = self.line_var.get()
            if not selected_line:
                messagebox.showerror("错误", "请选择一条线路")
                return

            # 启用取消按钮并禁用导出按钮
            self.root.after(0, lambda: [
                self.cancel_btn.config(state=tk.NORMAL),
                self.export_btn.config(state=tk.DISABLED),
                self.export_sensor_btn.config(state=tk.DISABLED)
            ])

            # 在线程中执行导出操作
            threading.Thread(target=self.export_sensor_data_thread,
                             args=(selected_line, start_time, end_time),
                             daemon=True).start()

        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")

    def export_sensor_data_thread(self, selected_line, start_time, end_time):
        """在独立线程中执行传感器数据导出"""
        try:
            self.log_message(f"开始导出 {selected_line} 的传感器历史数据...")

            # 获取所选线路的配置
            config_map = self.line_configs.get(selected_line, {})
            if not config_map:
                self.log_message(f"错误: 所选线路 {selected_line} 没有配置信息")
                return

            # 遍历所有车站配置
            for ip, config in config_map.items():
                if self._cancel_export:
                    self.log_message("导出已被用户取消")
                    return

                try:
                    self.log_message(f"正在处理 {ip} 的传感器数据...")
                    station_ip = config['ip']
                    api_url = f"http://{config['ip']}:9898"
                    DB_CONFIG['host'] = station_ip
                    
                    data_cgq = execute_query(db_config.SELECT_CGQ_OBJECT_POINT_DATA)
                    data1_fanfre = execute_query(db_config.SELECT_FANFRE_OBJECT_POINT_DATA)
                    data2_fanname = execute_query(db_config.SELECT_FANNAME_OBJECT_POINT_DATA)
                    
                    point_name_list, object_codes, data_codes = self.process_temperature_humidity_sensor_data(data_cgq, data1_fanfre, data2_fanname)
                    
                    # 获取传感器数据
                    sensor_data = self.fetch_sensor_data(api_url, data_codes, object_codes, start_time, end_time)
                    
                    if sensor_data:
                        filename = f"传感器历史数据_{config['station']}_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}.csv"
                        if self.export_temperature_humidity_sensor_data_to_csv(sensor_data, point_name_list, data2_fanname, filename):
                            self.log_message(f"成功导出 {ip} 的传感器数据到 {filename}")
                        else:
                            self.log_message(f"导出 {ip} 的传感器数据失败")
                    else:
                        self.log_message(f"警告: {ip} 没有传感器数据")

                except Exception as e:
                    self.log_message(f"处理 {ip} 时出错: {str(e)}")

            self.log_message("传感器数据导出完成")
            messagebox.showinfo("完成", "传感器历史数据导出完成")

        except Exception as e:
            self.log_message(f"导出过程中发生严重错误: {str(e)}")
            messagebox.showerror("错误", f"导出失败: {str(e)}")
        finally:
            # 恢复按钮状态
            self._cancel_export = False
            self.root.after(0, lambda: [
                self.cancel_btn.config(state=tk.DISABLED),
                self.export_btn.config(state=tk.NORMAL),
                self.export_sensor_btn.config(state=tk.NORMAL)
            ])

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
        注意：这是一个示例实现，需要根据实际的API和数据结构进行调整
        """
        try:
            # 构造查询对象 - 这里需要根据实际的传感器点位配置来构造
            obj = {
                "dataCodes": dataCodes,  # 需要根据实际传感器点位填写
                "endTime": int(end_time.timestamp() * 1000),
                "fill": "0",
                "funcName": "MEAN",
                "funcTime": "1h",
                "measurement": "realData",
                "objectCodes": objectCodes,  # 需要根据实际传感器点位填写
                "startTime": int(start_time.timestamp() * 1000)
            }

            # 发送请求获取历史数据
            response = requests.post(f"{api_url}/data/selectHisData", json=obj, timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", [])
                return data
            else:
                self.log_message(f"获取传感器数据失败，状态码: {response.status_code}")
                return None
        except requests.RequestException as e:
            self.log_message(f"获取传感器数据时网络错误: {str(e)}")
            return None
        except Exception as e:
            self.log_message(f"获取传感器数据时出错: {str(e)}")
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

            self.log_message(f"成功导出温湿度传感器数据到 {filename}")
            return True

        except Exception as e:
            self.log_message(f"导出温湿度传感器数据到CSV时出错: {str(e)}")
            return False

def main():
    root = tk.Tk()
    app = ElectricityExportApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
