# 平台底座实施状态

状态：In Progress

## Current Phase

Phase 1：安全与生产硬化。

## Last Landed

- 代码基线：`1966c53`。
- 2026-07-17：本次提交落地规划树、固定版本参考 submodule、前端生成/只读检查、忽略与环境策略及清单前身链接。
- 2026-07-17：工具链提交 `6ece7461` 固定 Python 3.12.13、uv 0.11.15、Node 24.15.0、pnpm 9.15.3 及 Compose 镜像补丁版本。
- 2026-07-17：根目录质量工作流覆盖后端、前端和 Compose，原子项目内无效工作流退出；本地基线结果已记录。
- 2026-07-17：修复 readiness 整数状态与字符串判断不兼容，并把订单详情用例改为验证不存在资源的明确业务 404；本地 265 项后端测试全部通过。
- 2026-07-17：修复 GitHub runner 上 `uv --version` 扩展输出导致的断言失败；[远端运行 #29587268152](https://github.com/jaredshuai/FastapiAdmin_RuoYi/actions/runs/29587268152) 的 backend、frontend、compose 三个 job 全绿，G0-G1 与 Phase 0 正式关闭。

## Next Target

完成草稿 PR #1 的评审与合并；随后用真实上一发布版本数据库副本完成 G3 升级与恢复演练。

## Active TODO

1. 评审并合并[草稿 PR #1](https://github.com/jaredshuai/FastapiAdmin_RuoYi/pull/1)。
2. 在真实旧库副本上演练备份、结构比较、受控 stamp、upgrade 和恢复，补齐 G3 证据。

## Blocked By

- 当前没有阻止 Phase 1 执行的架构决策。
- 当前没有阻止 Phase 1 启动的发布门槛；G2-G4 尚未通过，不能宣称 Phase 1 完成。
- [Phase 2 未决问题](open-questions.md)不阻止 Phase 1，但必须在 Phase 2 前关闭。

## Known Carryover

- ticket 是 Phase 2 首个完整用例/Repository/Fake 验证切片；其他存量 `*Service` 仍可能混合用例、持久化和框架职责。ticket 通过不等于全平台内部用例层已经迁移。
- 存量 service 暂时持有 `AsyncSession` 只代表内部重构尚未完成，不授权跨模块写表。Phase 2 必须建立全仓跨模块模型导入、裸 SQL 和写表清单并清零跨模块写入；只访问本模块表的混合 service 可作为后续逐模块迁移项保留。

## Last Verified

2026-07-18：Phase 1 审计修正已提交至[草稿 PR #1](https://github.com/jaredshuai/FastapiAdmin_RuoYi/pull/1)，首轮 GitHub Actions [运行 #29635091044](https://github.com/jaredshuai/FastapiAdmin_RuoYi/actions/runs/29635091044) 的后端、前端与 Compose 三个 job 全绿。本地后端为 `319 passed, 1 warning`，import-linter 存量冻结基线为 3 kept/0 broken；已消除 HTTP 测试假绿，生产配置、Alembic 基线/存量库保护、容器自包含、跨租户拒绝与超管规则均有对应证据。真实上一发布版本数据库恢复演练和 G5 严格边界仍待完成。详见[Phase 1 验证记录](../../baseline/verification-2026-07-18-phase1.md)。

2026-07-17：uv 托管 Python 3.12.13 与 107 个冻结依赖安装成功；Ruff 只读检查通过；pytest 收集 265 项并全部通过。Node 24.15.0 与 pnpm 9.15.3 下，前端冻结安装、只读 lint、3 项 Vitest、类型检查和生产构建通过；Compose 配置解析通过。GitHub Actions [运行 #29587268152](https://github.com/jaredshuai/FastapiAdmin_RuoYi/actions/runs/29587268152) 的 3 个 job 全绿。完整证据与已修正失败见[验证记录](../../baseline/verification-2026-07-17.md)。

2026-07-17 首次提交预检：`.codegraph/`、`.commandcode/`、Python 缓存、虚拟环境和本地环境文件已纳入忽略；`backend/uv.lock` 保持跟踪。两个 reference submodule 的索引 gitlink、工作树 HEAD 与远端发布标签提交一致。前端生成物继续忽略并由检查/构建前置生成；Docker 本地 `.env` 退出索引并由安全 example 取代，已提交的 `VITE_*` 文件只作为客户端可见构建配置。
