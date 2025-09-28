import requests
import pandas as pd
from datetime import datetime
import concurrent.futures
from functools import partial
import os
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
    response = requests.post(f"{api_url}/data/selectHisData", json=obj)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Failed to fetch data from {api_url}")
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
    response = requests.post(f"{api_url}/data/selectHisData", json=obj)
    if response.status_code == 200:
        data = response.json().get("data", [])
        print("节能状态数据数量:", len(data))
        if  len(data)==1:
            values = data[0].get("values", [])
            status_list = []
            if values:
                flag = values[0]["value"]
                print("开始时间:", values[0]["time"])
                status_list.append({
                    "开始时间": datetime.strptime(values[0]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S"),
                    "结束时间": "",
                    "节能状态": "节能" if flag == 1 else "非节能",
                    "系统": ""
                })
                for i in range(1, len(values)):
                    if values[i]["value"] != flag and values[i]["value"] != ''and values[i]["value"] is not None:
                        print("结束时间时间:", values[i]["time"])
                        status_list[-1]["结束时间"] = datetime.strptime(values[i]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
                        flag = values[i]["value"]
                        status_list.append({
                            "开始时间": datetime.strptime(values[i]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S"),
                            "结束时间": "",
                            "节能状态": "节能" if flag == 1 else "非节能",
                            "系统": ""
                        })
                if status_list:
                    print("最后时间:", values[-1]["time"])
                    status_list[-1]["结束时间"] = datetime.strptime(values[-1]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
            return status_list
        if len(data)==4:#针对8号线风水分开的特殊处理
            #水系统
            values = data[0].get("values", [])
            status_list = []
            if values:
                flag = values[0]["value"]
                status_list.append({
                    "开始时间": datetime.strptime(values[0]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S"),
                    "结束时间": "",
                    "节能状态": "节能" if flag == 1 else "非节能",
                    "系统":"水系统"
                })
                for i in range(1, len(values)):
                    if values[i]["value"] != flag and values[i]["value"] != ''and values[i]["value"] is not None:
                        status_list[-1]["结束时间"] = datetime.strptime(values[i]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
                        flag = values[i]["value"]
                        status_list.append({
                            "开始时间": datetime.strptime(values[i]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S"),
                            "结束时间": "",
                            "节能状态": "节能" if flag == 1 else "非节能",
                            "系统":"水系统"
                        })
                if status_list:
                   status_list[-1]["结束时间"] = datetime.strptime(values[-1]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
            #风系统
            values = data[3].get("values", [])
            #status_list = []
            if values:
                flag = values[0]["value"]
                status_list.append({
                    "开始时间": datetime.strptime(values[0]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S"),
                    "结束时间": "",
                    "节能状态": "节能" if flag == 1 else "非节能",
                    "系统":"风系统"
                })
                for i in range(1, len(values)):
                    if values[i]["value"] != flag and values[i]["value"] != ''and values[i]["value"] is not None:
                        status_list[-1]["结束时间"] = datetime.strptime(values[i]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
                        flag = values[i]["value"]
                        status_list.append({
                            "开始时间": datetime.strptime(values[i]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S"),
                            "结束时间": "",
                            "节能状态": "节能" if flag == 1 else "非节能",
                            "系统":"风系统"
                        })
                if status_list:
                    status_list[-1]["结束时间"] = datetime.strptime(values[-1]["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")

            return status_list
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
    #print("end_data:", end_data)
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
    #print("start_data:", start_data)
    # 计算耗电量
    index = 0
    for i in range(len(data_codes)):
        for j in range(len(object_codes)):
            #print(f"i:{i}, j:{j}")
            #print(f"object_codes:{object_codes}")
            if j == len(object_codes):# - 1:
                data_list[index]["p8"] = "0.00"
                index += 1
                break
            else:
                start_entry = next((item for item in start_data if item["tags"]["dataCode"] == data_codes[i] and item["tags"]["objectCode"] == object_codes[j]), None)
                end_entry = next((item for item in end_data if item["tags"]["dataCode"] == data_codes[i] and item["tags"]["objectCode"] == object_codes[j]), None)

                if start_entry and end_entry and start_entry["values"] and end_entry["values"]:
                    data_list[index]["p9"]  = round(start_entry["values"][0]["value"], 2)
                    data_list[index]["p10"] = round(end_entry["values"][0]["value"], 2)
                    if end_entry["values"][0]["value"] - start_entry["values"][0]["value"] >= -1:
                        data_list[index]["p8"] = round(end_entry["values"][0]["value"] - start_entry["values"][0]["value"], 2)
                    else:
                        data_list[index]["p8"] = "电表异常"
                    index += 1
                    break
    return data_list
#数据导出
def export_data(data_list, energy_status, start_time, end_time, filename="电耗统计.xls"):
    #准备查询起止时间
    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
    data_time=pd.DataFrame([{"开始时间": start_time}, {"结束时间": end_time}], columns=["开始时间", "结束时间"])

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
        data_time.to_excel(writer, sheet_name='Sheet1', startrow=0, index=False)
        # 导出节能状态
        energy_status_df.to_excel(writer, sheet_name='Sheet1', startrow=2, index=False)

        # 导出电表数据
        data_df.to_excel(writer, sheet_name='Sheet1', startrow=len(energy_status_df) + 4, index=False)

    print(f"数据已导出到 {filename}")


#def batch_export_data(ip_config_map, start_time, end_time):
    # # 定义一个内部函数来处理单个IP的数据导出
    # def export_single_ip(ip, config, start_time, end_time):
    #     try:
    #         api_url = f"http://{ip}:9898"
    #         data_list = config["data_list"]
    #         data_codes = config["data_codes"]
    #         object_codes = config["object_codes"]
    #
    #         # 获取数据
    #         energy_status = get_energy_status(api_url, "539", "PT_SDZ", start_time, end_time)
    #         processed_data = process_data(api_url, data_list, data_codes, object_codes, start_time, end_time)
    #
    #         # 生成文件名并导出
    #         filename = f"电耗统计_{config['station']}{ip.replace(':', '_')}{'_'}{str(start_time).split('-')[0:2]}.xls"
    #         export_data(processed_data, energy_status, start_time, end_time, filename)
    #
    #         return (ip, True, None)  # (IP地址, 是否成功, 错误信息)
    #     except Exception as e:
    #         return (ip, False, str(e))
    #
    # # 使用线程池并行处理
    # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    #     # 创建部分函数，固定start_time和end_time参数
    #     export_func = partial(export_single_ip, start_time=start_time, end_time=end_time)
    #
    #     # 提交所有任务到线程池
    #     futures = {executor.submit(export_func, ip, config): ip for ip, config in ip_config_map.items()}
    #
    #     # 处理结果
    #     success_count = 0
    #     fail_count = 0
    #
    #     for future in concurrent.futures.as_completed(futures):
    #         ip = futures[future]
    #         try:
    #             ip, success, error = future.result()
    #             if success:
    #                 print(f"成功导出 {ip} 的数据")
    #                 success_count += 1
    #             else:
    #                 print(f"导出 {ip} 数据失败: {error}")
    #                 fail_count += 1
    #         except Exception as e:
    #             print(f"处理 {ip} 时发生意外错误: {str(e)}")
    #             fail_count += 1
    #
    #     print(f"导出完成: 成功 {success_count} 个, 失败 {fail_count} 个")
def batch_export_data(ip_config_map, start_time, end_time):
    for ip, config in ip_config_map.items():
        api_url = f'http://{config["ip"]}:9898'
        data_list = config["data_list"]
        data_codes = config["data_codes"]
        object_codes = config["object_codes"]
        energy_status = get_energy_status(api_url, config["jienengfeijieneng"]["data_codes"], config["jienengfeijieneng"]["object_codes"], start_time, end_time)
        processed_data = process_data(api_url, data_list, data_codes, object_codes, start_time, end_time)

        #filename_startime = start_time.strftime("%Y-%m-%d-%H:%M")
        #filename_endime = end_time.strftime("%Y-%m-%d-%H:%M")
        filename = f"电耗统计_{config['ip']}_{ip}.xlsx"
        export_data(processed_data, energy_status, start_time, end_time, filename)
