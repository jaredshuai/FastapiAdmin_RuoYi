"""
module_ai 路由注册清单（AI 对话模块）。

动态路由映射：module_ai → /ai
本文件只验证方法与路径装配，不执行会话 CRUD 或模型调用。
"""

from conftest import assert_route_registered
from fastapi.testclient import TestClient


class TestAiChat:
    """AI 对话接口。"""

    def test_ai_chat_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/ai/chat/list")

    def test_ai_chat_detail(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/ai/chat/detail/test_session")

    def test_ai_chat_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/ai/chat/create")

    def test_ai_chat_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/ai/chat/update/test_session")

    def test_ai_chat_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/ai/chat/delete")

    def test_ai_chat_non_stream(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/ai/chat/ai-chat")
