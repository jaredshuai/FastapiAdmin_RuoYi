# 平台底座实施状态

状态：In Progress

## Current Phase

Phase 0：可重复基线。

## Last Landed

- 代码基线：`1966c53`。
- 2026-07-17：本次提交落地规划树、固定版本参考 submodule、前端生成/只读检查、忽略与环境策略及清单前身链接。
- 2026-07-17：工具链提交 `6ece7461` 固定 Python 3.12.13、uv 0.11.15、Node 24.15.0、pnpm 9.15.3 及 Compose 镜像补丁版本。
- 2026-07-17：根目录质量工作流覆盖后端、前端和 Compose，原子项目内无效工作流退出；本地基线结果已记录。
- 2026-07-17：修复 readiness 整数状态与字符串判断不兼容，并把订单详情用例改为验证不存在资源的明确业务 404；本地 265 项后端测试全部通过。

## Next Target

推送当前提交并取得根目录 backend/frontend/compose 三个 job 的绿色证据，随后关闭 G0-G1。

## Active TODO

1. 推送当前提交，用 GitHub Actions 验证 backend/frontend/compose 三个 job。
2. 若远端环境暴露差异，保持门槛不变并修复根因后重跑。
3. 三个 job 全绿后关闭 G0-G1，进入 Phase 1 安全与生产硬化。

## Blocked By

- 当前没有阻止 Phase 0 执行的架构决策。
- G0-G1 尚未通过，Phase 1 不能宣称完成准入。
- [Phase 2 未决问题](open-questions.md)不阻止 Phase 0，但必须在 Phase 2 前关闭。

## Known Carryover

- ticket 是 Phase 2 首个完整用例/Repository/Fake 验证切片；其他存量 `*Service` 仍可能混合用例、持久化和框架职责。ticket 通过不等于全平台内部用例层已经迁移。
- 存量 service 暂时持有 `AsyncSession` 只代表内部重构尚未完成，不授权跨模块写表。Phase 2 必须建立全仓跨模块模型导入、裸 SQL 和写表清单并清零跨模块写入；只访问本模块表的混合 service 可作为后续逐模块迁移项保留。

## Last Verified

2026-07-17：uv 托管 Python 3.12.13 与 107 个冻结依赖安装成功；Ruff 只读检查通过；pytest 收集 265 项并全部通过。Node 24.15.0 与 pnpm 9.15.3 下，前端冻结安装、只读 lint、3 项 Vitest、类型检查和生产构建通过；Compose 配置解析通过。根目录工作流 YAML 可解析为 3 个 job 且通过 Prettier。完整证据与已修正失败见[验证记录](../../baseline/verification-2026-07-17.md)。

2026-07-17 首次提交预检：`.codegraph/`、`.commandcode/`、Python 缓存、虚拟环境和本地环境文件已纳入忽略；`backend/uv.lock` 保持跟踪。两个 reference submodule 的索引 gitlink、工作树 HEAD 与远端发布标签提交一致。前端生成物继续忽略并由检查/构建前置生成；Docker 本地 `.env` 退出索引并由安全 example 取代，已提交的 `VITE_*` 文件只作为客户端可见构建配置。
