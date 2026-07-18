"""Alembic 启动路径和存量数据库保护测试。"""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from app.config.alembic_conf import get_alembic_config
from app.scripts.initialize import InitializeData

_BACKEND_DIR = Path(__file__).parent.parent
_REPO_ROOT = _BACKEND_DIR.parent


def _sqlite_engine(tmp_path: Path, name: str):
    return create_engine(f"sqlite:///{tmp_path / name}")


def test_alembic_config_is_independent_of_current_working_directory() -> None:
    config = get_alembic_config()
    assert Path(config.config_file_name).is_absolute()
    assert Path(config.get_main_option("script_location")).is_absolute()
    assert Path(config.config_file_name).name == "alembic.ini"


def test_upgrade_rejects_nonempty_database_without_alembic_version(
    tmp_path: Path,
) -> None:
    engine = _sqlite_engine(tmp_path, "legacy.db")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE legacy_table (id INTEGER PRIMARY KEY)"))

    with pytest.raises(RuntimeError, match="stamp --env"):
        InitializeData.assert_migration_state(engine)


def test_upgrade_accepts_empty_database(tmp_path: Path) -> None:
    engine = _sqlite_engine(tmp_path, "empty.db")
    InitializeData.assert_migration_state(engine)


def test_stamp_rejects_schema_that_is_not_equivalent(tmp_path: Path) -> None:
    engine = _sqlite_engine(tmp_path, "partial.db")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE sys_user (id INTEGER PRIMARY KEY)"))

    with pytest.raises(RuntimeError, match="结构不等价"):
        InitializeData.assert_legacy_schema_equivalent(engine)


def test_upgrade_runs_from_repository_root(tmp_path: Path) -> None:
    database_name = tmp_path / "root-upgrade"
    child_env = os.environ.copy()
    child_env.update(
        {
            "ENVIRONMENT": "dev",
            "PYTHONUTF8": "1",
            "SECRET_KEY": "real-random-secret-for-migration-test",
            "ALLOW_ORIGINS": '["https://test.example.com"]',
            "ALLOW_CREDENTIALS": "True",
            "DATABASE_TYPE": "sqlite",
            "DATABASE_NAME": str(database_name),
            "REDIS_ENABLE": "False",
        }
    )
    result = subprocess.run(
        [sys.executable, str(_BACKEND_DIR / "main.py"), "upgrade", "--env=dev"],
        cwd=str(_REPO_ROOT),
        env=child_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    with sqlite3.connect(f"{database_name}.db") as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    assert "alembic_version" in tables
    assert "sys_user" in tables
