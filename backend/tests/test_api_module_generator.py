"""
module_generator 路由注册清单（代码生成模块）。

动态路由映射：module_generator → /generator
本文件只验证方法与路径装配，不执行导入、同步或代码生成。
"""

from conftest import assert_route_registered
from fastapi.testclient import TestClient


class TestGenerator:
    """代码生成模块接口。"""

    def test_gencode_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/generator/gencode/list")

    def test_gencode_db_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/generator/gencode/db/list")

    def test_gencode_import(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/generator/gencode/import")

    def test_gencode_detail(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/generator/gencode/detail/1")

    def test_gencode_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/generator/gencode/create")

    def test_gencode_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/generator/gencode/update/1")

    def test_gencode_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/generator/gencode/delete")

    def test_gencode_preview(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/generator/gencode/preview/1")

    def test_gencode_output(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/generator/gencode/output/test_table")

    def test_gencode_sync_db(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/generator/gencode/sync_db/test_table")

    def test_gencode_sync_db_preview(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/generator/gencode/sync_db/preview/test_table")

    def test_gencode_batch_output(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PATCH", "/generator/gencode/batch/output")
