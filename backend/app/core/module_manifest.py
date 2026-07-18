"""模块清单（ModuleManifest）Pydantic Schema 与旧 plugin.toml 兼容读取。

Phase 1 前置：定义 Schema 与 JSON Schema 导出，但不做装配器、不改目录、
不强制所有 plugin.toml 升级；旧 plugin.toml 通过兼容读取器映射为新 Schema。

旧 plugin.toml 字段映射：
- name        → name
- title       → title
- version     → version
- description → description
- optional    → optional
- tags        → tags
- 缺失字段      → Schema 默认值（manifest_schema_version="legacy-v0"，无依赖/接口声明）

后续 Phase 2 引入装配器后，新模块必须用 manifest_schema_version="v1" 声明依赖与公共接口。
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# 旧 plugin.toml 兼容标识：不声明 manifest_schema_version 的文件一律视为 legacy
_LEGACY_SCHEMA_VERSION = "legacy-v0"

# 新模块推荐版本（Phase 2 装配器消费）
CURRENT_SCHEMA_VERSION = "v1"


class PublicInterfaceDecl(BaseModel):
    """公共接口声明 — 模块对外暴露的稳定调用面。

    Phase 2 装配器据此判定模块间允许的调用边界。
    """

    model_config = ConfigDict(use_enum_values=True)

    name: str = Field(description="接口名（如 OrderService）")
    kind: str = Field(description="接口类型（service / router / model / util）")
    public_methods: list[str] = Field(
        default_factory=list,
        description="对外暴露的方法名清单；空列表表示全部公开",
    )


class DependencyDecl(BaseModel):
    """依赖声明 — 模块显式声明的对内/对外依赖。"""

    model_config = ConfigDict(use_enum_values=True)

    module: str = Field(description="被依赖模块名（如 module_system）")
    kind: str = Field(description="依赖类型（service / model / util）")
    optional: bool = Field(default=False, description="是否可选依赖")


class ModuleManifest(BaseModel):
    """模块清单 Schema — 单个模块的元数据与边界声明。

    新模块必须用 manifest_schema_version="v1" 声明依赖与公共接口；
    旧 plugin.toml 经兼容读取器映射为 manifest_schema_version="legacy-v0"。
    """

    model_config = ConfigDict(use_enum_values=True, extra="forbid")

    manifest_schema_version: str = Field(
        default=_LEGACY_SCHEMA_VERSION,
        description="清单 Schema 版本（legacy-v0 / v1）",
    )
    name: str = Field(description="模块名（与目录名 module_<name> 一致）")
    title: str = Field(default="", description="展示标题")
    version: str = Field(default="0.0.0", description="模块版本")
    description: str = Field(default="", description="模块描述")
    optional: bool = Field(default=True, description="是否可选模块")
    tags: list[str] = Field(default_factory=list, description="标签")
    dependencies: list[DependencyDecl] = Field(
        default_factory=list,
        description="显式依赖声明（v1 必填，legacy-v0 一律为空）",
    )
    public_interfaces: list[PublicInterfaceDecl] = Field(
        default_factory=list,
        description="公共接口声明（v1 必填，legacy-v0 一律为空）",
    )


def load_legacy_plugin_toml(path: Path) -> ModuleManifest:
    """兼容读取旧 plugin.toml，映射为 ModuleManifest。

    旧 plugin.toml 无 manifest_schema_version、无依赖/接口声明，
    读取后一律标记为 legacy-v0，dependencies 与 public_interfaces 为空。

    参数:
        path: plugin.toml 文件路径。

    返回:
        ModuleManifest: 兼容映射后的清单实例。

    异常:
        FileNotFoundError: 文件不存在。
        ValueError: TOML 解析失败或缺失必填 name 字段。
    """
    if not path.exists():
        raise FileNotFoundError(f"plugin.toml 不存在: {path}")

    try:
        with open(path, "rb") as f:
            raw: dict[str, Any] = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"解析 {path} 失败: {e!s}") from e

    if "name" not in raw or not raw["name"]:
        raise ValueError(f"{path} 缺失必填 name 字段")

    # 旧 plugin.toml 无 manifest_schema_version，一律视为 legacy
    raw.setdefault("manifest_schema_version", _LEGACY_SCHEMA_VERSION)

    # 旧文件无 dependencies / public_interfaces，显式置空避免 extra="forbid" 拒绝
    raw.setdefault("dependencies", [])
    raw.setdefault("public_interfaces", [])

    return ModuleManifest(**raw)


def export_json_schema(output_path: Path) -> None:
    """导出 ModuleManifest 的 JSON Schema 至文件。

    供外部工具校验新模块 manifest 文件使用。

    参数:
        output_path: JSON Schema 输出路径。

    返回:
        None
    """
    schema = ModuleManifest.model_json_schema()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)


def validate_manifest_v1(manifest: ModuleManifest) -> list[str]:
    """校验 v1 清单的额外约束：必须声明依赖与公共接口。

    参数:
        manifest: 已加载的清单实例。

    返回:
        list[str]: 校验错误清单；空列表表示通过。
    """
    errors: list[str] = []
    if manifest.manifest_schema_version != CURRENT_SCHEMA_VERSION:
        # legacy-v0 不做 v1 专属校验
        return errors

    if "dependencies" not in manifest.model_fields_set:
        errors.append("v1 清单必须声明 dependencies（无依赖时显式写空列表）")
    if "public_interfaces" not in manifest.model_fields_set:
        errors.append("v1 清单必须声明 public_interfaces（无公开接口时显式写空列表）")
    return errors
