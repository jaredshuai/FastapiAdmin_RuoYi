# RuoYi 上游参考源码

本目录保存平台建设过程中使用的上游参考代码。它们用于核对业务规则、权限边界、接口行为和前后端联动，不属于本项目的运行时依赖，也不参与本项目的构建、测试和发布。

## 固定版本

| 目录 | 上游仓库 | 版本 | 固定提交 |
| --- | --- | --- | --- |
| `ruoyi-vue-plus/` | <https://gitee.com/dromara/RuoYi-Vue-Plus.git> | `v5.6.2` | `8136a0191a2258c0e1b36a8146a1c5ebc070c139` |
| `plus-ui/` | <https://gitee.com/JavaLionLi/plus-ui.git> | `v5.6.2-v2.6.2` | `d0d451967676707021b9857df529c395b27e90a7` |

## 获取源码

首次克隆本项目时使用：

```powershell
git clone --recurse-submodules <本项目仓库地址>
```

已有工作区补齐参考源码时使用：

```powershell
git submodule update --init --recursive
```

## 使用规则

- 参考目录只读；本项目实现仍位于 `backend/` 和 `frontend/`。
- 对标某项能力时，记录参考仓库、版本或提交、源码路径，以及采用、适配、推迟或拒绝的结论。
- 不直接照搬 Java/Spring 实现；先提取业务语义和验收场景，再用 FastAPI、SQLAlchemy 和 Vue 的惯用方式实现。
- 两个参考仓库应分别建立代码索引，不与本项目索引混合，避免同名符号和调用关系相互污染。
- 参考源码不进入本项目的 lint、测试、构建、镜像和发布范围。

## 更新版本

只在里程碑评审、安全修复或明确业务对标需要时更新。不要直接跟随 `5.X` 分支最新提交，应选择发布标签并评审差异：

```powershell
git -C references/ruoyi-vue-plus fetch --tags
git -C references/ruoyi-vue-plus checkout <目标标签>

git -C references/plus-ui fetch --tags
git -C references/plus-ui checkout <匹配的目标标签>
```

更新后同步修改本文件中的版本和提交，并把两个 submodule 指针作为一次独立变更提交。
