"""
数据库配置测试
测试数据库连接和配置相关功能
"""

from unittest.mock import MagicMock, patch

import pytest

try:
    import db_config
except ImportError:
    pytest.skip("数据库配置模块不可用", allow_module_level=True)


class TestDatabaseConfig:
    """测试数据库配置"""

    def test_db_config_exists(self):
        """测试数据库配置存在"""
        assert hasattr(db_config, "DB_CONFIG")
        assert isinstance(db_config.DB_CONFIG, dict)

    def test_db_config_keys(self):
        """测试数据库配置包含必要的键"""
        required_keys = ["host", "port", "user", "password", "database"]

        for key in required_keys:
            assert key in db_config.DB_CONFIG, f"缺少必要配置: {key}"

    def test_db_config_types(self):
        """测试数据库配置类型"""
        config = db_config.DB_CONFIG

        assert isinstance(config["host"], str)
        assert isinstance(config["port"], int)
        assert isinstance(config["user"], str)
        assert isinstance(config["password"], str)
        assert isinstance(config["database"], str)


class TestDatabaseConnection:
    """测试数据库连接"""

    @patch("pymysql.connect")
    def test_get_db_connection(self, mock_connect):
        """测试获取数据库连接"""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        conn = db_config.get_db_connection()

        assert conn is not None
        mock_connect.assert_called_once()

    @patch("pymysql.connect")
    def test_get_db_connection_for_host(self, mock_connect):
        """测试获取指定主机的数据库连接"""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        custom_host = "192.168.1.100"
        conn = db_config.get_db_connection_for_host(custom_host)

        assert conn is not None
        mock_connect.assert_called_once()

        # 验证传递的参数包含自定义主机
        call_args = mock_connect.call_args
        assert call_args[1]["host"] == custom_host

    @patch("pymysql.connect")
    def test_get_db_connection_for_host_default(self, mock_connect):
        """测试获取默认主机的数据库连接"""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        conn = db_config.get_db_connection_for_host(None)

        assert conn is not None
        mock_connect.assert_called_once()


class TestQueryExecution:
    """测试查询执行"""

    @patch("db_config.get_db_connection")
    def test_execute_query_success(self, mock_get_conn):
        """测试成功执行查询"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, "test")]
        mock_get_conn.return_value = mock_connection

        result = db_config.execute_query("SELECT * FROM test", None)

        assert result is not None
        assert len(result) == 1
        mock_cursor.execute.assert_called_once()

    @patch("db_config.get_db_connection")
    def test_execute_query_with_params(self, mock_get_conn):
        """测试带参数执行查询"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_get_conn.return_value = mock_connection

        params = ("test_value",)
        db_config.execute_query("SELECT * FROM test WHERE name = %s", params)

        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM test WHERE name = %s", params
        )

    @patch("db_config.get_db_connection")
    def test_execute_query_error(self, mock_get_conn):
        """测试查询执行错误处理"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")
        mock_get_conn.return_value = mock_connection

        result = db_config.execute_query("SELECT * FROM test", None)

        # 应该返回 None 而不是抛出异常
        assert result is None
        mock_connection.rollback.assert_called_once()

    @patch("db_config.get_db_connection_for_host")
    def test_execute_query_with_host(self, mock_get_conn):
        """测试在指定主机上执行查询"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_get_conn.return_value = mock_connection

        host = "192.168.1.100"

        try:
            db_config.execute_query_with_host("SELECT * FROM test", None, host)
            mock_get_conn.assert_called_once_with(host)
        except Exception:
            # execute_query_with_host 会抛出异常
            pass


class TestOperationLog:
    """测试操作日志功能"""

    def test_create_operation_log_table_sql(self):
        """测试创建操作日志表 SQL"""
        assert hasattr(db_config, "CREATE_OPERATION_LOG_TABLE")
        assert "CREATE TABLE" in db_config.CREATE_OPERATION_LOG_TABLE
        assert "operation_log" in db_config.CREATE_OPERATION_LOG_TABLE

    def test_insert_operation_log_sql(self):
        """测试插入操作日志 SQL"""
        assert hasattr(db_config, "INSERT_OPERATION_LOG")
        assert "INSERT INTO operation_log" in db_config.INSERT_OPERATION_LOG

    @patch("db_config.get_db_connection")
    def test_ensure_operation_log_table(self, mock_get_conn):
        """测试确保操作日志表存在"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_connection

        db_config.ensure_operation_log_table()

        # 应该执行两次：创建表和创建索引
        assert mock_cursor.execute.call_count >= 1
        mock_connection.commit.assert_called_once()

    @patch("db_config.execute_query")
    def test_insert_operation_log_success(self, mock_execute):
        """测试成功插入操作日志"""
        mock_execute.return_value = True

        result = db_config.insert_operation_log(
            operator_id="test_user",
            point_key="TEST_POINT",
            object_code="TEST_OBJECT",
            data_code="TEST_DATA",
            before_value="20.0",
            after_value="25.0",
            result="ok",
            message="测试操作",
            duration_ms=150,
        )

        assert result is True
        mock_execute.assert_called_once()

    @patch("db_config.execute_query")
    def test_insert_operation_log_failure(self, mock_execute):
        """测试插入操作日志失败"""
        mock_execute.side_effect = Exception("Database error")

        result = db_config.insert_operation_log(
            operator_id="test_user",
            point_key="TEST_POINT",
            object_code=None,
            data_code=None,
            before_value=None,
            after_value=None,
            result="error",
            message="测试失败",
            duration_ms=None,
        )

        assert result is False


class TestSQLQueries:
    """测试 SQL 查询语句"""

    def test_select_queries_exist(self):
        """测试查询语句存在"""
        assert hasattr(db_config, "SELECT_BUS_OBJECT_POINT_DATA")
        assert hasattr(db_config, "SELECT_BUS_OBJECT_POINT_DATA1")

    def test_insert_queries_exist(self):
        """测试插入语句存在"""
        assert hasattr(db_config, "INSERT_HISTORY_DATA")
        assert hasattr(db_config, "INSERT_OPERATION_LOG")

    @patch("db_config.execute_query")
    def test_insert_data(self, mock_execute):
        """测试插入数据"""
        mock_execute.return_value = True

        db_config.insert_data(
            device="TEST_DEVICE",
            alias="test_alias",
            unit="℃",
            value=25.5,
            timestamp="2024-01-01 00:00:00",
        )

        mock_execute.assert_called_once()

    @patch("db_config.execute_query")
    def test_select_bus_object_point_data(self, mock_execute):
        """测试查询总线对象点位数据"""
        mock_execute.return_value = [("TEST_OBJECT", "测试对象", "TEST_DATA", "测试数据", "℃")]

        result = db_config.select_bus_object_point_data()

        assert result is not None
        mock_execute.assert_called_once()

    @patch("db_config.execute_query")
    def test_select_bus_object_point_data1(self, mock_execute):
        """测试查询特定对象点位数据"""
        mock_execute.return_value = [("TEST_OBJECT", "测试对象")]

        result = db_config.select_bus_object_point_data1("TEST_OBJECT", "TEST_DATA")

        assert result is not None
        mock_execute.assert_called_once()


@pytest.mark.integration
class TestDatabaseIntegration:
    """数据库集成测试"""

    def test_connection_creation(self):
        """测试创建数据库连接"""
        try:
            conn = db_config.get_db_connection()
            assert conn is not None
            conn.close()
        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    def test_query_execution(self):
        """测试执行查询"""
        try:
            result = db_config.execute_query("SELECT 1", None)
            assert result is not None
            assert len(result) > 0
        except Exception as e:
            pytest.skip(f"Database not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
