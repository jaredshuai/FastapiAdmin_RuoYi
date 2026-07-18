import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, cast
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.common.enums import EnvironmentEnum
from app.config.path_conf import BASE_DIR, ENV_DIR

# 已知不安全占位符族：任一片段出现在 SECRET_KEY 中即视为未配置，
# 因而 `change-me-to-a-real-secret` 这类在占位符后追加文本的值也会被拒绝。
_INSECURE_SECRET_PLACEHOLDERS: tuple[str, ...] = (
    "vgb0tnl9d58+6n-6h-ea&u^1#s0ccp!794=krylxcjq75vzps$",
    "change-me",
    "changeme",
    "CHANGE_ME",
    "CHANGE-ME",
)


class Settings(BaseSettings):
    """系统配置类"""

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,  # 区分大小写
    )

    # ================================================= #
    # ******************* 项目环境 ****************** #
    # ================================================= #
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.DEV

    # ================================================= #
    # ******************* 服务器配置 ****************** #
    # ================================================= #
    SERVER_HOST: str = "0.0.0.0"  # 允许访问的IP地址
    SERVER_PORT: int = 8001  # 服务端口

    # ================================================= #
    # ******************* API文档配置 ****************** #
    # ================================================= #
    DEBUG: bool = True  # 调试模式
    TITLE: str = "🎉 FastapiAdmin 🎉 "  # 文档标题
    VERSION: str = "0.1.0"  # 版本号
    DESCRIPTION: str = "后台接口文档"  # 文档描述
    SUMMARY: str = "接口汇总"  # 文档概述
    DOCS_URL: str = "/docs"  # Swagger UI路径
    REDOC_URL: str = "/redoc"  # ReDoc路径
    ROOT_PATH: str = "/api/v1"  # API路由前缀
    # 是否启用 API 文档（/docs /redoc /openapi.json）；生产环境必须关闭
    DOCS_ENABLE: bool = True

    # ================================================= #
    # ******************** 日志配置 ******************** #
    # ================================================= #
    LOGGER_LEVEL: str = "DEBUG"  # 日志级别

    # ================================================= #
    # ******************** 跨域配置 ******************** #
    # ================================================= #
    CORS_ORIGIN_ENABLE: bool = True  # 是否启用跨域
    ALLOW_ORIGINS: list[str] = ["*"]  # 允许的域名列表
    ALLOW_METHODS: list[str] = ["*"]  # 允许的HTTP方法
    ALLOW_HEADERS: list[str] = ["*"]  # 允许的请求头
    ALLOW_CREDENTIALS: bool = True  # 是否允许携带cookie
    CORS_EXPOSE_HEADERS: list[str] = ["X-Request-ID"]

    # ================================================= #
    # ******************* 登录认证配置 ****************** #
    # ================================================= #
    # JWT 密钥：必须由环境变量提供，不接受源码默认值
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"  # JWT算法
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 12  # access_token过期时间(秒)12 小时
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 12  # refresh_token过期时间(秒)12 小时
    TOKEN_TYPE: str = "Bearer"  # token类型（RFC 6750 标准大小写）
    TOKEN_SLIDING_EXPIRE: bool = True  # 是否启用滑动过期(用户操作时自动续期)

    # 多租户中间件白名单路径（不需要租户上下文的公开接口）
    TENANT_WHITELIST_PATHS: list[str] = [
        "/api/v1/system/auth/",
        "/api/v1/health",
        "/api/v1/common/health",
    ]

    # ================================================= #
    # ******************* 支付配置 ******************* #
    # ================================================= #
    # 支付宝
    PAYMENT_ALIPAY_APP_ID: str = ""
    PAYMENT_ALIPAY_PRIVATE_KEY: str = ""
    PAYMENT_ALIPAY_PUBLIC_KEY: str = ""
    PAYMENT_ALIPAY_SANDBOX: bool = True
    # 站点 URL（用于生成支付通知 URL）
    SITE_URL: str = "http://localhost:8001"

    # ================================================= #
    # ******************** 数据库配置 ******************* #
    # ================================================= #
    SQL_DB_ENABLE: bool = True  # 是否启用数据库
    DATABASE_ECHO: bool | Literal["debug"] = False  # 是否显示SQL日志
    ECHO_POOL: bool | Literal["debug"] = False  # 是否显示连接池日志
    POOL_SIZE: int = 10  # 连接池大小
    MAX_OVERFLOW: int = 20  # 最大溢出连接数
    POOL_TIMEOUT: int = 30  # 连接超时时间(秒)
    POOL_RECYCLE: int = 1800  # 连接回收时间(秒)
    POOL_USE_LIFO: bool = True  # 是否使用LIFO连接池
    POOL_PRE_PING: bool = True  # 是否开启连接预检
    FUTURE: bool = True  # 是否使用SQLAlchemy 2.0特性
    AUTOCOMMIT: bool = False  # 是否自动提交（映射 SQLAlchemy sessionmaker(autocommit=...)）
    AUTOFLUSH: bool = False  # 是否自动刷新（映射 SQLAlchemy sessionmaker(autoflush=...)）
    AUTOFETCH: bool | None = None  # AUTOFLUSH 别名（优先级高于 AUTOFLUSH，兼容旧环境变量名）
    EXPIRE_ON_COMMIT: bool = False  # 是否在提交时过期

    # MySQL/PostgreSQL数据库连接
    DATABASE_TYPE: Literal["mysql", "postgres", "sqlite"] = "mysql"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = ""
    DATABASE_NAME: str = "fastapiadmin"

    # ================================================= #
    # ******************** Redis配置 ******************* #
    # ================================================= #
    REDIS_ENABLE: bool = True  # 是否启用Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB_NAME: int = 1
    REDIS_USER: str = ""
    REDIS_PASSWORD: str = ""

    # ================================================= #
    # ******************** 验证码配置 ******************* #
    # ================================================= #
    CAPTCHA_ENABLE: bool = True  # 是否启用验证码
    CAPTCHA_EXPIRE_SECONDS: int = 60 * 1  # 验证码过期时间(秒) 1分钟
    CAPTCHA_FONT_SIZE: int = 32  # 字体大小
    CAPTCHA_FONT_PATH: str = "static/assets/font/Arial.ttf"  # 字体路径

    # ================================================= #
    # ***************** 第三方 OAuth 登录（可选）********* #
    # ================================================= #
    # 自动注册用户的默认角色 ID 列表（须与库中角色主键一致）
    OAUTH_DEFAULT_ROLE_IDS: list[int] = [2]
    # 回调异常时回跳的前端地址（与前端实际 /login 一致，含协议与端口）
    OAUTH_FRONTEND_FALLBACK: str = "http://127.0.0.1:5173/login"
    OAUTH_GITHUB_CLIENT_ID: str = ""
    OAUTH_GITHUB_CLIENT_SECRET: str = ""
    OAUTH_GITEE_CLIENT_ID: str = ""
    OAUTH_GITEE_CLIENT_SECRET: str = ""
    OAUTH_WECHAT_OPEN_APP_ID: str = ""
    OAUTH_WECHAT_OPEN_APP_SECRET: str = ""
    OAUTH_QQ_APP_ID: str = ""
    OAUTH_QQ_APP_SECRET: str = ""

    # ================================================= #
    # ******************* 外部 HTTP（httpx）******************* #
    # ================================================= #
    HTTPX_DEFAULT_TIMEOUT: float = 10.0  # 对外 HTTP 请求默认超时（秒）
    IP_LOCATION_ENABLE: bool = True  # 是否启用 IP 归属地查询（登录时对外发起 HTTP 请求）

    # ================================================= #
    # ********************* 日志配置 ******************* #
    # ================================================= #
    OPERATION_LOG_RECORD: bool = True  # 是否记录操作日志
    OPERATION_RECORD_METHOD: list[str] = [
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "HEAD",
        "OPTIONS",
    ]  # 需要记录的请求方法

    # ================================================= #
    # ******************* Gzip压缩配置 ******************* #
    # ================================================= #
    GZIP_ENABLE: bool = True  # 是否启用Gzip
    GZIP_MIN_SIZE: int = 1000  # 最小压缩大小(字节)
    GZIP_COMPRESS_LEVEL: int = 9  # 压缩级别(1-9)

    # ================================================= #
    # ***************** 静态文件配置 ***************** #
    # ================================================= #
    STATIC_ENABLE: bool = True  # 是否启用静态文件
    STATIC_URL: str = "/static"  # 访问路由
    STATIC_DIR: str = "static"  # 目录名
    STATIC_ROOT: Path = BASE_DIR.joinpath(STATIC_DIR)  # 绝对路径

    # ================================================= #
    # ***************** 动态文件配置 ***************** #
    # ================================================= #
    UPLOAD_FILE_PATH: Path = Path("static/upload")  # 上传目录
    UPLOAD_MACHINE: str = "A"  # 上传机器标识
    ALLOWED_EXTENSIONS: list[str] = [  # 允许的文件类型
        ".gif",
        ".jpg",
        ".jpeg",
        ".png",
        ".ico",
        ".svg",
        ".xls",
        ".xlsx",
    ]
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 最大文件大小(10MB)

    # ================================================= #
    # ***************** Swagger配置 ***************** #
    # ================================================= #
    SWAGGER_CSS_URL: str = "static/swagger/swagger-ui/swagger-ui.css"
    SWAGGER_JS_URL: str = "static/swagger/swagger-ui/swagger-ui-bundle.js"
    REDOC_JS_URL: str = "static/swagger/redoc/bundles/redoc.standalone.js"
    FAVICON_URL: str = "static/image/favicon.ico"

    # ================================================= #
    # ******************* AI大模型配置 ****************** #
    # ================================================= #
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = ""
    OPENAI_BASE_URL: str = ""  # API Base URL，如 https://api.minimax.chat/v1

    # ================================================= #
    # ******************* 请求限制配置 ****************** #
    # ================================================= #
    REQUEST_LIMITER_REDIS_PREFIX: str = "fastapiadmin:request_limiter:"

    # ================================================= #
    # ******************* 动态配置 ******************* #
    # ================================================= #
    @property
    def MIDDLEWARE_LIST(self) -> list[str | None]:
        # 中间件列表（注册时逆序叠加：下列第一项在列表中最前，最终位于最外层，优先生效）
        # 中间件执行顺序（从外到内）：
        #   CORS → RequestLog → GZip → CorrelationId → 业务路由
        # 安全响应头（X-Content-Type-Options / Referrer-Policy / Permissions-Policy / HSTS）
        # 由前置 Nginx / 反向代理通过 add_header 设置，避免应用层 BaseHTTPMiddleware 开销。
        MIDDLEWARES: list[str | None] = [
            "app.core.middlewares.CustomCORSMiddleware" if self.CORS_ORIGIN_ENABLE else None,
            "app.core.middlewares.RequestLogMiddleware" if self.OPERATION_LOG_RECORD else None,
            "app.core.middlewares.CustomGZipMiddleware" if self.GZIP_ENABLE else None,
            "app.core.middlewares.CorrelationIdMiddleware",  # 请求上下文
            "app.core.middlewares.TenantMiddleware",  # 租户上下文（需 JWT）
        ]
        return MIDDLEWARES

    @property
    def EVENT_LIST(self) -> list[str | None]:
        EVENTS: list[str | None] = [
            "app.core.database.redis_connect" if self.REDIS_ENABLE else None,
        ]
        return EVENTS

    @property
    def ASYNC_DB_URI(self) -> str:
        if self.DATABASE_TYPE not in ("mysql", "postgres", "sqlite"):
            raise ValueError(
                f"数据库驱动不支持: {self.DATABASE_TYPE}, 异步数据库请选择 mysql、postgres、sqlite"
            )
        db_connect: str = ""
        if self.DATABASE_TYPE == "mysql":
            db_connect = f"mysql+asyncmy://{self.DATABASE_USER}:{quote_plus(self.DATABASE_PASSWORD)}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}?charset=utf8mb4"
        elif self.DATABASE_TYPE == "postgres":
            db_connect = f"postgresql+asyncpg://{self.DATABASE_USER}:{quote_plus(self.DATABASE_PASSWORD)}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        else:
            db_connect = f"sqlite+aiosqlite:///{self.DATABASE_NAME}.db"
        return db_connect

    @property
    def DB_URI(self) -> str:
        if self.DATABASE_TYPE not in ("mysql", "postgres", "sqlite"):
            raise ValueError(
                f"数据库驱动不支持: {self.DATABASE_TYPE}, 同步数据库请选择 mysql、postgres、sqlite"
            )
        db_connect: str = ""
        if self.DATABASE_TYPE == "mysql":
            db_connect = f"mysql+pymysql://{self.DATABASE_USER}:{quote_plus(self.DATABASE_PASSWORD)}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}?charset=utf8mb4"
        elif self.DATABASE_TYPE == "postgres":
            db_connect = f"postgresql+psycopg://{self.DATABASE_USER}:{quote_plus(self.DATABASE_PASSWORD)}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        else:
            db_connect = f"sqlite:///{self.DATABASE_NAME}.db"
        return db_connect

    @property
    def FASTAPI_CONFIG(self) -> dict[str, Any]:
        return {
            "debug": self.DEBUG,
            "title": self.TITLE,
            "version": self.VERSION,
            "description": self.DESCRIPTION,
            "summary": self.SUMMARY,
            "docs_url": None,
            "redoc_url": None,
            "openapi_url": "/openapi.json" if self.DOCS_ENABLE else None,
            "root_path": self.ROOT_PATH,
            "responses": {
                200: {"description": "成功"},
                400: {"description": "请求参数错误"},
                401: {"description": "未认证"},
                403: {"description": "未授权"},
                404: {"description": "资源不存在"},
                422: {"description": "请求参数验证错误"},
                500: {"description": "服务器内部错误"},
            },
        }

    def validate_runtime_config(self) -> None:
        """运行时配置校验。

        通用约束：
        - SECRET_KEY 必须由环境变量提供；空值或已知占位符直接失败。
        - ALLOW_ORIGINS=["*"] 与 ALLOW_CREDENTIALS=True 组合违反浏览器安全规范，禁止。

        生产环境（ENVIRONMENT == prod）额外约束：
        - DEBUG 必须为 False。
        - DOCS_ENABLE 必须为 False；/docs、/redoc、/openapi.json 不应暴露。
        - CORS 白名单不允许包含 "*"；必须填写实际前端域名。

        参数:
            self: Settings 实例。

        异常:
            RuntimeError: 任一校验失败时抛出，包含具体不满足的约束。
        """
        errors: list[str] = []

        # 通用：SECRET_KEY 必须真实
        secret = self.SECRET_KEY or ""
        if not secret:
            errors.append("SECRET_KEY 未设置：必须通过环境变量提供真实密钥")
        elif any(placeholder in secret for placeholder in _INSECURE_SECRET_PLACEHOLDERS):
            errors.append("SECRET_KEY 为已知不安全占位符：必须替换为真实密钥")

        # 通用：CORS 通配符 + 凭证组合禁止
        if "*" in self.ALLOW_ORIGINS and self.ALLOW_CREDENTIALS:
            errors.append(
                "ALLOW_ORIGINS=['*'] 与 ALLOW_CREDENTIALS=True 组合违反浏览器安全规范"
            )

        is_prod = self.ENVIRONMENT == EnvironmentEnum.PROD

        # 生产专属
        if is_prod:
            if self.DEBUG:
                errors.append("生产环境 DEBUG 必须为 False")
            if self.DOCS_ENABLE:
                errors.append("生产环境 DOCS_ENABLE 必须为 False")
            if "*" in self.ALLOW_ORIGINS:
                errors.append(
                    "生产环境 ALLOW_ORIGINS 不允许包含 '*'；必须填写实际前端域名"
                )

        if errors:
            raise RuntimeError(
                "运行时配置校验失败：\n  - " + "\n  - ".join(errors)
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    environment = os.getenv("ENVIRONMENT", EnvironmentEnum.DEV.value)
    env_file = ENV_DIR / f".env.{environment}"
    return Settings(_env_file=env_file)


class _SettingsProxy:
    """始终转发到当前缓存的 Settings，避免模块级旧实例锁死环境。"""

    def __getattr__(self, name: str) -> Any:
        return getattr(get_settings(), name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(get_settings(), name, value)


settings = cast(Settings, _SettingsProxy())
