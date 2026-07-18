# 项目基线

状态：已建立初始基线，待 Phase 0 运行验证刷新

基线提交：`1966c53d2f19cd5e194836cabd913556ccc97b67`

## 已确认事实

- `D:\codespace\FastapiAdmin_RuoYi` 是现有 FastapiAdmin 在相同提交上的干净副本。
- 该仓库远程已独立为 `https://github.com/jaredshuai/FastapiAdmin_RuoYi.git`。
- 后端使用 FastAPI、Pydantic、SQLAlchemy、Alembic、Redis 和 APScheduler；要求 Python 3.12 或以上。
- Web 前端使用 Vue、TypeScript、Vite、Element Plus 和 pnpm。
- 当前代码已有账户、角色、菜单、租户套餐、数据权限、动态路由和插件发现等平台骨架。
- 现有代码仍有权限、生产配置、容器交付和测试可信度方面的已知高风险，不能把当前提交当作生产基线。

## 基线文件

- [module-map.md](module-map.md)：当前模块边界及目标归属。
- [runtime-flows.md](runtime-flows.md)：登录菜单、接口鉴权、数据访问和插件注册链路。
- [storage-and-state.md](storage-and-state.md)：数据库、Redis、进程状态和配置边界。
- [toolchain.md](toolchain.md)：本地、CI 和容器使用的固定版本契约。
- [verification-2026-07-17.md](verification-2026-07-17.md)：Phase 0 本地命令、结果和失败基线。
- [verification-2026-07-18-phase1.md](verification-2026-07-18-phase1.md)：Phase 1 审计修正、本地数据库/容器 smoke 与剩余门槛。
- [test-and-release-gates.md](test-and-release-gates.md)：从可运行到可发布的验证门槛。
- [database-migration-runbook.md](database-migration-runbook.md)：全新数据库与旧 `create_all` 数据库的升级、stamp 和恢复步骤。
- [risk-hotspots.md](risk-hotspots.md)：当前优先处理的风险。

## 刷新规则

Phase 0 完成后，用真实命令输出更新以下内容：

- 锁定后的 Python、uv、Node、pnpm、数据库和 Redis 版本。
- 后端测试数、前端测试数、静态检查结果和构建结果。
- Docker 镜像构建及容器健康检查结果。
- 权限负向测试矩阵的实际覆盖结果。

未执行的命令不得记录为通过。
