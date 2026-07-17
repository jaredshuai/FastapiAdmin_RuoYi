# Phase 0 验证记录（2026-07-17）

状态：G0-G1 已通过本地与 GitHub Actions 验证

验证基于工具链提交 `6ece7461`、后端基线修复提交 `5781838a` 和 CI 兼容修复提交 `af725e32`。以下只记录实际执行结果，不把镜像构建或 HTTP smoke 记为通过。

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
| `uv run --project backend --managed-python ruff check --no-fix .` | 通过 | `All checks passed!` |
| `uv run --project backend --managed-python pytest` | 通过 | 收集 265 项：265 通过、1 warning，耗时 42.02 秒 |
| `pnpm install --frozen-lockfile` | 通过 | 锁文件最新，`HUSKY=0` 跳过 hook 安装 |
| `pnpm run lint:check` | 通过 | ESLint、Prettier、Stylelint 均为只读检查并通过 |
| `pnpm run test` | 通过 | 1 个测试文件、3 个测试全部通过 |
| `pnpm run build` | 通过 | 类型检查通过，Vite 转换 4384 个模块并完成生产构建 |
| `docker compose ... config --quiet` | 通过 | `docker/.env.example` 与示例 Compose 可解析 |
| 根工作流结构与格式 | 通过 | YAML 可解析为 backend/frontend/compose 3 个 job，Prettier 通过 |

## 远端验证

- GitHub Actions 首次[运行 #29587066550](https://github.com/jaredshuai/FastapiAdmin_RuoYi/actions/runs/29587066550) 暴露 `uv --version` 包含提交哈希和平台信息，整行精确比较导致后端在版本断言处失败。工作流改为解析第二列版本号，并在本地 Git Bash 验证该断言。
- 修正后的[运行 #29587268152](https://github.com/jaredshuai/FastapiAdmin_RuoYi/actions/runs/29587268152) 在提交 `af725e32` 上通过：backend 1 分 4 秒、frontend 2 分 31 秒、compose 7 秒；三个 job 的冻结安装、只读检查、测试、构建或配置解析及工作区洁净检查全部成功。

## 已修正的后端失败基线

1. `TestHealth.test_health_ready` 和 `test_check_readiness` 曾确定性返回 503。`DependencyStatus.status` 的类型是整数 `0/1`，旧汇总逻辑却与字符串 `"up"/"disabled"` 比较，导致 `all_ok` 恒为 `False`。现已按整数契约以 `status == 1` 判断，两个公开 HTTP 用例通过。
2. `TestOrder.test_order_detail` 曾把 `/platform/order/detail/1` 的业务 404 误判为路由未注册。实际路由存在，404 原因是测试数据库没有订单 `id=1`。测试现改为查询明确不存在的订单，断言 HTTP 404 和统一响应中的 `msg="订单不存在"`，不再依赖虚假种子，也能区分业务 404 与框架默认的路由 404。

Windows 默认 GBK 控制台曾使包含 emoji 的 Loguru 输出出现 `UnicodeEncodeError` 噪声。完整复测显式设置 `PYTHONUTF8=1` 后未再出现该噪声；根目录 CI 使用同一设置。

## 门槛结论

- 工具链固定、冻结安装、后端 265 项测试与只读静态检查、前端检查/3 项测试/构建和 Compose 解析均已有本地通过证据。
- 根目录 CI 的 backend、frontend、compose 三个 job 已在 GitHub Actions 对提交 `af725e32` 全部通过。
- G0-G1 正式关闭，Phase 0 完成；后续工作进入 Phase 1。
- 镜像拉取、后端镜像构建、容器健康检查与 HTTP smoke 属于 G4，本记录未验证。
