# FastapiAdmin_RuoYi 规划树

最后核对：2026-07-17，代码基线提交 `1966c53d2f19cd5e194836cabd913556ccc97b67`

## 目的

这里是项目唯一的长期规划入口。项目以 FastAPI + Vue 为实现技术栈，把 RuoYi-Vue-Plus 作为企业平台能力、业务规则和验收场景的参考项目，而不是待翻译的 Java 源码。

## 权威顺序

当文档之间出现差异时，按下面的职责判断：

1. 当前行为以已核对的代码、数据库迁移和可复现测试结果为准。
2. 目标方向以已接受的决策记录为准。
3. 工作顺序和阶段状态以目标计划的 `roadmap.md` 为准。
4. 方案细节以计划主题文档为准；未决定事项保留在 `open-questions.md`。

规划文档不能代替测试证据，也不能把“已有代码”直接等同于“可生产使用”。

## 项目基线

- [基线入口](baseline/README.md)
- [当前模块地图](baseline/module-map.md)
- [关键运行链路](baseline/runtime-flows.md)
- [存储与状态边界](baseline/storage-and-state.md)
- [测试与发布门槛](baseline/test-and-release-gates.md)
- [风险热点](baseline/risk-hotspots.md)

## 活跃计划

| Plan | Status | Current Phase | Last Landed | Next Target |
| --- | --- | --- | --- | --- |
| [平台底座建设](plans/platform-foundation/README.md) | In Progress | Phase 0 可重复基线 | 本地 G0-G1 全绿（2026-07-17） | 取得远端 CI 证据并关闭 Phase 0 |

## 阅读路径

1. 新加入项目：先读[基线入口](baseline/README.md)。
2. 判断为什么这样建设：读[RuoYi 参考决策](plans/platform-foundation/decisions/001-use-ruoyi-as-reference.md)和[模块装配决策](plans/platform-foundation/decisions/002-release-time-module-assembly.md)。
3. 准备执行：读[计划入口](plans/platform-foundation/README.md)和[路线图](plans/platform-foundation/roadmap.md)。
4. 实现某项能力：再读对应主题和[未决问题](plans/platform-foundation/open-questions.md)。

## 维护规则

- 人类阅读的自然语言使用中文；命令、路径、权限编码和机器标识保持精确。
- 只在证据存在时把路线图事项标为 Done。
- 实现过程中发现新的架构约束，应先更新计划或决策，避免形成无记录的隐性规则。
- 低承诺想法放入[想法收件箱](ideas/inbox.md)，进入路线图后再视为承诺。
