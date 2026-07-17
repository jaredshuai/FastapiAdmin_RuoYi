# 关键运行链路

状态：基于提交 `1966c53` 的代码核对

## 登录后菜单与页面注册

1. 后端取得当前用户、角色及角色菜单。
2. 普通租户用户的菜单还要与租户套餐允许菜单取交集。
3. 后端返回树形菜单。
4. 前端校验菜单路由数据、转换页面组件并动态注册到 Vue Router。

关键实现：

- `backend/app/api/v1/module_system/user/service.py::UserService.current_info`
- `frontend/web/src/router/core/RouteRegistry.ts::RouteRegistry.register`

结论：当前项目已经具备“不同账户看到不同页面”的主链，但页面隐藏仅是展示控制。

## 接口鉴权与数据访问

1. FastAPI 依赖解析当前登录用户。
2. `AuthPermission` 校验接口所需权限，并结合租户套餐过滤可用权限。
3. Controller 调用 Service 执行业务规则。
4. Service 通过通用或领域 CRUD 访问数据库。
5. 通用 CRUD 对查询应用数据权限，对创建、更新、删除应用租户约束和审计字段。
6. 请求级数据库会话统一提交或回滚事务。

关键实现：

- `backend/app/core/dependencies.py::AuthPermission.__call__`
- `backend/app/core/base_crud.py::CRUDBase.__filter_permissions`
- `backend/app/core/base_crud.py::CRUDBase.create/update/delete`

当前阻断问题：权限通配符的语义会让部分普通登录用户绕过接口权限，必须在扩展业务前修复。

当前模块耦合：

- `core/dependencies.py::_load_user_from_db` 直接导入用户和角色 ORM 模型。
- `core/dependencies.py::_get_cached_tenant_menu_ids` 直接导入套餐 `PackageService`，并使用 60 秒进程内缓存。
- `base_crud.py` 通过 `tenant_id == 1` 和 `__platform_data_shared__` 实现平台共享数据读取；这是现有业务不变量，但尚未形成正式决策。
- `PluginService.install` 在 `tenant_id == 1` 时跳过套餐插件范围和付费校验；平台租户特权不只存在于通用 CRUD。

## 后端路由注册

- 系统、平台、监控和公共路由由 `backend/app/init_app.py::register_routers` 静态挂载。
- `backend/app/core/discover.py` 扫描 `backend/app/plugin/module_*/**/controller.py` 中的顶层 `APIRouter`。
- 目录扫描不读取 `TenantPluginModel.enabled`，因此 `install/uninstall/toggle` 当前只改变租户数据，不控制 Router 是否注册。
- `reload_dynamic_router` 会为挂载和返回值分别调用 `_build_dynamic_router()`；返回的 Router 不是实际挂载实例，属于过渡路径的一致性缺陷。

目标行为：

- 生产应用由唯一装配层根据显式模块清单注册 Router、迁移、权限、事件和任务。
- 模块集合随制品发布并在启动时完成依赖校验；运行中的进程不安装、卸载或热替换代码。
- 当前目录扫描和热重载只作为过渡兼容或开发能力，必须能够从生产路径关闭；插件市场若保留，语义是能力目录和租户授权，不是运行时代码开关。

## 启动、建表、事件与任务

- lifespan 逐个调用租户、字典和参数服务初始化缓存，并直接启动 `SchedulerUtil`。
- `register_routers` 静态注册系统、平台、监控、公共模块和 AI WebSocket，然后追加动态目录扫描 Router。
- `scripts/initialize.py` 逐个导入所有 ORM 模型；`backend/alembic/versions/` 当前只有 `.gitkeep`，启动通过 `metadata.create_all` 建表并导入 JSON 种子。
- 全局事件来自 `settings.EVENT_LIST`，任务注册集中在调度器实现，而不是由模块清单声明。

这些事实意味着当前还不存在唯一组合根和可验证的迁移/事件/任务清单。Phase 1 先建立 Alembic 与架构检查基线，Phase 2 再迁移为清单驱动装配。

## 目标原则

- 菜单权限控制入口可见性。
- 操作/API 权限控制能否执行动作。
- 数据权限控制能访问哪些记录。
- 租户边界控制数据和套餐能力归属。

四层必须分别测试，不允许用前端隐藏替代后端拒绝。
