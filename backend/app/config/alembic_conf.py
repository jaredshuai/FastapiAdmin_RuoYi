"""与当前工作目录无关的 Alembic 配置入口。"""

from alembic.config import Config

from app.config.path_conf import BASE_DIR


def get_alembic_config() -> Config:
    """返回使用绝对配置和迁移目录的 Alembic Config。"""
    config = Config(str(BASE_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BASE_DIR / "app" / "alembic"))
    return config
