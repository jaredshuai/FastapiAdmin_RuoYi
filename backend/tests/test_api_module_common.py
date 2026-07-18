"""
module_common 路由注册清单（公共模块）。
本文件只验证方法与路径装配，不作为健康检查或文件业务证据。
"""

from conftest import assert_route_registered
from fastapi.testclient import TestClient


class TestHealth:
    """健康检查接口。"""

    def test_health_check(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/common/health")

    def test_health_ready(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/common/health/ready")

    def test_health_live(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/common/health/live")


class TestFile:
    """文件管理接口。"""

    def test_upload_file(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/common/file/upload")

    def test_download_file(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/common/file/download")
