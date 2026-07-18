"""G2 权限负向测试矩阵 — 测试数据工厂。

本模块负责在测试数据库中建立 G2 验收矩阵所需的多租户、多角色、多用户、
多菜单、多套餐的测试数据，并在每个测试函数运行前回滚到干净状态。

设计要点：
- 不复用 conftest.py 的 admin/auth_headers fixture；本模块自行登录。
- 通过直写 ORM 建立数据，绕过 Service 层的权限校验。
- 每个测试函数使用独立的数据库事务（function scope），测试结束自动回滚。
- 数据 ID 使用稳定常量，便于测试断言。
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.module_platform.menu.model import MenuModel
from app.api.v1.module_platform.package.model import PackageMenuModel, PackageModel
from app.api.v1.module_platform.tenant.model import TenantModel
from app.api.v1.module_system.dept.model import DeptModel
from app.api.v1.module_system.role.model import RoleMenusModel, RoleModel
from app.api.v1.module_system.user.model import UserModel, UserRolesModel
from app.utils.hash_bcrpy_util import PwdUtil

# ============================================================
# 稳定 ID 常量 — 测试断言依据
# ============================================================

# 租户
TENANT_A_ID = 9001
TENANT_B_ID = 9002

# 套餐
PKG_FULL_ID = 9101  # 含全部测试菜单
PKG_SHRUNK_ID = 9102  # 仅含部分测试菜单（用于套餐收缩测试）

# 角色
ROLE_DISABLED_A_ID = 9201  # 租户 A 下停用角色
ROLE_ENABLED_A_ID = 9202  # 租户 A 下启用角色
ROLE_NO_PERM_A_ID = 9203  # 租户 A 下无菜单的角色

# 菜单
MENU_USER_QUERY_ID = 9301  # module_system:user:query
MENU_USER_CREATE_ID = 9302  # module_system:user:create
MENU_ROLE_QUERY_ID = 9303  # module_system:role:query
MENU_DISABLED_ID = 9304  # 停用菜单 module_system:dict:query
MENU_USER_UPDATE_ID = 9305  # module_system:user:update
MENU_PLATFORM_MENU_CREATE_ID = 9306  # module_platform:menu:create

# 用户
USER_DISABLED_A_ID = 9401  # 租户 A 停用用户
USER_NO_ROLE_A_ID = 9402  # 租户 A 无角色用户
USER_DISABLED_ROLE_A_ID = 9403  # 租户 A 持有停用角色的用户
USER_NO_PERM_A_ID = 9404  # 租户 A 持有无菜单角色的用户
USER_TENANT_B_ID = 9405  # 租户 B 普通用户（用于跨租户测试）
USER_ENABLED_A_ID = 9406  # 租户 A 有用户读写与平台菜单创建权限的非超管
USER_DISABLED_MENU_A_ID = 9407  # 租户 A 持有停用菜单的用户

# 部门
DEPT_A_ID = 9501
DEPT_B_ID = 9502

ROLE_DISABLED_MENU_A_ID = 9204
ROLE_ENABLED_B_ID = 9205

TEST_USER_IDS = (
    USER_DISABLED_A_ID,
    USER_NO_ROLE_A_ID,
    USER_DISABLED_ROLE_A_ID,
    USER_NO_PERM_A_ID,
    USER_TENANT_B_ID,
    USER_ENABLED_A_ID,
    USER_DISABLED_MENU_A_ID,
)
TEST_ROLE_IDS = (
    ROLE_DISABLED_A_ID,
    ROLE_ENABLED_A_ID,
    ROLE_NO_PERM_A_ID,
    ROLE_DISABLED_MENU_A_ID,
    ROLE_ENABLED_B_ID,
)
TEST_MENU_IDS = (
    MENU_USER_QUERY_ID,
    MENU_USER_CREATE_ID,
    MENU_ROLE_QUERY_ID,
    MENU_DISABLED_ID,
    MENU_USER_UPDATE_ID,
    MENU_PLATFORM_MENU_CREATE_ID,
)
TEST_PACKAGE_IDS = (PKG_FULL_ID, PKG_SHRUNK_ID)
TEST_TENANT_IDS = (TENANT_A_ID, TENANT_B_ID)
TEST_DEPT_IDS = (DEPT_A_ID, DEPT_B_ID)


# ============================================================
# 测试数据工厂
# ============================================================


async def seed_permission_test_data(db: AsyncSession) -> dict[str, Any]:
    """建立 G2 权限负向测试所需的全套数据。

    建立顺序遵循外键依赖：租户 → 套餐 → 菜单 → 部门 → 角色 → 用户 → 关联。

    参数:
        db: 已开启事务的异步会话。

    返回:
        dict: 包含所有创建实体的 ID 映射，供测试断言使用。
    """
    created: dict[str, Any] = {}

    # ---------- 租户 ----------
    tenant_a = TenantModel(
        id=TENANT_A_ID,
        name="测试租户A",
        code="tenantA",
        package_id=PKG_FULL_ID,
        status=0,
    )
    tenant_b = TenantModel(
        id=TENANT_B_ID,
        name="测试租户B",
        code="tenantB",
        package_id=PKG_SHRUNK_ID,
        status=0,
    )
    db.add_all([tenant_a, tenant_b])
    await db.flush()
    created["tenants"] = [TENANT_A_ID, TENANT_B_ID]

    # ---------- 套餐 ----------
    pkg_full = PackageModel(
        id=PKG_FULL_ID,
        name="完整套餐",
        code="pkgFull",
        status=0,
    )
    pkg_shrunk = PackageModel(
        id=PKG_SHRUNK_ID,
        name="收缩套餐",
        code="pkgShrunk",
        status=0,
    )
    db.add_all([pkg_full, pkg_shrunk])
    await db.flush()
    created["packages"] = [PKG_FULL_ID, PKG_SHRUNK_ID]

    # ---------- 菜单（权限标识） ----------
    menus = [
        MenuModel(
            id=MENU_USER_QUERY_ID,
            name="用户查询",
            permission="module_system:user:query",
            type=3,
            status=0,
            title="用户查询",
        ),
        MenuModel(
            id=MENU_USER_CREATE_ID,
            name="用户创建",
            permission="module_system:user:create",
            type=3,
            status=0,
            title="用户创建",
        ),
        MenuModel(
            id=MENU_ROLE_QUERY_ID,
            name="角色查询",
            permission="module_system:role:query",
            type=3,
            status=0,
            title="角色查询",
        ),
        MenuModel(
            id=MENU_DISABLED_ID,
            name="停用菜单",
            permission="module_system:dict:query",
            type=3,
            status=1,  # 停用
            title="停用菜单",
        ),
        MenuModel(
            id=MENU_USER_UPDATE_ID,
            name="用户更新",
            permission="module_system:user:update",
            type=3,
            status=0,
            title="用户更新",
        ),
        MenuModel(
            id=MENU_PLATFORM_MENU_CREATE_ID,
            name="平台菜单创建",
            permission="module_platform:menu:create",
            type=3,
            status=0,
            title="平台菜单创建",
        ),
    ]
    db.add_all(menus)
    await db.flush()
    created["menus"] = [m.id for m in menus]

    # ---------- 部门 ----------
    dept_a = DeptModel(
        id=DEPT_A_ID,
        name="租户A部门",
        code="deptA",
        tenant_id=TENANT_A_ID,
        status=0,
    )
    dept_b = DeptModel(
        id=DEPT_B_ID,
        name="租户B部门",
        code="deptB",
        tenant_id=TENANT_B_ID,
        status=0,
    )
    db.add_all([dept_a, dept_b])
    await db.flush()
    created["depts"] = [DEPT_A_ID, DEPT_B_ID]

    # ---------- 角色 ----------

    # 租户 A：停用角色（持有启用菜单，但因角色停用应被拒绝）
    role_disabled_a = RoleModel(
        id=ROLE_DISABLED_A_ID,
        name="租户A停用角色",
        code="roleDisabledA",
        tenant_id=TENANT_A_ID,
        status=1,  # 停用
    )
    role_disabled_a.menus = [await db.get(MenuModel, MENU_USER_QUERY_ID)]
    # 租户 A：启用角色，持有 user:query 菜单
    role_enabled_a = RoleModel(
        id=ROLE_ENABLED_A_ID,
        name="租户A启用角色",
        code="roleEnabledA",
        tenant_id=TENANT_A_ID,
        status=0,
    )
    role_enabled_a.menus = [
        await db.get(MenuModel, MENU_USER_QUERY_ID),
    ]
    # 租户 A：无菜单角色
    role_no_perm_a = RoleModel(
        id=ROLE_NO_PERM_A_ID,
        name="租户A无权限角色",
        code="roleNoPermA",
        tenant_id=TENANT_A_ID,
        status=0,
    )
    role_disabled_menu_a = RoleModel(
        id=ROLE_DISABLED_MENU_A_ID,
        name="租户A停用菜单角色",
        code="roleDisabledMenuA",
        tenant_id=TENANT_A_ID,
        status=0,
    )
    role_disabled_menu_a.menus = [await db.get(MenuModel, MENU_DISABLED_ID)]
    role_enabled_b = RoleModel(
        id=ROLE_ENABLED_B_ID,
        name="租户B用户查询角色",
        code="roleEnabledB",
        tenant_id=TENANT_B_ID,
        status=0,
    )
    role_enabled_b.menus = [await db.get(MenuModel, MENU_USER_QUERY_ID)]
    role_enabled_a.menus = [
        await db.get(MenuModel, MENU_USER_QUERY_ID),
        await db.get(MenuModel, MENU_USER_UPDATE_ID),
        await db.get(MenuModel, MENU_PLATFORM_MENU_CREATE_ID),
    ]
    db.add_all([
        role_disabled_a,
        role_enabled_a,
        role_no_perm_a,
        role_disabled_menu_a,
        role_enabled_b,
    ])
    await db.flush()
    created["roles"] = [ROLE_DISABLED_A_ID, ROLE_ENABLED_A_ID, ROLE_NO_PERM_A_ID]

    # ---------- 用户 ----------
    password_hash = PwdUtil.hash_password("Test@123456")

    users_data = [
        (
            USER_DISABLED_A_ID,
            "user_disabled_a",
            "租户A停用用户",
            TENANT_A_ID,
            DEPT_A_ID,
            1,  # 停用
            [],  # 无角色
        ),
        (
            USER_NO_ROLE_A_ID,
            "user_no_role_a",
            "租户A无角色用户",
            TENANT_A_ID,
            DEPT_A_ID,
            0,
            [],
        ),
        (
            USER_DISABLED_ROLE_A_ID,
            "user_disabled_role_a",
            "租户A持停用角色用户",
            TENANT_A_ID,
            DEPT_A_ID,
            0,
            [ROLE_DISABLED_A_ID],
        ),
        (
            USER_NO_PERM_A_ID,
            "user_no_perm_a",
            "租户A无权限用户",
            TENANT_A_ID,
            DEPT_A_ID,
            0,
            [ROLE_NO_PERM_A_ID],
        ),
        (
            USER_TENANT_B_ID,
            "user_tenant_b",
            "租户B普通用户",
            TENANT_B_ID,
            DEPT_B_ID,
            0,
            [ROLE_ENABLED_B_ID],
        ),
        (
            USER_ENABLED_A_ID,
            "user_enabled_a",
            "租户A有权限用户",
            TENANT_A_ID,
            DEPT_A_ID,
            0,
            [ROLE_ENABLED_A_ID],
        ),
        (
            USER_DISABLED_MENU_A_ID,
            "user_disabled_menu_a",
            "租户A持停用菜单用户",
            TENANT_A_ID,
            DEPT_A_ID,
            0,
            [ROLE_DISABLED_MENU_A_ID],
        ),
    ]

    for (
        uid,
        username,
        name,
        tenant_id,
        dept_id,
        status,
        role_ids,
    ) in users_data:
        user = UserModel(
            id=uid,
            username=username,
            password=password_hash,
            name=name,
            tenant_id=tenant_id,
            dept_id=dept_id,
            status=status,
            is_superuser=False,
        )
        if role_ids:
            roles = []
            for rid in role_ids:
                role = await db.get(RoleModel, rid)
                if role:
                    roles.append(role)
            user.roles = roles
        db.add(user)

    await db.flush()
    created["users"] = [u[0] for u in users_data]

    # 完整套餐允许租户 A 的已授权用户访问三类测试接口；收缩套餐
    # 故意不含 user:query，以证明套餐过滤确实收回既有角色权限。
    db.add_all([
        PackageMenuModel(package_id=PKG_FULL_ID, menu_id=MENU_USER_QUERY_ID),
        PackageMenuModel(package_id=PKG_FULL_ID, menu_id=MENU_USER_UPDATE_ID),
        PackageMenuModel(package_id=PKG_FULL_ID, menu_id=MENU_PLATFORM_MENU_CREATE_ID),
        PackageMenuModel(package_id=PKG_SHRUNK_ID, menu_id=MENU_ROLE_QUERY_ID),
    ])
    await db.flush()

    return created


async def clear_permission_test_data(db: AsyncSession) -> None:
    """删除 G2 工厂写入的测试数据，使固定 ID 可在下一测试复用。"""
    await db.execute(delete(UserRolesModel).where(UserRolesModel.user_id.in_(TEST_USER_IDS)))
    await db.execute(delete(RoleMenusModel).where(RoleMenusModel.role_id.in_(TEST_ROLE_IDS)))
    await db.execute(delete(PackageMenuModel).where(PackageMenuModel.package_id.in_(TEST_PACKAGE_IDS)))
    await db.execute(delete(UserModel).where(UserModel.id.in_(TEST_USER_IDS)))
    await db.execute(delete(RoleModel).where(RoleModel.id.in_(TEST_ROLE_IDS)))
    await db.execute(delete(DeptModel).where(DeptModel.id.in_(TEST_DEPT_IDS)))
    await db.execute(delete(TenantModel).where(TenantModel.id.in_(TEST_TENANT_IDS)))
    await db.execute(delete(PackageModel).where(PackageModel.id.in_(TEST_PACKAGE_IDS)))
    await db.execute(delete(MenuModel).where(MenuModel.id.in_(TEST_MENU_IDS)))

    # AuthPermission 的套餐菜单缓存属于进程内状态，不能跨测试沿用。
    from app.core.dependencies import _package_menu_cache

    _package_menu_cache.clear()


async def login_user(
    test_client: Any,
    username: str,
    password: str = "Test@123456",
) -> dict[str, str]:
    """以指定用户登录并返回认证头。

    参数:
        test_client: FastAPI TestClient 实例。
        username: 用户名。
        password: 密码（默认 Test@123456）。

    返回:
        dict: 包含 Authorization 键的认证头。
    """
    resp = test_client.post(
        "/system/auth/login",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200, (
        f"用户 {username} 登录失败: status={resp.status_code} body={resp.text}"
    )
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
