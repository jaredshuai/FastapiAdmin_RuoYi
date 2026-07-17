# 平台底座建设计划

状态：In Progress

当前阶段：Phase 0 可重复基线

## 目标

把当前 FastapiAdmin 建设成适合公司长期扩展的模块化平台：账户权限决定页面入口，后端独立保护操作，租户/组织和数据权限限制数据范围，每个业务领域能够在不修改平台内核的前提下持续增加页面和能力。

## 成功标准

- 当前已知 P0/P1 底座风险关闭并有验证证据。
- 权限体系明确区分菜单、操作/API、数据范围和租户套餐。
- 新业务模块通过统一接口接入路由、权限、迁移、审计和前端页面。
- 首个真实业务需求完成端到端交付，且无需修改平台内核中的鉴权、租户和通用数据访问语义。
- 发布过程可重复，包含静态检查、测试、迁移、镜像构建、健康检查和回滚说明。

## 范围

- FastAPI 后端和 Vue Web 前端。
- 账户、组织、角色、菜单、操作权限、数据权限、租户/套餐和审计基础。
- 模块接口、代码生成骨架、测试与发布门槛。
- 以 RuoYi-Vue-Plus 为参考的能力差距管理。
- 一个真实业务模块样板。

## 非目标

- 不逐行翻译 RuoYi-Vue-Plus Java 源码。
- 不追求首期与 RuoYi-Vue-Plus 功能完全一致。
- 不在缺少实际负载、团队或部署边界前拆分微服务。
- 首期不建设运行时模块安装、卸载或热替换；模块变更随发布生效。
- 首期不承诺移动端、低代码平台、复杂工作流和多数据库同时运行。

## 计划文件

- [路线图](roadmap.md)
- [实施状态](implementation-status.md)
- [未决问题](open-questions.md)
- [目标架构](topics/target-architecture.md)
- [用例与 Port 边界](topics/use-case-and-port-boundaries.md)
- [RuoYi 对标方法](topics/ruoyi-benchmarking.md)
- [决策：把 RuoYi 作为参考项目](decisions/001-use-ruoyi-as-reference.md)
- [决策：采用发布时模块装配](decisions/002-release-time-module-assembly.md)
- [项目基线](../../baseline/README.md)

## 进入实现的条件

Phase 0 的实现可以在确认本计划后开始。进入 Phase 2 前，必须关闭[未决问题](open-questions.md)中标为“Phase 2 前必须确认”的事项，并完成 Alembic 基线、架构依赖检查与清单 Schema 的前置建设。任何涉及权限语义、数据所有权或偏离发布时模块装配决策的变化，都要先形成测试和决策记录。
