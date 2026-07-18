"""
module_system 路由注册清单，并保留少量带业务字段断言的 HTTP 契约测试。

`assert_route_registered` 只证明方法和路径已装配，不代表认证、请求校验或 CRUD 成功；
权限与租户业务语义由 test_permission_negative.py 等聚焦测试负责。
"""

from conftest import assert_route_registered
from fastapi.testclient import TestClient


class TestAuth:
    """认证授权接口（无需认证）。"""

    def test_auth_captcha(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/auth/captcha/get")

    def test_auth_login(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/auth/login")

    def test_auth_logout(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/auth/logout")

    def test_auth_refresh(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/auth/token/refresh")

    def test_auth_tenants(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/auth/tenants")

    def test_auth_select_tenant(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/auth/select-tenant")

    def test_auth_tenant_register(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/auth/tenant/register")

    def test_auth_auto_login_users(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/auth/auto-login/users")

    def test_auth_auto_login_token(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/auth/auto-login/token?user_id=1")


class TestUser:
    """用户管理接口 — 数据验证。"""

    def test_user_current_info(self, test_client: TestClient, auth_headers: dict) -> None:
        resp = test_client.get("/system/user/current/info", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["username"] == "admin", f"期望 admin，实际 {data['data'].get('username')}"

    def test_user_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/user/list")

    def test_user_detail(self, test_client: TestClient, auth_headers: dict) -> None:
        resp = test_client.get("/system/user/detail/1", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["username"] == "super", f"id=1 应为 super，实际 {data['data'].get('username')}"

    def test_user_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/user/create")

    def test_user_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/system/user/update/1")

    def test_user_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/system/user/delete")

    def test_user_import_template(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/user/import/template")

    def test_user_export(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/user/export")

    def test_user_import_data(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/user/import/data")

    def test_user_current_info_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/system/user/current/info/update")

    def test_user_password_change(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/system/user/password/change")

    def test_user_password_forget(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/user/password/forget")

    def test_user_password_reset(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/system/user/password/reset/1")

    def test_user_register(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/user/register")

    def test_user_status_batch(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PATCH", "/system/user/status/batch")


class TestRole:
    """角色管理接口 — 数据验证。"""

    def test_role_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/role/list")

    def test_role_detail(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/role/detail/1")

    def test_role_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/role/create")

    def test_role_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/system/role/update/1")

    def test_role_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/system/role/delete")

    def test_role_export(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/role/export")

    def test_role_permission(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/system/role/permission")

    def test_role_status_batch(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PATCH", "/system/role/status/batch")


class TestDept:
    """部门管理接口 — 数据验证。"""

    def test_dept_tree(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/dept/tree")

    def test_dept_detail(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/dept/detail/1")

    def test_dept_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/dept/create")

    def test_dept_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/system/dept/update/1")

    def test_dept_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/system/dept/delete")

    def test_dept_status_batch(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PATCH", "/system/dept/status/batch")


class TestPosition:
    """岗位管理接口 — 数据验证。"""

    def test_position_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/position/list")

    def test_position_detail(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/position/detail/1")

    def test_position_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/position/create")

    def test_position_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/system/position/update/1")

    def test_position_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/system/position/delete")

    def test_position_export(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/position/export")

    def test_position_status_batch(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PATCH", "/system/position/status/batch")


class TestDict:
    """字典管理接口 — 数据验证。"""

    def test_dict_type_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/dict/type/list")

    def test_dict_type_detail(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/dict/type/detail/1")

    def test_dict_type_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/dict/type/create")

    def test_dict_type_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/system/dict/type/update/1")

    def test_dict_type_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/system/dict/type/delete")

    def test_dict_data_by_type(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/dict/data/info/sys_normal_disable")

    def test_dict_data_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/dict/data/list")

    def test_dict_data_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/dict/data/create")

    def test_dict_data_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/system/dict/data/update/1")

    def test_dict_data_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/system/dict/data/delete")

    def test_dict_data_export(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/dict/data/export")

    def test_dict_data_status_batch(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PATCH", "/system/dict/data/status/batch")

    def test_dict_type_export(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/dict/type/export")

    def test_dict_type_optionselect(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/dict/type/optionselect")

    def test_dict_type_status_batch(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PATCH", "/system/dict/type/status/batch")


class TestNotice:
    """公告通知接口 — 数据验证。"""

    def test_notice_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/notice/list")

    def test_notice_detail(self, test_client: TestClient, auth_headers: dict) -> None:
        response = test_client.get("/system/notice/detail/1", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["msg"] == "该数据不存在"

    def test_notice_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/notice/create")

    def test_notice_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/system/notice/update/1")

    def test_notice_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/system/notice/delete")

    def test_notice_unread_count(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/notice/unread-count")

    def test_notice_available(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/notice/available")

    def test_notice_export(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/notice/export")

    def test_notice_panel(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/notice/panel")

    def test_notice_read(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/notice/read/1")

    def test_notice_read_all(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/notice/read-all")

    def test_notice_status_batch(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PATCH", "/system/notice/status/batch")


class TestParams:
    """参数管理接口 — 数据验证。"""

    def test_params_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/param/list")

    def test_params_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/param/create")

    def test_params_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/system/param/update/1")

    def test_params_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/system/param/delete")

    def test_params_detail(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/param/detail/1")

    def test_params_export(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/param/export")

    def test_params_info(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/param/info")

    def test_params_by_key(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/param/key/test.key")

    def test_params_value_by_key(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/param/value/test.key")

    def test_params_status_batch(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PATCH", "/system/param/status/batch")


class TestLog:
    """日志管理接口 — 数据验证。"""

    def test_login_log_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/log/login/list")

    def test_login_log_detail(self, test_client: TestClient, auth_headers: dict) -> None:
        response = test_client.get("/system/log/login/detail/1", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["msg"] == "该数据不存在"

    def test_operation_log_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/log/operation/list")

    def test_operation_log_detail(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/log/operation/detail/1")


class TestTicket:
    """工单管理接口 — 数据验证。"""

    def test_ticket_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/system/ticket/list")

    def test_ticket_detail(self, test_client: TestClient, auth_headers: dict) -> None:
        response = test_client.get("/system/ticket/detail/1", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["msg"] == "该数据不存在"

    def test_ticket_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/system/ticket/create")

    def test_ticket_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/system/ticket/update/1")

    def test_ticket_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/system/ticket/delete")

    def test_ticket_batch(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/system/ticket/batch")
