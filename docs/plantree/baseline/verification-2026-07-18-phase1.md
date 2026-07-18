# Phase 1 审计修正验证记录（2026-07-18）

状态：候选修正已提交至[草稿 PR #1](https://github.com/jaredshuai/FastapiAdmin_RuoYi/pull/1)；本地重验与首轮 GitHub Actions 均通过。

## 已验证

| 验证项 | 结果 | 证据摘要 |
| --- | --- | --- |
| 权限与平台发票 | 通过 | G2 负向矩阵包含启用用户 200 阳性对照、停用角色/菜单、套餐收缩、平台接口 403/200 和跨租户读写；逐项断言业务消息 |
| 生产配置 | 通过 | 隔离进程从临时 `.env.prod` 读取端口与安全开关；配置代理、`get_settings()` 与 `create_app()` 值一致；文档关闭时 `/docs`、`/openapi.json` 均为 404 |
| SQLite 迁移 | 通过 | 从仓库根目录对全新 SQLite 执行 `main.py upgrade`，生成业务表和 `alembic_version` |
| 存量库保护 | 通过 | 非空且无 `alembic_version` 的数据库被拒绝；`stamp` 前执行 Alembic 元数据差异比较，不允许盲目标记 |
| MySQL 迁移与全栈 smoke | 通过 | 全新 MySQL 8.0.43 完成 38 表基线，显式 seed 后，Redis 7.4.5 与后端容器均健康；`/common/health` 返回 200 |
| Docker 镜像 | 通过 | 镜像大小 167,574,521 字节；最终增量构建上下文约 32KB；镜像内无 `.venv`、测试缓存和实际环境文件，含 `alembic.ini` 与基线迁移；默认 CMD 缺密钥时在数据库连接前退出 |
| Compose | 通过 | 生产与开发两份 Compose 均通过 `config --quiet`；生产显式要求密钥/CORS，开发覆盖为 `--env=dev` |
| Ruff | 通过 | `All checks passed!` |
| import-linter 基线冻结 | 通过 | `uvx --from import-linter==2.3 lint-imports` 为 3 kept / 0 broken；契约仍用 `ignore_imports` 登记存量违规，本结果只证明没有超出当前基线，不代表 G5 严格边界已关闭 |
| 后端 pytest | 通过 | Python 3.12.13 下 `319 passed, 1 warning in 93.24s`；HTTP 助手不再吞异常，路由注册 smoke 严格拒绝状态码、认证和请求体参数；唯一警告来自第三方 `python_multipart` 弃用提示 |
| GitHub Actions | 通过 | [运行 #29635091044](https://github.com/jaredshuai/FastapiAdmin_RuoYi/actions/runs/29635091044) 的后端、前端与 Compose 三个 job 全绿 |

## 本轮额外发现

- 原基线迁移只在 SQLite 被验证；真实 MySQL 首次执行暴露 `sys_dept` 与 `sys_user` 循环外键建表顺序，已将 MySQL 空库基线调整为迁移连接内临时关闭外键检查、完成全部建表后恢复，并用全新 MySQL 实证。
- 取消启动期自动 seed 后，全新库必须在首次启动前显式执行 `seed`；默认管理员来源于公开种子，首次登录后必须立即改密并按公司策略处置默认账户。
- 原 `assert_route` 会吞应用异常且默认只检查非 404，现已改为必须显式状态码并校验 JSON 业务包络；应用异常直接失败。
- 既有 254 条浅层模块接口清单不具备稳定业务数据，现明确使用 `assert_route_registered` 只验证方法与路径装配，并通过严格三参数签名拒绝 `expected_status`、`auth`、`json` 等伪请求参数，不再冒充 CRUD 业务测试；权限、租户隔离和关键 404 继续由真实 HTTP 聚焦测试断言状态、消息和数据变化。
- 数据库 Engine 在模块导入时创建；CLI 现拒绝同一进程在 Engine 初始化后切换环境，避免 dev Engine 静默承载 prod 配置。

## 仍未关闭

- 草稿 PR #1 尚待评审和合并。
- 尚未用真实上一发布版本数据库副本演练备份、结构比较、stamp、升级和恢复；G3 不能只凭空库基线宣称完全关闭。
- 全栈 smoke 使用本机临时容器完成，不替代目标部署环境的发布验证。
- import-linter 仍是存量违规冻结基线；清空 `ignore_imports`、模块 DAG/数据所有权与装配纪律属于 Phase 2/G5，不能把 3 kept / 0 broken 表述为严格架构门禁已完成。

验证结束后已删除本轮创建的临时 MySQL、Redis、后端容器和临时网络；未删除或重建本机既有 Docker volume。
