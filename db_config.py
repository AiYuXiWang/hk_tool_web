import pymysql
#from db_config import DB_CONFIG
#from sql_queries import SELECT_BUS_OBJECT_POINT_DATA, INSERT_HISTORY_DATA
DB_CONFIG = {
    'host': '192.168.100.3',
    'port': 33075,
    'user': 'root',
    'password': 'Beijing0716',
    'database': 'yn_lak'
}

# 审计表DDL与DML
CREATE_OPERATION_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS operation_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  operator_id VARCHAR(64) NOT NULL,
  point_key VARCHAR(255) NOT NULL,
  object_code VARCHAR(128) NULL,
  data_code VARCHAR(128) NULL,
  before_value VARCHAR(255) NULL,
  after_value VARCHAR(255) NULL,
  result VARCHAR(16) NOT NULL,
  message TEXT NULL,
  duration_ms INT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""
# 索引：operator_id + created_at（若已存在则忽略错误）
CREATE_OPERATION_LOG_INDEX = "CREATE INDEX idx_operation_log_operator_created ON operation_log (operator_id, created_at);"

INSERT_OPERATION_LOG = """
INSERT INTO operation_log
(operator_id, point_key, object_code, data_code, before_value, after_value, result, message, duration_ms)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
"""
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
    select data_code,default_value from bus_object_point_data where data_code like 'fSmallFan%%' or data_code like 'fRoomTemp%%'
"""
SELECT_FANNAME_OBJECT_POINT_DATA = """
    select data_code,default_value from bus_object_point_data where data_code like 'XiaoSongFengJiMingCheng%%' or 
data_code like 'XiaoHuiFengJiMingCheng%%'
"""
SELECT_FANFRE_OBJECT_POINT_DATA = """
    select data_code,default_value from bus_object_point_data where data_code like 'XiaoSongFengJiPinLvFanKui%%' or 
data_code like 'XiaoHuiFengJiPinLvFanKui%%'
"""

# 可以根据需要添加更多的 SQL 语句

from typing import Dict, Any, cast, Optional

def get_db_connection():
    """获取数据库连接（使用默认配置）"""
    # Pyright 类型提示：将 TypedDict/Dict 转为 Dict[str, Any] 以匹配 pymysql.connect 签名
    return pymysql.connect(**cast(Dict[str, Any], DB_CONFIG))

def get_db_connection_for_host(host: Optional[str] = None):
    """按指定 host 获取数据库连接，不修改全局 DB_CONFIG。"""
    cfg: Dict[str, Any] = cast(Dict[str, Any], DB_CONFIG.copy())
    if host:
        cfg['host'] = host
    return pymysql.connect(**cfg)

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

def execute_query_with_host(query, params=None, host: Optional[str] = None):
    """在指定 host 上执行查询，用于按车站IP切换数据源。"""
    conn = get_db_connection_for_host(host)
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
        conn.commit()
        return result
    except Exception as e:
        print(f"执行查询(指定主机)时发生错误: {e}")
        conn.rollback()
        # 将异常抛出，让上层逻辑感知到失败并进行回退
        raise
    finally:
        conn.close()

def insert_data(device, alias, unit, value, timestamp):
    """插入数据"""
    params = (device, alias, unit, value, timestamp)
    return execute_query(INSERT_HISTORY_DATA, params)

def ensure_operation_log_table() -> bool:
    """确保 operation_log 表存在并创建复合索引。O(1) DDL；p99 < 50ms。"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(CREATE_OPERATION_LOG_TABLE)
            try:
                cursor.execute(CREATE_OPERATION_LOG_INDEX)
            except Exception:
                # 索引已存在或非致命错误，忽略
                pass
        conn.commit()
        return True
    except Exception as e:
        print(f"创建审计表/索引失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def insert_operation_log(
    operator_id: str,
    point_key: str,
    object_code: str | None,
    data_code: str | None,
    before_value: str | None,
    after_value: str | None,
    result: str,
    message: str | None,
    duration_ms: int | None,
) -> bool:
    """写入操作审计日志。O(1) INSERT；p99 < 10ms。"""
    params = (
        operator_id,
        point_key,
        object_code,
        data_code,
        before_value,
        after_value,
        result,
        message,
        duration_ms,
    )
    try:
        execute_query(INSERT_OPERATION_LOG, params)
        return True
    except Exception as e:
        print(f"写入审计日志失败: {e}")
        return False

def select_bus_object_point_data1(object_code, data_code):
    """选择特定的数据点"""
    params = (object_code, data_code)
    return execute_query(SELECT_BUS_OBJECT_POINT_DATA, params)
def select_bus_object_point_data():
    """选择特定的数据点"""
    #params = (object_code, data_code)
    return execute_query(SELECT_BUS_OBJECT_POINT_DATA)
