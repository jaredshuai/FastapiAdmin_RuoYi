"""运行时配置校验测试。

覆盖：
- `Settings.validate_runtime_config()` 的通用约束（SECRET_KEY、CORS 通配符+凭证）。
- 生产环境专属约束（DEBUG=False、DOCS_ENABLE=False、CORS 不含 `*`）。
- 隔离进程验证 `python main.py run --env=prod` 在缺密钥时启动失败。

不依赖 conftest.py 的全局 fixture；使用独立的 Settings 实例避免污染 lru_cache。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.common.enums import EnvironmentEnum
from app.config.setting import Settings

# ============================================================
# 辅助：构造独立 Settings 实例
# ============================================================


def _make_settings(**overrides) -> Settings:
    """构造一个不写入 lru_cache 的独立 Settings 实例。

    参数:
        **overrides: 覆盖默认值的字段。

    返回:
        Settings: 独立实例，validate_runtime_config 可直接调用。
    """
    base = {
        "ENVIRONMENT": EnvironmentEnum.DEV,
        "SECRET_KEY": "real-random-secret-for-testing-only-32bytes",
        "ALLOW_ORIGINS": ["https://test.example.com"],
        "ALLOW_CREDENTIALS": True,
        "DEBUG": False,
        "DOCS_ENABLE": False,
    }
    base.update(overrides)
    return Settings(**base)


# ============================================================
# 通用约束：SECRET_KEY
# ============================================================


class TestSecretKeyValidation:
    """SECRET_KEY 校验：必须由环境变量提供，空值或占位符直接失败。"""

    def test_empty_secret_key_fails(self) -> None:
        settings = _make_settings(SECRET_KEY="")
        with pytest.raises(RuntimeError, match="SECRET_KEY 未设置"):
            settings.validate_runtime_config()

    def test_placeholder_secret_key_fails(self) -> None:
        settings = _make_settings(
            SECRET_KEY="vgb0tnl9d58+6n-6h-ea&u^1#s0ccp!794=krylxcjq75vzps$"
        )
        with pytest.raises(RuntimeError, match="已知不安全占位符"):
            settings.validate_runtime_config()

    def test_change_me_placeholder_fails(self) -> None:
        settings = _make_settings(SECRET_KEY="change-me-to-a-real-secret")
        with pytest.raises(RuntimeError, match="已知不安全占位符"):
            settings.validate_runtime_config()

    def test_real_secret_key_passes(self) -> None:
        settings = _make_settings(
            SECRET_KEY="real-random-secret-for-testing-only-32bytes"
        )
        # 不应抛出异常
        settings.validate_runtime_config()


# ============================================================
# 通用约束：CORS 通配符 + 凭证
# ============================================================


class TestCorsValidation:
    """CORS 校验：ALLOW_ORIGINS=['*'] 与 ALLOW_CREDENTIALS=True 组合禁止。"""

    def test_wildcard_origin_with_credentials_fails(self) -> None:
        settings = _make_settings(
            ALLOW_ORIGINS=["*"],
            ALLOW_CREDENTIALS=True,
        )
        with pytest.raises(RuntimeError, match="ALLOW_ORIGINS=\\['\\*'\\] 与 ALLOW_CREDENTIALS=True"):
            settings.validate_runtime_config()

    def test_wildcard_origin_without_credentials_passes(self) -> None:
        settings = _make_settings(
            ALLOW_ORIGINS=["*"],
            ALLOW_CREDENTIALS=False,
        )
        settings.validate_runtime_config()

    def test_explicit_origin_with_credentials_passes(self) -> None:
        settings = _make_settings(
            ALLOW_ORIGINS=["https://test.example.com"],
            ALLOW_CREDENTIALS=True,
        )
        settings.validate_runtime_config()


# ============================================================
# 生产环境专属约束
# ============================================================


class TestProdEnvironmentValidation:
    """生产环境专属约束：DEBUG=False、DOCS_ENABLE=False、CORS 不含 '*'。"""

    def test_prod_debug_true_fails(self) -> None:
        settings = _make_settings(
            ENVIRONMENT=EnvironmentEnum.PROD,
            DEBUG=True,
        )
        with pytest.raises(RuntimeError, match="生产环境 DEBUG 必须为 False"):
            settings.validate_runtime_config()

    def test_prod_docs_enable_true_fails(self) -> None:
        settings = _make_settings(
            ENVIRONMENT=EnvironmentEnum.PROD,
            DOCS_ENABLE=True,
        )
        with pytest.raises(RuntimeError, match="生产环境 DOCS_ENABLE 必须为 False"):
            settings.validate_runtime_config()

    def test_prod_wildcard_origin_fails(self) -> None:
        settings = _make_settings(
            ENVIRONMENT=EnvironmentEnum.PROD,
            ALLOW_ORIGINS=["*"],
            ALLOW_CREDENTIALS=False,  # 避免触发通用 CORS 约束
        )
        with pytest.raises(RuntimeError, match="生产环境 ALLOW_ORIGINS 不允许包含 '\\*'"):
            settings.validate_runtime_config()

    def test_prod_valid_config_passes(self) -> None:
        settings = _make_settings(
            ENVIRONMENT=EnvironmentEnum.PROD,
            DEBUG=False,
            DOCS_ENABLE=False,
            ALLOW_ORIGINS=["https://prod.example.com"],
            ALLOW_CREDENTIALS=True,
            SECRET_KEY="real-random-secret-for-prod-32bytes-min",
        )
        settings.validate_runtime_config()


# ============================================================
# 隔离进程测试：python main.py run --env=prod
# ============================================================


_BACKEND_DIR = Path(__file__).parent.parent


def _run_main_cli(
    env: str,
    extra_env: dict[str, str] | None = None,
    command: str = "run",
) -> subprocess.CompletedProcess:
    """以子进程方式运行 `python main.py run --env=<env>`，捕获启动期失败。

    参数:
        env: 环境标识（dev/prod）。
        extra_env: 额外环境变量（用于注入或覆盖 SECRET_KEY 等）。
        command: 要执行的 main.py 子命令。

    返回:
        subprocess.CompletedProcess: 包含 returncode、stdout、stderr。
    """
    import os

    env_copy = os.environ.copy()
    env_copy["PYTHONUTF8"] = "1"
    env_copy["ENVIRONMENT"] = env
    if extra_env:
        env_copy.update(extra_env)

    # 使用 timeout 避免成功启动时无限挂起；启动失败会立即返回非零
    return subprocess.run(
        [sys.executable, "main.py", command, f"--env={env}"],
        cwd=str(_BACKEND_DIR),
        env=env_copy,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=15,
    )


class TestProdStartupIsolation:
    """隔离进程验证：生产环境启动链路必须满足安全底线。

    真实环境变量由 .env.prod 提供；此处通过 extra_env 精确控制被测变量，
    确保校验逻辑被独立触发。
    """

    def test_prod_missing_secret_key_fails_fast(self) -> None:
        """生产环境缺 SECRET_KEY 时，create_app() 必须在启动期失败。"""
        result = _run_main_cli(
            "prod",
            extra_env={"SECRET_KEY": ""},
        )
        assert result.returncode != 0, (
            f"缺 SECRET_KEY 时进程不应成功退出，实际 returncode={result.returncode}\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        combined = result.stdout + result.stderr
        assert "SECRET_KEY" in combined, (
            f"失败输出应包含 SECRET_KEY，实际：\n{combined}"
        )

    def test_prod_placeholder_secret_key_fails_fast(self) -> None:
        """生产环境使用占位符 SECRET_KEY 时，必须在启动期失败。"""
        result = _run_main_cli(
            "prod",
            extra_env={"SECRET_KEY": "vgb0tnl9d58+6n-6h-ea&u^1#s0ccp!794=krylxcjq75vzps$"},
        )
        assert result.returncode != 0
        combined = result.stdout + result.stderr
        assert "SECRET_KEY" in combined

    def test_prod_debug_true_fails_fast(self) -> None:
        """生产环境 DEBUG=True 时，必须在启动期失败。"""
        result = _run_main_cli(
            "prod",
            extra_env={
                "SECRET_KEY": "real-random-secret-for-prod-32bytes-min",
                "DEBUG": "True",
            },
        )
        assert result.returncode != 0
        combined = result.stdout + result.stderr
        assert "DEBUG" in combined

    def test_prod_docs_enable_true_fails_fast(self) -> None:
        """生产环境 DOCS_ENABLE=True 时，必须在启动期失败。"""
        result = _run_main_cli(
            "prod",
            extra_env={
                "SECRET_KEY": "real-random-secret-for-prod-32bytes-min",
                "DOCS_ENABLE": "True",
            },
        )
        assert result.returncode != 0
        combined = result.stdout + result.stderr
        assert "DOCS_ENABLE" in combined

    def test_prod_config_check_fails_before_database_access(self) -> None:
        result = _run_main_cli(
            "prod",
            extra_env={"SECRET_KEY": ""},
            command="config-check",
        )
        assert result.returncode != 0
        combined = result.stdout + result.stderr
        assert "SECRET_KEY" in combined
        assert "OperationalError" not in combined

    def test_prod_upgrade_fails_before_database_access(self) -> None:
        """迁移命令也必须先拒绝不安全配置，不能先尝试数据库连接。"""
        result = _run_main_cli(
            "prod",
            extra_env={
                "SECRET_KEY": "",
                "DATABASE_HOST": "database-host-that-must-not-be-contacted.invalid",
            },
            command="upgrade",
        )
        assert result.returncode != 0
        combined = result.stdout + result.stderr
        assert "SECRET_KEY" in combined
        assert "OperationalError" not in combined

    def test_prod_config_check_accepts_valid_environment(self) -> None:
        result = _run_main_cli(
            "prod",
            extra_env={
                "SECRET_KEY": "real-random-secret-for-prod-config-check",
                "DEBUG": "False",
                "DOCS_ENABLE": "False",
                "ALLOW_ORIGINS": '["https://prod.example.com"]',
                "ALLOW_CREDENTIALS": "True",
            },
            command="config-check",
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert "prod 环境配置校验通过" in result.stdout

    def test_prod_env_file_drives_the_same_runtime_settings(
        self, tmp_path: Path
    ) -> None:
        """.env.prod 必须被实际读取，create_app 也必须使用同一份配置。"""
        env_dir = tmp_path / "env"
        env_dir.mkdir()
        (env_dir / ".env.prod").write_text(
            "\n".join(
                (
                    "SECRET_KEY=real-random-secret-loaded-from-prod-file",
                    "DEBUG=False",
                    "DOCS_ENABLE=False",
                    'ALLOW_ORIGINS=["https://prod.example.com"]',
                    "ALLOW_CREDENTIALS=True",
                    "SERVER_PORT=9123",
                    "DATABASE_TYPE=sqlite",
                    f"DATABASE_NAME={tmp_path / 'runtime'}",
                    "REDIS_ENABLE=False",
                    "STATIC_ENABLE=False",
                )
            ),
            encoding="utf-8",
        )

        script = """
import json
import os
from pathlib import Path

import app.config.path_conf as path_conf

path_conf.ENV_DIR = Path(os.environ["TEST_ENV_DIR"])
from app.config.setting import get_settings, settings
from main import create_app

runtime = get_settings()
app = create_app()
print("CONFIG_RESULT=" + json.dumps({
    "environment": runtime.ENVIRONMENT.value,
    "port": runtime.SERVER_PORT,
    "proxy_port": settings.SERVER_PORT,
    "debug": app.debug,
    "openapi_url": app.openapi_url,
}))
"""
        child_env = os.environ.copy()
        for name in (
            "SECRET_KEY",
            "DEBUG",
            "DOCS_ENABLE",
            "ALLOW_ORIGINS",
            "ALLOW_CREDENTIALS",
            "SERVER_PORT",
            "DATABASE_TYPE",
            "DATABASE_NAME",
            "REDIS_ENABLE",
            "STATIC_ENABLE",
        ):
            child_env.pop(name, None)
        child_env.update(
            {
                "ENVIRONMENT": "prod",
                "PYTHONUTF8": "1",
                "TEST_ENV_DIR": str(env_dir),
            }
        )

        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=str(_BACKEND_DIR),
            env=child_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        result_line = next(
            line for line in result.stdout.splitlines() if line.startswith("CONFIG_RESULT=")
        )
        actual = json.loads(result_line.removeprefix("CONFIG_RESULT="))
        assert actual == {
            "environment": "prod",
            "port": 9123,
            "proxy_port": 9123,
            "debug": False,
            "openapi_url": None,
        }

    def test_cli_rejects_environment_switch_after_database_initialization(
        self, tmp_path: Path
    ) -> None:
        """已创建 dev Engine 的进程不得静默切换为 prod 配置。"""
        script = """
import os
from unittest.mock import patch

os.environ["ENVIRONMENT"] = "dev"
from app.core import database  # noqa: F401
from app.common.enums import EnvironmentEnum
from main import run

try:
    with patch("main.uvicorn.run", return_value=None):
        run(EnvironmentEnum.PROD)
except RuntimeError as exc:
    print("ENV_SWITCH_REJECTED=" + str(exc))
else:
    raise AssertionError("database environment switch was not rejected")
"""
        child_env = os.environ.copy()
        child_env.update(
            {
                "PYTHONUTF8": "1",
                "ENVIRONMENT": "dev",
                "DATABASE_TYPE": "sqlite",
                "DATABASE_NAME": str(tmp_path / "dev-runtime.db"),
                "SECRET_KEY": "real-random-secret-for-config-switch-test",
            }
        )

        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=str(_BACKEND_DIR),
            env=child_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert "ENV_SWITCH_REJECTED=" in result.stdout
        assert "dev" in result.stdout
        assert "prod" in result.stdout
