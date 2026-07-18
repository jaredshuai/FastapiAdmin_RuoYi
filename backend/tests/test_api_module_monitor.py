"""
module_monitor 路由注册清单（系统监控）。

本文件只验证方法与路径装配，不触发缓存、调度器或文件系统操作。
认证数据测试：admin 登录后验证监控接口数据。
"""

from conftest import assert_route_registered
from fastapi.testclient import TestClient


class TestCache:
    """缓存监控接口。"""

    def test_cache_info(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/monitor/cache/info")

    def test_cache_names(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/monitor/cache/get/names")

    def test_cache_keys(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/monitor/cache/get/keys/test")

    def test_cache_value(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/monitor/cache/get/value/test/key")

    def test_cache_delete_name(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/monitor/cache/delete/name/test")

    def test_cache_delete_key(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/monitor/cache/delete/key/test")

    def test_cache_clear_all(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/monitor/cache/delete/all")


class TestServer:
    """服务器监控接口。"""

    def test_server_info(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/monitor/server/info")


class TestOnline:
    """在线用户监控接口。"""

    def test_online_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/monitor/online/list")

    def test_online_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/monitor/online/delete")

    def test_online_clear(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/monitor/online/clear")


class TestResource:
    """资源管理接口。"""

    def test_resource_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/monitor/resource/list")

    def test_resource_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/monitor/resource/delete")

    def test_resource_create_dir(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/monitor/resource/create-dir")

    def test_resource_rename(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/monitor/resource/rename")

    def test_resource_copy(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/monitor/resource/copy")

    def test_resource_move(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/monitor/resource/move")

    def test_resource_upload(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/monitor/resource/upload")

    def test_resource_export(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/monitor/resource/export")
