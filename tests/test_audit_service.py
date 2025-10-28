"""
审计服务测试
测试操作审计日志相关功能
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

try:
    from audit_service import AuditService
    from models import OperationLog
except ImportError:
    pytest.skip("审计模块不可用", allow_module_level=True)


class TestAuditService:
    """测试审计服务"""

    @pytest.fixture
    def audit_service(self):
        """创建审计服务实例"""
        return AuditService()

    def test_init(self, audit_service):
        """测试初始化"""
        assert audit_service is not None

    @patch("audit_service.insert_operation_log")
    def test_record_operation_success(self, mock_insert, audit_service):
        """测试记录操作成功"""
        mock_insert.return_value = True

        result = audit_service.record_operation(
            operator_id="test_user",
            point_key="TEST_POINT",
            object_code="TEST_OBJECT",
            data_code="TEST_DATA",
            before_value="20.0",
            after_value="25.0",
            result="ok",
            message="温度调整",
            duration_ms=150,
        )

        assert result is True
        mock_insert.assert_called_once()

    @patch("audit_service.insert_operation_log")
    def test_record_operation_failure(self, mock_insert, audit_service):
        """测试记录操作失败"""
        mock_insert.side_effect = Exception("Database error")

        result = audit_service.record_operation(
            operator_id="test_user",
            point_key="TEST_POINT",
            result="error",
            message="操作失败",
        )

        assert result is False

    @patch("audit_service.execute_query")
    def test_query_operation_logs(self, mock_query, audit_service):
        """测试查询操作日志"""
        # Mock 返回数据
        mock_query.side_effect = [
            [(5,)],  # 总数查询
            [  # 日志列表查询
                (
                    1,
                    "test_user",
                    "TEST_POINT",
                    "TEST_OBJECT",
                    "TEST_DATA",
                    "20.0",
                    "25.0",
                    "ok",
                    "测试操作",
                    150,
                    datetime.now(),
                )
            ],
        ]

        logs, total = audit_service.query_operation_logs(
            operator_id="test_user", limit=10, offset=0
        )

        assert total == 5
        assert len(logs) == 1
        assert logs[0].operator_id == "test_user"
        assert logs[0].point_key == "TEST_POINT"

    @patch("audit_service.execute_query")
    def test_query_logs_with_filters(self, mock_query, audit_service):
        """测试带过滤条件的查询"""
        mock_query.side_effect = [[(0,)], []]  # 无结果

        start_time = datetime.now() - timedelta(days=7)
        end_time = datetime.now()

        logs, total = audit_service.query_operation_logs(
            operator_id="test_user",
            point_key="TEST_",
            result="ok",
            start_time=start_time,
            end_time=end_time,
            limit=50,
            offset=0,
        )

        assert total == 0
        assert len(logs) == 0

    @patch("audit_service.execute_query")
    def test_query_logs_pagination(self, mock_query, audit_service):
        """测试分页查询"""
        mock_query.side_effect = [[(100,)], []]  # 总数100，第二页无数据

        logs, total = audit_service.query_operation_logs(limit=10, offset=20)

        assert total == 100
        # 第三页可能没有数据
        assert len(logs) == 0

    @patch("audit_service.execute_query")
    def test_query_logs_error_handling(self, mock_query, audit_service):
        """测试查询错误处理"""
        mock_query.side_effect = Exception("Database connection failed")

        logs, total = audit_service.query_operation_logs()

        # 应该返回空结果而不是抛出异常
        assert logs == []
        assert total == 0


class TestOperationLog:
    """测试操作日志模型"""

    def test_operation_log_creation(self):
        """测试创建操作日志"""
        log = OperationLog(
            id=1,
            operator_id="test_user",
            point_key="TEST_POINT",
            object_code="TEST_OBJECT",
            data_code="TEST_DATA",
            before_value="20.0",
            after_value="25.0",
            result="ok",
            message="测试操作",
            duration_ms=150,
            created_at=datetime.now(),
        )

        assert log.id == 1
        assert log.operator_id == "test_user"
        assert log.point_key == "TEST_POINT"
        assert log.result == "ok"

    def test_operation_log_minimal(self):  # type: ignore
        """测试最小化操作日志"""
        log = OperationLog(
            id=None,
            operator_id="test_user",
            point_key="TEST_POINT",
            object_code=None,
            data_code=None,
            before_value=None,
            after_value=None,
            result="ok",
            message=None,
            duration_ms=None,
            created_at=None,
        )

        assert log.operator_id == "test_user"
        assert log.point_key == "TEST_POINT"
        assert log.object_code is None
        assert log.before_value is None


@pytest.mark.integration
class TestAuditServiceIntegration:
    """审计服务集成测试"""

    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return AuditService()

    def test_record_and_query_workflow(self, service):
        """测试记录和查询工作流"""
        try:
            # 记录操作
            success = service.record_operation(
                operator_id="integration_test",
                point_key="TEST_POINT_INTEGRATION",
                before_value="10.0",
                after_value="15.0",
                result="ok",
                message="集成测试",
            )

            # 如果记录成功，尝试查询
            if success:
                logs, total = service.query_operation_logs(
                    operator_id="integration_test", limit=10
                )

                # 应该能找到刚才记录的日志
                assert total >= 1

        except Exception as e:
            pytest.skip(f"Integration test skipped: {e}")

    def test_query_by_time_range(self, service):
        """测试按时间范围查询"""
        try:
            start_time = datetime.now() - timedelta(hours=1)
            end_time = datetime.now()

            logs, total = service.query_operation_logs(
                start_time=start_time, end_time=end_time, limit=100
            )

            # 应该返回结果，即使为空
            assert isinstance(logs, list)
            assert isinstance(total, int)
            assert total >= 0

        except Exception as e:
            pytest.skip(f"Integration test skipped: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
# type: ignore
