import os
import sys
from typing import Annotated

import typer
import uvicorn
from fastapi import FastAPI

from alembic import command
from app.common.enums import EnvironmentEnum
from app.config.alembic_conf import get_alembic_config

fastapiadmin_cli = typer.Typer()
alembic_cfg = get_alembic_config()


def _assert_database_environment(target: EnvironmentEnum) -> None:
    """数据库模块一旦初始化，当前进程就不能再切换运行环境。"""
    database_module = sys.modules.get("app.core.database")
    if database_module is None:
        return
    initialized = getattr(database_module, "DATABASE_ENVIRONMENT", None)
    if initialized is not None and initialized != target:
        initialized_value = getattr(initialized, "value", str(initialized))
        raise RuntimeError(
            "数据库 Engine 已按 "
            f"{initialized_value} 环境初始化，不能在同一进程切换到 {target.value}；"
            "请以目标 ENVIRONMENT 启动新进程。"
        )


def create_app() -> FastAPI:
    """
    创建 FastAPI 应用实例并完成日志、中间件、路由与静态资源注册。

    返回:
    - FastAPI: 已配置生命周期的应用对象。
    """
    # 延迟导入 settings：只有 ENVIRONMENT 已确定后才加载对应环境配置
    from app.config.setting import get_settings
    from app.init_app import (
        lifespan,
        register_exceptions,
        register_files,
        register_middlewares,
        register_routers,
        reset_api_docs,
    )

    # 配置校验：生产环境必须满足安全底线
    runtime_settings = get_settings()
    _assert_database_environment(runtime_settings.ENVIRONMENT)
    runtime_settings.validate_runtime_config()

    # 创建FastAPI应用
    app = FastAPI(**runtime_settings.FASTAPI_CONFIG, lifespan=lifespan)
    # 注册异常处理器
    register_exceptions(app)
    # 注册中间件
    register_middlewares(app)
    # 注册路由
    register_routers(app)
    # 注册静态文件
    register_files(app)
    # 重设API文档
    reset_api_docs(app)
    return app


@fastapiadmin_cli.command(
    name="config-check",
    help="只校验指定环境的运行时配置，不连接数据库或启动服务",
)
def config_check(
    env: Annotated[
        EnvironmentEnum, typer.Option("--env", help="运行环境 (dev, prod)")
    ] = EnvironmentEnum.DEV,
) -> None:
    """在迁移和启动前验证密钥、文档与 CORS 安全约束。"""
    os.environ["ENVIRONMENT"] = env.value
    from app.config.setting import get_settings

    get_settings.cache_clear()
    try:
        get_settings().validate_runtime_config()
    except RuntimeError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from None
    typer.echo(f"{env.value} 环境配置校验通过。")


# typer.Option是非必填；typer.Argument是必填
@fastapiadmin_cli.command(
    name="run",
    help="启动 FastapiAdmin 服务, 运行 uv run main.py run --env=dev 不加参数默认 dev 环境",
)
def run(
    env: Annotated[
        EnvironmentEnum, typer.Option("--env", help="运行环境 (dev, prod)")
    ] = EnvironmentEnum.DEV,
) -> None:
    """
    按指定环境加载配置并启动 Uvicorn（开发环境开启 reload）。

    参数:
    - env (EnvironmentEnum): 运行环境，对应 `--env`。

    返回:
    - None
    """

    # 设置环境变量（必须在 import settings 之前，确保加载正确环境）
    os.environ["ENVIRONMENT"] = env.value

    # 延迟导入：仅在 ENVIRONMENT 锁定后加载对应环境配置
    from app.config.setting import get_settings

    # 清除可能存在的旧缓存，强制按当前 ENVIRONMENT 重新读取
    get_settings.cache_clear()
    runtime_settings = get_settings()
    _assert_database_environment(runtime_settings.ENVIRONMENT)

    # logger 会读取运行时配置，必须在环境和 Settings 缓存确定后导入。
    from app.core.logger import logger
    from app.utils.banner import worship

    typer.secho(
        message="FastapiAdmin 服务启动",
        fg=typer.colors.GREEN,
    )
    logger.info(worship(env.value))

    # 启动uvicorn服务
    uvicorn.run(
        app="main:create_app",
        host=runtime_settings.SERVER_HOST,
        port=runtime_settings.SERVER_PORT,
        reload=env.value == EnvironmentEnum.DEV.value,
        factory=True,
        log_config=None,
    )


@fastapiadmin_cli.command(
    name="revision",
    help="生成新的 Alembic 迁移脚本, 运行 python main.py revision --env=dev",
)
def revision(
    env: Annotated[
        EnvironmentEnum, typer.Option("--env", help="运行环境 (dev, prod)")
    ] = EnvironmentEnum.DEV,
) -> None:
    """
    使用 Alembic 自动生成迁移脚本（autogenerate）。

    参数:
    - env (EnvironmentEnum): 运行环境，用于加载对应数据库模型元数据。

    返回:
    - None
    """
    os.environ["ENVIRONMENT"] = env.value
    from app.config.setting import get_settings

    get_settings.cache_clear()
    runtime_settings = get_settings()
    _assert_database_environment(runtime_settings.ENVIRONMENT)
    command.revision(alembic_cfg, autogenerate=True, message="迁移脚本")
    typer.echo("迁移脚本已生成")


@fastapiadmin_cli.command(
    name="upgrade",
    help="应用最新的 Alembic 迁移, 运行 python main.py upgrade --env=dev",
)
def upgrade(
    env: Annotated[
        EnvironmentEnum, typer.Option("--env", help="运行环境 (dev, prod)")
    ] = EnvironmentEnum.DEV,
) -> None:
    """
    将数据库升级到 Alembic 最新版本（head）。

    参数:
    - env (EnvironmentEnum): 运行环境。

    返回:
    - None
    """
    os.environ["ENVIRONMENT"] = env.value
    from app.config.setting import get_settings

    get_settings.cache_clear()
    runtime_settings = get_settings()
    _assert_database_environment(runtime_settings.ENVIRONMENT)
    runtime_settings.validate_runtime_config()
    from app.scripts.initialize import InitializeData

    InitializeData.assert_migration_state()
    command.upgrade(alembic_cfg, "head")
    typer.echo("所有迁移已应用。")


@fastapiadmin_cli.command(
    name="stamp",
    help="仅在存量库结构与当前模型等价时写入 Alembic 版本标记",
)
def stamp(
    env: Annotated[
        EnvironmentEnum, typer.Option("--env", help="运行环境 (dev, prod)")
    ] = EnvironmentEnum.DEV,
    confirm_schema_equivalent: Annotated[
        bool,
        typer.Option(
            "--confirm-schema-equivalent",
            help="确认已备份；命令仍会自动比较数据库与当前模型结构",
        ),
    ] = False,
) -> None:
    """验证存量数据库结构后，将其登记为 Alembic 基线版本。"""
    if not confirm_schema_equivalent:
        raise typer.BadParameter("必须显式传入 --confirm-schema-equivalent")

    os.environ["ENVIRONMENT"] = env.value
    from app.config.setting import get_settings

    get_settings.cache_clear()
    runtime_settings = get_settings()
    _assert_database_environment(runtime_settings.ENVIRONMENT)
    from app.scripts.initialize import InitializeData

    InitializeData.assert_legacy_schema_equivalent()
    command.stamp(alembic_cfg, "head")
    typer.echo("存量数据库结构校验通过，已写入 Alembic 版本标记。")


@fastapiadmin_cli.command(
    name="seed",
    help="幂等灌入种子数据, 运行 python main.py seed --env=dev",
)
def seed(
    env: Annotated[
        EnvironmentEnum, typer.Option("--env", help="运行环境 (dev, prod)")
    ] = EnvironmentEnum.DEV,
) -> None:
    """
    幂等灌入种子数据：每张表为空时一次性插入，已有数据则跳过。

    应用启动不再自动种子；本命令用于显式初始化或重灌。

    参数:
    - env (EnvironmentEnum): 运行环境。

    返回:
    - None
    """
    import asyncio

    os.environ["ENVIRONMENT"] = env.value
    from app.config.setting import get_settings

    get_settings.cache_clear()
    runtime_settings = get_settings()
    _assert_database_environment(runtime_settings.ENVIRONMENT)

    from app.scripts.initialize import InitializeData

    asyncio.run(InitializeData().seed())
    typer.echo("种子数据已灌入。")


if __name__ == "__main__":
    fastapiadmin_cli()
