import pymysql
#from db_config import DB_CONFIG
#from sql_queries import SELECT_BUS_OBJECT_POINT_DATA, INSERT_HISTORY_DATA
DB_CONFIG = {
    'host': 'localhost',
    'port': 33075,
    'user': 'root',
    'password': 'Beijing0716',
    'database': 'yn_lak'
}
# 常用的 SQL 查询语句
SELECT_BUS_OBJECT_POINT_DATA1 = """
    SELECT * FROM bus_object_point_data 
    WHERE object_id = %s AND data_id = %s
"""
SELECT_BUS_OBJECT_POINT_DATA = """
    SELECT o.object_code,o.object_name,p.data_code,p.data_name,p.unit FROM bus_object_point_data p join bus_object_info o on p.object_id =o.object_id
"""
INSERT_HISTORY_DATA = """
    INSERT INTO history_data (device, alias, unit, value, timestamp) 
    VALUES (%s, %s, %s, %s, %s)
"""
SELECT_CGQ_OBJECT_POINT_DATA = """
    select data_code,default_value from bus_object_point_data where data_code like 'fSmallFan%' or data_code like 'fRoomTemp%'
"""
SELECT_FANNAME_OBJECT_POINT_DATA = """
    select data_code,default_value from bus_object_point_data where data_code like 'XiaoSongFengJiMingCheng%' or 
data_code like 'XiaoHuiFengJiMingCheng%'
"""
SELECT_FANFRE_OBJECT_POINT_DATA = """
    select data_code,default_value from bus_object_point_data where data_code like 'XiaoSongFengJiPinLvFanKui%' or 
data_code like 'XiaoHuiFengJiPinLvFanKui%'
"""

# 可以根据需要添加更多的 SQL 语句

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def execute_query(query, params=None):
    """执行查询并返回结果"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
        conn.commit()
        return result
    except Exception as e:
        print(f"执行查询时发生错误: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def insert_data(device, alias, unit, value, timestamp):
    """插入数据"""
    params = (device, alias, unit, value, timestamp)
    return execute_query(INSERT_HISTORY_DATA, params)

def select_bus_object_point_data1(object_code, data_code):
    """选择特定的数据点"""
    params = (object_code, data_code)
    return execute_query(SELECT_BUS_OBJECT_POINT_DATA, params)
def select_bus_object_point_data():
    """选择特定的数据点"""
    #params = (object_code, data_code)
    return execute_query(SELECT_BUS_OBJECT_POINT_DATA)
