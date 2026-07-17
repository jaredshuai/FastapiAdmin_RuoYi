# Phase 0 本地验证记录（2026-07-17）

状态：已完成本地基线；存在 3 项后端测试失败，G0-G1 尚未关闭

验证基于工具链提交 `6ece7461` 及同批根目录 CI 工作流。以下只记录实际执行结果，不把未运行的远端 CI、镜像构建或 HTTP smoke 记为通过。

## 环境

| 能力 | 实际版本 |
| --- | --- |
| Python | `3.12.13`，由 uv 托管 |
| uv | `0.11.15` |
| Node.js | `24.15.0` |
| pnpm | `9.15.3` |
| Docker Compose | `v5.3.0` |

## 执行结果

| 验证 | 结果 | 证据摘要 |
| --- | --- | --- |
| `uv python install 3.12.13 --managed-python` | 通过 | 下载并安装 uv 托管的 CPython 3.12.13 |
| `uv sync --project backend --frozen --managed-python` | 通过 | 从 `backend/uv.lock` 安装 107 个包，锁文件未更新 |
| `uv run --project backend ruff check --no-fix .` | 通过 | `All checks passed!` |
| `uv run --project backend pytest` | 失败 | 收集 265 项：262 通过、3 失败、1 warning，耗时 151.36 秒 |
| `pnpm install --frozen-lockfile` | 通过 | 锁文件最新，`HUSKY=0` 跳过 hook 安装 |
| `pnpm run lint:check` | 通过 | ESLint、Prettier、Stylelint 均为只读检查并通过 |
| `pnpm run test` | 通过 | 1 个测试文件、3 个测试全部通过 |
| `pnpm run build` | 通过 | 类型检查通过，Vite 转换 4384 个模块并完成生产构建 |
| `docker compose ... config --quiet` | 通过 | `docker/.env.example` 与示例 Compose 可解析 |
| 根工作流结构与格式 | 通过 | YAML 可解析为 backend/frontend/compose 3 个 job，Prettier 通过 |

## 后端失败基线

1. `TestHealth.test_health_ready`：`GET /common/health/ready` 期望 200，实际 503。
2. `test_check_readiness`：同一 readiness 端点期望 200，实际 503。当前实现用整数 `0/1` 构造 `DependencyStatus.status`，但汇总函数用字符串 `"up"/"disabled"` 判断成功，状态语义不一致。
3. `TestOrder.test_order_detail`：`GET /platform/order/detail/1` 返回 404，测试与实际路由契约不一致。

Windows 默认 GBK 控制台还会使包含 emoji 的 Loguru 输出出现 `UnicodeEncodeError` 噪声，但未形成上述测试失败。根目录 CI 显式设置 `PYTHONUTF8=1`；该设置是否足以消除 Linux/Windows 差异仍须由 CI 和后续本地复测确认。

## 门槛结论

- 工具链固定、冻结安装、后端只读静态检查、前端检查/测试/构建和 Compose 解析已有本地证据。
- 根目录 CI 已落地，但尚未推送并获得 GitHub Actions 运行证据。
- 后端测试仍为红色，因此 G0-G1 不能标记通过，也不能进入 Phase 1 后宣称准入门槛已经关闭。
- 镜像拉取、后端镜像构建、容器健康检查与 HTTP smoke 属于 G4，本记录未验证。
