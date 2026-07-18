"""
module_platform 路由注册清单，并保留少量带业务消息断言的 HTTP 契约测试。

`assert_route_registered` 只证明方法和路径已装配，不代表认证、请求校验或业务成功；
超管与租户隔离语义由 test_permission_negative.py 的聚焦测试负责。
认证数据测试：admin 登录后验证 CRUD 真实数据。
"""

from conftest import assert_route_registered
from fastapi.testclient import TestClient


class TestTenant:
    """租户管理接口。"""

    def test_tenant_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/tenant/list")

    def test_tenant_detail(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/tenant/detail/1")

    def test_tenant_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/tenant/create")

    def test_tenant_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/platform/tenant/update/1")

    def test_tenant_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/platform/tenant/delete")

    def test_tenant_config_info(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/tenant/1/config/info")

    def test_tenant_config(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/platform/tenant/1/config")

    def test_tenant_renew(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/platform/tenant/renew/1")

    def test_tenant_status(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/platform/tenant/status/1")

    def test_tenant_status_batch(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PATCH", "/platform/tenant/status/batch")

    def test_tenant_package_change_preview(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/tenant/1/package-change-preview")

    def test_tenant_users(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/tenant/1/users")

    def test_tenant_add_user(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/tenant/1/users")

    def test_tenant_remove_user(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/platform/tenant/1/users/2")

    def test_tenant_invoice_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/tenant/invoice/list")

    def test_tenant_invoice_download(self, test_client: TestClient, auth_headers: dict) -> None:
        response = test_client.get(
            "/platform/tenant/invoice/1/download", headers=auth_headers
        )
        assert response.status_code == 404
        assert response.json()["msg"] == "发票不存在"

    def test_tenant_license_download(self, test_client: TestClient, auth_headers: dict) -> None:
        response = test_client.get(
            "/platform/tenant/invoice/1/license/download", headers=auth_headers
        )
        assert response.status_code == 404
        assert response.json()["msg"] == "发票不存在"


class TestPackage:
    """套餐管理接口。"""

    def test_package_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/package/list")

    def test_package_detail(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/package/detail/1")

    def test_package_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/package/create")

    def test_package_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/platform/package/update/1")

    def test_package_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/platform/package/delete")

    def test_package_menus(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/package/menus/1")

    def test_package_set_menus(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/package/menus/1/set")

    def test_package_plugins(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/package/plugins/1")

    def test_package_set_plugins(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/package/plugins/1/set")

    def test_package_status_batch(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PATCH", "/platform/package/status/batch")


class TestPlugin:
    """插件管理接口。"""

    def test_plugin_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/plugin/list")

    def test_plugin_detail(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/plugin/detail/1")

    def test_plugin_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/plugin/create")

    def test_plugin_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/platform/plugin/update/1")

    def test_plugin_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/platform/plugin/delete")

    def test_plugin_marketplace(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/plugin/marketplace")

    def test_plugin_my(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/plugin/my")

    def test_plugin_install(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/plugin/install")

    def test_plugin_uninstall(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/plugin/uninstall")

    def test_plugin_toggle(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/plugin/toggle")

    def test_plugin_reload(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/plugin/reload")


class TestMenu:
    """菜单管理接口。"""

    def test_menu_tree(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/menu/tree")

    def test_menu_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/menu/create")

    def test_menu_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/platform/menu/update/1")

    def test_menu_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/platform/menu/delete")

    def test_menu_detail(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/menu/detail/1")

    def test_menu_status_batch(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PATCH", "/platform/menu/status/batch")


class TestEmail:
    """邮件服务接口。"""

    def test_email_config_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/email/config/list")

    def test_email_config_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/email/config/create")

    def test_email_config_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/platform/email/config/update/1")

    def test_email_config_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/platform/email/config/delete")

    def test_email_config_detail(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/email/config/detail/1")

    def test_email_config_test(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/email/config/test")

    def test_email_send(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/email/send")

    def test_email_template_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/email/template/list")

    def test_email_template_detail(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/email/template/detail/1")

    def test_email_template_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/email/template/create")

    def test_email_template_update(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/platform/email/template/update/1")

    def test_email_template_delete(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "DELETE", "/platform/email/template/delete")

    def test_email_log_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/email/log/list")


class TestOrder:
    """订单管理接口。"""

    def test_order_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/order/list")

    def test_order_detail_not_found(self, test_client: TestClient, auth_headers: dict) -> None:
        response = test_client.get("/platform/order/detail/999999", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["msg"] == "订单不存在"

    def test_order_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/order/create")

    def test_order_cancel(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/order/cancel/1")

    def test_order_refund_apply(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/order/refund/apply/1")


class TestPayment:
    """支付管理接口。"""

    def test_payment_record_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/payment/record/list")

    def test_payment_pay(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/payment/pay/1")

    def test_payment_status(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/payment/status/1")

    def test_payment_callback(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/payment/callback/wechat")

    def test_payment_mock_callback(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/payment/mock/callback")


class TestRefund:
    """退款管理接口。"""

    def test_refund_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/refund/list")

    def test_refund_approve(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/platform/refund/approve/1")

    def test_refund_reject(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/platform/refund/reject/1")


class TestInvoice:
    """发票管理接口。"""

    def test_invoice_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/invoice/list")

    def test_invoice_apply(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/tenant/invoice/apply")

    def test_invoice_issue(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/platform/invoice/issue/1")

    def test_invoice_void(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "PUT", "/platform/invoice/void/1")


class TestSelfService:
    """租户自助服务接口。"""

    def test_package_available(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/tenant/package/available")

    def test_package_preview(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/tenant/package/preview")

    def test_plugin_purchase(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/tenant/plugin/purchase")

    def test_self_order_list(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/tenant/order/list")

    def test_self_order_detail(self, test_client: TestClient, auth_headers: dict) -> None:
        response = test_client.get(
            "/platform/tenant/order/detail/1", headers=auth_headers
        )
        assert response.status_code == 404
        assert response.json()["msg"] == "该数据不存在"

    def test_self_order_create(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "POST", "/platform/tenant/order/create")

    def test_self_workspace(self, test_client: TestClient) -> None:
        assert_route_registered(test_client, "GET", "/platform/tenant/workspace")
