# 用例与 Port 边界

角色：Phase 2 参考模块的实现约束

状态：采用为 `module_system/ticket` 验证假设；通过参考模块证据后再决定是否推广

## 目的

目标架构已经定义模块级边界，但现有 `controller/service/crud/model/schema` 结构仍可能让 `service` 同时承担用例编排、数据库访问和框架集成。Phase 2 不直接重写所有模块，而是先用 `ticket` 验证一条更清晰、可测试的内部边界。

基于提交 `1966c53` 的当前 ticket 代码：`TicketService` 同时导入 SQLAlchemy `select`、用户 `UserModel`、`TicketCRUD` 和 HTTP/Pydantic 输出 Schema，并通过 `auth.db` 执行用户查询；状态转换及操作者规则也位于同一类中。`TicketModel.assigned_by` 直接 relationship 到用户模型，当前代码索引未找到 `TicketService`/`TicketCRUD` 的直接覆盖测试。这正好构成参考切片需要拆开的真实 seam，而不是为了套用目录模板制造的抽象。

## 接口与边界类型的所有权

不能把所有 Port 都放进平台内核，也不能让提供方反向依赖调用方实现。按用途区分：

| 类型 | 所有者 | 作用 |
| --- | --- | --- |
| 平台稳定 Port | 平台内核 | 身份上下文、租户权益、审计、时钟等跨业务稳定策略 |
| 模块 Required Port | 发起用例的调用方模块 | 表达该用例需要的数据或外部能力，方法按用例收窄 |
| 模块 Provided Interface | 能力提供方模块 | 对其他模块公开稳定能力、错误语义和事务约束 |
| 边界 Adapter | 调用方的 Adapter 层或独立集成 Adapter | 实现调用方 Required Port，并转调提供方 Provided Interface |

默认同步协作链路：

```text
consumer application/use_case
  -> consumer application/ports/RequiredPort
  <- consumer adapters/outbound/ProviderAdapter
  -> provider interfaces/ProvidedInterface
  -> provider application/use_case
```

因此：

- 调用方的领域与用例代码不导入提供方模块。
- 提供方不导入调用方的 Port；Adapter 位于调用方边界或明确的集成包。
- Adapter 对提供方公开接口的依赖必须写入模块清单的直接依赖。
- 只有跨业务稳定且确实由平台策略使用的接口进入 `core`；不能为了消除模块依赖图中的边而把业务协作接口上提到内核。
- 若两个模块形成同步双向依赖，不允许用两个互相导入的 Adapter 掩盖循环。必须选择合并边界、引入拥有该流程的第三个编排模块、改为事件协作，或重新划分数据所有权，并由清单 DAG 检查拒绝未解决的循环。

## 模块内部用例边界

`ticket` 参考模块采用以下逻辑角色；最终目录名可以根据 Python 实践调整，但依赖方向不能反转：

```text
ticket/
  domain/                 # 业务实体、值对象和纯规则；不依赖 FastAPI/SQLAlchemy
  application/
    use_cases/            # 用例编排；依赖 domain、Required Port 和稳定 core Port
    ports/                # 用例需要的 Repository、身份或外部能力接口
  interfaces/             # 提供给其他模块的公开接口与契约
  adapters/
    inbound/http/         # FastAPI Router、请求/响应映射
    outbound/persistence/ # SQLAlchemy Repository、ORM 映射
```

迁移期允许其他模块继续保留现有文件名，但不把现有命名直接当成目标边界：

- `controller` 对应入站 Adapter，只负责协议、校验和结果映射。
- `service` 只有在不持有 FastAPI 对象、`AsyncSession`、ORM Model 或具体 CRUD 时，才视为用例层；混合职责的旧 service 作为待迁移事实登记。
- `crud/model` 属于持久化 Adapter 内部实现，不作为跨模块接口。
- `schema` 需要区分 HTTP DTO 与用例 Command/Result；用例契约优先使用标准 Python 类型、`dataclass` 或 `Protocol`，不携带 FastAPI/ORM 语义。
- 模块清单只声明公开接口、依赖和验证入口，不枚举内部类或方法；内部边界由导入检查和测试证明，避免清单变成实现细节索引。

## Ticket 验证切片

首轮只验证真实需要，不建设通用 Repository 框架：

1. 在 ticket 用例侧定义窄的 `TicketRepository` Port，只包含当前状态流转、查询和保存用例实际需要的操作。
2. SQLAlchemy Adapter 实现该 Port；只有该 Adapter 接收 `AsyncSession` 并访问 ticket 拥有的表。
3. ticket 用例依赖 `TicketRepository`、最小 `UserIdentityPort` 和必要的稳定上下文，不导入 FastAPI、SQLAlchemy、用户 ORM 或具体 CRUD。
4. 测试提供内存 Fake `TicketRepository`；Fake 与 SQLAlchemy Adapter 共享能够适用的 Port 行为契约，数据库约束和查询语义另由真实数据库集成测试验证。
5. 记录新增抽象数量、用例测试运行时间、事务表达是否更清楚以及新增需求的改动范围，再决定 Repository/Fake 模式是否推广到其他模块。

不在本切片中建设泛型 CRUD Repository、全平台 Unit of Work、完整账户 Port、伪造领域事件或伪造定时任务。

## Ticket 清单样板

ticket 切片完成时必须提交一份通过实际 Schema 校验的清单样板，用真实字段区分三类入口：

- HTTP Router 是入站协议入口，登记在 Router 入口中。
- 只有存在真实跨模块同步调用者时，才在 Provided Interface 声明中登记稳定 facade、版本、错误/事务语义和契约测试入口；没有调用者时显式声明为空，不为填字段制造公开服务。
- 内部 use case、`TicketRepository`、SQLAlchemy Adapter、Fake、Controller 和 CRUD 不进入 Provided Interface 清单。

清单测试必须证明公开入口可以解析、缺失契约时失败，并证明内部 use case 重命名不会导致清单变化。该样板用于回答“什么是公开接口”，但不把 ticket 的具体方法复制成所有模块的固定 API。

## 测试分层

发布门槛与测试层次是两个正交维度。`ticket` 至少提供：

1. 领域/用例测试：使用 Fake Port，不启动 FastAPI，不连接 MySQL/Redis，不导入 SQLAlchemy。
2. Port/Adapter 契约测试：验证 Fake 与 SQLAlchemy Adapter 共有的行为、错误模式和租户边界。
3. 持久化集成测试：使用真实测试数据库验证迁移、约束、事务和租户过滤。
4. HTTP/权限集成测试：验证身份、权限、状态码、序列化和跨租户拒绝。
5. 装配 smoke：验证清单、Router、菜单、权限和前端入口属于同一模块版本集合。

Phase 1 的安全修复仍可使用现有集成测试闭合真实 FastAPI 依赖链；不为追求“纯用例测试”提前扩大重构范围。Phase 2 以 ticket 证据决定后续推广，不把 Clean Architecture 的目录形式本身当作验收结果。

## 验收条件

- ticket 的主要状态流转可在无 Web、数据库和缓存的进程内测试。
- ticket 用例代码不能导入 FastAPI、SQLAlchemy、ORM Model 或具体 CRUD。
- SQLAlchemy Adapter 只能写 ticket 拥有的表，跨模块信息通过公开接口或 Port 获取。
- 跨模块同步依赖方向无环，调用方 Port、提供方接口和 Adapter 的所有权可从代码与清单同时识别。
- Fake 与真实 Adapter 的共有行为契约通过，数据库专属行为有独立集成测试。
- ticket 清单用实际 Schema 展示 Router、Provided Interface 和内部 use case 的边界；没有真实同步调用者时不制造 Provided Interface。
- 完成参考切片后形成“推广、调整或拒绝 Repository/Fake 模式”的明确结论，不默认全平台复制。
