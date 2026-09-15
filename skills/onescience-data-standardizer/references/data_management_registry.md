# `~/.onescience/data_management.json` 注册表规范

## 文件位置

固定为：`~/.onescience/data_management.json`

- Windows: `%USERPROFILE%\.onescience\data_management.json`
- POSIX: `$HOME/.onescience/data_management.json`

`~/.onescience/` 目录不存在时自动创建（`os.makedirs(exist_ok=True, mode=0o755)`）。

## Schema

顶层对象包含 `version` 与 `datasets` 数组：

```json
{
  "version": 1,
  "datasets": [
    {
      "name": "ERA5",
      "domain": "climate",
      "source_dir": "/public/share/onestore/onedatasets/ERA5",
      "target_dir": "/home/user/onedata/era5-ai-ready",
      "handler": "adapter:climate/era5",
      "created_at": "2026-09-14T16:20:00Z",
      "updated_at": "2026-09-14T16:20:00Z",
      "checksum": "sha256:abcdef...",
      "source_resolution_method": "local_probe",
      "modelscope_repo_id": null,
      "dataset_card_path": "/home/user/onedata/era5-ai-ready/dataset_card.json",
      "dataset_report_called": true,
      "notes": null
    }
  ]
}
```

## 字段说明

| 字段 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 数据集名，合并写入时的**唯一键** |
| `domain` | string | 是 | `cfd` \| `bio` \| `climate` \| `matchem`（别名已归一化） |
| `source_dir` | string | 是 | raw 数据绝对路径 |
| `target_dir` | string | 是 | AI-Ready 数据绝对路径 |
| `handler` | string | 是 | `adapter:<domain>/<name>` 或 `llm_synth:v1` |
| `created_at` | string | 是 | 首次注册时间，ISO8601 UTC |
| `updated_at` | string | 是 | 最近更新时间，ISO8601 UTC |
| `checksum` | string\|null | 否 | AI-Ready 目录聚合 sha256，前缀 `sha256:` |
| `source_resolution_method` | string | 是 | `explicit` \| `local_probe` \| `modelscope_download` |
| `modelscope_repo_id` | string\|null | 否 | 若通过下载获取，记录 repo id |
| `dataset_card_path` | string | 是 | `<target_dir>/dataset_card.json` 绝对路径 |
| `dataset_report_called` | bool | 是 | 是否成功调用宿主 `dataset_report` 工具 |
| `notes` | string\|null | 否 | 人工备注 |

**与用户示例的兼容性**：用户示例中的最小 payload `{name, target_dir}` 是本 schema 的**真子集**；`dataset_report` 调用时使用 `{name, target_dir, source_dir}` 三字段（详见 [dataset_report_probe.md](./dataset_report_probe.md)）。

## 合并写入规则

由 `scripts/registry.py::upsert` 实现：

1. **读取**：若文件不存在，视为 `{"version": 1, "datasets": []}`；若存在但 JSON 损坏，备份为 `data_management.json.corrupt.<timestamp>` 后重建。
2. **定位**：按 `name` 精确匹配查找现有条目。
3. **更新或追加**：
   - 命中：更新所有可变字段（`source_dir` / `target_dir` / `handler` / `updated_at` / `checksum` / `source_resolution_method` / `modelscope_repo_id` / `dataset_card_path` / `dataset_report_called`），**保留** `created_at` 与 `notes`。
   - 未命中：append 新条目，`created_at == updated_at == now()`。
4. **原子写入**：先写 `data_management.json.tmp.<pid>` → `os.replace()` 到目标路径。
5. **文件锁**：使用 `~/.onescience/.data_management.lock` 独占锁（`fcntl.flock` on POSIX / `msvcrt.locking` on Windows），超时 30 秒后放弃并抛出 `RegistryLockTimeout`。

## 并发场景

- 多个 orchestrator 会话同时注册不同数据集 → 通过文件锁串行化，全部成功。
- 多个会话同时注册同一数据集 → 后写入者覆盖前者（按 `updated_at` 排序），保留最新状态。
- 注册过程崩溃 → `.tmp.<pid>` 文件残留，主文件不受影响；下次启动时可清理。

## 查询接口

`scripts/registry.py` 提供：

- `list_datasets() -> list[dict]`：返回全部条目。
- `get_dataset(name: str) -> dict | None`：按 name 查询。
- `upsert(entry: dict) -> dict`：合并写入，返回写入后的完整条目。
- `remove(name: str) -> bool`：按 name 删除（用于清理失败注册）。

## 迁移与版本

- 当前 schema `version=1`。
- 未来 schema 变更时递增 `version`，并在 `registry.py::_migrate` 中添加从旧版到新版的路径。
- 读取时若 `version` 高于当前支持版本，抛出 `RegistryVersionError` 并提示升级技能。

## 与 dataset_card.json 的关系

- `dataset_card.json` 位于 `<target_dir>/`，包含**完整**转换上下文与质量校验结果。
- `data_management.json` 是**索引层**，只保留最小可查询字段，避免文件膨胀。
- 需要详细信息时通过 `dataset_card_path` 跳转到具体 card。

## 诊断命令

主入口 `scripts/standardize.py` 提供子命令：

```bash
# 列出所有已注册数据集
python scripts/standardize.py registry list

# 查询指定数据集
python scripts/standardize.py registry get --name ERA5

# 移除条目（不删除文件）
python scripts/standardize.py registry remove --name ERA5

# 校验注册表完整性（checksum、路径存在性）
python scripts/standardize.py registry verify
```
