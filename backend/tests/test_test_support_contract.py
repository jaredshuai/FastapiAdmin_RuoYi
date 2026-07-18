"""测试基础设施自身的可信度契约。"""

import pytest
from conftest import assert_route, assert_route_registered
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_assert_route_does_not_swallow_application_exceptions() -> None:
    """应用异常必须让路由测试失败，不能被测试助手变成假绿。"""
    app = FastAPI()

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("route exploded")

    with TestClient(app) as client:
        with pytest.raises(RuntimeError, match="route exploded"):
            assert_route(client, "GET", "/boom", expected_status=200)


def test_assert_route_rejects_incomplete_json_envelope() -> None:
    """精确状态码仍不够；JSON 响应必须满足统一业务包络。"""
    app = FastAPI()

    @app.get("/incomplete")
    def incomplete() -> dict[str, bool]:
        return {"success": True}

    with TestClient(app) as client:
        with pytest.raises(AssertionError):
            assert_route(client, "GET", "/incomplete", expected_status=200)


def test_assert_route_registered_does_not_claim_business_execution() -> None:
    """路由注册 smoke 只查装配，不能触发端点实现。"""
    app = FastAPI()

    @app.get("/registered/{item_id}")
    def registered(item_id: int) -> None:
        raise RuntimeError(f"should not execute {item_id}")

    with TestClient(app) as client:
        assert_route_registered(client, "GET", "/registered/1")


def test_assert_route_registered_rejects_request_arguments() -> None:
    """路由注册 smoke 必须拒绝会让人误以为实际发送请求的参数。"""
    app = FastAPI()

    @app.get("/registered")
    def registered() -> None:
        return None

    with TestClient(app) as client:
        with pytest.raises(TypeError, match="unexpected keyword argument 'expected_status'"):
            assert_route_registered(
                client,
                "GET",
                "/registered",
                expected_status=200,
            )
