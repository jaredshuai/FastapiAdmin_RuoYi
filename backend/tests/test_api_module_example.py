"""
module_example 路由注册清单（示例模块）。

动态路由映射：module_example → /example
本文件只验证方法与路径装配，不执行查询、新增、修改或删除。
"""

from conftest import assert_route_registered
from fastapi.testclient import TestClient


class TestExampleDemo:
    """示例模块接口。"""

    def test_demo_detail(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/example/demo/detail/1")

    def test_demo_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/example/demo/list")

    def test_demo_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/example/demo/create")

    def test_demo_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/example/demo/update/1")

    def test_demo_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/example/demo/delete")

    def test_demo_export(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/example/demo/export")

    def test_demo_import(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/example/demo/import")

    def test_demo_download_template(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/example/demo/download/template")

    def test_demo_status_batch(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PATCH", "/example/demo/status/batch")
