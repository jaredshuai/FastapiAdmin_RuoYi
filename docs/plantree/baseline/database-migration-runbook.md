# 数据库迁移运行手册

状态：Phase 1 基线迁移已建立，发布前仍须完成目标数据库验证。

## 全新数据库

1. 备份或确认目标数据库为空。
2. 配置真实环境变量或 `backend/env/.env.prod`，不得使用示例密钥。
3. 在 `backend/` 执行 `python main.py upgrade --env=prod`。
4. 全新安装首次启动前显式执行 `python main.py seed --env=prod`；应用启动不会自动灌入种子。
5. 种子包含公开仓库中的初始管理员凭据，首次登录后必须立即改密，并按公司策略轮换或禁用默认账户。
6. 启动服务并执行健康检查及权限 smoke。

## 旧 `metadata.create_all` 数据库

旧库存在业务表但没有 `alembic_version` 时，`upgrade` 和应用启动会主动拒绝，不能绕过该保护直接部署。

1. 先做可恢复备份，并在副本上演练。
2. 执行 `python main.py stamp --env=prod --confirm-schema-equivalent`。
3. 命令会用 Alembic 比较实际结构与当前 ORM 元数据；存在表、列、类型、约束等差异时拒绝 stamp。
4. 若比较失败，先编写并审查显式修复迁移；不得手工伪造 `alembic_version`。
5. stamp 成功后执行 `python main.py upgrade --env=prod`，再启动服务并验证。

## 恢复原则

- 基线迁移的 downgrade 会删除业务表，不作为生产回滚手段。
- 发布失败时优先停止新版本、恢复部署前备份和上一版本制品。
- 任何生产 stamp、upgrade、恢复操作都要保留命令输出、目标数据库标识和备份位置。
