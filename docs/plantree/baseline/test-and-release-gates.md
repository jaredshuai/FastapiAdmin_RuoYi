# 测试与发布门槛

状态：目标门槛已定义；当前提交尚未通过这些门槛

## 测试分层原则

G0-G6 是发布门槛，不替代测试层次。新架构切片按以下职责组织：

| 层次 | 主要证明 | 外部依赖 |
| --- | --- | --- |
| 领域/用例测试 | 业务规则、状态流转、失败模式 | 使用 Fake Port；不启动 FastAPI，不连接数据库/Redis |
| Port/Adapter 契约测试 | 不同 Adapter 对共有接口的行为兼容 | 对 Fake 和真实 Adapter 运行可共用契约 |
| 持久化集成测试 | 迁移、约束、事务、查询和租户过滤 | 使用真实测试数据库 |
| HTTP/权限集成测试 | 身份、权限、状态码、序列化和跨租户拒绝 | 启动 FastAPI 测试应用及必要依赖 |
| 装配/端到端 smoke | 清单、Router、菜单、权限、前端和制品一致 | 使用接近发布的装配结果 |

Phase 1 的权限修复可以继续用集成测试验证现有真实依赖链，不要求先完成用例层重构。Phase 2 的 ticket 参考模块必须同时给出无框架用例测试和真实 Adapter 集成测试，以证据决定该模式是否推广。

## G0：可重复环境

要求：

- 锁定并记录 Python `3.12.13`、uv `0.11.15`、Node `24.15.0`、pnpm `9.15.3`、MySQL `8.0.43` 和 Redis `7.4.5-alpine`；以[工具链版本契约](toolchain.md)为准。
- 新机器按照文档能够安装依赖、启动后端和前端。
- 不依赖宿主机偶然存在的 Python、全局包或未声明环境变量。
- 前端自动导入声明和 ESLint globals 必须由确定性命令生成或作为受审查产物提交；`type-check`、`lint:check`、`build` 不能依赖此前运行过 Vite。
- 后端与 Docker 的真实 `.env` 不进入版本库，只提交不含有效机密的 `.env.*.example`；前端提交的 `VITE_*` 属于会进入客户端制品的公开构建配置，禁止承载服务端密钥。

候选验证命令：

```powershell
uv --version # 必须为 0.11.15
uv python install 3.12.13
uv sync --project backend --frozen
uv run --project backend python --version # 必须为 3.12.13
uv run --project backend ruff check --no-fix .
uv run --project backend pytest

cd frontend\web
node --version # 必须为 v24.15.0
pnpm --version # 必须为 9.15.3
pnpm install --frozen-lockfile
pnpm run lint:check
pnpm run type-check
pnpm run test
pnpm run build
```

当前状态：本地命令已通过，G0 等待远端证据。2026-07-17 以固定工具链验证：后端冻结同步、Ruff 只读检查和 265 项 pytest 全部通过；前端冻结安装、`lint:check`、3 项 Vitest、类型检查和生产构建通过；Compose 示例配置解析通过。`pnpm run gen:auto-imports` 从 422 个源码文件确定性生成忽略产物，检查与构建不依赖此前运行 Vite。根目录 CI 已覆盖同一组命令并断言实际版本，但尚未获得 GitHub Actions 运行证据。详见[本地验证记录](verification-2026-07-17.md)。

## G1：非破坏性静态检查

- 后端增加明确的无自动修改检查，例如 `uv run ruff check --no-fix .`。
- 前端把 `lint:check` 与 `lint:fix` 分开；CI 只运行 `pnpm run lint:check`，不运行带 `--fix` 或 `--write` 的脚本。
- 根目录 CI 同时覆盖后端与前端，不能放在子项目内导致平台不识别。
- Phase 1 接入 `import-linter` 或等价工具并保存当前违规基线，CI 阻止新增反向依赖；G5 前必须清空相关基线并改为严格失败。

当前状态：后端 `ruff check --no-fix`、前端 `lint:check`、检查后 `git diff --exit-code` 及未跟踪文件检查已进入根目录工作流；本地只读检查通过。需取得远端运行证据后与 G0 一起关闭。

## G2：安全与权限矩阵

每个受保护动作至少覆盖：

| 身份 | 期望 |
| --- | --- |
| 未登录 | 401 或项目统一未登录响应 |
| 已登录但无权限 | 403 |
| 拥有所需菜单/操作权限 | 成功 |
| 角色或菜单已停用 | 403 |
| 权限不在租户套餐内 | 403 |
| 跨租户读取或修改 | 拒绝或空结果，不能泄露存在性 |
| 超级管理员 | 按明确规则放行，不依赖普通权限编码伪装 |

测试必须断言业务响应和数据变化，不能只断言路由不是 404。

## G3：数据库迁移

- 空数据库可升级到最新版本。
- 已有测试数据可从上一发布版本升级。
- 对由 `metadata.create_all` 建成的存量库，先备份并比较实际结构与基线；只有结构等价才允许 `alembic stamp head`，差异必须通过显式修复迁移处理。
- 关键迁移具有回滚方案；无法自动降级时要写明恢复步骤。
- 租户字段、唯一约束和索引通过数据库层验证。

当前状态：`backend/alembic/versions/` 只有 `.gitkeep`，启动通过 `metadata.create_all` 建表，尚不存在有效 Alembic 迁移，因此当前提交不能通过 G3。

## G4：生产容器

- 后端镜像包含应用代码，不依赖开发目录绑定挂载。
- 生产环境在应用导入配置前选定环境文件。
- JWT/会话密钥、数据库密码等通过环境或机密系统提供。
- Compose 配置解析、镜像构建、健康检查和最小 HTTP smoke 全部通过。

## G5：模块架构

- 每个正式模块的清单通过 Pydantic/JSON Schema 校验；缺失身份、版本、直接依赖、公开接口声明或必要入口时，清单检查命令非零退出。Provided Interface 可以显式为空，但不能省略声明或用内部 use case 填充。
- 导入级边界由 `import-linter` 或等价架构检查负责：严格禁止平台内核反向依赖业务模块、跨模块导入内部 CRUD/模型/Adapter，并检测模块依赖成环。
- 运行时数据所有权由契约测试负责：检查参考模块的迁移与显式 SQL 不写入其他模块拥有的表，并对公开只读查询和跨模块写入失败模式做测试。该门槛不能由导入检查替代。
- 参考模块的领域/用例代码不得导入 FastAPI、SQLAlchemy、ORM Model 或具体 CRUD；CI 必须能在不启动 Web、数据库和缓存的条件下运行主要用例测试。
- 调用方 Required Port、提供方公开接口和边界 Adapter 的所有权必须可检查；Fake 与 SQLAlchemy Adapter 对共有行为执行同一契约，数据库专属行为由真实数据库集成测试覆盖。
- 全仓跨模块模型导入、裸 SQL 和写表清单必须可审查，G5 前清零跨模块写入；只访问本模块表的存量混合 service 可以登记为后续迁移债务。ticket 评审形成“推广、调整或拒绝”结论后，新增或实质修改的模块必须遵循该结论提供明确的用例/持久化 seam，不能静默复制旧 service 的混合职责。
- 装配器测试覆盖依赖闭包、`packaging.specifiers` 版本兼容和稳定拓扑顺序；相同清单输入必须产生相同注册清单摘要。
- 新增、停用或移除参考模块不需要修改平台内核；CI 用严格导入检查、后端启动 smoke 和前端构建三类证据证明，并检查停用模块的 Router、菜单、权限、前端组件、事件和任务均未注册。不以 `git diff` 文件列表单独证明内核未改。
- 构建期校验“前端引用权限编码 ⊆ 后端模块清单权限编码”，并验证所有菜单 `component_path` 都能映射到构建产物中的懒加载组件。
- 生产构建输出 `bill-of-modules.json` 或等价制品清单，包含模块版本与清单 hash；摘要同时写入不可变制品元数据（例如镜像 label），生产启动重新计算并比对，漂移时拒绝启动。生产启动明确拒绝动态目录扫描和 `reload_dynamic_router`。

G5 的“全仓”含义是跨模块依赖、数据所有权和装配纪律已经成立；完整的无框架用例层先由 ticket 验证，之后新增/实质修改的模块执行 ticket 评审确认的模式。G5 通过不能表述为“所有存量 service 已完成 Clean Architecture 重构”。

以下是目标命令，不代表当前工作区已经具备对应实现。Phase 1 必须先落地 `lint-imports` 前置；Phase 2 必须实现其余架构命令并实际运行，不能只保留自然语言门槛。当前只有 `pnpm run build` 已存在，`pnpm run lint:check` 已新增但仍需运行基线证据。

```powershell
cd backend
uv run lint-imports
uv run python -m app.host.manifest_check --emit bill-of-modules.json
uv run pytest tests/architecture tests/modules

cd ..\frontend\web
pnpm run lint:check
pnpm run check:module-manifests
pnpm run build
```

| 目标命令 | 落地阶段 | 阻断条件 |
| --- | --- | --- |
| `uv run lint-imports` | Phase 1 | 新增反向依赖、跨模块内部导入或循环依赖 |
| `uv run python -m app.host.manifest_check --emit bill-of-modules.json` | Phase 2 | Schema/版本/依赖/循环/hash 校验失败 |
| `uv run pytest tests/architecture tests/modules` | Phase 2 | 装配顺序、停用断言、用例隔离、Port/Adapter 行为或数据所有权契约失败 |
| `pnpm run lint:check` | Phase 1 | 不自动修改源码的 ESLint/Prettier/Stylelint 检查失败 |
| `pnpm run check:module-manifests` | Phase 2 | 权限编码或 `component_path` 与构建入口不一致 |
| `pnpm run build` | 已存在，Phase 0 建基线 | 类型检查或 Vite 构建失败 |

## G6：业务样板

首个真实业务模块必须同时交付：

- 数据迁移、接口、页面、菜单和权限编码。
- 无框架用例测试、真实 Adapter/数据库集成测试、权限负向测试、跨租户测试和审计记录。
- 构建、容器 smoke、升级与回滚说明。

只有 G0-G5 通过后，G6 才能被视为平台扩展能力证明。
