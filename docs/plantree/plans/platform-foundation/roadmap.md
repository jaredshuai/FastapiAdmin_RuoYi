# 平台底座路线图

状态：In Progress

## Done

- 建立独立仓库 `FastapiAdmin_RuoYi`，基线提交与原项目一致：`1966c53`。
- 完成当前代码结构、权限链路、租户过滤、测试形态和交付配置评估。
- 接受“RuoYi-Vue-Plus 是能力参考，不做全量 FastAPI 翻译”的战略方向。
- 建立规划入口、基线、风险清单、阶段门槛和未决问题。
- 完成 Phase 0 首次提交：固定参考 submodule，闭合前端生成顺序，并落地忽略、环境示例和只读检查策略。
- 固定 Python、uv、Node、pnpm、MySQL、Redis 和 Nginx 版本，解决 Windows 误选 LibreOffice Python 的问题。
- 建立根目录 backend/frontend/compose 三任务质量工作流，并完成首轮本地基线记录。

## In Progress

- Phase 0 可重复基线：处理 3 项后端测试失败，取得 GitHub Actions 运行证据并关闭 G0-G1。

## Next

### Phase 0：可重复基线

交付：

- 固定本地与 CI 工具版本，建立一键安装和启动说明。
- 使用 `pnpm run gen:auto-imports` 修复前端自动导入产物的干净检出顺序，并由 `type-check`、`lint:check` 和 `build` 显式前置调用；CI 必须证明门槛不依赖开发者曾运行过 Vite。
- 在干净环境运行后端测试、前端类型检查/测试/构建和 Compose 配置校验。
- 记录失败基线，不为追求全绿而降低断言。
- 建立根目录非破坏性 CI 骨架。

退出条件：满足[测试门槛 G0-G1](../../baseline/test-and-release-gates.md)。

### Phase 1：安全与生产硬化

交付：

- 修复权限通配符、超级管理员判定和管理员专属服务保护不一致。
- 增加未登录、无权限、停用角色、套餐收缩、跨租户读写测试。
- 修复环境选择顺序、默认密钥、CORS、调试和文档生产配置。
- 使后端镜像自包含，完成生产 Compose 和 HTTP smoke。
- 建立 schema-only Alembic 基线迁移：空库从零升级到 `head` 后与 ORM 元数据做结构对比；现有库先备份并证明结构与基线等价，等价时才执行 `alembic stamp head`，不等价时编写显式修复迁移。把 JSON 种子迁到独立 seed 命令，生产启动不再依赖 `metadata.create_all`，种子也不进入版本迁移。
- 把 `import-linter` 或等价工具加入 `pyproject.toml`，提交可审查的契约配置，记录当前反向依赖和跨模块内部导入基线，并在 CI 中先阻止新增违规；Phase 2 关闭存量违规后转为严格门槛。
- 为现有 `plugin.toml` 定义含 `manifest_schema_version` 的第一版 Pydantic 清单模型和 JSON Schema，明确新清单为权威、旧 TOML 仅作告警式降级读取，使 Phase 2 的装配器从可执行契约开始。
- 提供前端只读 `lint:check`，CI 只调用不含 `--fix` 或 `--write` 的检查脚本。

退出条件：无已知 P0，满足 G2-G4，所有安全修复具有负向测试。

### Phase 2：平台内核与模块接口

交付：

- 固化菜单、操作/API、数据范围、租户套餐四层权限模型和编码规范。
- 建立应用装配层、平台内核、必选基础设施、可选公共能力、业务模块和独立扩展的物理结构；先迁移一个参考模块验证，不做一次性全量改名。
- 定义机器可校验的模块清单：身份、版本、直接依赖、公开接口、Router、迁移、权限、菜单、事件、任务、前端入口和验证命令。
- 迁移现有 `plugin.toml` 到统一清单 Schema；兼容期新清单为权威，旧 TOML 仅在新清单不存在时降级读取并告警。
- 实现发布时模块装配：启动时校验依赖闭包、版本和循环依赖，并按稳定顺序注册迁移、Router、事件和任务。
- 拆除 `init_app.py` lifespan/Router/WebSocket、`scripts/initialize.py` 模型导入、全局事件和任务中的逐模块硬编码，改由清单 hook 和唯一组合根装配。
- 反转 `core/dependencies.py` 对用户/角色 ORM 和 `PackageService` 的直接依赖，由内核拥有窄接口、身份与套餐模块提供 Adapter。
- 按已形成的产品决策保留或下线插件能力目录及租户授权 API；无论产品选择如何，都用显式清单替代生产目录扫描并移除 `reload_dynamic_router` 的生产依赖。
- 把文件、消息、邮件、任务等复用能力建设为可选择的深模块，防止 `core` 或 `common` 成为代码收容区。
- 明确跨模块同步调用采用“调用方 Required Port + 边界 Adapter + 提供方公开接口”，平台内核只拥有跨业务稳定 Port；建立禁止反向依赖、同步循环和跨模块内部导入的 CI 检查。
- 生成前端组件路径和权限编码清单，与后端菜单种子、模块清单及 `ComponentLoader` 可加载组件集合做构建期校验。
- 先以 `module_system/ticket` 作为参考模块，验证清单装配、身份 Port、租户隔离、状态流转、审计以及前后端一致性；同时建立不依赖 FastAPI/SQLAlchemy 的用例层、窄 `TicketRepository` Port、SQLAlchemy Adapter 和内存 Fake，以分层测试验证其价值。
- 用 ticket 的实际清单样板区分 Router、真实 Provided Interface 与内部 use case；无真实同步调用者时显式声明无 Provided Interface，不为填充清单制造公开服务。
- 建立全仓跨模块模型导入、裸 SQL 和写表清单，G5 前清零跨模块写入；只访问本模块数据的存量混合 service 继续作为显式迁移债务，不要求在 Phase 2 全量重写。
- 记录 ticket 切片的抽象成本、测试速度、事务清晰度和需求改动范围；只把有证据的结构固化为模块生成器或脚手架，不默认全平台复制 Repository/Fake 模式。

退出条件：新增、停用和移除参考模块时平台内核无需修改；非法依赖、循环依赖和不完整清单会被自动拒绝，已知或检查发现的跨模块写入已经清零；ticket 主要用例可使用 Fake Port 在无 Web、数据库和缓存的环境中运行，真实 SQLAlchemy Adapter 另有契约与集成测试；ticket 清单明确公开/内部边界；后端、前端、迁移、权限、事件和任务装配结果一致，并满足[模块架构门槛 G5](../../baseline/test-and-release-gates.md)。G5 不代表所有存量 service 已完成内部用例分层。

### Phase 3：首个真实业务样板

交付：

- 选择一个真实公司需求，先建立业务术语、状态流转和数据所有权。
- 完成数据库迁移、接口、页面、权限、审计、测试和部署。
- 验证不同角色页面可见性、后端拒绝、数据范围和租户边界一致。
- 把样板中发现的通用能力回收到平台接口，而不是复制到下一个页面。

退出条件：满足 G6，并形成第二个业务模块可以复用的模板。

### Phase 4：按需吸收 RuoYi 能力

按业务价值逐项评估字典/参数、文件、消息、任务、幂等、代码生成、SSO、工作流等能力。每项都经过“采用、适配、推迟或拒绝”决策，不做功能数量竞赛。

### Phase 5：运营与规模化

补齐可观测性、备份恢复、容量基线、性能测试、发布回滚和安全响应。只有出现明确的团队、负载、故障隔离或独立部署边界时才评估拆分服务。

## Deferred

- 全量工作流平台和低代码设计器。
- 同时支持多种关系数据库运行。
- 移动端、H5 和小程序补齐。
- 微服务、服务网格和分布式事务。
- 与 RuoYi-Vue-Plus 的 API 或数据库结构兼容。
