# 源数据解析规则（三段式）

本技能对 raw 数据集来源采用**严格顺序**的三段式解析，命中一段即停止后续段落。

## 段 1：显式路径

`step_handoff.task_context.source_dir` 非空时进入本段。

**校验步骤**：
1. 路径存在（`os.path.exists`）；不存在 → `status=failed, blocked_reason=source_dir_invalid, blocked_details="path does not exist: <source_dir>"`。
2. 是目录（`os.path.isdir`）；不是 → 同上，`blocked_details="path is not a directory"`。
3. 目录非空（`os.listdir` 结果非空）；空 → `status=failed, blocked_reason=source_dir_invalid, blocked_details="directory is empty"`。
4. 目录可读（尝试 `os.stat`）；不可读 → `blocked_details="permission denied"`。

**归一化**：将路径转为绝对路径（`os.path.abspath` + `os.path.realpath` 处理符号链接），写入 `execution_result.artifacts.source_dir`。

## 段 2：本地探测

段 1 未触发或校验失败但未强制 fail 时进入。**探测顺序**（严格从上到下，命中即返回）：

| 优先级 | 路径模板 | 说明 |
|---|---|---|
| 1 | `${ONESCIENCE_DATASETS_DIR}/<dataset_name>` | 项目级挂载根 |
| 2 | `${ONESCIENCE_DATASETS_DIR}/<domain>/<dataset_name>` | 分 domain 组织 |
| 3 | `${ONESCIENCE_DATASETS_DIR}/<domain>/<dataset_name_lowercase>` | 大小写归一化回退 |
| 4 | `~/.onescience/datasets/<dataset_name>/raw` | 本技能下载缓存约定 |
| 5 | `~/.onescience/datasets/<dataset_name>` | 手工放置 |
| 6 | `/public/share/onestore/onedatasets/<dataset_name>` | 集群共享存储 |
| 7 | `/public/share/onestore/onedatasets/<domain>/<dataset_name>` | 集群共享存储分 domain |
| 8 | `./<dataset_name>` | 当前工作目录 |
| 9 | `./data/<dataset_name>` | 当前工作目录 data 子目录 |

**探测规则**：
- 每个候选路径必须同时满足：存在 + 是目录 + 非空 + 可读，才算命中。
- `ONESCIENCE_DATASETS_DIR` 未设置时跳过 1-3 项。
- 所有探测过的路径必须记录到 `execution_result.observation.source_resolution.probed_paths`，无论命中与否，便于诊断。
- 命中时 `source_resolution.method = "local_probe"`。

**大小写与别名**：
- `dataset_name` 保留原始大小写用于路径 1、4、5、6、8、9。
- 路径 3、7 额外尝试 `<dataset_name_lowercase>`。
- domain 别名映射：`earth → climate`；`materials → matchem`；`biology / bioinformatics → bio`；`fluid / fluids → cfd`。

## 段 3：ModelScope 下载

段 1、段 2 均未命中时进入。

**门控**：
- `task_context.allow_download == true` 或 `execution_flags.autonomous_mode == true` → 直接进入下载流程。
- 否则 → `status=blocked, blocked_reason=raw_dataset_not_found`，`blocked_details` 必须包含：
  - 完整的 `probed_paths` 清单；
  - 建议的 ModelScope repo id（详见 `download_workflow.md::infer_repo_id`）；
  - 提示用户"设置 `allow_download=true` 或提供 `source_dir` 后重试"。

**下载完成后**：
- 缓存目录固定为 `~/.onescience/datasets/<dataset_name>/raw/`。
- `source_resolution.method = "modelscope_download"`。
- `source_dir` 归一化为缓存目录绝对路径。

## 特殊情形

### 数据集包含多个子集

例如 OC20 同时包含 `s2ef_200k_uncompressed`、`s2ef_val_id_uncompressed`、`uma_oc20_finetune`。此时 `source_dir` 应指向**父目录**，由 adapter/converter 内部识别子目录，不做二次探测。

### 符号链接与挂载点

`os.path.realpath` 会解析符号链接。若解析后路径不在探测清单中，仍以解析后的路径为准写入 `artifacts.source_dir`，但在 `observation.risks` 中标注 `symlink_resolved: <original> -> <resolved>`。

### 只读文件系统

若探测命中但目录不可写，不影响本技能（本技能只读 raw，写 target）。但若 `target_dir` 落在只读位置，会在阶段 4 前置校验中抛出 `status=failed, blocked_reason=target_dir_not_writable`。

## 返回结构

`execution_result.observation.source_resolution` 必须包含：

```yaml
source_resolution:
  method: explicit | local_probe | modelscope_download
  resolved_path: <绝对路径>
  probed_paths:
    - path: <候选路径>
      exists: <bool>
      is_dir: <bool>
      non_empty: <bool>
      readable: <bool>
      hit: <bool>
  download_details:   # 仅 method=modelscope_download 时
    repo_id: <modelscope repo id>
    cache_dir: <本地缓存目录>
    bytes_downloaded: <int>
    duration_seconds: <float>
```
