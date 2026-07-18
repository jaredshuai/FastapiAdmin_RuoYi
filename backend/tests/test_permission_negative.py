"""G2 权限负向测试矩阵。

覆盖 G2 权限矩阵，并用阳性对照证明请求真实走过角色、菜单和套餐过滤：
- 未登录 → 401
- 登录无权限 → 403
- 停用角色 → 403
- 停用菜单 → 403
- 套餐移除菜单 → 403
- 非超管调用平台管理服务 → 403
- 租户 A 读租户 B → 200 且结果不可见
- 租户 A 改租户 B → 404，不泄露存在性
- 超管跨租户行为 → 按明确规则断言

测试数据通过 permission_test_factory.seed_permission_test_data 建立，
每个测试函数独立提交测试数据供 HTTP 请求读取，结束后精确删除这些数据。

阳性对照是矩阵的必要组成：如果启用角色用户无法成功访问，任何 403 都不能
证明具体的角色、菜单、套餐或租户边界被真正执行。
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.database import async_db_session
from tests.permission_test_factory import (
    USER_TENANT_B_ID,
    clear_permission_test_data,
    login_user,
    seed_permission_test_data,
)

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
async def permission_data():
    """建立可被 HTTP 请求连接看到的 G2 测试数据，并在结束后清理。

    返回:
        dict: seed_permission_test_data 返回的 ID 映射。
    """
    async with async_db_session() as db:
        await clear_permission_test_data(db)
        created = await seed_permission_test_data(db)
        await db.commit()

    try:
        yield created
    finally:
        async with async_db_session() as db:
            await clear_permission_test_data(db)
            await db.commit()


@pytest.fixture
def no_auth_client(test_client: TestClient) -> TestClient:
    """无认证 TestClient。"""
    return test_client


# ============================================================
# G2-01: 未登录 → 401
# ============================================================


class TestUnauthenticated:
    """未登录访问受保护端点必须返回 401。"""

    def test_unauthenticated_list_users(self, no_auth_client: TestClient) -> None:
        resp = no_auth_client.get("/api/v1/system/user/list")
        assert resp.status_code == 401, (
            f"未登录应返回 401，实际 {resp.status_code}: {resp.text}"
        )

    def test_unauthenticated_create_role(self, no_auth_client: TestClient) -> None:
        resp = no_auth_client.post(
            "/api/v1/system/role/create",
            json={"name": "test", "code": "test_role"},
        )
        assert resp.status_code == 401


# ============================================================
# G2-02: 登录无权限 → 403
# ============================================================


class TestNoPermission:
    """已登录但无所需权限的用户必须返回 403。"""

    @pytest.mark.asyncio
    async def test_no_perm_user_list_users(
        self, test_client: TestClient, permission_data: dict
    ) -> None:
        headers = await login_user(test_client, "user_no_perm_a")
        resp = test_client.get("/api/v1/system/user/list", headers=headers)
        assert resp.status_code == 403, (
            f"无权限用户应返回 403，实际 {resp.status_code}: {resp.text}"
        )
        assert resp.json()["msg"] == "无权限操作"


class TestEnabledPermission:
    """启用角色、启用菜单且套餐允许时必须真正放行。"""

    @pytest.mark.asyncio
    async def test_enabled_role_user_can_list_users(
        self, test_client: TestClient, permission_data: dict
    ) -> None:
        headers = await login_user(test_client, "user_enabled_a")
        resp = test_client.get("/api/v1/system/user/list", headers=headers)
        assert resp.status_code == 200, (
            f"启用角色用户应成功访问，实际 {resp.status_code}: {resp.text}"
        )


# ============================================================
# G2-03: 停用角色 → 403
# ============================================================


class TestDisabledRole:
    """持有停用角色的用户访问受保护端点必须返回 403。"""

    @pytest.mark.asyncio
    async def test_disabled_role_user_list_users(
        self, test_client: TestClient, permission_data: dict
    ) -> None:
        headers = await login_user(test_client, "user_disabled_role_a")
        resp = test_client.get("/api/v1/system/user/list", headers=headers)
        assert resp.status_code == 403
        assert resp.json()["msg"] == "无权限操作"


# ============================================================
# G2-04: 停用菜单 → 403
# ============================================================


class TestDisabledMenu:
    """停用菜单后，依赖该菜单权限的 API 必须返回 403。"""

    @pytest.mark.asyncio
    async def test_disabled_menu_api_returns_403(
        self, test_client: TestClient, permission_data: dict
    ) -> None:
        # MENU_DISABLED_ID 的权限是 module_system:dict:query
        # 需要一个持有该停用菜单的角色对应的用户
        headers = await login_user(test_client, "user_disabled_menu_a")
        resp = test_client.get("/api/v1/system/dict/data/list", headers=headers)
        # 无权限用户访问任何受保护端点都应 403
        assert resp.status_code == 403
        assert resp.json()["msg"] == "无权限操作"


# ============================================================
# G2-05: 套餐移除菜单 → 403
# ============================================================


class TestPackageShrink:
    """租户套餐移除某菜单后，该菜单对应的 API 必须返回 403。"""

    @pytest.mark.asyncio
    async def test_shrunk_package_blocks_menu(
        self, test_client: TestClient, permission_data: dict
    ) -> None:
        # 租户 B 使用 PKG_SHRUNK_ID（收缩套餐）
        # 收缩套餐不包含 MENU_USER_QUERY_ID
        headers = await login_user(test_client, "user_tenant_b")
        resp = test_client.get("/api/v1/system/user/list", headers=headers)
        assert resp.status_code == 403, (
            f"套餐收缩后应返回 403，实际 {resp.status_code}: {resp.text}"
        )
        assert resp.json()["msg"] == "无权限操作"


# ============================================================
# G2-06: 非超管调用平台管理服务 → 403
# ============================================================


class TestAdminOnlyService:
    """非超级管理员调用管理员专属服务必须返回 403。"""

    @pytest.mark.asyncio
    async def test_non_superadmin_create_menu(
        self, test_client: TestClient, permission_data: dict
    ) -> None:
        headers = await login_user(test_client, "user_enabled_a")
        resp = test_client.post(
            "/api/v1/platform/menu/create",
            headers=headers,
            json={
                "name": "test_menu",
                "title": "测试菜单",
                "type": 2,
                "order": 1,
                "route_name": "TestMenu",
                "route_path": "/test-menu",
                "component_path": "test/menu/index",
            },
        )
        assert resp.status_code == 403
        assert resp.json()["msg"] == "仅平台管理员可操作"

    @pytest.mark.asyncio
    async def test_non_superadmin_cannot_list_platform_invoices(
        self, test_client: TestClient, permission_data: dict
    ) -> None:
        headers = await login_user(test_client, "user_enabled_a")
        resp = test_client.get("/api/v1/platform/invoice/list", headers=headers)
        assert resp.status_code == 403
        assert resp.json()["msg"] == "仅平台管理员可操作"

    @pytest.mark.asyncio
    async def test_superadmin_can_list_platform_invoices(
        self, test_client: TestClient, auth_headers: dict, permission_data: dict
    ) -> None:
        resp = test_client.get(
            "/api/v1/platform/invoice/list",
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text


# ============================================================
# G2-07: 租户 A 读租户 B → 403 或空结果
# ============================================================


class TestCrossTenantRead:
    """租户 A 用户读取租户 B 数据必须返回 403 或空结果，不泄露存在性。"""

    @pytest.mark.asyncio
    async def test_tenant_a_read_tenant_b_users(
        self, test_client: TestClient, permission_data: dict
    ) -> None:
        headers = await login_user(test_client, "user_enabled_a")
        resp = test_client.get("/api/v1/system/user/list", headers=headers)
        assert resp.status_code == 200, (
            f"有查询权限的租户用户应进入数据隔离查询，实际 {resp.status_code}: {resp.text}"
        )
        data = resp.json().get("data", {})
        items = data.get("items", []) if isinstance(data, dict) else []
        tenant_b_usernames = {"user_tenant_b"}
        visible = {u.get("username") for u in items}
        assert not (visible & tenant_b_usernames), (
            f"租户 A 用户不应看到租户 B 用户，实际可见: {visible & tenant_b_usernames}"
        )


# ============================================================
# G2-08: 租户 A 改租户 B → 403
# ============================================================


class TestCrossTenantWrite:
    """租户 A 用户修改租户 B 数据必须返回 403。"""

    @pytest.mark.asyncio
    async def test_tenant_a_modify_tenant_b_user(
        self,
        test_client: TestClient,
        auth_headers: dict,
        permission_data: dict,
    ) -> None:
        headers = await login_user(test_client, "user_enabled_a")
        # 尝试修改租户 B 的用户
        resp = test_client.put(
            f"/api/v1/system/user/update/{USER_TENANT_B_ID}",
            headers=headers,
            json={"username": "user_tenant_b", "name": "hacked"},
        )
        assert resp.status_code == 404, (
            f"跨租户修改应按不存在处理，实际 {resp.status_code}: {resp.text}"
        )
        payload = resp.json()
        assert payload["status_code"] == 404
        assert payload["success"] is False
        assert payload["msg"] == "该数据不存在"

        # 通过平台超管的公开 HTTP 读取接口验证目标记录没有被部分修改。
        verify_resp = test_client.get(
            f"/api/v1/system/user/detail/{USER_TENANT_B_ID}",
            headers=auth_headers,
        )
        assert verify_resp.status_code == 200, verify_resp.text
        verify_data = verify_resp.json()["data"]
        assert verify_data["username"] == "user_tenant_b"
        assert verify_data["name"] == "租户B普通用户"


# ============================================================
# G2-09: 超管跨租户行为 → 按明确规则断言
# ============================================================


class TestSuperadminCrossTenant:
    """超级管理员跨租户行为必须按明确规则断言。

    当前规则：平台超管从系统用户管理接口可查看所有租户用户，用于平台运维；
    普通租户用户仍由租户过滤限制。后续若改为显式租户上下文，必须同步修改本契约。
    """

    @pytest.mark.asyncio
    async def test_superadmin_cross_tenant_read(
        self, test_client: TestClient, auth_headers: dict, permission_data: dict
    ) -> None:
        # 使用现有 admin 超管
        resp = test_client.get(
            "/api/v1/system/user/list",
            headers=auth_headers,
        )
        assert resp.status_code == 200, (
            f"超管读取用户列表应成功，实际 {resp.status_code}: {resp.text}"
        )
        payload = resp.json()
        assert payload["status_code"] == 200
        assert payload["success"] is True
        data = payload.get("data", {})
        items = data.get("items", []) if isinstance(data, dict) else []
        visible = {user.get("username") for user in items}
        assert "user_tenant_b" in visible, (
            f"当前规则要求平台超管可见租户 B 用户，实际用户集合: {visible}"
        )
