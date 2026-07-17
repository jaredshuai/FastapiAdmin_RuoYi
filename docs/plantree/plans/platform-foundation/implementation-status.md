# 平台底座实施状态

状态：In Progress

## Current Phase

Phase 0：可重复基线。

## Last Landed

- 代码基线：`1966c53`。
- 2026-07-17：本次提交落地规划树、固定版本参考 submodule、前端生成/只读检查、忽略与环境策略及清单前身链接。

## Next Target

建立根目录非破坏性 CI，在干净检出中重复执行后端、前端和 Compose 基线命令。

## Active TODO

1. 固定 Python、uv、Node、pnpm、MySQL 和 Redis 版本。
2. 建立根目录 CI，设置 `HUSKY=0`，断言 `pnpm --version` 为 `9.15.3`，并运行前后端只读检查。
3. 运行后端测试、前端测试和 Compose 配置校验，记录失败基线。
4. 关闭 G0-G1 后进入 Phase 1 安全与生产硬化。

## Blocked By

- 当前没有阻止 Phase 0 执行的架构决策。
- G0-G1 尚未通过，Phase 1 不能宣称完成准入。
- [Phase 2 未决问题](open-questions.md)不阻止 Phase 0，但必须在 Phase 2 前关闭。

## Known Carryover

- ticket 是 Phase 2 首个完整用例/Repository/Fake 验证切片；其他存量 `*Service` 仍可能混合用例、持久化和框架职责。ticket 通过不等于全平台内部用例层已经迁移。
- 存量 service 暂时持有 `AsyncSession` 只代表内部重构尚未完成，不授权跨模块写表。Phase 2 必须建立全仓跨模块模型导入、裸 SQL 和写表清单并清零跨模块写入；只访问本模块表的混合 service 可作为后续逐模块迁移项保留。

## Last Verified

2026-07-17：在不含依赖、构建目录和三个忽略生成物的隔离前端副本中，设置 `HUSKY=0` 后，`pnpm install --frozen-lockfile`、`pnpm run lint:check`、`pnpm run build` 依次通过；`gen:auto-imports` 从 422 个源码文件生成声明。另以明确的 `pnpm@9.15.3` 再次执行冻结安装并通过，确认现有 `pnpm.overrides` 与锁文件匹配；本机全局 pnpm 11 启动器的迁移告警不应驱动仓库在升级包管理器前搬迁配置。G0 仍等待根目录 CI、后端、测试和 Compose 基线。

2026-07-17 首次提交预检：`.codegraph/`、`.commandcode/`、Python 缓存、虚拟环境和本地环境文件已纳入忽略；`backend/uv.lock` 保持跟踪。两个 reference submodule 的索引 gitlink、工作树 HEAD 与远端发布标签提交一致。前端生成物继续忽略并由检查/构建前置生成；Docker 本地 `.env` 退出索引并由安全 example 取代，已提交的 `VITE_*` 文件只作为客户端可见构建配置。
