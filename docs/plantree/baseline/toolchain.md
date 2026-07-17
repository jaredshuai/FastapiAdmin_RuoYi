# 工具链版本契约

状态：版本已固定；本地与 CI 验证进行中

最后更新：2026-07-17

## 固定版本

| 能力 | 固定版本 | 权威位置 |
| --- | --- | --- |
| Python | `3.12.13` | `backend/.python-version`、`docker/backend/Dockerfile` |
| uv | `0.11.15` | `backend/pyproject.toml` 的 `tool.uv.required-version` |
| Node.js | `24.15.0` | `.node-version`、`frontend/web/package.json` |
| pnpm | `9.15.3` | `frontend/web/package.json` 的 `packageManager` 和 `engines` |
| MySQL | `8.0.43` | `docker/docker-compose-example.yaml` |
| Redis | `7.4.5-alpine` | `docker/docker-compose-example.yaml` |
| Nginx | `1.25.5-alpine` | `docker/docker-compose-example.yaml` |

锁文件是依赖版本契约的一部分：后端提交 `backend/uv.lock`，前端提交 `frontend/web/pnpm-lock.yaml`。安装和 CI 必须使用冻结模式，不允许在验证过程中静默更新锁文件。

## 本地安装与检查

后端只接受 uv 托管的 Python，避免 Windows 上误选 LibreOffice 等软件自带的解释器：

```powershell
uv --version # 必须为 0.11.15
uv python install 3.12.13
uv sync --project backend --frozen
uv run --project backend python --version # 必须为 3.12.13
uv run --project backend ruff check --no-fix .
uv run --project backend pytest
```

前端使用 Corepack 在临时目录创建 shim，并把该目录放到当前 PowerShell 会话的 `PATH` 首位。这样即使机器已经全局安装其他 pnpm，脚本内部递归调用的 `pnpm run` 也仍使用仓库声明的版本：

```powershell
node --version # 必须为 v24.15.0
$corepackBin = Join-Path $env:TEMP "fastapiadmin-corepack"
New-Item -ItemType Directory -Force -Path $corepackBin | Out-Null
corepack enable --install-directory $corepackBin
$env:PATH = "$corepackBin;$env:PATH"
cd frontend\web
$env:HUSKY = "0"
pnpm --version # 必须为 9.15.3
pnpm install --frozen-lockfile
pnpm run lint:check
pnpm run test
pnpm run build
```

Compose 先做不启动服务的解析校验：

```powershell
docker compose --env-file docker/.env.example -f docker/docker-compose-example.yaml config
```

镜像拉取、构建、健康检查和 HTTP smoke 属于 G4；仅通过 Compose 解析不能表述为容器交付通过。

## 变更规则

- 版本升级必须同时修改权威位置、锁文件（如受影响）和根目录 CI。
- Python、uv、Node、pnpm 任一实际版本与契约不一致时，验证直接失败。
- 容器基础镜像使用精确补丁标签；生产制品进入 G4 后再增加 digest 固定和镜像来源审计。
- 不为追求 CI 全绿而放宽版本断言或改用非冻结安装。
