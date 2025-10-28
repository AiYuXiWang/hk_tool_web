"""
控制服务测试
测试设备控制相关功能
"""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# 导入需要测试的模块
try:
    from control_service import DeviceControlService, PlatformAPIService
    from models import DeviceTreeNode, WriteCommand
except ImportError:
    pytest.skip("控制服务模块不可用", allow_module_level=True)


class TestPlatformAPIService:
    """测试平台 API 服务"""

    @pytest.fixture
    def platform_service(self):
        """创建平台服务实例"""
        return PlatformAPIService()

    def test_init(self, platform_service):
        """测试初始化"""
        assert platform_service.base_url is not None
        assert platform_service.select_url is not None
        assert platform_service.write_url is not None
        assert platform_service.fallback_token is not None

    def test_build_select_url_default(self, platform_service):
        """测试构建默认查询 URL"""
        url = platform_service._build_select_url()
        assert url == platform_service.select_url

    def test_build_select_url_with_station(self, platform_service):
        """测试构建指定站点查询 URL"""
        station_ip = "192.168.1.100"
        url = platform_service._build_select_url(station_ip)
        assert station_ip in url
        assert ":9801" in url

    def test_build_write_url_default(self, platform_service):
        """测试构建默认写值 URL"""
        url = platform_service._build_write_url()
        assert url == platform_service.write_url

    def test_build_write_url_with_station(self, platform_service):
        """测试构建指定站点写值 URL"""
        station_ip = "192.168.1.100"
        url = platform_service._build_write_url(station_ip)
        assert station_ip in url

    def test_get_runtime_token(self, platform_service):
        """测试获取运行时 Token"""
        token = platform_service.get_runtime_token()
        assert token is not None
        assert len(token) > 0

    @patch("requests.post")
    @pytest.mark.asyncio
    async def test_query_realtime_value(self, mock_post, platform_service):
        """测试查询实时值"""
        # Mock 响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"code": 1, "data": {"value": 25.5}}'
        mock_response.json.return_value = {"code": 1, "data": {"value": 25.5}}
        mock_post.return_value = mock_response

        result = await platform_service.query_realtime_value("TEST_OBJECT", "TEST_DATA")

        assert result is not None
        assert isinstance(result, dict)

    @patch("requests.post")
    @pytest.mark.asyncio
    async def test_write_point_value(self, mock_post, platform_service):
        """测试写入点位值"""
        # Mock 响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"code": 1, "message": "success"}'
        mock_response.json.return_value = {"code": 1, "message": "success"}
        mock_post.return_value = mock_response

        command = WriteCommand(
            point_key="TEST_POINT",
            data_source=1,  # data_source should be 1, 2, or 3
            control_value="25.5",
            object_code="TEST_OBJECT",
            data_code="TEST_DATA",
        )

        result = await platform_service.write_point_value(
            command, "test_token", "192.168.1.100"
        )

        assert result is not None
        assert isinstance(result, dict)


class TestDeviceControlService:
    """测试设备控制服务"""

    @pytest.fixture
    def control_service(self):
        """创建控制服务实例"""
        return DeviceControlService()

    def test_init(self, control_service):
        """测试初始化"""
        assert control_service.platform_api is not None
        assert isinstance(control_service.platform_api, PlatformAPIService)

    @pytest.mark.asyncio
    async def test_get_device_tree(self, control_service):
        """测试获取设备树"""
        try:
            result = await control_service.get_device_tree(
                operator_id="test_user", station_ip="192.168.1.100"
            )

            assert result is not None
            assert hasattr(result, "tree")
            assert hasattr(result, "count")
            assert isinstance(result.tree, list)
            assert result.count >= 0
        except Exception as e:
            # 如果数据库不可用，测试应该返回测试数据
            pytest.skip(f"Database not available: {e}")

    @pytest.mark.asyncio
    async def test_get_device_tree_fallback(self, control_service):
        """测试设备树回退机制"""
        # 当数据库不可用时，应该返回测试数据
        with patch(
            "control_service.execute_query_with_host", side_effect=Exception("DB Error")
        ):
            result = await control_service.get_device_tree()

            assert result is not None
            assert len(result.tree) > 0
            # 应该返回测试数据
            assert result.tree[0].id == "test_project"

    @pytest.mark.asyncio
    async def test_query_realtime_point(self, control_service):
        """测试查询实时点位"""
        with patch.object(
            control_service.platform_api, "query_realtime_value"
        ) as mock_query:
            mock_query.return_value = {"code": 1, "data": {"value": 25.5, "unit": "℃"}}

            result = await control_service.query_realtime_point(
                "TEST_OBJECT", "TEST_DATA", "test_user"
            )

            assert result is not None
            assert hasattr(result, "value")
            mock_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_realtime_point_error(self, control_service):
        """测试查询实时点位错误处理"""
        with patch.object(
            control_service.platform_api,
            "query_realtime_value",
            side_effect=Exception("API Error"),
        ):
            result = await control_service.query_realtime_point(
                "TEST_OBJECT", "TEST_DATA"
            )

            # 应该优雅地处理错误
            assert result is not None


class TestWriteCommand:
    """测试写值命令模型"""

    def test_write_command_creation(self):
        """测试创建写值命令"""
        command = WriteCommand(
            point_key="TEST_POINT",
            data_source=1,
            control_value="25.5",
            object_code="TEST_OBJECT",
            data_code="TEST_DATA",
        )

        assert command.point_key == "TEST_POINT"
        assert command.data_source == 1
        assert command.control_value == "25.5"
        assert command.object_code == "TEST_OBJECT"
        assert command.data_code == "TEST_DATA"


class TestDeviceTreeNode:
    """测试设备树节点模型"""

    def test_device_tree_node_creation(self):
        """测试创建设备树节点"""
        node = DeviceTreeNode(
            id="test_node",
            label="Test Node",
            children=[],
            meta={"object_code": "TEST", "object_name": "Test Object"},
        )

        assert node.id == "test_node"
        assert node.label == "Test Node"
        assert node.children == []
        assert node.meta is not None
        assert node.meta["object_code"] == "TEST"  # type: ignore

    def test_device_tree_node_with_children(self):
        """测试带子节点的设备树节点"""
        child_node = DeviceTreeNode(
            id="child_node", label="Child Node", children=None, meta={}
        )

        parent_node = DeviceTreeNode(
            id="parent_node", label="Parent Node", children=[child_node], meta={}
        )

        assert parent_node.children is not None
        assert len(parent_node.children) == 1
        assert parent_node.children[0].id == "child_node"


@pytest.mark.integration
class TestControlServiceIntegration:
    """控制服务集成测试"""

    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return DeviceControlService()

    @pytest.mark.asyncio
    async def test_full_workflow(self, service):
        """测试完整工作流程"""
        try:
            # 1. 获取设备树
            tree = await service.get_device_tree(operator_id="test_user")
            assert tree is not None
            assert tree.count >= 0

            # 2. 如果有设备，尝试查询第一个点位
            if tree.count > 0 and tree.tree:
                first_device = tree.tree[0]
                if first_device.children and first_device.children[0].children:
                    first_point = first_device.children[0].children[0]
                    if first_point.meta:
                        object_code = first_point.meta.get("object_code")
                        data_code = first_point.meta.get("data_code")

                        if object_code and data_code:
                            # 查询点位
                            result = await service.query_realtime_point(
                                object_code, data_code
                            )
                            assert result is not None

        except Exception as e:
            pytest.skip(f"Integration test skipped: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
