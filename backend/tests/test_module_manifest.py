"""ModuleManifest Schema 与旧 plugin.toml 兼容读取测试。

覆盖：
- 旧 plugin.toml 兼容读取：映射为 legacy-v0，dependencies/public_interfaces 为空。
- v1 清单校验：必须声明 dependencies 与 public_interfaces。
- JSON Schema 导出：可生成有效 JSON Schema 文件。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.core.module_manifest import (
    CURRENT_SCHEMA_VERSION,
    DependencyDecl,
    ModuleManifest,
    PublicInterfaceDecl,
    export_json_schema,
    load_legacy_plugin_toml,
    validate_manifest_v1,
)

# ============================================================
# 旧 plugin.toml 兼容读取
# ============================================================


class TestLegacyPluginTomlCompat:
    """旧 plugin.toml 必须能映射为 ModuleManifest，标注为 legacy-v0。"""

    @pytest.mark.parametrize(
        "module_dir",
        ["module_ai", "module_example", "module_generator", "module_task"],
    )
    def test_legacy_read_all_plugins(self, module_dir: str) -> None:
        path = Path("app/plugin") / module_dir / "plugin.toml"
        manifest = load_legacy_plugin_toml(path)
        assert manifest.manifest_schema_version == "legacy-v0"
        assert manifest.name != ""
        assert manifest.dependencies == []
        assert manifest.public_interfaces == []

    def test_legacy_missing_name_rejected(self, tmp_path: Path) -> None:
        toml = tmp_path / "plugin.toml"
        toml.write_text('title = "无 name"\n', encoding="utf-8")
        with pytest.raises(ValueError, match="缺失必填 name 字段"):
            load_legacy_plugin_toml(toml)

    def test_legacy_nonexistent_file_rejected(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_legacy_plugin_toml(tmp_path / "no_such.toml")


# ============================================================
# v1 清单校验
# ============================================================


class TestV1ManifestValidation:
    """v1 清单必须声明 dependencies 与 public_interfaces。"""

    def test_v1_missing_both_rejected(self) -> None:
        manifest = ModuleManifest(
            manifest_schema_version=CURRENT_SCHEMA_VERSION,
            name="demo",
        )
        errors = validate_manifest_v1(manifest)
        assert any("dependencies" in e for e in errors)
        assert any("public_interfaces" in e for e in errors)

    def test_v1_with_both_passes(self) -> None:
        manifest = ModuleManifest(
            manifest_schema_version=CURRENT_SCHEMA_VERSION,
            name="demo",
            dependencies=[DependencyDecl(module="module_system", kind="service")],
            public_interfaces=[
                PublicInterfaceDecl(name="DemoService", kind="service"),
            ],
        )
        assert validate_manifest_v1(manifest) == []

    def test_v1_explicit_empty_declarations_pass(self) -> None:
        manifest = ModuleManifest(
            manifest_schema_version=CURRENT_SCHEMA_VERSION,
            name="standalone",
            dependencies=[],
            public_interfaces=[],
        )
        assert validate_manifest_v1(manifest) == []

    def test_legacy_not_subject_to_v1_rules(self) -> None:
        manifest = ModuleManifest(
            manifest_schema_version="legacy-v0",
            name="legacy",
            dependencies=[],
            public_interfaces=[],
        )
        assert validate_manifest_v1(manifest) == []


# ============================================================
# JSON Schema 导出
# ============================================================


class TestJsonSchemaExport:
    """JSON Schema 导出必须生成有效文件。"""

    def test_export_creates_valid_schema(self, tmp_path: Path) -> None:
        out = tmp_path / "manifest.schema.json"
        export_json_schema(out)
        assert out.exists()
        schema = json.loads(out.read_text(encoding="utf-8"))
        assert schema["title"] == "ModuleManifest"
        # 关键字段必须出现在 properties
        props = schema["properties"]
        for key in (
            "manifest_schema_version",
            "name",
            "title",
            "version",
            "dependencies",
            "public_interfaces",
        ):
            assert key in props, f"JSON Schema 缺失字段: {key}"

    def test_committed_schema_matches_pydantic_model(self) -> None:
        committed = json.loads(
            (
                Path(__file__).parent.parent
                / "docs/plantree/baseline/module-manifest.schema.json"
            ).read_text(encoding="utf-8")
        )
        assert committed == ModuleManifest.model_json_schema(), (
            "提交的 JSON Schema 已漂移；请重新运行 export_json_schema"
        )
